# Module for updating a FANG Material to the version from this Add-On

# BUILT IN
import os
import uuid
# BLENDER
import bpy

FANG_MAT_VERSION  = 1
FANG_COMP_VERSION = 1

FANG_MATERIAL_SOCKET_MAP = {
    "Tint Color",
    "Diffuse Color",
    "Alpha Mask",
    "Emissive Mask",
    "Environment Map",
    "Bump Map",
    "Detail Map",
    "Emissive",
    "Two-Sided",
}

FANG_COMPOSITE_SOCKET_MAP = {
    "Base",
    "Layer 1",
    "Vertex Color",
}

def migrate_node(in_node, in_new_group):
    """Replace a group node's node tree while preserving connections."""
    nt = in_node.id_data

    # Capture the state of the current node group
    inputs   = {}
    defaults = {}
    outputs  = {}
    
    for s in in_node.inputs:
        if s.is_linked:
            inputs[s.name] = s.links[0].from_socket
        elif hasattr(s, "default_value"):
            defaults[s.name] = s.default_value
    
    for s in in_node.outputs:
        if s.is_linked:
            outputs[s.name] = [l.to_socket for l in s.links]

    # Replace the node group
    in_node.node_tree = in_new_group

    # Reconnect inputs
    for name, from_socket in inputs.items():
        if name in in_node.inputs:
            nt.links.new(from_socket, in_node.inputs[name])

    # Reconnect outputs
    for name, to_sockets in outputs.items():
        if name in in_node.outputs:
            for ts in to_sockets:
                nt.links.new(in_node.outputs[name], ts)

    # Restore default values
    for name, value in defaults.items():
        if name in in_node.inputs and hasattr(in_node.inputs[name], "default_value"):
            in_node.inputs[name].default_value = value

def iter_node_trees():
    '''Currated itterator for all Fang Node Groups'''
    # Nested node groups
    yield from bpy.data.node_groups

    # Materials
    for material in bpy.data.materials:
        if material.use_nodes and material.node_tree:
            yield material.node_tree

def replace_group_everywhere(old_group, new_group):
    """Replace all material references to legacy node groups."""
    for tree in iter_node_trees():
        for node in tree.nodes:
            if node.type == 'GROUP' and node.node_tree == old_group:
                migrate_node(node, new_group)

def append_nodegroup(blend_path, group_name):
    """Append the replacement node group from the addon blend file."""
    with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
        if group_name not in data_from.node_groups:
            raise RuntimeError(f"Missing node group: {group_name}")
        data_to.node_groups = [group_name]

    return bpy.data.node_groups[group_name]

def update_group(blend_path, group_name):
    """Replace all legacy versions of a node group."""

    # Get all the old groups
    old_groups = [
        g for g in bpy.data.node_groups
        if g.name == group_name or g.name.startswith(f"{group_name}.")
    ]

    # Give the old groups unique temporary names so no name fighting
    for group in old_groups:
        group.name = f"__OLD__{uuid.uuid4().hex}"

    # Append the replacement node group.
    new_group = append_nodegroup(blend_path, group_name)

    # Update every instance to reference the new group.
    for old in old_groups:
        replace_group_everywhere(old, new_group)

    # Remove the old datablocks.
    for old in old_groups:
        bpy.data.node_groups.remove(old)
    
class MA_FMat_Update(bpy.types.Operator):
    bl_idname = "object.ma_update_material"
    bl_label  = "Update FANG Material / Composite"

    def execute(self, context):
        # Start by grabbing our shader node from the addon
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        DATA_DIR = os.path.join(BASE_DIR, "data")
        blend_path = os.path.join(DATA_DIR, "FangMasterShader.blend")

        # Update the node groups
        update_group( blend_path, "FANG Material"  )
        update_group( blend_path, "FANG Composite" )

        self.report({'INFO'}, "FANG Materials updated successfully")

        return {'FINISHED'}