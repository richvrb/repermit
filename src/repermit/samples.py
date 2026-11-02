"""Synthetic IFC models for the test cases: a 12-storey tower with a lobby, apartments and offices.

GUIDs are stable, so a baseline and a proposal can be compared.
"""

import textwrap
import uuid
from functools import lru_cache

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.guid

from repermit.knowledge import PUBLIC_PACK, load_pack
from repermit.service import UnknownItem

PARTITION = {"LoadBearing": False, "FireRating": "NONE", "IsExternal": False}
SEPARATING = {"LoadBearing": True, "FireRating": "EI60", "IsExternal": False}
CORE = {"LoadBearing": True, "FireRating": "EI120", "IsExternal": False}
FACADE = {"LoadBearing": True, "FireRating": "EI60", "IsExternal": True}
GLAZING = {"IsExternal": True}
APARTMENT = {**PARTITION, "FireRating": "EI60"}

WIDTH, DEPTH = 36.0, 20.0
LEVELS = 12
ROOF = LEVELS + 1
STOREY_HEIGHT = 3.4
WALL = 0.2
COLOURS = {
    "concrete": (0.68, 0.68, 0.66),
    "facade": (0.86, 0.84, 0.79),
    "glass": (0.42, 0.63, 0.78),
    "partition": (0.95, 0.94, 0.90),
    "finish": (0.74, 0.60, 0.44),
    "steel": (0.35, 0.37, 0.40),
}
TRANSPARENCY = {"glass": 0.55}


def part(ifc_class: str, x0: float, y0: float, x1: float, y1: float, level: int = 1, base: float = 0.0,
         height: float = 3.2, properties: dict | None = None, material: str = "concrete") -> dict:
    """A box on a storey: the plan rectangle, and its height above the base."""
    return {"class": ifc_class, "x0": x0, "y0": y0, "x1": x1, "y1": y1, "level": level, "base": base,
            "height": height, "properties": properties or {}, "material": material}


def wall(x0: float, y0: float, x1: float, y1: float, level: int, properties: dict, material: str = "partition", **extra) -> dict:
    """A wall along one axis, from one point to the other."""
    half = WALL / 2
    if x0 == x1:
        return part("IfcWall", x0 - half, y0, x0 + half, y1, level, properties=properties, material=material, **extra)
    return part("IfcWall", x0, y0 - half, x1, y0 + half, level, properties=properties, material=material, **extra)


def facade(level: int, tag: str, x0: float, y0: float, x1: float, y1: float, bays: int, glazed: bool = False) -> dict:
    """A facade side: a band under and over the windows, with a window per bay."""
    parts, along_x = {}, y0 == y1
    for name, base, height in (("sill", 0.0, 0.9), ("head", 2.9, 0.5)):
        if not glazed or name == "head":
            parts[f"Facade {tag} {name} L{level}"] = wall(x0, y0, x1, y1, level, FACADE, "facade", base=base, height=height)
    span = ((x1 - x0) if along_x else (y1 - y0)) / bays
    base, height = (0.1, 2.8) if glazed else (0.9, 2.0)
    for bay in range(bays):
        start, end = bay * span + 0.08, (bay + 1) * span - 0.08
        box_area = (x0 + start, y0 - 0.04, x0 + end, y0 + 0.04) if along_x else (x0 - 0.04, y0 + start, x0 + 0.04, y0 + end)
        parts[f"Window {tag} {bay + 1} L{level}"] = part("IfcWindow", *box_area, level, base, height, GLAZING, "glass")
    return parts


def columns(level: int) -> dict:
    grid = [(x, y) for x in (0.6, 9, 18, 27, 35.4) for y in (0.6, 7, 13, 19.4) if not (x == 18 and y in (7, 13))]
    return {
        f"Column {index} L{level}": part("IfcColumn", x - 0.25, y - 0.25, x + 0.25, y + 0.25, level)
        for index, (x, y) in enumerate(grid, 1)
    }


def core(level: int) -> dict:
    sides = {"west": (16, 7, 16, 13), "east": (20, 7, 20, 13), "south": (16, 7, 20, 7), "north": (16, 13, 20, 13)}
    parts = {f"Core {side} L{level}": wall(*line, level, CORE, "concrete") for side, line in sides.items()}
    if level == 1:
        parts["Stair core wall"] = parts.pop("Core east L1")
    parts[f"Stair L{level}"] = part("IfcStair", 16.4, 7.4, 18.0, 12.6, level, material="steel")
    return parts


