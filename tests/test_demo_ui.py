from fastapi.testclient import TestClient

from repermit.api import create_app
from repermit.demo import SCENARIOS, catalog
from repermit.knowledge import PUBLIC_PACK, load_pack
from tests.test_llm import FakeAssessor, review


def test_index_is_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "RePermit" in response.text
    assert '<html lang="en">' in response.text


def test_knowledge_page_data(database_url):
    client = TestClient(create_app(database_url, load_pack(PUBLIC_PACK)))
    data = client.get("/knowledge").json()
    assert data["pack_version"].startswith("dubai-public")
    assert all(rule["id"] and rule["source_url"] for rule in data["rules"])
    assert data["gaps"] and data["documents"] and data["sources"] and data["cards"]
    assert data["index_available"] is False


def test_navigation_is_served(client):
    html = client.get("/").text
    assert 'id="nav"' in html and "CASE_TABS" in html


def test_meta_exposes_pack_choices(client):
    meta = client.get("/meta").json()
    assert meta["llm_enabled"] is False
    assert "authority" in meta["roles"]


def test_catalog_lists_every_scenario():
    entries = catalog()
    live = [entry for entry in entries if entry["live"]]
    assert len(entries) == len(SCENARIOS) + len(live)
    assert {entry["expected_type"] for entry in live} == set(load_pack(PUBLIC_PACK).change_types)


def test_live_scenarios_are_unavailable_without_llm(client):
    scenarios = {item["id"]: item for item in client.get("/demo/scenarios").json()}
    assert scenarios["llm_free_text"]["available"] is False
    assert scenarios["h0_happy_path"]["available"] is True


def test_start_fixed_scenario(client):
    response = client.post("/demo/scenarios/h0_happy_path")
    assert response.status_code == 201
    assert response.json()["project_name"].startswith("[SYNTHETIC]")
    assert response.json()["status"] == "completed"


def test_start_live_scenario_uses_the_assessor(database_url, pack):
    assessor = FakeAssessor(review())
    client = TestClient(create_app(database_url, pack, assessor))
    assert client.post("/demo/scenarios/llm_free_text").json()["status"] == "pending_evidence"
    assert assessor.calls == 1


def test_fixed_scenarios_never_call_the_assessor(database_url, pack):
    assessor = FakeAssessor(review())
    client = TestClient(create_app(database_url, pack, assessor))
    client.post("/demo/scenarios/h0_happy_path")
    assert assessor.calls == 0


def test_unknown_scenario_is_not_found(client):
    assert client.post("/demo/scenarios/nope").status_code == 404


def test_cases_are_listed_newest_first(client):
    first = client.post("/demo/scenarios/e1_missing_evidence").json()
    second = client.post("/demo/scenarios/h0_happy_path").json()
    cases = client.get("/cases").json()
    assert [case["case_id"] for case in cases] == [second["case_id"], first["case_id"]]
    assert cases[0]["status"] == "completed"


def test_case_can_be_read_at_an_earlier_step(client):
    case = client.post("/demo/scenarios/h0_happy_path").json()
    url = f"/cases/{case['case_id']}"
    assert client.get(url, params={"at": 1}).json()["status"] == "open"
    assert client.get(url, params={"at": 1}).json()["assessment"] is None
    assert client.get(url).json()["status"] == "completed"


def test_step_below_one_is_rejected(client):
    case = client.post("/demo/scenarios/h0_happy_path").json()
    assert client.get(f"/cases/{case['case_id']}", params={"at": 0}).status_code == 422
