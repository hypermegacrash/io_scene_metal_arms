# Module for updating a FANG Material to the version from this Add-On

# BUILT IN
import os
# BLENDER
import bpy
    
# V0 -> V1 Mapping
FANG_MATERIAL_SOCKET_MAP = {
    "Tint Color":      "Tint Color",
    "Diffuse Color":   "Diffuse Color",
    "Alpha Mask":      "Alpha Mask",
    "Emissive Mask":   "Emissive Mask",
    "Environment Map": "Environment Map",
    "Bump Map":        "Bump Map",
    "Detail Map":      "Detail Map",
    "Emissive":        "Emissive",
    "Two-Sided":       "Two-Sided",
}

# V0 -> V1 Mapping
FANG_COMPOSITE_SOCKET_MAP = {
    "Base":         "Base",
    "Layer 1":      "Layer 1",
    "Vertex Color": "Vertex Color",
}

def capture_state(node):
    inputs   = {}
    defaults = {}

    for s in node.inputs:
        if s.is_linked:
            inputs[s.name] = s.links[0].from_socket
        elif hasattr(s, "default_value"):
            defaults[s.name] = s.default_value

    outputs = {}
    for s in node.outputs:
        if s.is_linked:
            outputs[s.name] = [l.to_socket for l in s.links]

    return inputs, outputs, defaults

def migrate_node(node, new_group, socket_map):
    nt = node.id_data
    inputs, outputs, defaults = capture_state(node)

    node.node_tree = new_group

    # inputs
    for old, from_socket in inputs.items():
        new = socket_map.get(old)
        if new in node.inputs:
            nt.links.new(from_socket, node.inputs[new])

    # outputs
    for old, to_sockets in outputs.items():
        new = socket_map.get(old)
        if new in node.outputs:
            for ts in to_sockets:
                nt.links.new(node.outputs[new], ts)

    # defaults
    for old, value in defaults.items():
        new = socket_map.get(old)
        if new in node.inputs and hasattr(node.inputs[new], "default_value"):
            try:
                node.inputs[new].default_value = value
            except:
                pass

def replace_group_everywhere(old_group, new_group, socket_map):
    for tree in bpy.data.node_groups:
        for node in tree.nodes:
            if node.type == 'GROUP' and node.node_tree == old_group:
                migrate_node(node, new_group, socket_map)

def append_nodegroup(blend_path, group_name):
    with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
        if group_name not in data_from.node_groups:
            raise RuntimeError(f"Missing node group: {group_name}")
        data_to.node_groups = [group_name]

    return bpy.data.node_groups[group_name]

def update_group(blend_path, group_name, socket_map):
    old_groups = [g for g in bpy.data.node_groups if g.name == group_name]

    new_group = append_nodegroup(blend_path, group_name)

    for old in old_groups:
        replace_group_everywhere(old, new_group, socket_map)
        if old != new_group:
            bpy.data.node_groups.remove(old)
    
class MA_FMat_Update(bpy.types.Operator):
    bl_idname = "object.ma_update_material"
    bl_label = "Update FANG Material / Composite"

    def execute(self, context):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        DATA_DIR = os.path.join(BASE_DIR, "data")

        blend_path = os.path.join(DATA_DIR, "FangMasterShader.blend")

        # 1. Update FANG Material
        update_group(
            blend_path,
            "FANG Material",
            socket_map=FANG_MATERIAL_SOCKET_MAP
        )

        # 2. Update FANG Composite
        update_group(
            blend_path,
            "FANG Composite",
            socket_map=FANG_COMPOSITE_SOCKET_MAP
        )

        self.report({'INFO'}, "FANG Materials updated successfully")
        return {'FINISHED'}