"""Synthetic example cases that demonstrate the UC-01 flows.

Run with: python -m repermit.demo
Add --llm for one live free-text scenario, which calls the Claude API.
Each run adds new cases to the configured database.
"""

import json
import os
import sys
from collections.abc import Sequence

from repermit.knowledge import PUBLIC_PACK, load_pack
from repermit.llm import MODEL, ClaudeAssessor
from repermit.samples import PROPOSALS, sample_model
from repermit.service import ActionForbidden, ActionHeld, CaseService, InvalidRequest, UnknownItem
from repermit.store import EventStore

SAFE = {"load_bearing": False, "fire_compartment_boundary": False, "occupancy": "residential"}
LLM_DESCRIPTION = (
    "We want to move the internal wall between apartments 4A and 4B 1.2 metres towards the corridor, "
    "so that the kitchen of 4A becomes larger. The wall separates the two apartments."
)
LLM_OUT_OF_SCOPE = (
    "We want to add a light 40 square metre rooftop extension to the existing building, "
    "with a new staircase from the top floor."
)


class Demo:
    def __init__(self, service: CaseService, title: str, role: str = "consultant", permit_type: str = "modification"):
        self.service = service
        self.case = service.open_case(f"[SYNTHETIC] {title}", "A", role, permit_type)
        self.case_id = self.case["case_id"]

    def modify(self, revision: str = "B", change_type: str = "wall_relocation", **facts) -> None:
        self.case = self.service.submit_modification(self.case_id, {
            "revision": revision,
            "change_type": change_type,
            "description": "Relocate an internal wall",
            "facts": facts,
        })

    def evidence(self, evidence_id: str, type: str, domain: str, revision: str | None = "B", **extra) -> None:
        self.case = self.service.register_evidence(self.case_id, {
            "evidence_id": evidence_id,
            "category": "document",
            "type": type,
            "domain": domain,
            "status": "current",
            "revision": revision,
            "format": None,
            "valid_until": None,
            "facts": {},
            **extra,
        })

    def act(self, action: str, role: str) -> None:
        self.case = self.service.request_action(self.case_id, action, "demo-user", role)

    def attempt(self, action: str, role: str) -> None:
        """Request an action that is expected to be refused and recorded."""
        try:
            self.act(action, role)
        except (ActionForbidden, ActionHeld):
            self.case = self.service.get_case(self.case_id)

    def resolve(self, issue_id: str, selected_rule_id: str | None = None) -> None:
        self.case = self.service.resolve_issue(self.case_id, issue_id, {
            "actor_id": "demo-authority",
            "role": "authority",
            "source": "Synthetic authority clarification",
            "decision": "Clarified for the demonstration",
            "selected_rule_id": selected_rule_id,
        })


def ready_case(service: CaseService, title: str) -> Demo:
    demo = Demo(service, title)
    demo.modify(**SAFE)
    demo.evidence("plan-b", "floor_plan", "architectural")
    return demo


def h0_happy_path(service: CaseService) -> Demo:
    demo = ready_case(service, "H0 happy path")
    demo.act("approve_modification", "authority")
    return demo


def e1_missing_evidence(service: CaseService) -> Demo:
    demo = Demo(service, "E1 missing evidence")
    demo.modify(**SAFE)
    demo.attempt("prepare_review_package", "consultant")
    return demo


def e2_design_revision(service: CaseService) -> Demo:
    demo = ready_case(service, "E2 design revision")
    demo.modify(revision="C", **SAFE)
    return demo


def e3_conflicting_rules(service: CaseService) -> Demo:
    demo = Demo(service, "E3 conflicting rules")
    demo.evidence("plan-b", "floor_plan", "architectural")
    demo.evidence("fs-b", "fire_strategy", "fire_safety")
    demo.modify(load_bearing=False, fire_compartment_boundary=True, occupancy="mixed_use")
    return demo


def e4_authorization_conflict(service: CaseService) -> Demo:
    demo = ready_case(service, "E4 authorization conflict")
    demo.attempt("approve_modification", "consultant")
    return demo


