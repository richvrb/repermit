"""Case state, derived by folding the event history."""

from dataclasses import dataclass, field

from repermit.knowledge import LEGACY_PACK_VERSION


@dataclass
class CaseState:
    case_id: str
    seq: int = 0
    project_name: str = ""
    permit_type: str = ""
    pack_version: str = LEGACY_PACK_VERSION
    responsible_role: str = ""
    revision: str = ""
    stage: str = ""
    base_revision: str = ""
    scenario: str | None = None
    review_rounds: int = 0
    # Calls since the last modification, including failed ones, and the cost of all calls in this case.
    review_attempts: int = 0
    llm_cost_usd: float = 0.0
    # Why the latest review was not made, until a review is made again.
    ai_stop: str | None = None
    document_verdicts: dict[str, dict] = field(default_factory=dict)
    declined_facts: set[tuple[str, str]] = field(default_factory=set)
    modification: dict | None = None
    evidence: dict[str, list[dict]] = field(default_factory=dict)
    resolutions: dict[str, dict] = field(default_factory=dict)
    assessment: dict | None = None
    llm_review: dict | None = None
    basis_fingerprint: str | None = None
    last_action: str | None = None
    auto_denied_action: str | None = None

    def apply(self, event: dict) -> None:
        self.seq = event["seq"]
        payload = event["payload"]
        match event["type"]:
            case "case_opened":
                self.project_name = payload["project_name"]
                self.permit_type = payload["permit_type"]
                self.pack_version = payload.get("pack_version", LEGACY_PACK_VERSION)
                self.responsible_role = payload["responsible_role"]
                self.revision = payload["revision"]
                self.base_revision = payload["revision"]
                self.scenario = payload.get("scenario")
                self.stage = payload["stage"]
            case "modification_submitted":
                self.modification = dict(payload)
                self.revision = payload["revision"]
                self.llm_review = None
                self.review_rounds = 0
                self.review_attempts = 0
                self.ai_stop = None
            case "llm_documents_read":
                self.document_verdicts |= {item["evidence_id"]: item for item in payload["document_verdicts"]}
                self.llm_cost_usd += (payload.get("usage") or {}).get("cost_usd") or 0.0
            case "document_assessed":
                self.document_verdicts[payload["evidence_id"]] = payload
            case "llm_review_skipped":
                self.ai_stop = payload["reason"]
            case "llm_review_recorded":
                self.llm_review = payload
                self.review_rounds += payload["status"] == "completed"
                self.review_attempts += 1
                self.llm_cost_usd += (payload.get("usage") or {}).get("cost_usd") or 0.0
                self.ai_stop = None
                self.document_verdicts |= {item["evidence_id"]: item for item in payload.get("document_verdicts", [])}
                if self.modification["change_type_source"] == "llm":
                    self.modification["change_type"] = payload["effective_change_type"]
            case "evidence_registered":
                self.evidence.setdefault(payload["evidence_id"], []).append(payload)
            case "issue_resolved":
                self.resolutions[payload["issue_id"]] = payload
            case "fact_declined":
                self.declined_facts.add((payload["name"], payload["evidence_id"]))
            case "assessment_recorded":
                self.assessment = payload
            case "action_executed":
                self.stage = payload["to_stage"]
                self.basis_fingerprint = payload["basis_fingerprint"]
                self.last_action = payload["action"]
                self.auto_denied_action = None
            case "action_denied":
                # A denial is history only; the stage is deliberately untouched (BR-06).
                if payload["automatic"]:
                    self.auto_denied_action = payload["action"]
            case "stage_reversed":
                self.stage = payload["to_stage"]
                self.basis_fingerprint = None
                self.last_action = None

    def latest_evidence(self) -> list[dict]:
        return [versions[-1] for versions in self.evidence.values()]


def fold(case_id: str, events: list[dict]) -> CaseState:
    state = CaseState(case_id)
    for event in events:
        state.apply(event)
    return state
