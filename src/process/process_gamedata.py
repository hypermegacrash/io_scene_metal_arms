"""
Gamedata Parsing and Validation Module
--------------------------------------

This module provides a system for parsing, validating, and embedding
custom gamedata attached to Blender objects into the PASM Tool Format.

Key Features:
- Parses `ma` strings (custom property data) into
  the correct format for binary embedding.
- Loads and resolves an XML-based gamedata schema (madb.xml)
- Validates object gamedata against the schema with helpful logging for:
    - Unknown keys
    - Deprecated keys
    - Unimplemented keys
- Suggests close matches for mistyped entity types or keys.

Core Components:
- `GDNode`: Dataclass representing a schema node (class or group) with
  inheritance and parameter sets.
- `parse_ma_string()`: Parses raw gamedata strings into key/value dicts.
- `setup_gd_schema()`: Loads and processes the XML database into
  a resolved schema dictionary.
- `ProcessGamedata()`: Main entry point for parsing and embedding
  gamedata for a Blender object.
- `validate_gamedata()`, `write_user_data()`, and logging helpers
  support structured validation and user feedback.

Usage:
    # Initialize schema once (typically at Blender startup)
    setup_gd_schema()

    # Process gamedata attached to an object
    ProcessGamedata(blender_object, default_entity_type, output_object)
"""

# PYTHON BUILT-IN
from difflib import get_close_matches
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Dict, Set
import os

# FANG TOOLKIT
from . import g_class  # For global variables and logging

_XML_DATABASE_NAME = "madb.xml"

# Data structures
def _empty_schema() -> Dict[str, Set[str]]:
    return {
        "valid":         set(),
        "deprecated":    set(),
        "unimplemented": set(),
        "all":           set(),
    }

@dataclass
class GDNode:
    kind:     str  # "group" or "class"
    inherits: List[str]           = field(default_factory=list)
    params:   Dict[str, Set[str]] = field(default_factory=_empty_schema)

# XML Parsing and Schema Setup
def _parse_params(parent_elem: ET.Element) -> Dict[str, Set[str]]:
    schema = _empty_schema()
    for param in parent_elem.findall("param"):
        try:
            name          = param.attrib["name"].strip().lower()
            deprecated    = int(param.attrib.get("deprecated", 0))
            unimplemented = int(param.attrib.get("unimplemented", 0))
        except (KeyError, ValueError):
            continue

        if deprecated:      schema["deprecated"].add(name)
        elif unimplemented: schema["unimplemented"].add(name)
        else:               schema["valid"].add(name)

    return schema

def _merge_schema(dst: Dict[str, Set[str]], src: Dict[str, Set[str]]):
    for key in ("valid", "deprecated", "unimplemented"):
        dst[key].update(src[key])

def _parse_nodes(root: ET.Element) -> Dict[str, GDNode]:
    nodes: Dict[str, GDNode] = {}

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

def _resolve_schema(name: str, nodes: Dict[str, GDNode], visited=None) -> Dict[str, Set[str]]:
    visited = visited or set()
    if name in visited:
        raise ValueError(f"Cyclic inheritance detected: {name}")
    visited.add(name)

    node = nodes.get(name)
    if not node:
        return _empty_schema()

    schema = _empty_schema()
    for parent in node.inherits:
        _merge_schema(schema, _resolve_schema(parent, nodes, visited))
    _merge_schema(schema, node.params)
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
        schema["all"] = schema["valid"] | schema["deprecated"] | schema["unimplemented"]
        g_class.g_GDSchema[name] = schema

    return True

# MA String Parsing
def parse_ma_string(ma_string: str) -> Dict[str, str]:
    data = {}
    for line in ma_string.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = map(str.strip, line.split("=", 1))
        data[key] = value
    return data

# Gamedata Validation Helpers
def log_gamedata_error(obj_name: str, key: str, entity_type: str, message: str, warning: bool = False):
    g_class.logError(f"GAMEDATA ERROR: {message} '{key}' found in {obj_name} for entity type {entity_type}.")

def get_entity_type(parsed: Dict[str, str], default: str) -> str:
    return parsed.get("Type") or parsed.get("type") or default

def suggest_entity_type(entity_type_lc: str, obj_name: str):
    all_classes = g_class.g_GDSchema.keys()
    matches = get_close_matches(entity_type_lc, all_classes, n=1, cutoff=0.7)
    if matches:
        suggestion = matches[0]
        g_class.logError(
            f"GAMEDATA ERROR: Unknown entity type '{entity_type_lc}' on {obj_name}. Did you mean '{suggestion}'?"
        )
    else:
        g_class.logError(f"GAMEDATA ERROR: Unknown entity type '{entity_type_lc}' on {obj_name}. No potential matches found.")

def validate_gamedata(parsed: Dict[str, str], schema: Dict[str, Set[str]], obj_name: str, entity_type: str) -> List[str]:
    out_items = []

    keys = list(parsed.items())
    for i, (key, value) in enumerate(keys):
        key_lc = key.lower()

        # Invalid key
        if key_lc not in schema["all"]:
            matches = get_close_matches(key_lc, schema["all"], n=1, cutoff=0.7)
            if matches and matches[0] != "goodie":
                log_gamedata_error(obj_name, key, entity_type, f"Unknown gamedata key. Did you mean '{matches[0]}'?")
            elif not matches:
                log_gamedata_error(obj_name, key, entity_type, "Unknown gamedata key. No potential matches found.")
            continue

        # Deprecated key
        if key_lc in schema["deprecated"]:
            log_gamedata_error(obj_name, key, entity_type, "Key is deprecated and should be removed.")
            continue

        # Unimplemented key
        if key_lc in schema["unimplemented"]:
            log_gamedata_error(obj_name, key, entity_type, "Key is not implemented in the game.")
            continue

        # Valid key
        out_items.append(f"{key}={value}")
        if i < len(keys) - 1:
            out_items.append("\r\n")

    return out_items

def write_user_data(outObj, items: List[str]):
    outObj.userData.extend(items)

# Main Processing Function
def ProcessGamedata(obj, entityType, outObj):
    ma_str = obj.get("ma")
    if not ma_str:
        return

    try:
        parsed = parse_ma_string(ma_str)
    except Exception as e:
        print(f"Failed to parse gamedata on {obj.name}: {e}")
        return

    if not parsed:
        return

    entity_type_lc = get_entity_type(parsed, entityType).lower()
    schema = g_class.g_GDSchema.get(entity_type_lc)
    if not schema:
        suggest_entity_type(entity_type_lc, obj.name)
        return

    validated_items = validate_gamedata(parsed, schema, obj.name, entity_type_lc)
    write_user_data(outObj, validated_items)