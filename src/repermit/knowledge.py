"""Knowledge pack: rules, sources, roles and process actions with provenance."""

from datetime import date
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, model_validator

DEFAULT_PACK = Path(__file__).parent / "packs" / "synthetic.yaml"
PUBLIC_PACK = Path(__file__).parent / "packs" / "dubai_public.yaml"
LEGACY_PACK_VERSION = "synthetic-2026.1"


class Source(BaseModel):
    id: str
    title: str
    kind: Literal["authoritative", "derived", "synthetic"]
    issuer: str = ""
    url: str = ""
    retrieved: date | None = None


class FactOption(BaseModel):
    value: Any
    label: str


class Fact(BaseModel):
    question: str
    options: list[FactOption] = []


class Setting(BaseModel):
    parameter: str
    value: Any


class Rule(BaseModel):
    id: str
    domain: str
    source: str
    when: dict[str, Any]
    requires_evidence: list[str] = []
    sets: Setting | None = None
    title: str = ""
    text: str = ""
    reference: str = ""


class Gap(BaseModel):
    id: str
    source: str
    when: dict[str, Any]
    description: str


class Action(BaseModel):
    id: str
    from_stage: str
    to_stage: str
    roles: list[str]
    autonomy: Literal["autonomous", "conditional", "human_only"]


class Pack(BaseModel):
    version: str
    sources: list[Source]
    change_types: list[str]
    safety_domains: list[str]
    roles: list[str]
    resolution_roles: list[str]
    bim_formats: list[str]
    bim_evidence_types: list[str]
    bim_required_for: list[str] = []
    max_review_rounds: int = 3
    stages: list[str]
    actions: list[Action]
    rules: list[Rule]
    gaps: list[Gap] = []
    change_type_definitions: dict[str, str] = {}
    facts: dict[str, Fact] = {}
    labels: dict[str, str] = {}

    @model_validator(mode="after")
    def check_integrity(self) -> "Pack":
        sources = {source.id: source for source in self.sources}
        for item in [*self.rules, *self.gaps]:
            if item.source not in sources:
                raise ValueError(f"{item.id} references undeclared source {item.source}")

        for source in self.sources:
            if source.kind != "synthetic" and not (source.issuer and source.url):
                raise ValueError(f"source {source.id} needs an issuer and url")
        for rule in self.rules:
            if sources[rule.source].kind != "synthetic" and not (rule.title and rule.text and rule.reference):
                raise ValueError(f"{rule.id} needs a title, text and reference")

        seen_stages = set()
        for action in self.actions:
            unknown_stages = {action.from_stage, action.to_stage} - set(self.stages)
            if unknown_stages:
                raise ValueError(f"{action.id} references undeclared stages {unknown_stages}")
            unknown_roles = set(action.roles) - set(self.roles)
            if unknown_roles:
                raise ValueError(f"{action.id} references undeclared roles {unknown_roles}")
            if action.from_stage in seen_stages:
                raise ValueError(f"stage {action.from_stage} has more than one action")
            seen_stages.add(action.from_stage)

        unknown_roles = set(self.resolution_roles) - set(self.roles)
        if unknown_roles:
            raise ValueError(f"resolution_roles references undeclared roles {unknown_roles}")
        return self

    @property
    def initial_stage(self) -> str:
        return self.stages[0]

    def source(self, source_id: str) -> Source:
        return next(source for source in self.sources if source.id == source_id)

    def action(self, action_id: str) -> Action | None:
        return next((action for action in self.actions if action.id == action_id), None)

    def action_from(self, stage: str) -> Action | None:
        return next((action for action in self.actions if action.from_stage == stage), None)


def load_pack(path: Path | str = DEFAULT_PACK) -> Pack:
    with open(path, encoding="utf-8") as handle:
        return Pack.model_validate(yaml.safe_load(handle))
