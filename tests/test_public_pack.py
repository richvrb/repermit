from datetime import date

import pytest
import yaml
from fastapi.testclient import TestClient
from pydantic import ValidationError

from repermit.api import create_app
from repermit.assessment import assess, evaluate
from repermit.knowledge import LEGACY_PACK_VERSION, PUBLIC_PACK, Pack, load_pack
from repermit.samples import sample_model
from repermit.state import CaseState, fold
from tests.test_llm import FakeAssessor, review

TODAY = date(2026, 11, 1)


@pytest.fixture
def public():
    return load_pack(PUBLIC_PACK)


def raw_pack():
    return yaml.safe_load(PUBLIC_PACK.read_text(encoding="utf-8"))


def state(change_type, **facts):
    case = CaseState("c1", revision="B", stage="design_change")
    case.modification = {"revision": "B", "change_type": change_type, "facts": facts}
    return case


def unknown(result):
    return {d["subject"] for d in result["deficiencies"] if d["code"] == "unknown_fact"}


def missing(result):
    return {d["subject"] for d in result["deficiencies"] if d["code"] == "missing"}


def test_every_rule_is_derived_and_referenced(public):
    for rule in public.rules:
        source = public.source(rule.source)
        assert source.kind == "derived" and source.url and source.issuer
        assert rule.title and rule.text and rule.reference


def test_change_types_follow_the_building_code(public):
    assert public.change_types == ["renovation", "modification", "reconstruction", "change_of_use", "addition"]
    assert set(public.change_type_definitions) == set(public.change_types)


def test_rule_without_reference_is_rejected():
    data = raw_pack()
    data["rules"][0]["reference"] = ""
    with pytest.raises(ValidationError, match="reference"):
        Pack.model_validate(data)


def test_derived_source_without_url_is_rejected():
    data = raw_pack()
    data["sources"][0]["url"] = ""
    with pytest.raises(ValidationError, match="issuer and url"):
        Pack.model_validate(data)


def test_condition_accepts_a_listed_value():
    assert evaluate({"a": [1, 2]}, {"a": 2}) == (True, [])
    assert evaluate({"a": [1, 2]}, {"a": 3}) == (False, [])


def test_first_question_is_the_competent_entity(public):
    assert "competent_entity" in unknown(assess(state("modification"), public, TODAY))


def test_open_facts_are_asked_together_once_the_authority_is_known(public):
    result = unknown(assess(state("modification", competent_entity="dda"), public, TODAY))
    assert {"building_completed", "load_bearing", "exceeds_zoning"} <= result


def test_dependent_facts_wait_for_the_first_answer(public):
    result = unknown(assess(state("modification", competent_entity="dm"), public, TODAY))
    assert "decoration_works" in result
    assert "unit_over_100m2" not in result


def test_authority_is_asked_before_the_first_review(public):
    case = state(None)
    case.permit_type = "modification"
    result = assess(case, public, TODAY)
    assert {d["subject"] for d in result["deficiencies"]} == {"design_model", "competent_entity"}
    assert result["issues"] == []


def test_only_the_first_unknown_fact_per_rule_is_asked(public):
    result = assess(state("modification"), public, TODAY)
    assert "building_completed" not in unknown(result)
    assert "building_completed" in unknown(assess(state("modification", competent_entity="dda"), public, TODAY))


def test_questions_and_options_come_from_the_pack(public):
    deficiency = next(d for d in assess(state("modification"), public, TODAY)["deficiencies"] if d["subject"] == "competent_entity")
    assert deficiency["question"]
    assert [option["value"] for option in deficiency["options"]] == ["dda", "dm", "other"]


def test_dda_modification_requires_the_service_card_documents(public):
    result = assess(state("modification", competent_entity="dda", building_completed=True), public, TODAY)
    assert {"owner_noc", "consultant_appointment", "project_details_sheet", "modified_drawings"} <= missing(result)


def test_structural_and_fire_triggers(public):
    for entity in ("dda", "dm"):
        result = assess(state("modification", competent_entity=entity, load_bearing=True, fire_compartment_boundary=True), public, TODAY)
        assert {"structural_calculations", "civil_defence_noc"} <= missing(result)


def test_no_fire_value_is_stated(public):
    assert all(rule.sets is None for rule in public.rules)


def test_change_of_use_assesses_impacted_areas(public):
    assert "impacted_area_assessment" in missing(assess(state("change_of_use"), public, TODAY))


def test_addition_relying_on_existing_building(public):
    result = assess(state("addition", relies_on_existing_building=True), public, TODAY)
    assert "existing_building_assessment" in missing(result)


def test_dubai_municipality_case_is_a_process_gap(public):
    issues = assess(state("modification", competent_entity="dm"), public, TODAY)["issues"]
    assert [issue["id"] for issue in issues] == ["gap:DM-DOCS"]
    assert issues[0]["kind"] == "process_gap"


def test_decoration_licence_applies_above_100m2_outside_commercial_centres(public):
    facts = dict(competent_entity="dm", decoration_works=True, non_residential_unit=True, in_commercial_centre=False)
    assert "decoration_licence" in missing(assess(state("modification", unit_over_100m2=True, **facts), public, TODAY))
    assert "decoration_licence" not in missing(assess(state("modification", unit_over_100m2=False, **facts), public, TODAY))


