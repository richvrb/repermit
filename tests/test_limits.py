from types import SimpleNamespace

from fastapi.testclient import TestClient

from repermit.api import create_app
from repermit.llm import AssessorUnavailable, usage_of
from tests.conftest import Api
from tests.test_llm import SAFE, FakeAssessor, modify, review
from tests.test_rounds import asking, flags, respond


def costly(cost, result=None):
    result = result or review()
    result._usage = {"model": "claude-sonnet-5-5", "input_tokens": 1000, "output_tokens": 100, "cache_read_tokens": 0, "cache_write_tokens": 0, "cost_usd": cost}
    return result


def start(database_url, pack, *results, **budgets):
    assessor = FakeAssessor(*results)
    api = Api(TestClient(create_app(database_url, pack, assessor, **budgets)))
    api.assessor = assessor
    api.open()
    return api


def skipped(api):
    return [event["payload"]["reason"] for event in api.client.get(f"/cases/{api.case_id}/history").json() if event["type"] == "llm_review_skipped"]


def test_no_call_after_the_last_round(database_url, pack):
    api = start(database_url, pack, asking("Which wall?"))
    modify(api, "wall_relocation", **SAFE)
    api.evidence("plan-1", "floor_plan", "architectural")
    respond(api, note="Do not know.")
    assert api.assessor.calls == 3
    for number in range(5):
        respond(api, note=f"More {number}.")
        api.evidence(f"extra-{number}", "floor_plan", "architectural")
    assert api.assessor.calls == 3
    case = api.case()
    assert skipped(api) and set(skipped(api)) == {"round_limit"}
    assert "ai_stop:B:round_limit" in flags(case)
    assert case["status"] == "escalated"


def test_rerun_is_refused_after_the_last_round(database_url, pack):
    api = start(database_url, pack, asking("Which wall?"))
    modify(api, "wall_relocation", **SAFE)
    api.evidence("plan-1", "floor_plan", "architectural")
    respond(api, note="Do not know.")
    response = api.client.post(f"/cases/{api.case_id}/llm-review")
    assert response.status_code == 422
    assert "round limit" in response.json()["detail"]
    assert api.assessor.calls == 3


def test_failed_calls_are_capped(database_url, pack):
    api = start(database_url, pack, AssessorUnavailable("connection failed"))
    modify(api, "wall_relocation", **SAFE)
    for number in range(10):
        api.evidence(f"plan-{number}", "floor_plan", "architectural")
    assert api.assessor.calls == pack.max_review_rounds + 2


def test_case_budget_stops_calls(database_url, pack):
    api = start(database_url, pack, costly(0.6, asking("Which wall?")), case_budget_usd=1.0)
    modify(api, "wall_relocation", **SAFE)
    api.evidence("plan-1", "floor_plan", "architectural")
    api.evidence("plan-2", "floor_plan", "architectural")
    assert api.assessor.calls == 2
    case = api.case()
    assert case["llm_cost_usd"] == 1.2
    assert skipped(api) == ["case_budget"]
    assert "ai_stop:B:case_budget" in flags(case)
    assert api.resolve("ai_stop:B:case_budget").status_code == 200
    assert "ai_stop:B:case_budget" not in flags(api.case())


def test_daily_budget_spans_cases(database_url, pack):
    first = start(database_url, pack, costly(3.0), daily_budget_usd=5.0)
    modify(first, "wall_relocation", **SAFE)
    first.evidence("plan-1", "floor_plan", "architectural")
    assert first.assessor.calls == 2
    second = start(database_url, pack, costly(3.0), daily_budget_usd=5.0)
    modify(second, "wall_relocation", **SAFE)
    assert second.assessor.calls == 0
    assert skipped(second) == ["daily_budget"]


def test_usage_is_recorded_per_call(database_url, pack):
    api = start(database_url, pack, costly(0.25))
    modify(api, "wall_relocation", **SAFE)
    event = next(event for event in api.client.get(f"/cases/{api.case_id}/history").json() if event["type"] == "llm_review_recorded")
    assert event["payload"]["usage"]["cost_usd"] == 0.25
    assert event["payload"]["usage"]["input_tokens"] == 1000


def test_usage_prices_known_and_unknown_models():
    def response(model):
        usage = SimpleNamespace(input_tokens=1_000_000, output_tokens=100_000, cache_read_input_tokens=0, cache_creation_input_tokens=0)
        return SimpleNamespace(model=model, usage=usage)

    assert usage_of(response("claude-sonnet-5-5"))["cost_usd"] == 3.0
    # Above 100K prompt tokens Haiku charges its long-prompt price; an unknown model pays the highest price.
    assert usage_of(response("claude-haiku-5-5"))["cost_usd"] == 0.75
    assert usage_of(response("some-other-model"))["cost_usd"] == 15.0
