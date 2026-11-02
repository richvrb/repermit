import pytest
from fastapi.testclient import TestClient

from repermit.api import create_app
from repermit.documents import InvalidDocument, coerce, read_document
from repermit.knowledge import PUBLIC_PACK, load_pack
from repermit.llm import ChecklistItem, DocumentReview, ExtractedFact
from repermit.samples import sample_document, sample_model
from tests.test_llm import FakeAssessor, review

PACK = load_pack(PUBLIC_PACK)


def assessment(*reviews):
    result = review("modification")
    result.document_reviews = list(reviews)
    return result


def reading(type, evidence_id=None, facts=(), leave_out=(), expected=True, matches=True):
    items = [ChecklistItem(item=item, present=item not in leave_out, location="p. 1") for item in PACK.documents[type].must_contain]
    return DocumentReview(
        evidence_id=evidence_id or f"{type}-B", is_expected_type=expected, matches_case=matches, checklist=items,
        extracted_facts=[ExtractedFact(name=name, value=value, quote=f"{name}: {value}") for name, value in facts], problems=[],
    )


class Case:
    def __init__(self, database_url, *results):
        self.assessor = FakeAssessor(review("modification"), *results)
        self.client = TestClient(create_app(database_url, PACK, self.assessor))
        case = self.client.post("/demo/scenarios/llm_free_text").json()
        self.id = case["case_id"]
        self.client.post(f"/cases/{self.id}/responses", json={"facts": {"competent_entity": "dda"}})
        self.client.post(f"/cases/{self.id}/models", content=sample_model("llm_free_text", "proposed"))

    def upload(self, type, content=None):
        content = content or sample_document("llm_free_text", type)
        return self.client.post(f"/cases/{self.id}/documents", params={"type": type, "filename": f"{type}.pdf"}, content=content)

    def submit(self):
        return self.client.post(f"/cases/{self.id}/responses", json={}).json()

    def decide(self, name, accepted=True, role="authority"):
        return self.client.post(f"/cases/{self.id}/fact-decisions", json={"name": name, "accepted": accepted, "actor_id": "r", "role": role})

    def state(self):
        return self.client.get(f"/cases/{self.id}").json()


def codes(case):
    return {item["subject"]: item["code"] for item in case["assessment"]["deficiencies"]}


def test_every_required_document_has_a_checklist():
    required = {name for rule in PACK.rules for name in rule.requires_evidence}
    assert required <= set(PACK.documents)
    assert all(document.must_contain for document in PACK.documents.values())


def test_every_asked_fact_can_be_proven():
    provable = {name for document in PACK.documents.values() for name in document.proves}
    assert set(PACK.facts) - set(PACK.opening_facts) <= provable


@pytest.mark.parametrize("content", [b"not a pdf", b"%PDF-1.4 broken"])
def test_invalid_files_are_refused(content):
    with pytest.raises(InvalidDocument):
        read_document(content)


def test_sample_documents_are_readable():
    for type in PACK.documents:
        assert read_document(sample_document("llm_free_text", type))["document"]["pages"] >= 1


def test_incomplete_sample_leaves_something_out():
    full = read_document(sample_document("llm_free_text", "owner_noc"))["text"]
    partial = read_document(sample_document("llm_free_text", "owner_noc", incomplete=True))["text"]
    assert len(partial) < len(full)


def test_statement_states_the_case_facts():
    text = read_document(sample_document("llm_free_text", "consultant_statement"))["text"]
    assert "load_bearing: yes" in text.replace("\n", " ")


def test_coerce():
    assert (coerce("Yes"), coerce("false"), coerce("dda")) == (True, False, "dda")


def test_open_facts_name_their_documents(database_url):
    case = Case(database_url).state()
    item = next(d for d in case["assessment"]["deficiencies"] if d["subject"] == "building_completed")
    assert item["documents"] == ["completion_certificate"]


def test_direct_answer_is_refused(database_url):
    case = Case(database_url)
    response = case.client.post(f"/cases/{case.id}/responses", json={"facts": {"load_bearing": False}})
    assert response.status_code == 422
    assert "document" in response.text


def test_simulated_document_is_refused(database_url):
    case = Case(database_url)
    assert case.client.post(f"/cases/{case.id}/responses", json={"documents": ["modified_drawings"]}).status_code == 422


def test_text_alone_establishes_nothing(database_url):
    case = Case(database_url)
    updated = case.client.post(f"/cases/{case.id}/responses", json={"note": "The building is completed."}).json()
    assert codes(updated)["building_completed"] == "unknown_fact"


def test_invalid_upload_records_nothing(database_url):
    case = Case(database_url)
    before = len(case.client.get(f"/cases/{case.id}/history").json())
    assert case.upload("owner_noc", b"nonsense").status_code == 422
    assert len(case.client.get(f"/cases/{case.id}/history").json()) == before


def test_unknown_type_is_refused(database_url):
    assert Case(database_url).upload("passport", sample_document("llm_free_text", "owner_noc")).status_code == 422


