"""Deterministic assessment: a pure function of case state, pack and date."""

import hashlib
import json
from datetime import date
from typing import Any

from repermit.knowledge import Pack, Rule
from repermit.state import CaseState

DISCLAIMER = (
    "RePermit does not issue government permits, certify engineering compliance or substitute for "
    "competent-authority decisions. Its rules do not represent complete Dubai Municipality/BPS decision logic."
)
DOMAIN_ORDER = {"not_affected": 0, "potentially_affected": 1, "affected": 2}


def evaluate(when: dict[str, Any], context: dict[str, Any]) -> tuple[bool | None, list[str]]:
    """Three-valued match: True, False, or None with the unknown fact names."""
    unknown = []
    for name, expected in when.items():
        if name not in context:
            unknown.append(name)
        elif context[name] not in (expected if isinstance(expected, list) else [expected]):
            return False, []
    return (None, unknown) if unknown else (True, [])


def collect_facts(state: CaseState) -> tuple[dict[str, Any], list[dict]]:
    seen: dict[str, list[Any]] = {}
    for name, value in state.modification["facts"].items():
        seen.setdefault(name, []).append(value)
    for item in state.latest_evidence():
        if item["status"] == "current":
            for name, value in item["facts"].items():
                seen.setdefault(name, []).append(value)

    facts, deficiencies = {}, []
    for name, values in seen.items():
        if all(value == values[0] for value in values):
            facts[name] = values[0]
        else:
            deficiencies.append(
                {"code": "inconsistent_fact", "domain": None, "subject": name, "detail": f"Contradictory values for {name}."}
            )
    return facts, deficiencies


def find_conflicts(rules: list[Rule], state: CaseState) -> tuple[list[dict], set[str]]:
    """Group applicable rules by parameter. Returns open issues and the rule ids to exclude."""
    by_parameter: dict[str, list[Rule]] = {}
    for rule in rules:
        if rule.sets:
            by_parameter.setdefault(rule.sets.parameter, []).append(rule)

    issues, excluded = [], set()
    for parameter, candidates in by_parameter.items():
        if len({json.dumps(rule.sets.value) for rule in candidates}) < 2:
            continue
        issue_id = f"conflict:{parameter}"
        resolution = state.resolutions.get(issue_id)
        if resolution:
            excluded |= {rule.id for rule in candidates if rule.id != resolution["selected_rule_id"]}
        else:
            issues.append({
                "id": issue_id,
                "kind": "rule_conflict",
                "detail": f"Applicable rules set different values for {parameter}.",
                "rules": [rule.id for rule in candidates],
                "sources": sorted({rule.source for rule in candidates}),
            })
    return issues, excluded


def find_gaps(state: CaseState, pack: Pack, context: dict[str, Any]) -> list[dict]:
    issues = []
    change_type = state.modification["change_type"]
    if change_type not in pack.change_types:
        issues.append({
            "id": f"retrieval:{change_type}",
            "kind": "retrieval_gap",
            "detail": f"The knowledge pack does not cover change type {change_type}.",
            "rules": [],
            "sources": [],
        })
    for gap in pack.gaps:
        if evaluate(gap.when, context)[0] is True:
            issues.append({
                "id": f"gap:{gap.id}",
                "kind": "process_gap",
                "detail": gap.description,
                "rules": [],
                "sources": [gap.source],
            })
    return [issue for issue in issues if issue["id"] not in state.resolutions]


def open_questions(state: CaseState, pack: Pack) -> list[dict]:
    """Questions of the latest review hold the case until the round limit."""
    review = state.llm_review
    if review is None or review["status"] != "completed" or state.review_rounds >= pack.max_review_rounds:
        return []
    return [
        {"code": "ai_question", "domain": item["domain"], "subject": f"ai-{index}", "detail": item["reason"], "question": item["question"], "document": item.get("document", "")}
        for index, item in enumerate(review["information_requests"], 1)
    ]


