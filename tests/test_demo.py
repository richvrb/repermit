from repermit.demo import SCENARIOS, main, run
from repermit.knowledge import load_pack
from repermit.service import CaseService
from repermit.store import EventStore


def test_every_scenario_reaches_its_expected_status(database_url):
    results = run(CaseService(EventStore(database_url), load_pack()))
    assert len(results) == len(SCENARIOS)
    for name, case, expected in results:
        assert case["status"] == expected, name
        assert case["project_name"].startswith("[SYNTHETIC]")


def test_refused_demo_actions_are_in_the_history(database_url):
    service = CaseService(EventStore(database_url), load_pack())
    cases = {name: case for name, case, _ in run(service)}
    types = [event["type"] for event in service.get_history(cases["e4_authorization_conflict"]["case_id"])]
    assert "action_denied" in types


def test_main_prints_each_scenario(database_url, monkeypatch, capsys):
    monkeypatch.setenv("REPERMIT_DATABASE_URL", database_url)
    main()
    assert len(capsys.readouterr().out.strip().splitlines()) == len(SCENARIOS)
