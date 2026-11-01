"""UC-01 flows, driven through the HTTP API."""

import yaml

from fastapi.testclient import TestClient

from repermit.api import create_app
from repermit.knowledge import DEFAULT_PACK, Pack
from tests.conftest import Api

SAFE = {"load_bearing": False, "fire_compartment_boundary": False, "occupancy": "residential"}
MIXED = {"load_bearing": False, "fire_compartment_boundary": True, "occupancy": "mixed_use"}


def test_h0_happy_path(api):
    case = api.ready_case()
    assert case["stage"] == "under_review"
    assert case["status"] == "awaiting_review"
    assert case["plan"]["next_action"] == "approve_modification"
    assert case["plan"]["autonomy"] == "human_only"

    response = api.act("approve_modification", role="authority")
    assert response.status_code == 200
    assert response.json()["stage"] == "approved_simulated"
    assert response.json()["status"] == "completed"
    assert "disclaimer" in response.json()["assessment"]
    assert response.json()["assessment"]["pack_version"] == "synthetic-2026.1"

    assert api.history_types()[:2] == ["case_opened", "modification_submitted"]
    assert api.history_types().count("action_executed") == 3


def test_t0_to_t5_event_sequence(api):
    # T0: design and evidence appear complete; no assessment before a modification.
    api.open()
    api.evidence("plan-a", "floor_plan", "architectural", revision="A")
    case = api.evidence("fs-1", "fire_strategy", "fire_safety", revision=None)
    assert case["status"] == "open"

    # T1: wall relocation reported; potentially affected domains identified.
    case = api.modify(occupancy="residential")
    assert case["assessment"]["domains"]["structural"] == "potentially_affected"
    assert case["assessment"]["domains"]["fire_safety"] == "potentially_affected"
    assert case["status"] == "pending_evidence"
    api.evidence("plan-b", "floor_plan", "architectural")

    # T2: non-load-bearing updates structural without clearing other domains.
    case = api.evidence("survey", "survey", "structural", facts={"load_bearing": False})
    assert case["assessment"]["domains"]["structural"] == "not_affected"
    assert case["assessment"]["domains"]["fire_safety"] == "potentially_affected"
    assert case["stage"] == "design_change"

    # T3: fire compartment boundary; fire safety affected and actions held.
    case = api.evidence("survey-2", "survey", "fire_safety", facts={"fire_compartment_boundary": True})
    assert case["assessment"]["domains"]["fire_safety"] == "affected"
    assert case["plan"]["held"] is True
    assert ("revision_unknown", "fire_strategy") in {
        (d["code"], d["subject"]) for d in case["assessment"]["deficiencies"]
    }

    # T4: fire evidence turns out to be linked to the earlier revision.
    case = api.evidence("fs-1", "fire_strategy", "fire_safety", revision="A")
    impact = {item["evidence_id"]: item["impact"] for item in case["assessment"]["impact"]}
    assert impact["fs-1"] == "revalidate"
    assert case["plan"]["held"] is True

    # T5: updated evidence; permitted activity resumes, but safety needs human review.
    case = api.evidence("fs-1", "fire_strategy", "fire_safety", revision="B")
    assert case["stage"] == "package_prepared"
    assert case["status"] == "awaiting_review"
    assert case["plan"] == {"next_action": "submit_for_review", "autonomy": "human_review", "held": False, "hold_reasons": []}


def test_e1_missing_evidence_holds_then_resumes(api):
    api.open()
    case = api.modify(**SAFE)
    assert case["status"] == "pending_evidence"
    assert case["stage"] == "design_change"

    response = api.act("prepare_review_package")
    assert response.status_code == 409
    assert api.case()["stage"] == "design_change"
    assert "action_denied" in api.history_types()

    assert api.evidence("plan-1", "floor_plan", "architectural")["stage"] == "under_review"


def test_e2_new_revision_prevents_stale_conclusion(api):
    api.ready_case()
    case = api.modify(revision="C", **SAFE)
    assert case["stage"] == "design_change"
    assert case["assessment"]["basis"]["revision"] == "C"
    assert ("stale_revision", "floor_plan") in {(d["code"], d["subject"]) for d in case["assessment"]["deficiencies"]}
    assert api.history_types().count("assessment_recorded") >= 2


