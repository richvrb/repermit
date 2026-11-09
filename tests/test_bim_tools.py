import json
from types import SimpleNamespace

import pytest

from repermit.bim import read_model
from repermit.bim_tools import TOOLS, ModelTools
from repermit.llm import AssessorUnavailable, ClaudeAssessor
from repermit.samples import sample_model
from repermit.state import CaseState
from tests.test_llm import review

SCENARIO = "llm_renovation_floors"


@pytest.fixture(scope="module")
def models():
    items = []
    for kind, type_ in (("baseline", "baseline_model"), ("proposed", "design_model")):
        parsed = read_model(sample_model(SCENARIO, kind))
        items.append({"evidence_id": f"{kind}-model", "version": 1, "type": type_, "status": "current", "revision": "B", "facts": {},
                      "elements": parsed["elements"], "details": parsed["details"], "model": {"filename": f"{kind}.ifc"}})
    return items


def case_with(models):
    state = CaseState("c1", revision="B")
    state.modification = {"description": "Replace the lobby floor finish", "change_type": "renovation", "facts": {}}
    for item in models:
        state.evidence[item["evidence_id"]] = [item]
    return state


def call(tools, name, **arguments):
    return json.loads(tools.run(name, arguments))


def find(tools, **filters):
    arguments = {"model": "proposed", "ifc_class": None, "storey": None, "name_contains": None, "property": None, "change": "any"} | filters
    return call(tools, "find_elements", **arguments)


def test_tools_are_not_strict():
    # Strict tools with the review's output schema make the grammar too large for the API.
    for tool in TOOLS:
        assert "strict" not in tool and tool["input_schema"]["additionalProperties"] is False


def test_inputs_are_checked_without_strict_mode(models):
    tools = ModelTools(case_with(models))
    assert call(tools, "find_elements", model="proposed", change="added")["count"] == 1
    assert "missing inputs" in call(tools, "find_elements")["error"]
    assert "unknown inputs" in call(tools, "model_overview", model="proposed", sql="drop")["error"]
    assert "must be one of" in call(tools, "model_overview", model="draft")["error"]
    assert "must be number" in call(tools, "elements_near", model="proposed", global_id="x", radius_m="far")["error"]
    assert "must be string" in call(tools, "find_elements", model="proposed", storey=3)["error"]


def test_reading_keeps_storeys_and_details(models):
    details = models[1]["details"]
    assert details["storeys"][0] == {"name": "Level 1", "elevation": 0.0}
    assert all("storey" in item for item in details["elements"].values())


def test_overview_and_changes(models):
    tools = ModelTools(case_with(models))
    overview = call(tools, "model_overview", model="proposed")
    assert len(overview["storeys"]) == 13 and overview["elements"]["IfcWall"] > 0
    assert overview["changes"]["added"] == 1


def test_find_and_get_an_element(models):
    tools = ModelTools(case_with(models))
    [added] = find(tools, change="added")["elements"]
    assert added["name"] == "Lobby floor finish (new)" and added["storey"] == "Level 1"
    element = call(tools, "get_element", model="proposed", global_id=added["global_id"])
    assert element["class"] == "IfcCovering" and "property_sets" in element
    walls = find(tools, ifc_class="IfcWall", storey="Level 12", property="LoadBearing")
    assert walls["count"] > 0 and all(row["storey"] == "Level 12" for row in walls["elements"])
    assert len(find(tools)["elements"]) == 30 and find(tools)["truncated"]


def test_elements_near(models):
    tools = ModelTools(case_with(models))
    [added] = find(tools, change="added")["elements"]
    near = call(tools, "elements_near", model="proposed", global_id=added["global_id"], radius_m=4)
    distances = [row["distance_m"] for row in near["elements"]]
    assert distances == sorted(distances) and all(value <= 4 for value in distances)
    assert call(tools, "elements_near", model="proposed", global_id=added["global_id"], radius_m=500)["radius_m"] == 20


def test_mistakes_come_back_as_errors(models):
    tools = ModelTools(case_with(models))
    assert "error" in call(tools, "get_element", model="proposed", global_id="nope")
    assert "error" in json.loads(tools.run("drop_tables", {}))
    assert "error" in call(ModelTools(case_with(models[1:])), "model_overview", model="baseline")


class Turns:
    """A fake client that answers with tool calls first and a review last."""

    def __init__(self, *turns):
        self.turns = list(turns)
        self.requests = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(parse=self.parse))

    def parse(self, **kwargs):
        self.requests.append(kwargs | {"messages": list(kwargs["messages"])})
        turn = self.turns.pop(0) if len(self.turns) > 1 else self.turns[0]
        usage = SimpleNamespace(input_tokens=1000, output_tokens=100, cache_read_input_tokens=0, cache_creation_input_tokens=0)
        return SimpleNamespace(model="claude-sonnet-5-5", usage=usage, **turn)


def asks(name, **arguments):
    block = SimpleNamespace(type="tool_use", id=f"t-{name}", name=name, input=arguments)
    return {"stop_reason": "tool_use", "content": [block], "parsed_output": None}


DONE = {"stop_reason": "end_turn", "content": [], "parsed_output": review()}


def test_claude_calls_tools_and_then_reviews(models, pack):
    client = Turns(asks("model_overview", model="proposed"), DONE)
    result = ClaudeAssessor(client=client, max_tool_calls=4).review(case_with(models), pack)
    assert result.summary == "Wall moves."
    assert [call["name"] for call in result._tool_calls] == ["model_overview"]
    assert result._usage["turns"] == 2 and result._usage["input_tokens"] == 2000
    first, second = client.requests
    assert first["tools"] and first["cache_control"] == {"type": "ephemeral"} and "fallbacks" in first
    assert "fallbacks" not in second and second["model"] == "claude-sonnet-5-5"
    tool_result = second["messages"][-1]["content"][0]
    assert tool_result["type"] == "tool_result" and "Level 1" in tool_result["content"]


def test_tool_calls_are_capped(models, pack):
    client = Turns(asks("model_overview", model="proposed"))
    with pytest.raises(AssessorUnavailable) as error:
        ClaudeAssessor(client=client, max_tool_calls=2).review(case_with(models), pack)
    assert len(client.requests) == 4
    assert error.value.usage["turns"] == 4
    refused = client.requests[-1]["messages"][-1]["content"][0]
    assert refused["is_error"] is True


def test_no_tools_when_switched_off_or_without_a_model(models, pack):
    client = Turns(DONE)
    ClaudeAssessor(client=client, max_tool_calls=0).review(case_with(models), pack)
    ClaudeAssessor(client=client, max_tool_calls=4).review(case_with([]), pack)
    assert all("tools" not in request for request in client.requests)


def test_tool_calls_are_recorded_in_the_review(database_url, pack):
    from fastapi.testclient import TestClient

    from repermit.api import create_app
    from tests.conftest import Api
    from tests.test_llm import SAFE, FakeAssessor, modify

    result = review()
    result._tool_calls = [{"name": "model_overview", "input": {"model": "proposed"}, "result": "{}", "error": False}]
    api = Api(TestClient(create_app(database_url, pack, FakeAssessor(result))))
    api.open()
    modify(api, "wall_relocation", **SAFE)
    event = next(event for event in api.client.get(f"/cases/{api.case_id}/history").json() if event["type"] == "llm_review_recorded")
    assert event["payload"]["tool_calls"][0]["name"] == "model_overview"
