import pytest

from repermit.knowledge import load_pack
from repermit.service import CaseService
from repermit.store import ConcurrentWrite, EventStore


def event(seq):
    return {"seq": seq, "type": "x", "at": "2026-01-01T00:00:00+00:00", "payload": {}}


def test_events_load_in_sequence(database_url):
    store = EventStore(database_url)
    store.append("c1", [event(1), event(2)])
    assert [item["seq"] for item in store.load("c1")] == [1, 2]


def test_concurrent_write_is_rejected_without_partial_writes(database_url):
    store = EventStore(database_url)
    store.append("c1", [event(1)])
    with pytest.raises(ConcurrentWrite):
        store.append("c1", [event(2), event(1)])
    assert len(store.load("c1")) == 1


def test_state_survives_restart(database_url):
    pack = load_pack()
    first = CaseService(EventStore(database_url), pack)
    case = first.open_case("Tower 7", "A", "consultant")
    second = CaseService(EventStore(database_url), pack)
    assert second.get_case(case["case_id"]) == case