def apartments(level: int) -> dict:
    parts = {}
    for side, y in (("south", 9), ("north", 11)):
        parts[f"Corridor wall west {side} L{level}"] = wall(0.2, y, 16, y, level, SEPARATING)
        parts[f"Corridor wall east {side} L{level}"] = wall(20, y, 35.8, y, level, SEPARATING)
    for x in (6, 12, 24, 30):
        parts[f"Apartment wall {level}-{x}S"] = wall(x, 0.2, x, 9, level, SEPARATING)
        parts[f"Apartment wall {level}-{x}N"] = wall(x, 11, x, 19.8, level, SEPARATING)
    if level == 4:
        parts["Wall 4A-4B"] = parts.pop("Apartment wall 4-12S")
    return parts


def lobby() -> dict:
    return {
        "Lobby floor finish": part("IfcCovering", 0.2, 0.2, 16, 19.8, height=0.02, material="finish"),
        "Lobby wall lining": part("IfcCovering", 0.2, 9.8, 16, 10.2, height=3.0, material="finish"),
        "Restaurant wall": wall(24, 0.2, 24, 12, 1, SEPARATING),
        "Terrace deck": part("IfcSlab", 24, -4, 36, 0, base=-0.2, height=0.2, material="finish"),
        "Terrace canopy": part("IfcSlab", 24, -4, 36, 0, base=3.0, height=0.2),
        "Terrace post west": part("IfcColumn", 24.1, -3.9, 24.3, -3.7, height=3.0, material="steel"),
        "Terrace post east": part("IfcColumn", 35.7, -3.9, 35.9, -3.7, height=3.0, material="steel"),
    }


def storey(level: int) -> dict:
    return (
        {f"Floor L{level}": part("IfcSlab", 0, 0, WIDTH, DEPTH, level, base=-0.25, height=0.25)}
        | facade(level, "south", 0, 0, WIDTH, 0, 6, glazed=level == 1)
        | facade(level, "north", 0, DEPTH, WIDTH, DEPTH, 6)
        | facade(level, "west", 0, 0, 0, DEPTH, 3)
        | facade(level, "east", WIDTH, 0, WIDTH, DEPTH, 3)
        | columns(level)
        | core(level)
    )


def roof() -> dict:
    parapet = {"LoadBearing": False, "FireRating": "NONE", "IsExternal": True}
    return {
        "Roof slab": part("IfcSlab", 0, 0, WIDTH, DEPTH, ROOF, base=-0.25, height=0.25),
        "Parapet south": wall(0, 0.1, WIDTH, 0.1, ROOF, parapet, "facade", height=1.1),
        "Parapet north": wall(0, DEPTH - 0.1, WIDTH, DEPTH - 0.1, ROOF, parapet, "facade", height=1.1),
        "Parapet west": wall(0.1, 0, 0.1, DEPTH, ROOF, parapet, "facade", height=1.1),
        "Parapet east": wall(WIDTH - 0.1, 0, WIDTH - 0.1, DEPTH, ROOF, parapet, "facade", height=1.1),
    }


@lru_cache
def building() -> dict:
    parts = lobby() | roof() | {"Partition 12-A": wall(28, 0.2, 28, 9, 12, PARTITION)}
    for level in range(1, LEVELS + 1):
        parts |= storey(level)
    for level in (2, 3, 4):
        parts |= apartments(level)
    return parts


def fit_out() -> dict:
    return {
        "Partition 12-B": wall(26, 0.2, 26, 9, 12, PARTITION),
        "Partition 12-C": wall(31, 0.2, 31, 9, 12, PARTITION),
        "Ceiling unit 1204": part("IfcCovering", 24, 0.2, 35.8, 9, 12, base=2.8, height=0.05, material="partition"),
    }


def apartment_conversion() -> dict:
    return {
        f"Apartment wall {level}-{x}{side}": wall(x, start, x, end, level, APARTMENT)
        for level in (5, 6, 7) for x in (6, 12, 24, 30) for side, start, end in (("S", 0.2, 9), ("N", 11, 19.8))
    }