def test_apartment_is_outside_the_decoration_route(public):
    result = assess(state("modification", competent_entity="dm", decoration_works=True, non_residential_unit=False), public, TODAY)
    assert "decoration_licence" not in missing(result)


def test_civil_defence_applies_under_every_authority(public):
    result = assess(state("modification", competent_entity="other", fire_compartment_boundary=True), public, TODAY)
    assert "civil_defence_noc" in missing(result)
    assert "gap:FIRE-VALUES" in [issue["id"] for issue in result["issues"]]


def test_safety_system_change_needs_civil_defence(public):
    assert "civil_defence_noc" in missing(assess(state("modification", safety_systems_changed=True), public, TODAY))


def test_structural_rule_of_dda_does_not_reach_another_authority(public):
    result = assess(state("modification", competent_entity="other", load_bearing=True), public, TODAY)
    assert "structural_calculations" not in missing(result)


def test_moved_unit_boundary_goes_to_a_reviewer(public):
    result = assess(state("modification", changes_unit_boundary=True, load_bearing=True), public, TODAY)
    assert {"gap:OWN-WALL", "gap:OWN-COMMON"} <= {issue["id"] for issue in result["issues"]}
    assert result["domains"]["property"] == "affected"


def test_unit_boundary_is_asked(public):
    assert "changes_unit_boundary" in unknown(assess(state("modification"), public, TODAY))


def test_simple_maintenance_is_a_reviewer_decision(public):
    result = assess(state("renovation", simple_maintenance=True), public, TODAY)
    assert "modified_drawings" not in missing(result)
    assert "gap:EXEMPT-WORKS" in [issue["id"] for issue in result["issues"]]


def test_renovation_beyond_maintenance_needs_drawings(public):
    assert "modified_drawings" in missing(assess(state("renovation", simple_maintenance=False), public, TODAY))


def test_planning_use_differs_from_change_of_use(public):
    result = assess(state("modification", competent_entity="dm", planning_use_change=True), public, TODAY)
    assert "use_change_approval" in missing(result)
    assert "impacted_area_assessment" not in missing(result)


def test_decoration_boundary_rule_is_dubai_municipality_only(public):
    facts = dict(decoration_works=True, changes_unit_boundary=True)
    assert "owner_noc" not in missing(assess(state("modification", competent_entity="other", **facts), public, TODAY))
    assert "owner_noc" in missing(assess(state("modification", competent_entity="dm", **facts), public, TODAY))


def test_case_keeps_the_pack_it_started_with(database_url, public):
    from repermit.knowledge import ARCHIVED_PACKS, load_pack
    from repermit.service import CaseService
    from repermit.store import EventStore

    old = load_pack(ARCHIVED_PACKS[0])
    store = EventStore(database_url)
    case = CaseService(store, old).open_case("x", "A", "consultant")
    current = CaseService(store, public, packs={old.version: old})
    assert current.get_case(case["case_id"])["pack_version"] == "dubai-public-2026.1"


def test_unknown_change_type_is_a_retrieval_gap(public):
    issues = assess(state("wall_relocation"), public, TODAY)["issues"]
    assert issues[0]["kind"] == "retrieval_gap"


def test_applied_rule_shows_title_and_reference(public):
    rule = assess(state("modification"), public, TODAY)["applied_rules"][0]
    assert rule["source_kind"] == "derived"
    assert rule["reference"] == "LO 3/1999 art. 4 as replaced by Res. 65/2022, and art. 14"
    assert "Resolution No. (65)" in rule["source_title"]


def test_prompt_carries_rule_content(public):
    from repermit.llm import build_prompt

    case = state("modification")
    case.modification["description"] = "Move a wall"
    prompt = build_prompt(case, public)
    assert "Fit-out of a space or unit" in prompt
    assert "Civil Defence NOC" in prompt
    assert "fire_compartment_boundary" in prompt


@pytest.fixture
def client(database_url, public):
    return TestClient(create_app(database_url, public, FakeAssessor(review(change_type="modification"))))


def test_live_case_uses_public_pack_and_fixed_case_stays_synthetic(client):
    live = client.post("/demo/scenarios/llm_free_text").json()
    assert live["modification"]["change_type"] is None
    assert client.post(f"/cases/{live['case_id']}/llm-review").status_code == 422
    live = client.post(f"/cases/{live['case_id']}/models", content=sample_model("llm_free_text", "proposed")).json()
    fixed = client.post("/demo/scenarios/h0_happy_path").json()
    assert live["pack_version"] == "dubai-public-2026.4"
    assert live["modification"]["change_type"] == "modification"
    assert fixed["pack_version"] == LEGACY_PACK_VERSION
    assert fixed["status"] == "completed"
    assert client.get(f"/cases/{fixed['case_id']}").json()["status"] == "completed"


def test_case_without_a_recorded_pack_is_synthetic():
    event = {
        "seq": 1, "type": "case_opened",
        "payload": {"project_name": "x", "permit_type": "modification", "revision": "A", "responsible_role": "consultant", "stage": "s"},
    }
    assert fold("c1", [event]).pack_version == LEGACY_PACK_VERSION
