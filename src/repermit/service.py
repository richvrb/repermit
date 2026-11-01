"""Case commands. Each command appends its events in one atomic write."""

import uuid
from collections.abc import Callable
from datetime import date, datetime, timezone

from repermit.assessment import assess
from repermit.bim import MAX_LISTED_CHANGES, InvalidModel, compare, derive_facts, read_model
from repermit.control import derive_status, is_authorized, plan
from repermit.knowledge import Action, Pack
from repermit.llm import Assessor, AssessorUnavailable, completed_payload, unavailable_payload
from repermit.state import CaseState, fold
from repermit.store import EventStore


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
    ):
        self.store = store
        self.pack = pack
        self.today = today
        self.assessor = assessor
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
        self._review(unit)
        self._progress(unit)
        return self._commit(unit)

    def rerun_review(self, case_id: str) -> dict:
        unit = self._load(case_id)
        if self.assessor is None or unit.state.modification is None:
            raise InvalidRequest("a review needs a configured LLM and a submitted modification")
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
        ))
        self._after_information(unit)
        return self._commit(unit)

    def submit_response(self, case_id: str, response: dict) -> dict:
        """One round: everything the applicant adds, followed by one new assessment."""
        unit = self._load(case_id)
        state = unit.state
        if state.modification is None:
            raise InvalidRequest("a response needs a submitted modification")
        answers = [item for item in response["answers"] if item["answer"].strip()]
        note = (response["note"] or "").strip()
        if not (response["facts"] or response["documents"] or answers or note):
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
        if unit.state.llm_review is not None:
            self._review(unit)
        self._progress(unit)

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

    def _review(self, unit: _Unit) -> None:
        if self.assessor is None:
            return
        state, model = unit.state, self.assessor.model
        try:
            review = self.assessor.review(state, unit.pack)
        except AssessorUnavailable as error:
            payload = unavailable_payload(str(error), state.revision, model)
        else:
            payload = completed_payload(review, state.revision, model, unit.pack)
        unit.emit("llm_review_recorded", {**payload, "round": state.review_rounds + 1})

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
            "evidence": [{key: value for key, value in item.items() if key != "elements"} for item in state.latest_evidence()],
            "scenario": state.scenario,
            "bim_required": state.permit_type in pack.bim_required_for,
            "review_round": state.review_rounds,
            "max_review_rounds": pack.max_review_rounds,
            "resolutions": list(state.resolutions.values()),
            "assessment": state.assessment,
            "plan": plan(state, pack),
        }
