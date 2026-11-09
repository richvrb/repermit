"""Case commands. Each command appends its events in one atomic write."""

import uuid
from collections.abc import Callable
from datetime import date, datetime, timezone

from repermit.assessment import AI_STOP_DETAIL, assess, check_required
from repermit.bim import MAX_LISTED_CHANGES, InvalidModel, compare, derive_facts, read_model
from repermit.documents import InvalidDocument, coerce, judge_reviews, read_document
from repermit.control import derive_status, is_authorized, plan
from repermit.knowledge import Action, Pack
from repermit.llm import Assessor, AssessorUnavailable, DocumentReader, completed_payload, is_unread, unavailable_payload
from repermit.retrieval import Retriever
from repermit.state import CaseState, fold
from repermit.store import EventStore

# Failed calls beyond the round limit before the AI stops for this modification.
MAX_FAILED_ATTEMPTS = 2
# Stored with the evidence, but too large to show: model elements and details, and document text.
BULKY = ("elements", "details", "text")


class CaseNotFound(Exception):
    pass


class UnknownItem(Exception):
    pass


class InvalidRequest(Exception):
    pass


class ActionForbidden(Exception):
    pass


class ActionHeld(Exception):
    pass


def _item(evidence_id: str, type: str, domain: str, revision: str, **extra) -> dict:
    return {
        "evidence_id": evidence_id,
        "category": "document",
        "type": type,
        "domain": domain,
        "status": "current",
        "revision": revision,
        "format": None,
        "description": None,
        "valid_until": None,
        "facts": {},
        **extra,
    }


