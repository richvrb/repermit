from types import SimpleNamespace

from fastapi.testclient import TestClient

from repermit.api import create_app
from repermit.retrieval import Retriever
from tests.test_llm import FakeAssessor, review
from tests.test_retrieval import index  # noqa: F401


class Worker:
    def __init__(self, model, effort):
        self.model, self.effort = model, effort

    def review(self, state, pack, passages=()):
        return review()


def app(database_url, pack, factory=Worker, assessor="default", retriever=None):
    assessor = Worker("claude-sonnet-5-5", "high") if assessor == "default" else assessor
    return TestClient(create_app(database_url, pack, assessor, retriever, case_budget_usd=1.0, daily_budget_usd=5.0, assessor_factory=factory))


def body(**changes):
    values = {
        "review_model": "claude-sonnet-5-5", "review_effort": "high", "documents_model": None, "documents_effort": "medium",
        "case_budget_usd": 1.0, "daily_budget_usd": 5.0, "actor_id": "admin-1", "role": "coordinator",
    }
    return values | changes


def test_settings_show_the_current_configuration(database_url, pack):
    data = app(database_url, pack).get("/settings").json()
    assert data["current"]["review_model"] == "claude-sonnet-5-5"
    assert data["current"]["documents_model"] is None
    assert data["ceilings"] == {"case_budget_usd": 1.0, "daily_budget_usd": 5.0}
    assert data["models_editable"] and "claude-haiku-5-5" in data["allowed_models"]


def test_models_and_budgets_can_be_changed(database_url, pack):
    client = app(database_url, pack)
    response = client.put("/settings", json=body(documents_model="claude-haiku-5-5", documents_effort="low", case_budget_usd=0.5))
    assert response.status_code == 200, response.text
    meta = client.get("/meta").json()
    assert meta["ai"]["documents"] == {"model": "claude-haiku-5-5", "effort": "low"}
    assert meta["case_budget_usd"] == 0.5
    [change] = response.json()["history"]
    assert change["actor_id"] == "admin-1" and change["settings"]["documents_model"] == "claude-haiku-5-5"


def test_budgets_cannot_exceed_the_server_limit(database_url, pack):
    client = app(database_url, pack)
    assert client.put("/settings", json=body(case_budget_usd=2.0)).status_code == 422
    assert client.put("/settings", json=body(daily_budget_usd=-1)).status_code == 422
    assert client.get("/meta").json()["case_budget_usd"] == 1.0


def test_only_allowed_models_and_efforts(database_url, pack):
    client = app(database_url, pack)
    assert client.put("/settings", json=body(review_model="claude-fable-5-1")).status_code == 422
    assert client.put("/settings", json=body(review_effort="extreme")).status_code == 422
    assert client.put("/settings", json=body(review_model=None)).status_code == 422


def test_settings_survive_a_restart(database_url, pack):
    app(database_url, pack).put("/settings", json=body(review_model="claude-haiku-5-5", daily_budget_usd=2.0))
    meta = app(database_url, pack).get("/meta").json()
    assert meta["ai"]["review"]["model"] == "claude-haiku-5-5"
    assert meta["daily_budget_usd"] == 2.0


def test_models_are_fixed_without_a_factory(database_url, pack):
    client = app(database_url, pack, factory=None)
    assert client.get("/settings").json()["models_editable"] is False
    assert client.put("/settings", json=body(review_model="claude-haiku-5-5")).status_code == 422
    assert client.put("/settings", json=body(case_budget_usd=0.25)).status_code == 200


def test_retrieval_is_shown_and_adjustable(database_url, pack, index):  # noqa: F811
    retriever = Retriever(index)
    client = app(database_url, pack, retriever=retriever)
    data = client.get("/settings").json()
    assert data["retrieval"]["available"] and sum(data["retrieval"]["index"].values()) > 0
    assert data["current"]["retrieval_enabled"] is True and data["current"]["retrieval_passages"] == 5
    response = client.put("/settings", json=body(retrieval_enabled=False, retrieval_passages=2, retrieval_cards=0))
    assert response.status_code == 200, response.text
    assert retriever.enabled is False and retriever.passage_limits["total"] == 2 and retriever.card_limits["total"] == 0
    assert client.get("/meta").json()["knowledge_enabled"] is False


def test_retrieval_limits_are_capped(database_url, pack, index):  # noqa: F811
    client = app(database_url, pack, retriever=Retriever(index))
    assert client.put("/settings", json=body(retrieval_passages=11)).status_code == 422
    assert client.put("/settings", json=body(retrieval_cards=-1)).status_code == 422


def test_left_out_retrieval_settings_are_kept(database_url, pack, index):  # noqa: F811
    retriever = Retriever(index)
    client = app(database_url, pack, retriever=retriever)
    client.put("/settings", json=body(retrieval_passages=3))
    assert client.put("/settings", json=body(case_budget_usd=0.8)).status_code == 200
    assert retriever.passage_limits["total"] == 3


def test_switched_off_retrieval_returns_nothing(index):  # noqa: F811
    retriever = Retriever(index)
    retriever.enabled = False
    state = SimpleNamespace(modification={"description": "wall", "change_type": "x"}, latest_evidence=lambda: [], llm_review=None)
    assert retriever.for_case(state) == []


def test_settings_list_the_bim_tools(database_url, pack):
    from repermit.bim_tools import TOOLS

    tools = app(database_url, pack).get("/settings").json()["bim_tools"]
    assert [tool["name"] for tool in tools] == [tool["name"] for tool in TOOLS]
    assert all(tool["description"] and tool["inputs"] for tool in tools)


def test_bim_tool_calls_can_be_set(database_url, pack):
    from repermit.llm import ClaudeAssessor

    def factory(model, effort):
        return ClaudeAssessor(model, effort=effort)

    client = app(database_url, pack, factory=factory, assessor=ClaudeAssessor("claude-sonnet-5-5", max_tool_calls=6))
    assert client.get("/settings").json()["current"]["review_tool_calls"] == 6
    assert client.put("/settings", json=body(review_tool_calls=21)).status_code == 422
    data = client.put("/settings", json=body(review_tool_calls=2, review_model="claude-haiku-5-5")).json()
    assert data["current"]["review_tool_calls"] == 2 and data["current"]["review_model"] == "claude-haiku-5-5"
    assert client.put("/settings", json=body(review_model="claude-haiku-5-5", case_budget_usd=0.9)).json()["current"]["review_tool_calls"] == 2


def test_new_models_are_used_for_the_next_review(database_url, pack):
    used = []

    def factory(model, effort):
        used.append(model)
        return FakeAssessor(review())

    client = app(database_url, pack, factory=factory)
    client.put("/settings", json=body(review_model="claude-haiku-5-5"))
    assert used == ["claude-haiku-5-5"]