def rooftop_extension() -> dict:
    return {
        "Rooftop wall south": wall(14, 8, 22, 8, ROOF, FACADE, "facade"),
        "Rooftop wall north": wall(14, 13, 22, 13, ROOF, FACADE, "facade"),
        "Rooftop wall west": wall(14, 8, 14, 13, ROOF, FACADE, "facade"),
        "Rooftop wall east": wall(22, 8, 22, 13, ROOF, FACADE, "facade"),
        "Rooftop column": part("IfcColumn", 19.0, 10.25, 19.5, 10.75, ROOF),
        "Rooftop stair": part("IfcStair", 16.4, 8.4, 18.0, 12.6, ROOF, material="steel"),
        "Rooftop roof": part("IfcSlab", 13.8, 7.8, 22.2, 13.2, ROOF, base=3.2, height=0.25),
    }


def meeting_rooms() -> dict:
    return {
        "Meeting room wall 1": wall(24, 4, 30, 4, 8, PARTITION),
        "Meeting room wall 2": wall(30, 0.2, 30, 4, 8, PARTITION),
        "Office floor finish": part("IfcCovering", 20.2, 0.2, 35.8, 9, 8, height=0.02, material="finish"),
        "Office ceiling": part("IfcCovering", 20.2, 0.2, 35.8, 9, 8, base=2.8, height=0.05, material="partition"),
    }


def terrace_glazing() -> dict:
    return {
        "Terrace glazing south": wall(24, -3.9, 36, -3.9, 1, GLAZING, "glass"),
        "Terrace glazing west": wall(24.1, -3.9, 24.1, 0, 1, GLAZING, "glass"),
        "Terrace glazing east": wall(35.9, -3.9, 35.9, 0, 1, GLAZING, "glass"),
    }


# Each test case: what the proposed model adds or replaces, and what it removes.
PROPOSALS = {
    "llm_renovation_floors": (lambda: {"Lobby floor finish (new)": part("IfcCovering", 0.2, 0.2, 16, 19.8, height=0.03, material="finish")}, ["Lobby floor finish"]),
    "llm_office_fit_out": (fit_out, ["Partition 12-A"]),
    "llm_free_text": (lambda: {"Wall 4A-4B": wall(13.2, 0.2, 13.2, 9, 4, SEPARATING)}, []),
    "llm_lobby_reconfiguration": (lambda: {
        "Stair core wall": wall(21.5, 7, 21.5, 13, 1, CORE, "concrete"),
        "Stair exit door": part("IfcDoor", 21.35, 9.5, 21.65, 10.5, height=2.1, material="steel"),
    }, []),
    "llm_office_to_residential": (apartment_conversion, []),
    "llm_out_of_scope": (rooftop_extension, []),
    "llm_edge_floor_ceiling": (meeting_rooms, []),
    "llm_edge_terrace": (terrace_glazing, []),
    "bim_new_permit": (dict, []),
}


def guid(name: str) -> str:
    return ifcopenshell.guid.compress(uuid.uuid5(uuid.NAMESPACE_URL, f"repermit:{name}").hex)


def box(model, body, item: dict, style) -> object:
    centre = model.createIfcAxis2Placement2D(model.createIfcCartesianPoint((0.0, 0.0)))
    profile = model.create_entity(
        "IfcRectangleProfileDef", ProfileType="AREA", Position=centre,
        XDim=item["x1"] - item["x0"], YDim=item["y1"] - item["y0"],
    )
    start = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    solid = model.createIfcExtrudedAreaSolid(profile, start, model.createIfcDirection((0.0, 0.0, 1.0)), item["height"])
    model.createIfcStyledItem(solid, [style], None)
    shape = model.createIfcShapeRepresentation(body, "Body", "SweptSolid", [solid])
    return model.createIfcProductDefinitionShape(None, None, [shape])


def surface_style(model, name: str):
    red, green, blue = COLOURS[name]
    colour = model.createIfcColourRgb(None, red, green, blue)
    rendering = model.create_entity(
        "IfcSurfaceStyleRendering", SurfaceColour=colour, Transparency=TRANSPARENCY.get(name, 0.0), ReflectanceMethod="NOTDEFINED",
    )
    return model.create_entity("IfcSurfaceStyle", Name=name, Side="BOTH", Styles=[rendering])