class _Unit:
    """A case state, its knowledge pack, and the events the current command will append."""

    def __init__(self, state: CaseState, pack: Pack):
        self.state = state
        self.pack = pack
        self.pending: list[dict] = []

    def emit(self, event_type: str, payload: dict) -> None:
        event = {
            "seq": self.state.seq + 1,
            "type": event_type,
            "at": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
        self.state.apply(event)
        self.pending.append(event)


class CaseService:
    def __init__(
        self,
        store: EventStore,
        pack: Pack,
        today: Callable[[], date] = date.today,
        assessor: Assessor | None = None,
        packs: dict[str, Pack] | None = None,
        retriever: Retriever | None = None,
        case_budget_usd: float | None = None,
        daily_budget_usd: float | None = None,
        document_reader: DocumentReader | None = None,
    ):
        self.store = store
        self.pack = pack
        self.today = today
        self.assessor = assessor
        # Without a separate reader, the review itself reads new documents.
        self.document_reader = document_reader
        self.retriever = retriever
        self.case_budget_usd = case_budget_usd
        self.daily_budget_usd = daily_budget_usd
        self.packs = {**(packs or {}), pack.version: pack}

    def open_case(
        self, project_name: str, revision: str, responsible_role: str, permit_type: str = "modification", scenario: str | None = None
    ) -> dict:
        if responsible_role not in self.pack.roles:
            raise InvalidRequest(f"unknown role {responsible_role}")
        unit = _Unit(CaseState(str(uuid.uuid4())), self.pack)
        unit.emit("case_opened", {
            "project_name": project_name,
            "permit_type": permit_type,
            "pack_version": self.pack.version,
            "revision": revision,
            "responsible_role": responsible_role,
            "stage": self.pack.initial_stage,
            "scenario": scenario,
        })
        return self._commit(unit)

    def submit_modification(self, case_id: str, modification: dict) -> dict:
        unit = self._load(case_id)
        if modification["revision"] == unit.state.revision:
            raise InvalidRequest("a modification requires a new design revision")
        if modification["change_type"] is None and self.assessor is None:
            raise InvalidRequest("change_type is required when no LLM is configured")
        source = "llm" if modification["change_type"] is None else "client"
        unit.emit("modification_submitted", {**modification, "change_type_source": source})
        if not self._awaiting_model(unit):
            self._review(unit)
        self._progress(unit)
        return self._commit(unit)

    def rerun_review(self, case_id: str) -> dict:
        unit = self._load(case_id)
        if self.assessor is None or unit.state.modification is None:
            raise InvalidRequest("a review needs a configured LLM and a submitted modification")
        if self._awaiting_model(unit):
            raise InvalidRequest("the first review follows when the design model is delivered")
        stop = self._stop_reason(unit)
        if stop:
            raise InvalidRequest(f"no further AI review: {AI_STOP_DETAIL[stop]}")
        self._review(unit)
        self._progress(unit)
        return self._commit(unit)

    def register_evidence(self, case_id: str, evidence: dict) -> dict:
        unit = self._load(case_id)
        self._check_bim_delivery(unit, evidence)
        self._add_evidence(unit, evidence)
        self._after_information(unit)
        return self._commit(unit)

    def register_model(self, case_id: str, kind: str, filename: str, content: bytes) -> dict:
        unit = self._load(case_id)
        state = unit.state
        try:
            parsed = read_model(content)
        except InvalidModel as error:
            raise InvalidRequest(str(error)) from error
        baseline = next((item for item in state.latest_evidence() if item["type"] == "baseline_model"), None)
        changes = compare(baseline["elements"], parsed["elements"]) if baseline and kind == "proposed" else []
        self._add_evidence(unit, _item(
            "baseline-model" if kind == "baseline" else "design-model",
            "baseline_model" if kind == "baseline" else "design_model",
            "architectural",
            state.base_revision if kind == "baseline" else state.revision,
            format="ifc",
            description=f"{filename}: {len(changes)} changed elements" if kind == "proposed" else filename,
            facts=derive_facts(changes),
            model={**parsed["summary"], "filename": filename, "compared": baseline is not None and kind == "proposed"},
            changes=changes[:MAX_LISTED_CHANGES],
            elements=parsed["elements"],
            details=parsed["details"],
        ))
        self._after_information(unit)
        return self._commit(unit)

    def register_document(self, case_id: str, type: str, filename: str, content: bytes) -> dict:
        """Stored without a review: the round is assessed once, when it is submitted."""
        unit = self._load(case_id)
        state = unit.state
        if type not in unit.pack.documents:
            raise InvalidRequest(f"{type} is not a known document type")
        try:
            parsed = read_document(content)
        except InvalidDocument as error:
            raise InvalidRequest(str(error)) from error
        # Kept before the event, so a recorded document always has its file.
        self.store.save_file(parsed["document"]["sha256"], content)
        self._add_evidence(unit, _item(
            f"{type}-{state.revision}", type, "general", state.revision, format="pdf", description=filename,
            document={**parsed["document"], "filename": filename}, text=parsed["text"],
        ))
        if state.modification:
            self._progress(unit)
        return self._commit(unit)

    def decide_fact(self, case_id: str, decision: dict) -> dict:
        """A person confirms or declines a fact that was read from a document."""
        unit = self._load(case_id)
        state = unit.state
        role, name = decision["role"], decision["name"]
        deficiencies = state.assessment["deficiencies"] if state.assessment else []
        item = next((d for d in deficiencies if d["code"] == "fact_to_confirm" and d["subject"] == name), None)
        if item is None:
            raise UnknownItem(f"no fact {name} to confirm")
        if role not in unit.pack.resolution_roles:
            unit.emit("resolution_denied", {"issue_id": f"fact:{name}", "actor_id": decision["actor_id"], "role": role})
            self._commit(unit)
            raise ActionForbidden(f"role {role} may not confirm facts")
        reading = item["reading"]
        if decision["accepted"]:
            self._add_evidence(unit, _item(
                f"confirmed-{name}", "confirmed_fact", item["domain"] or "general", state.revision, facts={name: reading["value"]},
                description=f"Confirmed by {role} from {reading['document']}: {reading['quote']}",
            ))
        else:
            unit.emit("fact_declined", {"name": name, "evidence_id": reading["evidence_id"], "actor_id": decision["actor_id"], "role": role})
        self._progress(unit)
        return self._commit(unit)

    def assess_document(self, case_id: str, decision: dict) -> dict:
        """A reviewer assesses a document instead of the AI. Facts a reviewer records count as confirmed."""
        unit = self._load(case_id)
        state, pack = unit.state, unit.pack
        evidence_id, role = decision["evidence_id"], decision["role"]
        item = next((item for item in state.latest_evidence() if item["evidence_id"] == evidence_id and item["type"] in pack.documents), None)
        if item is None:
            raise UnknownItem(f"no document {evidence_id}")
        if role not in pack.resolution_roles:
            unit.emit("resolution_denied", {"issue_id": f"document:{evidence_id}", "actor_id": decision["actor_id"], "role": role})
            self._commit(unit)
            raise ActionForbidden(f"role {role} may not assess documents")
        spec = pack.documents[item["type"]]
        present = set(decision["present"])
        if present - set(spec.must_contain):
            raise InvalidRequest(f"unknown checklist items: {sorted(present - set(spec.must_contain))}")
        facts = {name: coerce(str(value)) for name, value in decision["facts"].items() if str(value).strip()}
        if set(facts) - set(spec.proves):
            raise InvalidRequest(f"a {item['type']} does not prove {sorted(set(facts) - set(spec.proves))}")
        missing = [entry for entry in spec.must_contain if entry not in present]
        if facts and missing:
            raise InvalidRequest("facts can only be taken from a complete document")
        note = (decision["note"] or "").strip()
        unit.emit("document_assessed", {
            "evidence_id": evidence_id,
            "version": item["version"],
            "type": item["type"],
            "status": "incomplete" if missing else "complete",
            "missing": missing,
            "problems": [note] if note and missing else [],
            "checklist": [{"item": entry, "present": entry in present, "location": ""} for entry in spec.must_contain],
            "facts": [{"name": name, "value": value, "quote": note or "Recorded by the reviewer."} for name, value in facts.items()],
            "assessed_by": "reviewer",
            "actor_id": decision["actor_id"],
            "role": role,
            "note": note,
        })
        for name, value in facts.items():
            self._add_evidence(unit, _item(
                f"confirmed-{name}", "confirmed_fact", "general", state.revision, facts={name: value},
                description=f"Recorded by {role} from {item['type']}{f': {note}' if note else ''}",
            ))
        self._progress(unit)
        return self._commit(unit)

    def submit_response(self, case_id: str, response: dict) -> dict:
        """One round: everything the applicant adds, followed by one new assessment."""
        unit = self._load(case_id)
        state = unit.state
        if state.modification is None:
            raise InvalidRequest("a response needs a submitted modification")
        answers = [item for item in response["answers"] if item["answer"].strip()]
        note = (response["note"] or "").strip()
        requires_proof = bool(unit.pack.documents)
        if requires_proof and (response["documents"] or set(response["facts"]) - set(unit.pack.opening_facts)):
            raise InvalidRequest("this information must be proven with an uploaded document")
        unread = [
            item for item in state.latest_evidence() if item["type"] in unit.pack.documents
            and state.document_verdicts.get(item["evidence_id"], {}).get("version") != item["version"]
        ]
        if not (response["facts"] or response["documents"] or answers or note or unread):
            raise InvalidRequest("a response needs at least one answer, document or note")
        open_items = {item["subject"]: item for item in state.assessment["deficiencies"]}
        for document in response["documents"]:
            if document == "design_model" or open_items.get(document, {}).get("code") in (None, "unknown_fact", "ai_question"):
                raise InvalidRequest(f"{document} is not an open document request")

        for name, value in response["facts"].items():
            fact = unit.pack.facts.get(name)
            domain = open_items.get(name, {}).get("domain") or "general"
            question = fact.question if fact else name
            self._add_evidence(unit, _item(f"answer-{name}", "statement", domain, state.revision, facts={name: value}, description=f"Applicant's answer to: {question}"))
        for document in response["documents"]:
            existing = next((item for item in state.latest_evidence() if item["type"] == document), None)
            evidence_id = existing["evidence_id"] if existing else f"{document}-{state.revision}"
            self._add_evidence(unit, _item(evidence_id, document, open_items[document]["domain"] or "general", state.revision))
        lines = [f"Q: {item['question']}\nA: {item['answer'].strip()}" for item in answers] + ([note] if note else [])
        if lines:
            self._add_evidence(unit, _item(f"response-{state.seq}", "note", "general", state.revision, description="\n".join(lines)))
        self._after_information(unit)
        return self._commit(unit)

    def request_action(self, case_id: str, action_id: str, actor_id: str, role: str) -> dict:
        unit = self._load(case_id)
        action = unit.pack.action(action_id)
        if action is None:
            raise UnknownItem(f"unknown action {action_id}")
        if unit.state.modification:
            self._reassess(unit)

        if not is_authorized(action, role):
            self._deny(unit, action_id, actor_id, role, "not_authorized")
            self._commit(unit)
            raise ActionForbidden(f"role {role} may not perform {action_id}")

        planned = plan(unit.state, unit.pack)
        if planned["next_action"] != action_id or planned["held"]:
            reason = "held" if planned["next_action"] == action_id else "not_available"
            self._deny(unit, action_id, actor_id, role, reason)
            self._commit(unit)
            raise ActionHeld(f"{action_id} is {reason}: {planned['hold_reasons']}")

        self._execute(unit, action, actor_id, role)
        self._progress(unit)
        return self._commit(unit)

    def resolve_issue(self, case_id: str, issue_id: str, resolution: dict) -> dict:
        unit = self._load(case_id)
        issues = unit.state.assessment["issues"] if unit.state.assessment else []
        issue = next((item for item in issues if item["id"] == issue_id), None)
        if issue is None:
            raise UnknownItem(f"no open issue {issue_id}")
        if resolution["role"] not in unit.pack.resolution_roles:
            unit.emit("resolution_denied", {"issue_id": issue_id, **resolution})
            self._commit(unit)
            raise ActionForbidden(f"role {resolution['role']} may not resolve issues")
        if issue["kind"] == "rule_conflict" and resolution.get("selected_rule_id") not in issue["rules"]:
            raise InvalidRequest(f"selected_rule_id must be one of {issue['rules']}")
        unit.emit("issue_resolved", {"issue_id": issue_id, **resolution})
        self._progress(unit)
        return self._commit(unit)

    def get_case(self, case_id: str, at: int | None = None) -> dict:
        if at is None:
            return self._view(self._load(case_id).state)
        if at < 1:
            raise InvalidRequest("at must be 1 or higher")
        return self._view(fold(case_id, self.get_history(case_id)[:at]))

    def list_cases(self) -> list[dict]:
        cases = []
        for case_id in self.store.case_ids():
            view = self.get_case(case_id)
            cases.append({key: view[key] for key in ("case_id", "project_name", "permit_type", "revision", "stage", "status")})
        return cases

    def document_file(self, case_id: str, evidence_id: str, version: int | None = None) -> tuple[bytes, str]:
        """The original file of an uploaded document, and its file name."""
        state = self._load(case_id).state
        versions = [item for item in state.evidence.get(evidence_id, []) if item.get("document")]
        item = next((item for item in reversed(versions) if version in (None, item["version"])), None)
        if item is None:
            raise UnknownItem(f"no document {evidence_id}" + (f" version {version}" if version else ""))
        content = self.store.load_file(item["document"]["sha256"])
        if content is None:
            raise UnknownItem("the original file was not kept: it was uploaded before files were stored")
        return content, item["document"].get("filename") or f"{evidence_id}.pdf"

    def get_history(self, case_id: str) -> list[dict]:
        events = self.store.load(case_id)
        if not events:
            raise CaseNotFound(case_id)
        return events

    def _pack_of(self, state: CaseState) -> Pack:
        return self.packs[state.pack_version]

    def _check_bim_delivery(self, unit: _Unit, evidence: dict) -> None:
        pack = unit.pack
        if unit.state.permit_type not in pack.bim_required_for or evidence["type"] not in pack.bim_evidence_types:
            return
        if (evidence.get("format") or "").lower() not in pack.bim_formats:
            raise InvalidRequest(f"this permit type requires BIM delivery: {pack.bim_formats}")
        if evidence["type"] == "design_model":
            raise InvalidRequest("a design model must be uploaded as an IFC file")

    def _add_evidence(self, unit: _Unit, evidence: dict) -> None:
        version = len(unit.state.evidence.get(evidence["evidence_id"], [])) + 1
        unit.emit("evidence_registered", {**evidence, "version": version})

    def _after_information(self, unit: _Unit) -> None:
        """New information always gets a new assessment, so nothing progresses on an old review."""
        if unit.state.modification is None:
            return
        unclassified = unit.state.modification["change_type"] is None
        if (unit.state.llm_review is not None or unclassified) and not self._awaiting_model(unit):
            self._review(unit)
        self._progress(unit)

    def _awaiting_model(self, unit: _Unit) -> bool:
        """The first paid review waits for the model, which answers many of its questions."""
        state = unit.state
        return (
            state.modification["change_type"] is None
            and state.permit_type in unit.pack.bim_required_for
            and check_required("design_model", "architectural", state, self.today()) is not None
        )

    def _load(self, case_id: str) -> _Unit:
        events = self.store.load(case_id)
        if not events:
            raise CaseNotFound(case_id)
        state = fold(case_id, events)
        return _Unit(state, self._pack_of(state))

    def _commit(self, unit: _Unit) -> dict:
        self.store.append(unit.state.case_id, unit.pending)
        unit.pending = []
        return self._view(unit.state)

    def _stop_reason(self, unit: _Unit) -> str | None:
        """Hard limits on paid calls. They hold whatever the client keeps sending."""
        state, limit = unit.state, unit.pack.max_review_rounds
        if state.review_rounds >= limit or state.review_attempts >= limit + MAX_FAILED_ATTEMPTS:
            return "round_limit"
        if self.case_budget_usd is not None and state.llm_cost_usd >= self.case_budget_usd:
            return "case_budget"
        if self.daily_budget_usd is not None:
            midnight = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            if self.store.llm_cost_since(midnight.isoformat()) >= self.daily_budget_usd:
                return "daily_budget"
        return None

    def _read_documents(self, unit: _Unit) -> None:
        """The document check on its own model, before the review, so the review no longer needs the full texts."""
        state, reader = unit.state, self.document_reader
        if reader is None or not any(is_unread(item, state, unit.pack) for item in state.latest_evidence()):
            return
        try:
            reading = reader.read_documents(state, unit.pack)
        except AssessorUnavailable as error:
            # The review then reads the documents itself.
            unit.emit("llm_documents_read", {"status": "unavailable", "reason": str(error), "model": reader.model, "document_verdicts": [], "usage": error.usage})
            return
        reviews = [item.model_dump() for item in reading.document_reviews]
        unit.emit("llm_documents_read", {
            "status": "completed",
            "model": reader.model,
            "document_verdicts": judge_reviews(reviews, state, unit.pack),
            "usage": getattr(reading, "_usage", None),
        })

    def _review(self, unit: _Unit) -> None:
        if self.assessor is None:
            return
        state, model = unit.state, self.assessor.model
        stop = self._stop_reason(unit)
        if not stop:
            self._read_documents(unit)
            stop = self._stop_reason(unit)
        if stop:
            unit.emit("llm_review_skipped", {
                "reason": stop,
                "round": state.review_rounds,
                "max_review_rounds": unit.pack.max_review_rounds,
                "case_cost_usd": round(state.llm_cost_usd, 4),
                "case_budget_usd": self.case_budget_usd,
                "daily_budget_usd": self.daily_budget_usd,
            })
            return
        passages = self.retriever.for_case(state) if self.retriever else []
        try:
            review = self.assessor.review(state, unit.pack, passages)
        except AssessorUnavailable as error:
            payload = unavailable_payload(str(error), state.revision, model)
            usage = error.usage
        else:
            payload = completed_payload(review, state.revision, model, unit.pack, passages)
            payload["document_verdicts"] = judge_reviews(payload["document_reviews"], state, unit.pack)
            payload["tool_calls"] = getattr(review, "_tool_calls", [])
            usage = getattr(review, "_usage", None)
        unit.emit("llm_review_recorded", {**payload, "round": state.review_rounds + 1, "usage": usage})

    def _reassess(self, unit: _Unit) -> None:
        state = unit.state
        assessment = assess(state, unit.pack, self.today())
        if state.basis_fingerprint and assessment["fingerprint"] != state.basis_fingerprint:
            unit.emit("stage_reversed", {
                "from_stage": state.stage,
                "to_stage": unit.pack.initial_stage,
                "action": state.last_action,
                "reason": "material information changed the assessment",
            })
        if state.assessment is None or assessment != state.assessment:
            unit.emit("assessment_recorded", assessment)

    def _progress(self, unit: _Unit) -> None:
        self._reassess(unit)
        state, pack = unit.state, unit.pack
        # Every action leaves its stage, so this ends within the process length.
        for _ in pack.actions:
            planned = plan(state, pack)
            unit.emit("plan_recorded", planned)
            if planned["next_action"] is None or planned["held"] or planned["autonomy"] != "autonomous":
                return
            action = pack.action(planned["next_action"])
            if not is_authorized(action, state.responsible_role):
                self._deny(unit, action.id, "repermit", state.responsible_role, "not_authorized", automatic=True)
                return
            self._execute(unit, action, "repermit", state.responsible_role)

    def _execute(self, unit: _Unit, action: Action, actor_id: str, role: str) -> None:
        unit.emit("action_executed", {
            "action": action.id,
            "actor_id": actor_id,
            "role": role,
            "from_stage": unit.state.stage,
            "to_stage": action.to_stage,
            "basis_fingerprint": unit.state.assessment["fingerprint"],
        })

    def _deny(self, unit: _Unit, action_id: str, actor_id: str, role: str, reason: str, automatic: bool = False) -> None:
        unit.emit("action_denied", {
            "action": action_id,
            "actor_id": actor_id,
            "role": role,
            "reason": reason,
            "automatic": automatic,
        })

    def _view(self, state: CaseState) -> dict:
        pack = self._pack_of(state)
        kept = self.store.stored_files({item["document"]["sha256"] for item in state.latest_evidence() if item.get("document")})
        evidence = [
            {key: value for key, value in item.items() if key not in BULKY} | ({"file_kept": item["document"]["sha256"] in kept} if item.get("document") else {})
            for item in state.latest_evidence()
        ]
        return {
            "case_id": state.case_id,
            "project_name": state.project_name,
            "permit_type": state.permit_type,
            "pack_version": state.pack_version,
            "labels": pack.labels,
            "responsible_role": state.responsible_role,
            "revision": state.revision,
            "stage": state.stage,
            "status": derive_status(state, pack),
            "modification": state.modification,
            "evidence": evidence,
            "document_verdicts": list(state.document_verdicts.values()),
            "document_types": sorted(pack.documents),
            "document_specs": {name: spec.model_dump(include={"must_contain", "proves"}) for name, spec in pack.documents.items()},
            "scenario": state.scenario,
            "bim_required": state.permit_type in pack.bim_required_for,
            "review_round": state.review_rounds,
            "max_review_rounds": pack.max_review_rounds,
            "ai_stop": state.ai_stop,
            "llm_cost_usd": round(state.llm_cost_usd, 4),
            "case_budget_usd": self.case_budget_usd,
            "resolutions": list(state.resolutions.values()),
            "assessment": state.assessment,
            "plan": plan(state, pack),
        }
