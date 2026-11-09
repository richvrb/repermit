"""Tools the AI review can call to look things up in the case's IFC models. They only read.

The tools are not strict: together with the review's output schema the grammar would be too large. Inputs are
therefore checked here, and a wrong input comes back as an error the model can read.
"""

import json
import math

from repermit.state import CaseState

MAX_RESULTS = 30
MAX_RESULT_CHARS = 12_000
MODEL_CHOICE = {"type": "string", "enum": ["proposed", "baseline"], "description": "The proposed design model or the approved baseline."}
NULLABLE = {"type": ["string", "null"]}
GLOBAL_ID = {"type": "string", "description": "The element's IFC GlobalId, as returned by find_elements or elements_near."}
CHANGES = ["any", "added", "removed", "changed", "unchanged"]

TOOLS = [
    {
        "name": "model_overview",
        "description": "Storeys with their elevation, the number of elements per IFC class in a model, and how many elements were added, removed or changed against the baseline.",
        "input_schema": {"type": "object", "properties": {"model": MODEL_CHOICE}, "required": ["model"], "additionalProperties": False},
    },
    {
        "name": "find_elements",
        "description": (
            "Elements of a model that match all given filters, at most 30. Leave out a filter you do not need. "
            "change is the difference with the baseline: added, removed, changed, unchanged, or any."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "model": MODEL_CHOICE,
                "ifc_class": {**NULLABLE, "description": "For example IfcWall, IfcSlab, IfcSpace."},
                "storey": {**NULLABLE, "description": "Storey name as given by model_overview."},
                "name_contains": {**NULLABLE, "description": "Part of the element name, case-insensitive."},
                "property": {**NULLABLE, "description": "A property name, such as LoadBearing or FireRating; the element must have it."},
                "change": {"type": "string", "enum": CHANGES},
            },
            "required": ["model"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_element",
        "description": "Everything recorded for one element: class, name, storey, position, type, material, properties and quantities, and how it differs from the baseline.",
        "input_schema": {
            "type": "object",
            "properties": {"model": MODEL_CHOICE, "global_id": GLOBAL_ID},
            "required": ["model", "global_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "elements_near",
        "description": (
            "Elements whose placement point lies within a radius of an element's placement point, nearest first, at most 30. "
            "Placement points are insertion points, not geometry, so treat this as an indication of what is nearby."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "model": MODEL_CHOICE,
                "global_id": GLOBAL_ID,
                "radius_m": {"type": "number", "description": "Radius in metres, at most 20."},
            },
            "required": ["model", "global_id", "radius_m"],
            "additionalProperties": False,
        },
    },
]


SCHEMAS = {tool["name"]: tool["input_schema"] for tool in TOOLS}
TYPES = {"string": str, "number": (int, float), "null": type(None)}


def check_input(schema: dict, arguments: dict) -> None:
    """The checks strict mode would have made: known and required inputs, their types and allowed values."""
    if not isinstance(arguments, dict):
        raise ValueError("the input must be an object")
    unknown = set(arguments) - set(schema["properties"])
    if unknown:
        raise ValueError(f"unknown inputs: {sorted(unknown)}")
    missing = [name for name in schema["required"] if name not in arguments]
    if missing:
        raise ValueError(f"missing inputs: {missing}")
    for name, value in arguments.items():
        spec = schema["properties"][name]
        allowed = spec["type"] if isinstance(spec["type"], list) else [spec["type"]]
        if isinstance(value, bool) or not isinstance(value, tuple(TYPES[kind] for kind in allowed)):
            raise ValueError(f"{name} must be {' or '.join(allowed)}")
        if "enum" in spec and value not in spec["enum"]:
            raise ValueError(f"{name} must be one of {spec['enum']}")


def summarize(name: str, output: str) -> str:
    """One line for the flow, made from the full result before the log cuts it short."""
    try:
        result = json.loads(output)
    except ValueError:
        return "Result too long to summarise."
    if "error" in result:
        return result["error"]
    if name == "model_overview":
        return f"{len(result['storeys'])} storeys, {sum(result['elements'].values())} elements" + (
            f", changes: {', '.join(f'{count} {kind}' for kind, count in result['changes'].items() if kind != 'unchanged')}" if result.get("changes") else "")
    if name in ("find_elements", "elements_near"):
        names = ", ".join(row["name"] for row in result["elements"][:3])
        return f"{result['count']} elements" + (f", such as {names}" if names else "")
    return f"{result['class']} {result['name']}" + (f" on {result['storey']}" if result.get("storey") else "") + (f", {result['change']}" if result.get("change") else "")


def latest_model(state: CaseState, evidence_type: str) -> dict | None:
    return next((item for item in state.latest_evidence() if item["type"] == evidence_type and item.get("elements")), None)


class ModelTools:
    """Answers tool calls from the stored models of one case."""

    def __init__(self, state: CaseState):
        self.models = {"proposed": latest_model(state, "design_model"), "baseline": latest_model(state, "baseline_model")}
        proposed, baseline = self.models["proposed"], self.models["baseline"]
        # The same comparison as bim.compare, kept per GlobalId.
        self.changes = {}
        if proposed and baseline:
            before, after = baseline["elements"], proposed["elements"]
            for key in before.keys() | after.keys():
                self.changes[key] = (
                    "added" if key not in before else "removed" if key not in after
                    else "unchanged" if before[key] == after[key] else "changed"
                )

    @property
    def available(self) -> bool:
        return self.models["proposed"] is not None or self.models["baseline"] is not None

    def run(self, name: str, arguments: dict) -> str:
        """The result as JSON text. Mistakes are returned as an error the AI can read."""
        handlers = {"model_overview": self.overview, "find_elements": self.find, "get_element": self.element, "elements_near": self.near}
        try:
            if name not in handlers:
                raise ValueError(f"unknown tool {name}")
            check_input(SCHEMAS[name], arguments)
            result = handlers[name](**arguments)
        except KeyError as error:
            result = {"error": f"unknown element: {error}"}
        except (TypeError, ValueError) as error:
            result = {"error": str(error)}
        text = json.dumps(result, ensure_ascii=False)
        return text if len(text) <= MAX_RESULT_CHARS else text[:MAX_RESULT_CHARS] + ' ... (truncated)"'

    def _model(self, model: str) -> dict:
        item = self.models.get(model)
        if item is None:
            raise ValueError(f"no {model} model has been delivered")
        return item

    def _detail(self, item: dict, global_id: str) -> dict:
        return ((item.get("details") or {}).get("elements") or {}).get(global_id, {})

    def _row(self, item: dict, global_id: str) -> dict:
        element = item["elements"][global_id]
        return {
            "global_id": global_id,
            "class": element["class"],
            "name": element["name"],
            "storey": self._detail(item, global_id).get("storey"),
            "change": self.changes.get(global_id),
        }

    def overview(self, model: str) -> dict:
        item = self._model(model)
        counts: dict[str, int] = {}
        for element in item["elements"].values():
            counts[element["class"]] = counts.get(element["class"], 0) + 1
        result = {"file": (item.get("model") or {}).get("filename"), "storeys": (item.get("details") or {}).get("storeys", []), "elements": counts}
        if self.changes:
            tally: dict[str, int] = {}
            for change in self.changes.values():
                tally[change] = tally.get(change, 0) + 1
            result["changes"] = tally
        return result

    def find(self, model: str, ifc_class=None, storey=None, name_contains=None, property=None, change="any") -> dict:
        item = self._model(model)
        rows = []
        for global_id, element in item["elements"].items():
            detail = self._detail(item, global_id)
            names = {key.split(".")[-1] for key in detail.get("property_sets", {})} | set(element["properties"])
            if ifc_class and element["class"].lower() != ifc_class.lower():
                continue
            if storey and (detail.get("storey") or "").lower() != storey.lower():
                continue
            if name_contains and name_contains.lower() not in element["name"].lower():
                continue
            if property and property not in names:
                continue
            if change and change != "any" and self.changes.get(global_id) != change:
                continue
            rows.append(self._row(item, global_id))
        return {"count": len(rows), "elements": rows[:MAX_RESULTS], "truncated": len(rows) > MAX_RESULTS}

    def element(self, model: str, global_id: str) -> dict:
        item = self._model(model)
        if global_id not in item["elements"]:
            raise ValueError(f"no element {global_id} in the {model} model")
        result = {**self._row(item, global_id), **item["elements"][global_id], **self._detail(item, global_id)}
        other = self.models["baseline" if model == "proposed" else "proposed"]
        if other and global_id in other["elements"] and other["elements"][global_id] != item["elements"][global_id]:
            result["in_other_model"] = other["elements"][global_id]
        return result

    def near(self, model: str, global_id: str, radius_m: float) -> dict:
        item = self._model(model)
        if global_id not in item["elements"]:
            raise ValueError(f"no element {global_id} in the {model} model")
        origin = item["elements"][global_id].get("placement")
        if origin is None:
            raise ValueError("this element has no placement")
        radius = min(max(float(radius_m), 0.0), 20.0)
        found = []
        for other_id, element in item["elements"].items():
            if other_id == global_id or element.get("placement") is None:
                continue
            distance = math.dist(origin, element["placement"])
            if distance <= radius:
                found.append({**self._row(item, other_id), "distance_m": round(distance, 2)})
        found.sort(key=lambda row: row["distance_m"])
        return {"radius_m": radius, "count": len(found), "elements": found[:MAX_RESULTS]}