def add_element(model, body, styles: dict, storey_entity, name: str, item: dict) -> None:
    element = model.create_entity(item["class"], GlobalId=guid(name), Name=name)
    centre = ((item["x0"] + item["x1"]) / 2, (item["y0"] + item["y1"]) / 2, (item["level"] - 1) * STOREY_HEIGHT + item["base"])
    element.ObjectPlacement = model.createIfcLocalPlacement(None, model.createIfcAxis2Placement3D(model.createIfcCartesianPoint(centre)))
    element.Representation = box(model, body, item, styles[item["material"]])
    ifcopenshell.api.run("spatial.assign_container", model, products=[element], relating_structure=storey_entity)
    if item["properties"]:
        pset = ifcopenshell.api.run("pset.add_pset", model, product=element, name=f"Pset_{item['class'][3:]}Common")
        ifcopenshell.api.run("pset.edit_pset", model, pset=pset, properties=item["properties"])


def build_model(elements: dict[str, dict]) -> bytes:
    model = ifcopenshell.file(schema="IFC4")
    project = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject", name="[SYNTHETIC] RePermit sample")
    metre = ifcopenshell.api.run("unit.add_si_unit", model, unit_type="LENGTHUNIT")
    ifcopenshell.api.run("unit.assign_unit", model, units=[metre])
    context = ifcopenshell.api.run("context.add_context", model, context_type="Model")
    body = ifcopenshell.api.run("context.add_context", model, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=context)
    site = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSite", name="Site")
    tower = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuilding", name="Tower 7")
    ifcopenshell.api.run("aggregate.assign_object", model, products=[site], relating_object=project)
    ifcopenshell.api.run("aggregate.assign_object", model, products=[tower], relating_object=site)
    storeys = {}
    for level in range(1, ROOF + 1):
        name = "Roof" if level == ROOF else f"Level {level}"
        storeys[level] = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuildingStorey", name=name)
        storeys[level].Elevation = (level - 1) * STOREY_HEIGHT
    ifcopenshell.api.run("aggregate.assign_object", model, products=list(storeys.values()), relating_object=tower)
    styles = {name: surface_style(model, name) for name in COLOURS}
    for name, item in elements.items():
        add_element(model, body, styles, storeys[item["level"]], name, item)
    return model.to_string().encode("utf-8")


@lru_cache
def sample_model(scenario_id: str, kind: str) -> bytes:
    if scenario_id not in PROPOSALS or kind not in ("baseline", "proposed"):
        raise UnknownItem(f"no {kind} sample model for {scenario_id}")
    if kind == "baseline":
        return build_model(building())
    changed, removed = PROPOSALS[scenario_id]
    return build_model({**{name: item for name, item in building().items() if name not in removed}, **changed()})


# What each test case's documents say. Yes or no per fact, for the consultant statement.
BASE_FACTS = {
    "load_bearing": False, "fire_compartment_boundary": False, "safety_systems_changed": False, "affects_egress": False,
    "decoration_works": False, "non_residential_unit": True, "in_commercial_centre": False, "unit_over_100m2": False,
    "changes_unit_boundary": False, "heritage_area": False, "facade_change": False, "historical_building": False,
    "relies_on_existing_building": False, "exceeds_zoning": False, "simple_maintenance": False, "planning_use_change": False,
}
CASE_DOCUMENTS = {
    "llm_renovation_floors": ({"decoration_works": True}, "The lobby is not an escape route. Tiles are non-combustible A1 and plaster A2-s1,d0."),
    "llm_office_fit_out": ({"decoration_works": True, "unit_over_100m2": True}, "All work stays inside unit 1204. Sprinklers and detectors move within the unit only, and no shared system changes."),
    "llm_free_text": ({"load_bearing": True, "fire_compartment_boundary": True, "changes_unit_boundary": True, "non_residential_unit": False}, "Apartments 4A and 4B have one owner. All added area comes from 4B and the corridor width is unchanged. A new load-bearing EI60 wall replaces the old one."),
    "llm_lobby_reconfiguration": ({"load_bearing": True, "fire_compartment_boundary": True, "affects_egress": True}, "The building stays occupied. Upper floors use stair B during the works. The old exit is closed with EI120 construction and the new door is EI120, self-closing, discharging directly outside."),
    "llm_office_to_residential": ({"fire_compartment_boundary": True, "exceeds_zoning": True, "planning_use_change": True}, "Floors 5 to 7 hold 18 apartments separated by EI60 walls. The building has one owner. Stairs, lifts and sanitary risers are covered by the impacted area assessment."),
    "llm_out_of_scope": ({"load_bearing": True, "fire_compartment_boundary": True, "relies_on_existing_building": True, "facade_change": True}, "The rooftop room is a 40 m2 office with an enclosed EI60 stair. The building has one owner. Calculations cover the added load."),
    "llm_edge_floor_ceiling": ({}, "The two meeting rooms open directly onto the main office. Sprinklers and detectors are moved inside the unit only."),
    "llm_edge_terrace": ({"facade_change": True, "exceeds_zoning": True}, "The terrace is not an exit route and holds seating only, with no cooking. Alarm coverage extends from the restaurant's own zone and the owner of the restaurant unit owns the whole building."),
}


