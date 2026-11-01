from datetime import date

from repermit.assessment import assess, evaluate
from repermit.state import CaseState

TODAY = date(2026, 11, 1)


def state(facts=None, evidence=(), revision="B", change_type="wall_relocation"):
    case = CaseState("c1", revision=revision, stage="design_change")
    case.modification = {"revision": revision, "change_type": change_type, "facts": facts or {}}
    for item in evidence:
        case.evidence.setdefault(item["evidence_id"], []).append(item)
    return case


def item(evidence_id, type, domain, revision="B", status="current", valid_until=None, facts=None):
    return {
        "evidence_id": evidence_id, "type": type, "domain": domain, "revision": revision,
        "status": status, "valid_until": valid_until, "facts": facts or {}, "version": 1,
    }


def codes(result):
    return {(d["code"], d["subject"]) for d in result["deficiencies"]}


def test_evaluate_is_three_valued():
    assert evaluate({"a": 1}, {"a": 1}) == (True, [])
    assert evaluate({"a": 1}, {"a": 2}) == (False, [])
    assert evaluate({"a": 1, "b": 2}, {"a": 1}) == (None, ["b"])
    assert evaluate({"a": 1, "b": 2}, {"a": 2}) == (False, [])


def test_unknown_fact_keeps_domain_open(pack):
    result = assess(state(), pack, TODAY)
    assert result["domains"]["fire_safety"] == "potentially_affected"
    assert ("unknown_fact", "fire_compartment_boundary") in codes(result)


def test_known_fact_closes_only_its_own_domain(pack):
    result = assess(state({"load_bearing": False}), pack, TODAY)
    assert result["domains"]["structural"] == "not_affected"
    assert result["domains"]["fire_safety"] == "potentially_affected"


def test_applied_rules_show_source_kind(pack):
    rule = assess(state(), pack, TODAY)["applied_rules"][0]
    assert (rule["rule"], rule["source"], rule["source_kind"]) == ("R-ARC-01", "SYN-ARCH", "synthetic")


def test_missing_evidence_named(pack):
    assert ("missing", "floor_plan") in codes(assess(state(), pack, TODAY))


def test_evidence_problems(pack):
    cases = [
        (item("p", "floor_plan", "architectural", status="incomplete"), "insufficient"),
        (item("p", "floor_plan", "architectural", valid_until="2026-10-31"), "outdated"),
        (item("p", "floor_plan", "architectural", revision=None), "revision_unknown"),
        (item("p", "floor_plan", "architectural", revision="A"), "stale_revision"),
    ]
    for evidence, code in cases:
        assert (code, "floor_plan") in codes(assess(state(evidence=[evidence]), pack, TODAY))


def test_evidence_valid_on_its_last_day(pack):
    evidence = item("p", "floor_plan", "architectural", valid_until="2026-11-01")
    assert "floor_plan" not in {subject for _, subject in codes(assess(state(evidence=[evidence]), pack, TODAY))}


def test_contradictory_facts_are_unresolved(pack):
    evidence = [
        item("a", "note", "structural", facts={"load_bearing": True}),
        item("b", "note", "structural", facts={"load_bearing": False}),
    ]
    result = assess(state(evidence=evidence), pack, TODAY)
    assert ("inconsistent_fact", "load_bearing") in codes(result)
    assert result["domains"]["structural"] == "potentially_affected"


def test_withdrawn_evidence_supplies_no_facts(pack):
    evidence = item("a", "note", "structural", status="withdrawn", facts={"load_bearing": False})
    assert assess(state(evidence=[evidence]), pack, TODAY)["domains"]["structural"] == "potentially_affected"


def test_revision_keeps_approval_in_unaffected_domain(pack):
    approval = item("noc", "structural_noc", "structural", revision="A")
    result = assess(state({"load_bearing": False}, [approval]), pack, TODAY)
    assert result["impact"] == [{"evidence_id": "noc", "domain": "structural", "impact": "retained"}]


def test_stale_evidence_in_affected_domain_needs_revalidation(pack):
    strategy = item("fs", "fire_strategy", "fire_safety", revision="A")
    result = assess(state({"fire_compartment_boundary": True}, [strategy]), pack, TODAY)
    assert result["impact"][0]["impact"] == "revalidate"
    assert ("stale_revision", "fire_strategy") in codes(result)
