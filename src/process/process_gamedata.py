"""
Gamedata Processor Module
-------------------------

Module for 
1. Parsing 'Gamedata' ( key value entity parameters ) ( Also referred to as UserData )
2. Validating against an XML-based schema
3. Exporting to binary data.

Usage: 
    setup_gd_schema()                                # Load Gamedata schema
    ProcessGamedata(in_obj, in_entity_type, out_obj) # Export object gamedata
"""

# PYTHON BUILT-IN
from difflib import get_close_matches
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
import os
import re
# FANG TOOLKIT
from . import g_class  # For global variables and logging

_XML_DATABASE_NAME = "madb.xml"
_COMMENT_PREFIX      = "#"
_KEY_VALUE_DELIMITER = "="
_GOODIE_PATTERN = re.compile(r"^goodie\d+$", re.IGNORECASE)

@dataclass(slots=True)
class GamedataSchema:
    valid:         set[str] = field(default_factory=set)
    deprecated:    set[str] = field(default_factory=set)
    unimplemented: set[str] = field(default_factory=set)

    @property
    def all_keys(self) -> set[str]:
        return self.valid | self.deprecated | self.unimplemented

    def merge(self, other: "GamedataSchema") -> None:
        self.valid         |= other.valid
        self.deprecated    |= other.deprecated
        self.unimplemented |= other.unimplemented

@dataclass(slots=True)
class GDNode:
    kind:     str
    inherits: list[str]      = field(default_factory=list)
    params:   GamedataSchema = field(default_factory=GamedataSchema)

def _parse_params(parent_elem: ET.Element) -> GamedataSchema:
    schema = GamedataSchema()

    for param in parent_elem.findall("param"):
        try:
            name          = param.attrib["name"].strip().lower()
            deprecated    = param.attrib.get("deprecated") == "1"
            unimplemented = param.attrib.get("unimplemented") == "1"
        except KeyError:
            continue

        if deprecated:      schema.deprecated.add(name)
        elif unimplemented: schema.unimplemented.add(name)
        else:               schema.valid.add(name)

    return schema

def _parse_nodes(root: ET.Element) -> dict[str, GDNode]:
    nodes: dict[str, GDNode] = {}

    def add_node(elem: ET.Element, kind: str):
        name = elem.attrib.get("name", "").lower()
        if not name:
            return

        inherits = [i.attrib.get("name", "").lower() for i in elem.findall("inherit") if i.attrib.get("name")]
        nodes[name] = GDNode(kind=kind, inherits=inherits, params=_parse_params(elem))

    for group in root.findall(".//group"):
        add_node(group, "group")
    for cls in root.findall(".//class"):
        add_node(cls, "class")

    return nodes

def _resolve_schema(name: str, nodes: dict[str, GDNode], visited: set[str] | None = None) -> GamedataSchema:
    if visited is None:
        visited = set()

    if name in visited:
        raise ValueError(f"Cyclic inheritance detected: {name}")
    
    visited.add(name)

    node = nodes.get(name)
    if not node:
        return GamedataSchema()

    schema = GamedataSchema()

    for parent in node.inherits:
        schema.merge(_resolve_schema(parent, nodes, visited.copy()))

    schema.merge(node.params)

    return schema

def setup_gd_schema() -> bool:
    BASE_DIR  = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    DATA_DIR  = os.path.join(BASE_DIR, "data")
    FILE_PATH = os.path.join(DATA_DIR, _XML_DATABASE_NAME)

    try:
        tree = ET.parse(FILE_PATH)
        root = tree.getroot()
    except Exception as e:
        print(f"Failed to load XML database: {e}")
        return False

    nodes = _parse_nodes(root)
    g_class.g_GDSchema = {}

    for name, node in nodes.items():
        if node.kind != "class":
            continue

        schema = _resolve_schema(name, nodes)

        g_class.g_GDSchema[name] = schema

    return True

def parse_gamedata_string(gamedata_string: str) -> dict[str, str]:
    data = {}
    for line in gamedata_string.splitlines():
        line = line.strip()
        if not line or line.startswith(_COMMENT_PREFIX) or _KEY_VALUE_DELIMITER not in line:
            continue
        key, value = map(str.strip, line.split(_KEY_VALUE_DELIMITER, 1))
        data[key] = value
    return data

# Gamedata Validation Helpers
def log_gamedata_error(obj_name: str, key: str, entity_type: str, message: str):
    g_class.logError(f"GAMEDATA ERROR: {message} '{key}' found in {obj_name} for entity type {entity_type}.")

def get_entity_type(parsed: dict[str, str], default: str) -> str:
    return parsed.get("Type") or parsed.get("type") or default

def suggest_entity_type(entity_type_lc: str, obj_name: str):
    all_classes = g_class.g_GDSchema.keys()
    matches = get_close_matches(entity_type_lc, all_classes, n=1, cutoff=0.7)
    if matches:
        suggestion = matches[0]
        g_class.logError(f"GAMEDATA ERROR: Unknown entity type '{entity_type_lc}' on {obj_name}. Did you mean '{suggestion}'?")
    else:
        g_class.logError(f"GAMEDATA ERROR: Unknown entity type '{entity_type_lc}' on {obj_name}. No potential matches found.")

def validate_gamedata(parsed: dict[str, str], schema: GamedataSchema, obj_name: str, entity_type: str) -> list[str]:
    def emit_gamedata(key, value, i):
        out_items.append(f"{key}={value}")
        if i < len(keys) - 1:
            out_items.append("\r\n")

    out_items = []

    all_keys = schema.all_keys

    keys = list(parsed.items())
    for i, (key, value) in enumerate(keys):
        key_lc = key.lower()

        # Make an exception for gamedata keys that starts with goodie by parsing and continuing the loop early
        if _GOODIE_PATTERN.match(key_lc):
            emit_gamedata(key, value, i)
            continue

        # Invalid key
        if key_lc not in all_keys:
            matches = get_close_matches(key_lc, all_keys, n=1, cutoff=0.7)
            if matches:
                log_gamedata_error(obj_name, key, entity_type, f"Unknown gamedata key. Did you mean '{matches[0]}'?")
            else:
                log_gamedata_error(obj_name, key, entity_type, "Unknown gamedata key. No potential matches found.")
            continue

        # Deprecated key
        if key_lc in schema.deprecated:
            log_gamedata_error(obj_name, key, entity_type, "Key is deprecated and should be removed.")
            continue

        # Unimplemented key
        if key_lc in schema.unimplemented:
            log_gamedata_error(obj_name, key, entity_type, "Key is not implemented in the game.")
            continue

        # Valid key
        emit_gamedata(key, value, i)

    return out_items

def ProcessGamedata(in_obj, in_entity_type, out_obj):
    ma_str = in_obj.get("ma")
    if not ma_str:
        return

    try:
        parsed = parse_gamedata_string(ma_str)
    except Exception as e:
        g_class.logError(f"GAMEDATA ERROR: Failed to parse gamedata on {in_obj.name}: {e}")
        return

    if not parsed:
        return

    entity_type_lc = get_entity_type(parsed, in_entity_type).lower()
    schema = g_class.g_GDSchema.get(entity_type_lc)
    if not schema:
        suggest_entity_type(entity_type_lc, in_obj.name)
        return

    validated_items = validate_gamedata(parsed, schema, in_obj.name, entity_type_lc)

    out_obj.userData.extend(validated_items)