from repermit.llm import InformationRequest, build_prompt
from tests.test_llm import SAFE, AssessorUnavailable, finding, modify, review, run  # noqa: F401


def asking(*questions, **kwargs):
    result = review(**kwargs)
    result.information_requests = [InformationRequest(question=text, domain="structural", reason="Matters.") for text in questions]
    return result


def respond(api, **body):
    return api.client.post(f"/cases/{api.case_id}/responses", json=body)


def subjects(case):
    return [item["subject"] for item in case["assessment"]["deficiencies"]]


def flags(case):
    return [issue["id"] for issue in case["assessment"]["issues"]]


def ready(api):
    return modify(api, "wall_relocation", **SAFE)


def test_evidence_triggers_a_review(run):
    api = run(review())
    ready(api)
    api.evidence("plan-1", "floor_plan", "architectural")
    assert api.assessor.calls == 2


def test_no_call_without_an_earlier_review(database_url, pack):
    from fastapi.testclient import TestClient

    from repermit.api import create_app
    from tests.conftest import Api
    from tests.test_llm import FakeAssessor

    assessor = FakeAssessor(review())
    client = TestClient(create_app(database_url, pack, assessor))
    case = client.post("/demo/scenarios/e1_missing_evidence").json()
    api = Api(client)
    api.case_id = case["case_id"]
    api.evidence("plan-1", "floor_plan", "architectural")
    assert assessor.calls == 0


def test_response_is_one_round(run):
    api = run(asking("Which wall?"), review())
    case = modify(api)
    assert case["review_round"] == 1
    body = {
        "facts": {"load_bearing": False, "fire_compartment_boundary": False},
        "answers": [{"question": "Which wall?", "answer": "Wall 4A."}],
        "documents": ["floor_plan"],
        "note": "Extra note.",
    }
    response = respond(api, **body)
    assert response.status_code == 200, response.text
    case = response.json()
    assert api.assessor.calls == 2
    assert case["review_round"] == 2
    assert {item["type"] for item in case["evidence"]} == {"statement", "floor_plan", "note"}
    assert "Wall 4A." in next(item for item in case["evidence"] if item["type"] == "note")["description"]
    assert "ai-1" not in subjects(case)


def test_empty_response_is_rejected(run):
    api = run(review())
    ready(api)
    assert respond(api, answers=[{"question": "q", "answer": "  "}]).status_code == 422
    assert api.assessor.calls == 1


def test_response_needs_a_modification(run):
    assert respond(run(review()), note="x").status_code == 422


def test_unrequested_document_records_nothing(run):
    api = run(review())
    ready(api)
    before = len(api.history_types())
    assert respond(api, note="x", documents=["fire_strategy"]).status_code == 422
    assert len(api.history_types()) == before


def test_open_question_holds_the_case_until_a_review_drops_it(run):
    api = run(asking("Which wall?"), asking("Which wall?"), review())
    ready(api)
    case = api.evidence("plan-1", "floor_plan", "architectural")
    assert case["status"] == "pending_evidence"
    assert subjects(case) == ["ai-1"]
    assert case["stage"] == "design_change"
    case = respond(api, answers=[{"question": "Which wall?", "answer": "Wall 4A."}]).json()
    assert case["assessment"]["deficiencies"] == []
    assert case["stage"] == "under_review"


def test_round_limit_goes_to_the_authority(run):
    api = run(asking("Which wall?"))
    ready(api)
    api.evidence("plan-1", "floor_plan", "architectural")
    case = respond(api, note="Do not know.").json()
    assert case["review_round"] == 3
    assert subjects(case) == []
    assert flags(case) == ["llm:B:open_questions"]
    assert api.resolve("llm:B:open_questions", role="consultant").status_code == 403
    assert api.resolve("llm:B:open_questions").json()["stage"] == "under_review"


def test_explicit_withdrawal_closes_a_flag(run):
    api = run(review(domains=[finding("fire_safety")]), review(domains=[finding("fire_safety", "not_affected")]))
    ready(api)
    case = api.evidence("plan-1", "floor_plan", "architectural")
    assert flags(case) == []
    withdrawn = [
        event["payload"]["withdrawn_flags"]
        for event in api.client.get(f"/cases/{api.case_id}/history").json()
        if event["type"] == "assessment_recorded"
    ]
    assert ["llm:B:fire_safety"] in withdrawn


def test_flag_stays_when_the_domain_is_left_out(run):
    api = run(review(domains=[finding("fire_safety")]), review())
    ready(api)
    assert flags(api.evidence("plan-1", "floor_plan", "architectural")) == ["llm:B:fire_safety"]


def test_flag_stays_after_a_failed_review(run):
    api = run(review(domains=[finding("fire_safety")]), AssessorUnavailable("connection failed"))
    ready(api)
    assert "llm:B:fire_safety" in flags(api.evidence("plan-1", "floor_plan", "architectural"))


def test_flag_closes_when_the_rules_cover_the_domain(run):
    api = run(review(domains=[finding("fire_safety")]), review(domains=[finding("fire_safety")]))
    modify(api, "wall_relocation", load_bearing=False, occupancy="residential", fire_compartment_boundary=False)
    case = respond(api, facts={"fire_compartment_boundary": True}).json()
    assert "llm:B:fire_safety" not in flags(case)


def test_first_review_waits_for_the_model(database_url):
    from fastapi.testclient import TestClient

    from repermit.api import create_app
    from repermit.knowledge import PUBLIC_PACK, load_pack
    from repermit.samples import sample_model
    from tests.test_llm import FakeAssessor

    assessor = FakeAssessor(review("modification"))
    client = TestClient(create_app(database_url, load_pack(PUBLIC_PACK), assessor))
    case = client.post("/demo/scenarios/llm_free_text").json()
    case_id = case["case_id"]
    assert assessor.calls == 0
    assert case["status"] == "pending_evidence"
    case = client.post(f"/cases/{case_id}/responses", json={"facts": {"competent_entity": "dda"}}).json()
    assert assessor.calls == 0
    assert case["assessment"]["llm_review"] is None
    case = client.post(f"/cases/{case_id}/models", content=sample_model("llm_free_text", "proposed")).json()
    assert assessor.calls == 1
    assert case["review_round"] == 1
    assert case["modification"]["change_type"] == "modification"


def test_prompt_carries_round_facts_and_model_changes(run, pack):
    from repermit.state import fold

    api = run(review(domains=[finding("fire_safety")]))
    ready(api)
    state = fold(api.case_id, api.client.get(f"/cases/{api.case_id}/history").json())
    prompt = build_prompt(state, pack)
    assert '"review_round": 2' in prompt
    assert '"established_facts"' in prompt
    assert '"previous_findings"' in prompt
    assert '"elements"' not in prompt.split("<case>")[1]