def find_llm_issues(state: CaseState, domains: dict[str, str], pack: Pack) -> tuple[list[dict], list[str]]:
    """LLM findings can add issues but never change a domain status. Also returns withdrawn flags."""
    review = state.llm_review
    if review is None:
        return [], []
    revision = review["revision"]
    if review["status"] == "unavailable":
        issues = [{
            "id": f"llm:{revision}:unavailable",
            "kind": "llm_unavailable",
            "detail": f"No LLM review was obtained: {review['reason']}.",
            "rules": [],
            "sources": [],
        }]
    else:
        issues = []
        if state.modification["change_type_source"] == "client" and review["change_type"] != state.modification["change_type"]:
            issues.append({
                "id": f"llm:{revision}:change_type",
                "kind": "llm_flag",
                "detail": f"The LLM classified the change as {review['change_type']}.",
                "rules": [],
                "sources": [],
            })
        for finding in review["domains"]:
            if finding["status"] != "not_affected" and domains.get(finding["domain"], "not_affected") == "not_affected":
                issues.append({
                    "id": f"llm:{revision}:{finding['domain']}",
                    "kind": "llm_flag",
                    "detail": f"AI finding on {finding['domain']}: {finding['rationale']}",
                    "rules": finding["rule_ids"],
                    "sources": [],
                })
        questions = review["information_requests"]
        if questions and state.review_rounds >= pack.max_review_rounds:
            issues.append({
                "id": f"llm:{revision}:open_questions",
                "kind": "llm_flag",
                "detail": "Round limit reached with open AI questions: " + " ".join(item["question"] for item in questions),
                "rules": [],
                "sources": [],
            })
    # A flag closes on a resolution, on an explicit withdrawal, or once the rules cover its domain.
    cleared = set()
    if review["status"] == "completed":
        cleared = {f"llm:{revision}:{name}" for name, status in domains.items() if status != "not_affected"}
        cleared |= {f"llm:{revision}:{item['domain']}" for item in review["domains"] if item["status"] == "not_affected"}
        if not review["information_requests"]:
            cleared.add(f"llm:{revision}:open_questions")
    raised = {issue["id"] for issue in issues}
    earlier = state.assessment["issues"] if state.assessment else []
    kept = [
        issue for issue in earlier
        if issue["kind"] == "llm_flag" and issue["id"].startswith(f"llm:{revision}:") and issue["id"] not in raised
    ]
    issues += [issue for issue in kept if issue["id"] not in cleared]
    withdrawn = [issue["id"] for issue in kept if issue["id"] in cleared]
    return [issue for issue in issues if issue["id"] not in state.resolutions], withdrawn


def check_item(item: dict, revision: str, today: date) -> str | None:
    if item["status"] != "current":
        return "insufficient"
    if item["valid_until"] and date.fromisoformat(item["valid_until"]) < today:
        return "outdated"
    if item["revision"] is None:
        return "revision_unknown"
    if item["revision"] != revision:
        return "stale_revision"
    return None


def check_required(evidence_type: str, domain: str, state: CaseState, today: date) -> dict | None:
    items = [item for item in state.latest_evidence() if item["type"] == evidence_type]
    if not items:
        return {"code": "missing", "domain": domain, "subject": evidence_type, "detail": f"No {evidence_type} registered."}
    problems = [(item, check_item(item, state.revision, today)) for item in items]
    if any(code is None for _, code in problems):
        return None
    item, code = problems[0]
    return {"code": code, "domain": domain, "subject": evidence_type, "detail": f"{item['evidence_id']}: {code}."}


def check_document(evidence_type: str, domain: str, state: CaseState, pack: Pack, today: date) -> dict | None:
    """Beyond being there: a document must have been read and contain what it should."""
    deficiency = check_required(evidence_type, domain, state, today)
    if deficiency or evidence_type not in pack.documents:
        return deficiency
    item = next(item for item in state.latest_evidence() if item["type"] == evidence_type)
    verdict = state.document_verdicts.get(item["evidence_id"])
    if verdict is None or verdict["version"] != item["version"]:
        return {"code": "document_pending", "domain": domain, "subject": evidence_type, "detail": "Waiting for the assessment in the next round."}
    if verdict["status"] == "incomplete":
        details = verdict["problems"] + [f"Missing: {entry}" for entry in verdict["missing"]]
        return {"code": "document_incomplete", "domain": domain, "subject": evidence_type, "detail": " ".join(details)}
    return None


def facts_to_confirm(state: CaseState) -> dict[str, dict]:
    """Facts read from complete documents, waiting for a person."""
    found = {}
    for verdict in state.document_verdicts.values():
        if verdict["status"] == "complete":
            for fact in verdict["facts"]:
                if (fact["name"], verdict["evidence_id"]) not in state.declined_facts:
                    found.setdefault(fact["name"], {**fact, "evidence_id": verdict["evidence_id"], "document": verdict["type"]})
    return found


def classify_impact(item: dict, status: str, revision: str) -> str:
    if status == "not_affected" or item["revision"] == revision:
        return "retained"
    return "revalidate" if status == "affected" else "review"


def fingerprint(domains: dict, deficiencies: list[dict], issues: list[dict]) -> str:
    content = {
        "domains": domains,
        "deficiencies": sorted((d["code"], d["domain"] or "", d["subject"]) for d in deficiencies),
        "issues": sorted(issue["id"] for issue in issues),
    }
    return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()


def unknown_fact(name: str, domain: str, pack: Pack) -> dict:
    fact = pack.facts.get(name)
    documents = [] if name in pack.opening_facts else [key for key, item in pack.documents.items() if name in item.proves]
    return {
        "documents": documents,
        "code": "unknown_fact",
        "domain": domain,
        "subject": name,
        "detail": f"{name} is not established.",
        "question": fact.question if fact else None,
        "options": [option.model_dump() for option in fact.options] if fact else [],
    }