def test_e3_conflict_is_escalated_not_decided(api):
    api.open()
    api.evidence("plan-1", "floor_plan", "architectural")
    api.evidence("fs-1", "fire_strategy", "fire_safety")
    case = api.modify(**MIXED)
    assert case["status"] == "escalated"
    issue = case["assessment"]["issues"][0]
    assert issue["kind"] == "rule_conflict"
    assert issue["rules"] == ["R-FIR-02", "R-FIR-03"]
    assert issue["sources"] == ["SYN-FIRE-A", "SYN-FIRE-B"]
    applied = {rule["rule"] for rule in case["assessment"]["applied_rules"]}
    assert {"R-FIR-02", "R-FIR-03"} <= applied

    assert api.resolve("conflict:fire_rating_minutes", selected_rule_id="R-XXX").status_code == 422

    resolved = api.resolve("conflict:fire_rating_minutes", selected_rule_id="R-FIR-03").json()
    assert resolved["status"] == "awaiting_review"
    assert resolved["assessment"]["issues"] == []
    applied = {rule["rule"] for rule in resolved["assessment"]["applied_rules"]}
    assert "R-FIR-02" not in applied and "R-FIR-03" in applied
    assert resolved["resolutions"][0]["source"] == "Authority clarification 12"


def test_only_authority_resolves_issues(api):
    api.open()
    api.modify(**MIXED)
    response = api.resolve("conflict:fire_rating_minutes", role="consultant", selected_rule_id="R-FIR-02")
    assert response.status_code == 403
    assert api.case()["status"] == "escalated"
    assert "resolution_denied" in api.history_types()


def test_e4_unauthorized_action_denied_then_authorized(api):
    api.ready_case()
    denied = api.act("approve_modification", role="consultant")
    assert denied.status_code == 403
    assert api.case()["stage"] == "under_review"
    assert "action_denied" in api.history_types()
    assert api.act("approve_modification", role="authority").status_code == 200


def test_e4_autonomy_does_not_override_authorization(api):
    api.open(role="observer")
    case = api.modify(**SAFE)
    case = api.evidence("plan-1", "floor_plan", "architectural")
    assert case["plan"]["autonomy"] == "autonomous"
    assert case["stage"] == "design_change"
    assert case["status"] == "awaiting_review"
    assert "action_denied" in api.history_types()

    assert api.act("prepare_review_package", role="coordinator").status_code == 200
    assert api.case()["stage"] != "design_change"


def test_action_not_available_from_stage_is_refused(api):
    api.ready_case()
    assert api.act("prepare_review_package").status_code == 409
    assert api.case()["stage"] == "under_review"


def test_e5_late_material_information_reverses_and_replans(api):
    api.ready_case()
    assert api.act("approve_modification", role="authority").status_code == 200

    case = api.evidence("late", "survey", "fire_safety", facts={"heritage_zone": True})
    assert case["stage"] == "design_change"
    assert case["status"] == "escalated"
    assert "stage_reversed" in api.history_types()
    history = api.client.get(f"/cases/{api.case_id}/history").json()
    reversal = next(event for event in history if event["type"] == "stage_reversed")
    assert reversal["payload"]["action"] == "approve_modification"
    assert "action_executed" in api.history_types()


def test_non_material_evidence_changes_nothing(api):
    case = api.ready_case()
    after = api.evidence("note", "photo", "architectural")
    assert after["stage"] == case["stage"]
    assert "stage_reversed" not in api.history_types()


def test_e6_process_gap_is_escalated(api):
    api.open()
    api.evidence("plan-1", "floor_plan", "architectural")
    case = api.modify(heritage_zone=True, **SAFE)
    assert case["status"] == "escalated"
    assert case["assessment"]["issues"][0]["kind"] == "process_gap"
    assert api.resolve("gap:GAP-01").json()["status"] == "awaiting_review"


def test_uncovered_change_type_is_a_retrieval_gap(api):
    api.open()
    case = api.modify(change_type="roof_extension")
    assert case["status"] == "escalated"
    assert case["assessment"]["issues"][0]["kind"] == "retrieval_gap"


def test_conditional_action_runs_without_safety_impact(api):
    assert api.ready_case()["stage"] == "under_review"


def test_custom_pack_can_be_used(database_url):
    data = yaml.safe_load(DEFAULT_PACK.read_text(encoding="utf-8"))
    data["version"] = "custom"
    api = Api(TestClient(create_app(database_url, Pack.model_validate(data))))
    api.open()
    assert api.modify()["assessment"]["pack_version"] == "custom"