def test_upload_makes_no_llm_call_and_waits_for_the_round(database_url):
    case = Case(database_url)
    calls = case.assessor.calls
    updated = case.upload("modified_drawings").json()
    assert case.assessor.calls == calls
    assert codes(updated)["modified_drawings"] == "document_pending"
    assert "text" not in updated["evidence"][-1]


def test_round_with_only_uploads_is_one_call(database_url):
    case = Case(database_url, assessment(reading("modified_drawings")))
    calls = case.assessor.calls
    case.upload("modified_drawings")
    updated = case.submit()
    assert case.assessor.calls == calls + 1
    assert "modified_drawings" not in codes(updated)


def test_item_left_out_counts_as_missing(database_url):
    partial = reading("modified_drawings")
    partial.checklist = partial.checklist[:-1]
    case = Case(database_url, assessment(partial))
    case.upload("modified_drawings")
    updated = case.submit()
    item = next(d for d in updated["assessment"]["deficiencies"] if d["subject"] == "modified_drawings")
    assert item["code"] == "document_incomplete"
    assert "Proposed situation" in item["detail"]


@pytest.mark.parametrize("kwargs", [{"expected": False}, {"matches": False}])
def test_wrong_document_is_incomplete(database_url, kwargs):
    case = Case(database_url, assessment(reading("modified_drawings", **kwargs)))
    case.upload("modified_drawings")
    assert codes(case.submit())["modified_drawings"] == "document_incomplete"


def test_new_version_is_assessed_again(database_url):
    case = Case(database_url, assessment(reading("modified_drawings", leave_out=["Design revision"])), assessment(reading("modified_drawings")))
    case.upload("modified_drawings")
    case.submit()
    assert codes(case.upload("modified_drawings").json())["modified_drawings"] == "document_pending"
    assert "modified_drawings" not in codes(case.submit())


def test_fact_needs_a_person(database_url):
    case = Case(database_url, assessment(reading("completion_certificate", facts=[("building_completed", "true")])))
    case.upload("completion_certificate")
    updated = case.submit()
    item = next(d for d in updated["assessment"]["deficiencies"] if d["subject"] == "building_completed")
    assert item["code"] == "fact_to_confirm"
    assert item["reading"]["value"] is True
    assert item["reading"]["quote"]
    assert "DXB-ROU-01" not in [rule["rule"] for rule in updated["assessment"]["applied_rules"]]

    assert case.decide("building_completed", role="consultant").status_code == 403
    assert "resolution_denied" in [event["type"] for event in case.client.get(f"/cases/{case.id}/history").json()]

    calls = case.assessor.calls
    confirmed = case.decide("building_completed").json()
    assert case.assessor.calls == calls
    assert "DXB-ROU-01" in [rule["rule"] for rule in confirmed["assessment"]["applied_rules"]]
    assert "building_completed" not in codes(confirmed)


def test_declined_fact_is_requested_again(database_url):
    case = Case(database_url, assessment(reading("completion_certificate", facts=[("building_completed", "true")])))
    case.upload("completion_certificate")
    case.submit()
    assert codes(case.decide("building_completed", accepted=False).json())["building_completed"] == "unknown_fact"


def test_fact_outside_the_type_is_ignored(database_url):
    case = Case(database_url, assessment(reading("completion_certificate", facts=[("load_bearing", "false")])))
    case.upload("completion_certificate")
    assert codes(case.submit()).get("load_bearing") != "fact_to_confirm"


def test_incomplete_document_proves_nothing(database_url):
    faulty = reading("completion_certificate", facts=[("building_completed", "true")], leave_out=["Issue date"])
    case = Case(database_url, assessment(faulty))
    case.upload("completion_certificate")
    assert codes(case.submit())["building_completed"] == "unknown_fact"


def test_document_that_contradicts_the_model_is_shown(database_url):
    statement = reading("consultant_statement", facts=[("load_bearing", "false")])
    case = Case(database_url, assessment(statement))
    case.upload("consultant_statement")
    assert codes(case.submit())["load_bearing"] == "inconsistent_fact"


def test_prompt_sends_a_document_once(database_url):
    from repermit.llm import build_prompt
    from repermit.state import fold

    case = Case(database_url, assessment(reading("modified_drawings")))
    case.upload("modified_drawings")
    events = case.client.get(f"/cases/{case.id}/history").json()
    assert events
    state = fold(case.id, case.client.app.state.store.load(case.id))
    assert "must_contain" in build_prompt(state, PACK).split("<case>")[1]
    case.submit()
    state = fold(case.id, case.client.app.state.store.load(case.id))
    assert "must_contain" not in build_prompt(state, PACK).split("<case>")[1]


def test_text_stays_out_of_the_history_endpoint(database_url):
    case = Case(database_url)
    case.upload("modified_drawings")
    events = case.client.get(f"/cases/{case.id}/history").json()
    assert all("text" not in event["payload"] for event in events)
