import copy

import pytest
import yaml
from pydantic import ValidationError

from repermit.knowledge import DEFAULT_PACK, Pack, load_pack


def raw_pack():
    return yaml.safe_load(DEFAULT_PACK.read_text(encoding="utf-8"))


def test_bundled_pack_loads_and_is_synthetic():
    pack = load_pack()
    assert pack.initial_stage == "design_change"
    assert {source.kind for source in pack.sources} == {"synthetic"}


def test_rule_with_undeclared_source_is_rejected():
    data = raw_pack()
    data["rules"][0]["source"] = "NOPE"
    with pytest.raises(ValidationError, match="undeclared source"):
        Pack.model_validate(data)


def test_source_without_valid_kind_is_rejected():
    data = raw_pack()
    data["sources"][0]["kind"] = "rumour"
    with pytest.raises(ValidationError):
        Pack.model_validate(data)


def test_two_actions_from_one_stage_are_rejected():
    data = raw_pack()
    duplicate = copy.deepcopy(data["actions"][0])
    duplicate["id"] = "other"
    data["actions"].append(duplicate)
    with pytest.raises(ValidationError, match="more than one action"):
        Pack.model_validate(data)


def test_action_with_undeclared_role_is_rejected():
    data = raw_pack()
    data["actions"][0]["roles"] = ["wizard"]
    with pytest.raises(ValidationError, match="undeclared roles"):
        Pack.model_validate(data)
