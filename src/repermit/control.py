"""Planning, autonomy and authorization. Autonomy and authorization stay separate (BR-05)."""

from repermit.knowledge import Action, Pack
from repermit.state import CaseState


def evaluate_autonomy(action: Action, assessment: dict, pack: Pack) -> str:
    if action.autonomy == "human_only":
        return "human_only"
    if action.autonomy == "conditional":
        domains = assessment["domains"]
        if any(domains.get(domain) == "affected" for domain in pack.safety_domains):
            return "human_review"
    return "autonomous"


def is_authorized(action: Action, role: str) -> bool:
    return role in action.roles


def plan(state: CaseState, pack: Pack) -> dict:
    action = pack.action_from(state.stage)
    assessment = state.assessment
    if assessment is None or action is None:
        return {"next_action": None, "roles": [], "to_stage": None, "autonomy": None, "held": False, "hold_reasons": []}
    reasons = [f"{d['code']}: {d['subject']}" for d in assessment["deficiencies"]]
    reasons += [f"{issue['kind']}: {issue['id']}" for issue in assessment["issues"]]
    return {
        "next_action": action.id,
        "roles": action.roles,
        "to_stage": action.to_stage,
        "autonomy": evaluate_autonomy(action, assessment, pack),
        "held": bool(reasons),
        "hold_reasons": reasons,
    }


def derive_status(state: CaseState, pack: Pack) -> str:
    if state.assessment is None:
        return "open"
    if state.assessment["issues"]:
        return "escalated"
    if state.assessment["deficiencies"]:
        return "pending_evidence"
    planned = plan(state, pack)
    if planned["next_action"] is None:
        return "completed"
    if planned["autonomy"] != "autonomous" or state.auto_denied_action == planned["next_action"]:
        return "awaiting_review"
    return "ready"