def pdf_escape(line: str) -> str:
    return line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def simple_pdf(lines: list[str]) -> bytes:
    """A small text PDF, without another dependency."""
    wrapped = [piece for line in lines for piece in (textwrap.wrap(line, 90) or [""])]
    pages = [wrapped[index:index + 48] for index in range(0, len(wrapped), 48)]
    objects = ["<< /Type /Catalog /Pages 2 0 R >>", "", "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    kids = []
    for page in pages:
        body = "BT /F1 11 Tf 50 790 Td 15 TL " + " ".join(f"({pdf_escape(line)}) Tj T*" for line in page) + " ET"
        objects.append(f"<< /Length {len(body)} >>\nstream\n{body}\nendstream")
        objects.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R >> >> /Contents {len(objects)} 0 R >>")
        kids.append(f"{len(objects)} 0 R")
    objects[1] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {len(kids)} >>"
    output, offsets = b"%PDF-1.4\n", []
    for number, item in enumerate(objects, 1):
        offsets.append(len(output))
        output += f"{number} 0 obj\n{item}\nendobj\n".encode("latin-1", "replace")
    start = len(output)
    table = "".join(f"{offset:010} 00000 n \n" for offset in offsets)
    output += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n{table}trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n".encode()
    return output


def sample_document(scenario_id: str, document_type: str, incomplete: bool = False) -> bytes:
    pack = load_pack(PUBLIC_PACK)
    if scenario_id not in CASE_DOCUMENTS or document_type not in pack.documents:
        raise UnknownItem(f"no {document_type} sample for {scenario_id}")
    facts, narrative = CASE_DOCUMENTS[scenario_id]
    items = pack.documents[document_type].must_contain[:-1 if incomplete else None]
    values = {
        "Project and unit identification": "Tower 7, Dubai, the unit concerned by this case",
        "Project and plot identification": "Tower 7, plot 7-001, Dubai",
        "Design revision": "Revision B",
        "Name and licence of the consultant": "Atlas Consulting Engineers, licence 7788",
        "Name of the owner": "Tower 7 Holdings",
        "Date and signature or stamp": "1 October 2026, signed and stamped by the consultant",
        "Date and signature": "1 October 2026, signed by the authorised person",
        "Issuing authority": "the competent authority",
        "Reference number and date": "Reference 2026-1187, 1 October 2026",
        "Consultant's stamp": "Stamped by Atlas Consulting Engineers",
    }
    lines = ["[SYNTHETIC DEMONSTRATION DOCUMENT]", pack.labels.get(document_type, document_type.replace("_", " ").title()), ""]
    lines += [f"{item}: {values.get(item, 'As set out for this case in revision B of Tower 7.')}" for item in items if item != "Consultant's statement on each listed subject"]
    if document_type == "consultant_statement" and not incomplete:
        lines += ["", "Consultant's statement on each listed subject:"]
        lines += [f"{name}: {'yes' if {**BASE_FACTS, **facts}[name] else 'no'}" for name in BASE_FACTS]
    if document_type == "completion_certificate":
        lines.append("A completion certificate has been issued for this building: yes")
    for name in pack.documents[document_type].proves if document_type != "consultant_statement" else []:
        lines.append(f"{name}: {'yes' if {**BASE_FACTS, **facts}.get(name, True) else 'no'}")
    if document_type in ("supporting_document", "consultant_statement"):
        lines += ["", narrative]
    return simple_pdf(lines)
