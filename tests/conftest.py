import pytest
from fastapi.testclient import TestClient

from repermit.api import create_app
from repermit.knowledge import load_pack


class Api:
    """Small driver so flow tests read like the use case."""

    def __init__(self, client: TestClient):
        self.client = client
        self.case_id = None

    def open(self, role="consultant", revision="A") -> dict:
        response = self.client.post(
            "/cases", json={"project_name": "Tower 7", "revision": revision, "responsible_role": role}
        )
        assert response.status_code == 201
        self.case_id = response.json()["case_id"]
        return response.json()

    def modify(self, revision="B", change_type="wall_relocation", **facts) -> dict:
        body = {"revision": revision, "change_type": change_type, "description": "Relocate wall", "facts": facts}
        response = self.client.post(f"/cases/{self.case_id}/modifications", json=body)
        assert response.status_code == 200, response.text
        return response.json()

    def evidence(self, evidence_id, type, domain, revision="B", **extra) -> dict:
        body = {"evidence_id": evidence_id, "category": "document", "type": type, "domain": domain, "revision": revision, **extra}
        response = self.client.post(f"/cases/{self.case_id}/evidence", json=body)
        assert response.status_code == 200, response.text
        return response.json()

    def act(self, action, role="consultant"):
        body = {"action": action, "actor_id": "user-1", "role": role}
        return self.client.post(f"/cases/{self.case_id}/actions", json=body)

    def resolve(self, issue_id, role="authority", selected_rule_id=None):
        body = {
            "issue_id": issue_id,
            "actor_id": "user-2",
            "role": role,
            "source": "Authority clarification 12",
            "decision": "Clarified",
            "selected_rule_id": selected_rule_id,
        }
        return self.client.post(f"/cases/{self.case_id}/resolutions", json=body)

    def case(self) -> dict:
        return self.client.get(f"/cases/{self.case_id}").json()

    def history_types(self) -> list[str]:
        return [event["type"] for event in self.client.get(f"/cases/{self.case_id}/history").json()]

    def ready_case(self) -> dict:
        """A case that has passed the happy path up to authority review."""
        self.open()
        self.modify(load_bearing=False, fire_compartment_boundary=False, occupancy="residential")
        return self.evidence("plan-1", "floor_plan", "architectural")


@pytest.fixture
def pack():
    return load_pack()


@pytest.fixture
def database_url(tmp_path):
    return f"sqlite:///{(tmp_path / 'test.db').as_posix()}"


@pytest.fixture
def client(database_url, pack):
    return TestClient(create_app(database_url, pack))


@pytest.fixture
def api(client):
    return Api(client)
