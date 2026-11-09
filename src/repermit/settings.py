"""AI settings that can be changed in the application, within limits set on the server."""

from collections.abc import Callable
from datetime import datetime, timezone

from repermit.bim_tools import TOOLS as BIM_TOOLS
from repermit.llm import EFFORTS
from repermit.retrieval import MAX_PER_SOURCE
from repermit.service import CaseService, InvalidRequest
from repermit.store import EventStore

DEFAULT_MODELS = ("claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5")
FIELDS = ("review_model", "review_effort", "documents_model", "documents_effort", "case_budget_usd", "daily_budget_usd")
# Retrieval settings may be left out, for example in settings saved before they existed.
RETRIEVAL_FIELDS = ("retrieval_enabled", "retrieval_passages", "retrieval_cards")
# More passages make every review prompt longer, so the number is capped.
MAX_PASSAGES = 10
MAX_CARDS = 5
# Each tool call is another turn of the review, so the number per review is capped.
MAX_TOOL_CALLS = 20


class AISettings:
    """The models per AI task and the budgets. The server's budgets are ceilings: the application can only lower them."""

    def __init__(
        self,
        service: CaseService,
        store: EventStore,
        factory: Callable[[str, str], object] | None = None,
        allowed_models: tuple[str, ...] = DEFAULT_MODELS,
    ):
        self.service = service
        self.store = store
        # Without a factory, as with test doubles, models cannot be swapped.
        self.factory = factory
        self.allowed_models = tuple(allowed_models)
        self.ceilings = {"case_budget_usd": service.case_budget_usd, "daily_budget_usd": service.daily_budget_usd}

    def current(self) -> dict:
        review, documents, retriever = self.service.assessor, self.service.document_reader, self.service.retriever
        return {
            "review_model": review.model if review else None,
            "review_effort": getattr(review, "effort", None),
            "documents_model": documents.model if documents else None,
            "documents_effort": getattr(documents, "effort", None) or "medium",
            "review_tool_calls": getattr(review, "max_tool_calls", None),
            "case_budget_usd": self.service.case_budget_usd,
            "daily_budget_usd": self.service.daily_budget_usd,
            "retrieval_enabled": bool(retriever and retriever.enabled),
            "retrieval_passages": retriever.passage_limits["total"] if retriever else None,
            "retrieval_cards": retriever.card_limits["total"] if retriever else None,
        }

    def describe(self) -> dict:
        retriever = self.service.retriever
        return {
            "current": self.current(),
            "llm_enabled": self.service.assessor is not None,
            "models_editable": self.service.assessor is not None and self.factory is not None,
            "allowed_models": list(self.allowed_models),
            "efforts": list(EFFORTS),
            "max_tool_calls": MAX_TOOL_CALLS,
            # The definitions Claude receives, so the overview cannot drift from them.
            "bim_tools": [
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "inputs": {name: spec.get("description") or ", ".join(map(str, spec.get("enum", []))) or spec["type"]
                               for name, spec in tool["input_schema"]["properties"].items()},
                }
                for tool in BIM_TOOLS
            ],
            "ceilings": self.ceilings,
            "retrieval": {
                "available": retriever is not None,
                "method": "Keyword search (BM25, SQLite FTS5); no AI model and no separate cost",
                "index": retriever.stats() if retriever else {},
                "max_passages": MAX_PASSAGES,
                "max_cards": MAX_CARDS,
                "thresholds": {
                    "passages": {key: value for key, value in retriever.passage_limits.items() if key != "total"},
                    "cards": {key: value for key, value in retriever.card_limits.items() if key != "total"},
                    "max_per_source": MAX_PER_SOURCE,
                } if retriever else None,
            },
            "history": [
                {key: row[key] for key in ("at", "actor_id", "role", "settings")}
                for row in self.store.settings_history()
            ],
        }

    def change(self, values: dict, actor_id: str, role: str) -> dict:
        settings = {key: values[key] for key in FIELDS} | {key: values.get(key) for key in (*RETRIEVAL_FIELDS, "review_tool_calls")}
        self._apply(settings)
        self.store.save_settings(self.current(), actor_id, role, datetime.now(timezone.utc).isoformat())
        return self.describe()

    def restore(self) -> None:
        """Applies the last saved settings at start-up, unless the server's limits no longer allow them."""
        history = self.store.settings_history(limit=1)
        if history:
            try:
                self._apply(history[0]["settings"])
            except InvalidRequest:
                pass

    def _apply(self, settings: dict) -> None:
        retrieval = self._check_retrieval(settings)
        # Left out, the number of tool calls stays as it is.
        tool_calls = settings.get("review_tool_calls")
        if tool_calls is None:
            tool_calls = self.current()["review_tool_calls"]
        elif isinstance(tool_calls, bool) or not isinstance(tool_calls, int) or not 0 <= tool_calls <= MAX_TOOL_CALLS:
            raise InvalidRequest(f"review_tool_calls must be a whole number from 0 to {MAX_TOOL_CALLS}")
        for name, ceiling in self.ceilings.items():
            value = settings[name]
            if value is None or value < 0 or (ceiling is not None and value > ceiling):
                raise InvalidRequest(f"{name} must be between 0 and {ceiling}, the limit set on the server")
        current = self.current()
        models = {key: settings[key] for key in ("review_model", "review_effort", "documents_model", "documents_effort")}
        changed = any(models[key] != current[key] for key in models) and self.service.assessor is not None
        if changed:
            if self.factory is None:
                raise InvalidRequest("models cannot be changed in this configuration")
            for key in ("review_model", "documents_model"):
                if models[key] is not None and models[key] not in self.allowed_models:
                    raise InvalidRequest(f"{models[key]} is not an allowed model: {list(self.allowed_models)}")
            for key in ("review_effort", "documents_effort"):
                if models[key] not in EFFORTS:
                    raise InvalidRequest(f"effort must be one of {list(EFFORTS)}")
            if models["review_model"] is None:
                raise InvalidRequest("the review needs a model")
            review = self.factory(models["review_model"], models["review_effort"])
            documents = self.factory(models["documents_model"], models["documents_effort"]) if models["documents_model"] else None
            self.service.assessor, self.service.document_reader = review, documents
        self.service.case_budget_usd = settings["case_budget_usd"]
        self.service.daily_budget_usd = settings["daily_budget_usd"]
        if tool_calls is not None and hasattr(self.service.assessor, "max_tool_calls"):
            self.service.assessor.max_tool_calls = tool_calls
        retriever = self.service.retriever
        if retriever and retrieval:
            retriever.enabled = retrieval["retrieval_enabled"]
            retriever.passage_limits["total"] = retrieval["retrieval_passages"]
            retriever.card_limits["total"] = retrieval["retrieval_cards"]

    def _check_retrieval(self, settings: dict) -> dict | None:
        """Retrieval values left out keep their current value."""
        if self.service.retriever is None:
            return None
        current = self.current()
        values = {key: current[key] if settings.get(key) is None else settings[key] for key in RETRIEVAL_FIELDS}
        if not isinstance(values["retrieval_enabled"], bool):
            raise InvalidRequest("retrieval_enabled must be true or false")
        for key, ceiling in (("retrieval_passages", MAX_PASSAGES), ("retrieval_cards", MAX_CARDS)):
            if not isinstance(values[key], int) or isinstance(values[key], bool) or not 0 <= values[key] <= ceiling:
                raise InvalidRequest(f"{key} must be a whole number from 0 to {ceiling}")
        return values