def describe_rule(rule: Rule, pack: Pack) -> dict:
    source = pack.source(rule.source)
    return {
        "rule": rule.id,
        "domain": rule.domain,
        "source": rule.source,
        "source_kind": source.kind,
        "title": rule.title,
        "reference": rule.reference,
        "source_title": source.title,
    }


def pending_assessment(state: CaseState, pack: Pack, today: date, facts: dict[str, Any]) -> dict:
    """Before the first review: the type is not known, so only the opening facts and the model are open."""
    domains = {rule.domain: "potentially_affected" for rule in pack.rules}
    model = check_required("design_model", "architectural", state, today)
    deficiencies = ([model] if model else []) + [
        unknown_fact(name, "permitting", pack) for name in pack.opening_facts if name not in facts
    ]
    return {
        "revision": state.revision,
        "pack_version": pack.version,
        "domains": domains,
        "applied_rules": [],
        "impact": [],
        "deficiencies": deficiencies,
        "issues": [],
        "withdrawn_flags": [],
        "llm_review": None,
        "basis": {"revision": state.revision, "evidence": {item["evidence_id"]: item["version"] for item in state.latest_evidence()}},
        "fingerprint": fingerprint(domains, deficiencies, []),
        "disclaimer": DISCLAIMER,
    }


def assess(state: CaseState, pack: Pack, today: date) -> dict:
    facts, deficiencies = collect_facts(state)
    if state.modification["change_type"] is None:
        return pending_assessment(state, pack, today, facts)
    context = {**facts, "change_type": state.modification["change_type"]}

    proposed = facts_to_confirm(state)
    for name, reading in proposed.items():
        if name in facts and facts[name] != reading["value"]:
            deficiencies.append({
                "code": "inconsistent_fact", "domain": None, "subject": name,
                "detail": f"{reading['document']} states {reading['value']}, but the case has {facts[name]}.",
            })
    results = [(rule, *evaluate(rule.when, context)) for rule in pack.rules]
    applicable = [rule for rule, match, _ in results if match is True]
    conflicts, excluded = find_conflicts(applicable, state)
    issues = conflicts + find_gaps(state, pack, context)
    applied = [rule for rule in applicable if rule.id not in excluded]

    domains = {rule.domain: "not_affected" for rule in pack.rules}
    for rule in applied:
        domains[rule.domain] = "affected"
    for rule, match, unknown in results:
        if match is None:
            domains[rule.domain] = max(domains[rule.domain], "potentially_affected", key=DOMAIN_ORDER.get)
            # Ask everything at once, except facts that depend on the answer to an earlier one.
            first_only = rule.sequential or "competent_entity" in unknown
            for name in unknown[:1] if first_only else unknown:
                if not any(d["subject"] == name for d in deficiencies):
                    deficiency = unknown_fact(name, rule.domain, pack)
                    if name in proposed:
                        deficiency |= {"code": "fact_to_confirm", "detail": f"{name} was read from a document.", "reading": proposed[name]}
                    deficiencies.append(deficiency)

    for rule in applied:
        for evidence_type in rule.requires_evidence:
            deficiency = check_document(evidence_type, rule.domain, state, pack, today)
            if deficiency and deficiency not in deficiencies:
                deficiencies.append(deficiency)

    if state.permit_type in pack.bim_required_for:
        deficiency = check_required("design_model", "architectural", state, today)
        if deficiency:
            deficiencies.append(deficiency)
    deficiencies += open_questions(state, pack)
    for item in state.latest_evidence():
        if item["type"] == "supporting_document" or (item["type"] in pack.documents and pack.documents[item["type"]].proves):
            deficiency = check_document(item["type"], item["domain"], state, pack, today)
            if deficiency and not any(d["subject"] == item["type"] for d in deficiencies):
                deficiencies.append(deficiency)

    llm_issues, withdrawn = find_llm_issues(state, domains, pack)
    issues += llm_issues

    return {
        "revision": state.revision,
        "pack_version": pack.version,
        "domains": domains,
        "applied_rules": [describe_rule(rule, pack) for rule in applied],
        "impact": [
            {
                "evidence_id": item["evidence_id"],
                "domain": item["domain"],
                "impact": classify_impact(item, domains.get(item["domain"], "not_affected"), state.revision),
            }
            for item in state.latest_evidence()
        ],
        "deficiencies": deficiencies,
        "issues": issues,
        "withdrawn_flags": withdrawn,
        "llm_review": state.llm_review,
        "basis": {"revision": state.revision, "evidence": {item["evidence_id"]: item["version"] for item in state.latest_evidence()}},
        "fingerprint": fingerprint(domains, deficiencies, issues),
        "disclaimer": DISCLAIMER,
    }
