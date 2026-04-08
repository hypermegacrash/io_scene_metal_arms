# Module for converting a Principal BSDF to FANG Material

# BLENDER
import bpy

PRINCIPLED_TO_FANG = {
    "Base Color":        "Diffuse Color",
    "Alpha":             "Alpha Mask",
    "Emission":          "Emissive",
    "Emission Strength": "Emissive Mask",
    "Normal":            "Bump Map",
}

def get_active_surface(mat):
    """Return the node connected to the Material Output surface, or None."""
    if mat.name == "Dots Stroke":
        return None
    
    mat_out = next(
        (node for node in mat.node_tree.nodes if node.type == "OUTPUT_MATERIAL" and node.is_active_output),
        None
    )
    if not mat_out:
        return None

    if mat_out.inputs["Surface"].is_linked:
        return mat_out.inputs["Surface"].links[0].from_node
    return None

def capture_bsdf_state(bsdf):
    inputs   = {}
    defaults = {}

    for s in bsdf.inputs:
        if s.is_linked:
            inputs[s.name] = s.links[0].from_socket
        elif hasattr(s, "default_value"):
            defaults[s.name] = s.default_value

    return inputs, defaults

def replace_with_fang(mat, bsdf, fang_group_name="FANG Material"):
    nt = mat.node_tree

    if fang_group_name not in bpy.data.node_groups:
        print(f"Missing node group: {fang_group_name}")
        return

    inputs, defaults = capture_bsdf_state(bsdf)

    # Create FANG node
    fang = nt.nodes.new("ShaderNodeGroup")
    fang.node_tree = bpy.data.node_groups[fang_group_name]
    fang.location = bsdf.location

    # Reconnect linked inputs
    for bsdf_name, from_socket in inputs.items():
        fang_name = PRINCIPLED_TO_FANG.get(bsdf_name)
        if not fang_name:
            continue

        if fang_name in fang.inputs:
            nt.links.new(from_socket, fang.inputs[fang_name])

    # Restore default values
    for bsdf_name, value in defaults.items():
        fang_name = PRINCIPLED_TO_FANG.get(bsdf_name)
        if not fang_name:
            continue

        if (
            fang_name in fang.inputs and
            hasattr(fang.inputs[fang_name], "default_value")
        ):
            try:
                fang.inputs[fang_name].default_value = value
            except:
                pass

    # Connect to Material Output
    mat_out = next(
        (n for n in nt.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output),
        None
    )
    if mat_out:
        nt.links.new(fang.outputs[0], mat_out.inputs["Surface"])

    # Remove old BSDF LAST
    nt.nodes.remove(bsdf)

class MA_FMat_Convert(bpy.types.Operator):
    """Replace Principled BSDF with FANG Material"""
    bl_idname = "object.ma_bsdf_to_fang"
    bl_label  = "Convert BSDF to FANG Material"

    def execute(self, context):
        for mat in bpy.data.materials:
            surface = get_active_surface(mat)
            if not surface:
                continue

            # Skip if already FANG
            if surface.type == 'GROUP' and surface.node_tree and surface.node_tree.name == "FANG Material":
                continue

            if surface.type == 'BSDF_PRINCIPLED':
                replace_with_fang(mat, surface)

        self.report({'INFO'}, "Converted Principled BSDFs to FANG Material")
        return {'FINISHED'}