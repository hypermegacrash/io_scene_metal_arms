# Module that processes gamedata attached to an object

# PYTHON BUILT IN
from difflib import get_close_matches
import xml.etree.ElementTree as ET
# FANG TOOLKIT
from . import g_class       # Get our global variables like header data & I/O file
import os

_XML_DATABASE_NAME = "madb.xml"

def _empty_schema():
    return {
        "valid": set(),
        "deprecated": set(),
        "unimplemented": set(),
        "all": set(),
    }

def _parse_params(parent_elem):
    schema = _empty_schema()

    for param in parent_elem.findall("param"):
        try:
            name = param.attrib["name"].strip().lower()
            deprecated = int(param.attrib.get("deprecated", 0))
            unimplemented = int(param.attrib.get("unimplemented", 0))
        except (KeyError, ValueError):
            continue

        if deprecated:      schema["deprecated"].add(name)
        elif unimplemented: schema["unimplemented"].add(name)
        else:               schema["valid"].add(name)

    return schema

def _merge_schema(dst, src):
    dst["valid"].update(src["valid"])
    dst["deprecated"].update(src["deprecated"])
    dst["unimplemented"].update(src["unimplemented"])

def _parse_nodes(root):
    nodes = {}

    def add_node(elem, kind):
        name = elem.attrib.get("name", "").lower()
        if not name:
            return

        inherits = [
            i.attrib.get("name", "").lower()
            for i in elem.findall("inherit")
            if i.attrib.get("name")
        ]

        nodes[name] = {
            "kind": kind,  # group | class
            "inherits": inherits,
            "params": _parse_params(elem),
        }

    for group in root.findall(".//group"):
        add_node(group, "group")

    for cls in root.findall(".//class"):
        add_node(cls, "class")

    return nodes

def _resolve_schema(name, nodes, visited):
    if name in visited:
        raise ValueError(f"Cyclic inheritance detected: {name}")

    visited.add(name)

    node = nodes.get(name)
    if not node:
        return _empty_schema()

    schema = _empty_schema()

    # resolve parents first
    for parent in node["inherits"]:
        parent_schema = _resolve_schema(parent, nodes, visited)
        _merge_schema(schema, parent_schema)

    # then merge own params
    _merge_schema(schema, node["params"])

    return schema

def setup_gd_schema():
    path = os.path.join(os.path.dirname(__file__), _XML_DATABASE_NAME)

    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except Exception as e:
        print(f"Failed to load XML database: {e}")
        return False

    nodes = _parse_nodes(root)

    g_class.gd_schema = {}

    for name, node in nodes.items():
        if node["kind"] != "class":
            continue

        schema = _resolve_schema(name, nodes, visited=set())

        schema["all"] = (
            schema["valid"]
            | schema["deprecated"]
            | schema["unimplemented"]
        )

        g_class.gd_schema[name] = schema

    return True

def parse_ma_string(ma_string: str) -> dict:
    data = {}
    if not ma_string:
        return data

    for line in ma_string.splitlines():
        line = line.strip()

        # is a comment line for level designers
        if not line or line.startswith("#"):
            continue

        # Can't work with a key that has no value
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()

    return data

# Grab custom properties from the object
def ProcessGamedata(obj, entityType, outObj):
    # Check if we have custom properties
    if "ma" not in obj:
        return
    
    # Attempt to parse if we do have them
    try:
        parsed = parse_ma_string(obj["ma"])
    except Exception as e:
        print(f"Failed to parse gamedata on {obj.name}: {e}")
        return
    
    # Check if this dictionary is empty, if so nothing to do
    if not parsed:
        return
    
    # Determine object type
    entity_type = parsed.get("Type") or parsed.get("type")
    if not entity_type:
       entity_type = entityType

    entity_type_lc = entity_type.lower()

    # Fetch schema for this class
    schema = g_class.gd_schema.get(entity_type_lc)
    if not schema:
        # Look for close matches across all known classes
        all_classes = g_class.gd_schema.keys()
        matches = get_close_matches(entity_type_lc, all_classes, n=1, cutoff=0.7)
        if matches:
            suggestion = matches[0]
            g_class.logError(
                f"GAMEDATA ERROR: Unknown entity type '{entity_type}' on {obj.name}. "
                f"Did you mean '{suggestion}'?"
            )
        else:
            g_class.logError(
                f"GAMEDATA ERROR: Unknown entity type '{entity_type}' on {obj.name}."
                "No potential matches found."
            )
        return

    # Validate keys
    for i, (key, value) in enumerate(parsed.items()):
        key_lc = key.lower()

        # Invalid key
        if key_lc not in schema["all"]:
            matches = get_close_matches(key_lc, schema["all"], n=1, cutoff=0.7)
            if matches:
                # Level Designers added numbers to the end of the goodie field
                # The game only confirms it starts with Goodie so we'll let this slide
                if matches[0] == "goodie":
                    pass
                else:
                    g_class.logError(
                        f"GAMEDATA ERROR: Unknown gamedata key '{key}' found in {obj.name} for entity type {entity_type}. "
                        f"Did you mean '{matches[0]}'?"
                    )
            else:
                g_class.logError(
                    f"GAMEDATA ERROR: Unknown gamedata key '{key}' found in {obj.name} for entity type {entity_type}. "
                    "No potential matches found."
                )
            continue

        # Deprecated key
        if key_lc in schema["deprecated"]:
            g_class.logError(
                f"GAMEDATA ERROR: The gamedata key '{key}' found in {obj.name} for entity type {entity_type} "
                "is deprecated and should be removed."
            )
            continue

        # Unimplemented key
        if key_lc in schema["unimplemented"]:
            g_class.logError(
                f"GAMEDATA WARNING: The gamedata key '{key}' found in {obj.name} for entity type {entity_type} "
                "is not implemented in the game."
            )
            continue

        # Valid key
        outObj.userData.append(f"{key}={value}")

        # only add newline if not the last item
        if i < len(parsed.items()) - 1:
            outObj.userData.append("\r\n")
    
    # Go back and patch up userData length
    dataLen = 0
    for data in outObj.userData:
        if type(data) == float:
            dataLen = dataLen + 4
        else:
            dataLen = dataLen + len(data)
    outObj.nBytesOfUserData = dataLen