def e5_late_material_information(service: CaseService) -> Demo:
    demo = ready_case(service, "E5 late material information")
    demo.act("approve_modification", "authority")
    demo.evidence("late-survey", "survey", "fire_safety", facts={"fire_compartment_boundary": True})
    return demo


def e6_governance_gap(service: CaseService) -> Demo:
    demo = Demo(service, "E6 governance gap")
    demo.evidence("plan-b", "floor_plan", "architectural")
    demo.modify(heritage_zone=True, **SAFE)
    return demo


def t0_t5_wall_relocation(service: CaseService) -> Demo:
    demo = Demo(service, "T0-T5 wall relocation")
    demo.evidence("plan-a", "floor_plan", "architectural", revision="A")
    demo.evidence("fs-1", "fire_strategy", "fire_safety", revision=None)
    demo.modify(occupancy="residential")
    demo.evidence("plan-b", "floor_plan", "architectural")
    demo.evidence("survey-1", "survey", "structural", facts={"load_bearing": False})
    demo.evidence("survey-2", "survey", "fire_safety", facts={"fire_compartment_boundary": True})
    demo.evidence("fs-1", "fire_strategy", "fire_safety", revision="A")
    demo.evidence("fs-1", "fire_strategy", "fire_safety", revision="B")
    return demo


def bim_new_permit(service: CaseService) -> Demo:
    demo = Demo(service, "New permit BIM delivery", permit_type="new_permit")
    try:
        demo.evidence("model-1", "design_model", "architectural", revision="A", format="pdf")
    except InvalidRequest:
        pass
    demo.modify(**SAFE)
    demo.attempt("prepare_review_package", "consultant")
    content = sample_model("bim_new_permit", "proposed")
    demo.case = service.register_model(demo.case_id, "proposed", "tower-7.ifc", content)
    demo.evidence("plan-b", "floor_plan", "architectural", format="ifc")
    return demo


SCENARIOS = [
    (h0_happy_path, "completed"),
    (e1_missing_evidence, "pending_evidence"),
    (e2_design_revision, "pending_evidence"),
    (e3_conflicting_rules, "escalated"),
    (e4_authorization_conflict, "awaiting_review"),
    (e5_late_material_information, "pending_evidence"),
    (e6_governance_gap, "escalated"),
    (t0_t5_wall_relocation, "awaiting_review"),
    (bim_new_permit, "awaiting_review"),
]


def run(service: CaseService) -> list[tuple[str, dict, str]]:
    return [(scenario.__name__, scenario(service).case, expected) for scenario, expected in SCENARIOS]


def free_text_case(service: CaseService, title: str, description: str, scenario_id: str = "llm_free_text") -> dict:
    """A live scenario: an approved baseline model, and a modification in free text only."""
    case = service.open_case(f"[SYNTHETIC] {title}", "A", "consultant", scenario=scenario_id)
    if scenario_id in PROPOSALS:
        service.register_model(case["case_id"], "baseline", "approved-model.ifc", sample_model(scenario_id, "baseline"))
    return service.submit_modification(case["case_id"], {
        "revision": "B",
        "change_type": None,
        "description": description,
        "facts": {},
    })


def llm_free_text(service: CaseService) -> dict:
    return free_text_case(service, "Wall relocation with AI", LLM_DESCRIPTION)


