import ifcopenshell
import ifcopenshell.geom
import pytest
from fastapi.testclient import TestClient

from repermit.api import create_app
from repermit.bim import InvalidModel, compare, derive_facts, read_model
from repermit.demo import LIVE_SCENARIOS
from repermit.knowledge import PUBLIC_PACK, load_pack
from repermit.samples import PROPOSALS, sample_model
from tests.test_llm import FakeAssessor, review


def changes(scenario):
    baseline = read_model(sample_model(scenario, "baseline"))["elements"]
    return compare(baseline, read_model(sample_model(scenario, "proposed"))["elements"])


@pytest.mark.parametrize("content", [b"%PDF-1.7", b"ISO-10303-21;\ngarbage", b""])
def test_invalid_files_are_refused(content):
    with pytest.raises(InvalidModel):
        read_model(content)


def test_model_summary():
    summary = read_model(sample_model("llm_free_text", "baseline"))["summary"]
    assert summary["schema"] == "IFC4"
    assert summary["storeys"] == 13
    assert summary["elements"]["IfcWindow"] > 100
    assert len(summary["sha256"]) == 64


def test_sample_elements_have_visible_geometry():
    model = ifcopenshell.file.from_string(sample_model("llm_free_text", "proposed").decode())
    settings = ifcopenshell.geom.settings()
    elements = model.by_type("IfcElement")
    assert elements
    for element in elements:
        assert ifcopenshell.geom.create_shape(settings, element).geometry.verts, element.Name


def test_every_live_case_has_a_changing_sample_model():
    for scenario in LIVE_SCENARIOS:
        assert scenario in PROPOSALS
        assert changes(scenario), scenario


def test_moved_wall_is_a_change():
    found = changes("llm_free_text")
    assert [(item["change"], item["name"]) for item in found] == [("changed", "Wall 4A-4B")]


def test_facts_follow_the_changed_elements():
    assert derive_facts(changes("llm_free_text")) == {"load_bearing": True, "fire_compartment_boundary": True, "facade_change": False}
    assert derive_facts(changes("llm_renovation_floors")) == {"load_bearing": False, "fire_compartment_boundary": False, "facade_change": False}


def test_missing_values_stay_unknown():
    assert derive_facts(changes("llm_edge_terrace")) == {"facade_change": True}


def test_structural_class_counts_as_load_bearing():
    assert derive_facts([{"class": "IfcColumn", "properties": {}}])["load_bearing"] is True


def test_no_changes_derive_no_facts():
    assert derive_facts([]) == {}


@pytest.fixture
def public(database_url):
    return TestClient(create_app(database_url, load_pack(PUBLIC_PACK), FakeAssessor(review("modification"))))


def start(client):
    return client.post("/demo/scenarios/llm_free_text").json()


def upload(client, case_id, content, kind="proposed"):
    return client.post(f"/cases/{case_id}/models", params={"kind": kind, "filename": "m.ifc"}, content=content)


def subjects(case):
    return [item["subject"] for item in case["assessment"]["deficiencies"]]


def test_live_case_starts_with_baseline_and_no_proposal(public):
    case = start(public)
    assert [item["type"] for item in case["evidence"]] == ["baseline_model"]
    assert "elements" not in case["evidence"][0]
    assert "design_model" in subjects(case)


def test_proposed_model_closes_the_deficiency_and_answers_questions(public):
    case = start(public)
    assert subjects(case) == ["design_model", "competent_entity"]
    updated = upload(public, case["case_id"], sample_model("llm_free_text", "proposed")).json()
    assert "design_model" not in subjects(updated)
    assert "fire_compartment_boundary" not in subjects(updated)
    assert "civil_defence_noc" in subjects(updated)
    assert updated["evidence"][-1]["changes"][0]["name"] == "Wall 4A-4B"


def test_invalid_upload_records_nothing(public):
    case = start(public)
    before = len(public.get(f"/cases/{case['case_id']}/history").json())
    assert upload(public, case["case_id"], b"%PDF-1.7").status_code == 422
    assert len(public.get(f"/cases/{case['case_id']}/history").json()) == before


def test_metadata_only_model_is_refused(public):
    case = start(public)
    body = {"evidence_id": "m", "category": "document", "type": "design_model", "domain": "architectural", "revision": "B", "format": "ifc"}
    response = public.post(f"/cases/{case['case_id']}/evidence", json=body)
    assert response.status_code == 422
    assert "uploaded" in response.text


def test_without_baseline_no_facts_are_derived(database_url):
    client = TestClient(create_app(database_url, load_pack(PUBLIC_PACK)))
    body = {"project_name": "x", "revision": "A", "responsible_role": "consultant"}
    case_id = client.post("/cases", json=body).json()["case_id"]
    case = upload(client, case_id, sample_model("llm_free_text", "proposed")).json()
    assert case["evidence"][0]["facts"] == {}
    assert case["evidence"][0]["model"]["compared"] is False


def test_sample_download(client):
    response = client.get("/demo/models/llm_free_text/baseline")
    assert response.status_code == 200
    assert read_model(response.content)["summary"]["schema"] == "IFC4"
    assert client.get("/demo/models/nope/baseline").status_code == 404


def test_new_permit_is_held_without_a_model(client):
    body = {"project_name": "x", "revision": "A", "responsible_role": "consultant", "permit_type": "new_permit"}
    case_id = client.post("/cases", json=body).json()["case_id"]
    modification = {"revision": "B", "change_type": "wall_relocation", "description": "x", "facts": {"load_bearing": False, "fire_compartment_boundary": False}}
    case = client.post(f"/cases/{case_id}/modifications", json=modification).json()
    assert "design_model" in subjects(case)
    assert case["stage"] == "design_change"
    assert "design_model" not in subjects(upload(client, case_id, sample_model("bim_new_permit", "proposed")).json())


def test_synthetic_modification_needs_no_model(api):
    assert "design_model" not in subjects(api.ready_case())
