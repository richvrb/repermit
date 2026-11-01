"""IFC models: reading, comparison and facts for the rules."""

import hashlib
from typing import Any

import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.placement

MAX_MODEL_BYTES = 50 * 1024 * 1024
ELEMENT_CLASSES = ("IfcWall", "IfcSlab", "IfcColumn", "IfcBeam", "IfcDoor", "IfcWindow", "IfcStair", "IfcRoof", "IfcCovering", "IfcSpace")
STRUCTURAL_CLASSES = ("IfcColumn", "IfcBeam")
FINISH_CLASSES = ("IfcCovering", "IfcSpace", "IfcDoor", "IfcWindow")
PROPERTIES = ("LoadBearing", "FireRating", "IsExternal")
MAX_LISTED_CHANGES = 50


class InvalidModel(Exception):
    pass


def snapshot(element: Any) -> dict:
    properties = {}
    for pset in ifcopenshell.util.element.get_psets(element, psets_only=True).values():
        properties.update({name: pset[name] for name in PROPERTIES if name in pset})
    placement = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement) if element.ObjectPlacement else None
    return {
        "class": element.is_a(),
        "name": element.Name or "",
        "placement": None if placement is None else [round(float(value), 3) for value in placement[:3, 3]],
        "properties": properties,
    }


def read_model(content: bytes) -> dict:
    """Parse an IFC file. Returns its summary and a snapshot per GlobalId."""
    if len(content) > MAX_MODEL_BYTES:
        raise InvalidModel("the model is larger than 50 MB")
    if not content.lstrip().startswith(b"ISO-10303-21"):
        raise InvalidModel("the file is not an IFC-SPF model")
    try:
        model = ifcopenshell.file.from_string(content.decode("utf-8", errors="replace"))
        elements = {element.GlobalId: snapshot(element) for name in ELEMENT_CLASSES for element in model.by_type(name)}
        storeys = len(model.by_type("IfcBuildingStorey"))
    except (RuntimeError, ValueError, AttributeError, TypeError) as error:
        raise InvalidModel(f"the IFC model could not be read: {error}") from error
    if not elements:
        raise InvalidModel("the IFC model contains no building elements")

    counts: dict[str, int] = {}
    for element in elements.values():
        counts[element["class"]] = counts.get(element["class"], 0) + 1
    return {
        "summary": {
            "schema": model.schema,
            "sha256": hashlib.sha256(content).hexdigest(),
            "size": len(content),
            "storeys": storeys,
            "elements": dict(sorted(counts.items())),
        },
        "elements": elements,
    }


def compare(baseline: dict[str, dict], proposed: dict[str, dict]) -> list[dict]:
    changes = []
    for key in sorted(proposed.keys() | baseline.keys()):
        before, after = baseline.get(key), proposed.get(key)
        if before == after:
            continue
        change = "added" if before is None else "removed" if after is None else "changed"
        changes.append({"change": change, **(after or before)})
    return changes


def derive(changes: list[dict], claim, excluded: tuple[str, ...], forced: tuple[str, ...] = ()) -> bool | None:
    """True if any element claims it, False if all deny or are excluded, otherwise unknown."""
    values = []
    for element in changes:
        if element["class"].startswith(forced):
            values.append(True)
        else:
            value = claim(element["properties"])
            values.append(False if value is None and element["class"].startswith(excluded) else value)
    if any(value is True for value in values):
        return True
    return False if values and all(value is False for value in values) else None


def fire_rated(properties: dict) -> bool | None:
    rating = properties.get("FireRating")
    if rating is None or rating == "":
        return None
    return str(rating).upper() != "NONE"


def derive_facts(changes: list[dict]) -> dict[str, bool]:
    derived = {
        "load_bearing": derive(changes, lambda item: item.get("LoadBearing"), FINISH_CLASSES, STRUCTURAL_CLASSES),
        "fire_compartment_boundary": derive(changes, fire_rated, FINISH_CLASSES),
        "facade_change": derive(changes, lambda item: item.get("IsExternal"), FINISH_CLASSES),
    }
    return {name: value for name, value in derived.items() if value is not None}