DESCRIPTIONS = {
    "h0_happy_path": ("Happy path", "H0", "Evidence is complete and the request goes straight through to approval."),
    "e1_missing_evidence": ("Missing evidence", "E1", "The floor plan is missing, so the action is held until it arrives."),
    "e2_design_revision": ("New design revision", "E2", "A new revision makes earlier evidence out of date."),
    "e3_conflicting_rules": ("Conflicting rules", "E3", "Two fire rules clash. The system does not choose and escalates."),
    "e4_authorization_conflict": ("Authorization conflict", "E4", "A consultant tries to approve and is refused."),
    "e5_late_material_information": ("Late material information", "E5", "After approval the wall turns out to be a fire separation. The case moves back."),
    "e6_governance_gap": ("Process gap", "E6", "The sources do not say who reviews this, so the case escalates."),
    "t0_t5_wall_relocation": ("Wall relocation step by step", "T0–T5", "The full sequence from the use case: information arrives piece by piece."),
    "bim_new_permit": ("New permit in BIM", "BIM", "A PDF is refused, the case is held without a model, and a real IFC file releases it."),
}
# Expected types are an interpretation of DBC Table A.1, not an official classification.
LIVE_SCENARIOS = {
    "llm_renovation_floors": ("Replacing floors", "renovation", "Clear case of finishes only.", (
        "We are replacing the floor tiles and plasterwork in the lobby with new finishes. The layout stays exactly the same."
    )),
    "llm_office_fit_out": ("Office fit-out", "modification", "Fit-out of an office unit.", (
        "We are refitting the 240 square metre office unit 1204 with new partition walls, "
        "a suspended ceiling and adapted air conditioning."
    )),
    "llm_free_text": ("Wall between two apartments", "modification", "Claude reads free text and checks it against rules from public sources. You add information up to approval.", LLM_DESCRIPTION),
    "llm_lobby_reconfiguration": ("Reconfiguring the lobby", "reconstruction", "The change affects egress routes outside its own area.", (
        "We are reconfiguring the ground floor lobby. This moves the stairwell exit, "
        "and the escape route from the floors above changes during and after the works."
    )),
    "llm_office_to_residential": ("Offices to apartments", "change_of_use", "The use of three floors changes.", (
        "We are converting floors 5 to 7 of the office building into apartments with their own kitchens and bathrooms."
    )),
    "llm_out_of_scope": ("Rooftop extension", "addition", "More area and height, with follow-up questions about the existing building.", LLM_OUT_OF_SCOPE),
    "llm_edge_floor_ceiling": ("Borderline: floors and ceiling layout", "modification", "Borderline case between renovation and modification.", (
        "We are replacing the floors in our office unit and installing a new ceiling. "
        "We are also adding two light partition walls for meeting rooms."
    )),
    "llm_edge_terrace": ("Borderline: enclosing a terrace", "addition", "Borderline case between modification and addition.", (
        "We are enclosing the existing covered terrace of the ground floor restaurant with glass walls, "
        "so that it becomes indoor space."
    )),
}


def catalog() -> list[dict]:
    live = [
        {"id": key, "title": title, "flow": "AI", "summary": summary, "live": True, "expected_type": expected}
        for key, (title, expected, summary, _) in LIVE_SCENARIOS.items()
    ]
    fixed = [
        {"id": scenario.__name__, "title": title, "flow": flow, "summary": summary, "live": False}
        for scenario, _ in SCENARIOS
        for title, flow, summary in [DESCRIPTIONS[scenario.__name__]]
    ]
    return live + fixed


def start_scenario(scenario_id: str, offline: CaseService, live: CaseService) -> dict:
    if scenario_id in LIVE_SCENARIOS:
        title, _, _, description = LIVE_SCENARIOS[scenario_id]
        return free_text_case(live, title, description, scenario_id)
    for scenario, _ in SCENARIOS:
        if scenario.__name__ == scenario_id:
            return scenario(offline).case
    raise UnknownItem(f"unknown test case {scenario_id}")


def print_case(name: str, case: dict) -> None:
    print(f"{name:32} {case['case_id']}  {case['stage']:20} {case['status']}")


def main(argv: Sequence[str] = ()) -> None:
    url = os.environ.get("REPERMIT_DATABASE_URL", "sqlite:///repermit.db")
    store = EventStore(url)
    if "--llm" in argv:
        pack = load_pack(os.environ.get("REPERMIT_PACK_PATH", PUBLIC_PACK))
        model = os.environ.get("REPERMIT_LLM_MODEL", MODEL)
        case = llm_free_text(CaseService(store, pack, assessor=ClaudeAssessor(model)))
        print_case("llm_free_text", case)
        print(json.dumps(case["assessment"]["llm_review"], indent=2))
        return
    for name, case, _ in run(CaseService(store, load_pack())):
        print_case(name, case)


if __name__ == "__main__":
    main(sys.argv[1:])
