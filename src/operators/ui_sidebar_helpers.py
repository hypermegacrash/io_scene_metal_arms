# Module that defines a sidebar panel containing useful QOL buttons that ease development

# BLENDER
import bpy
# FANG TOOLKIT
from ..defs import shader_table


class MA_Panel_Helpers(bpy.types.Panel):
    """Helper Side Panel for MA Toolkit containing QOL features for development"""
    bl_label       = "MA Toolkit"
    bl_idname      = "OBJECT_PT_panel"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category    = "MA Toolkit"

    # Boolean property to toggle PASM Shader section
    bpy.types.Scene.show_pasm_shaders = bpy.props.BoolProperty(
        name="Show PASM Shaders",
        description="Toggle visibility of PASM Shaders",
        default=False
    )
    
    def draw(self, context):
        layout = self.layout
        scene  = context.scene

        box = layout.box()
        box.label(text="FANG Material Tools", icon='MATERIAL')
        col = box.column(align=True)
        col.operator("object.ma_update_material", text = "Add / Update")
        col.operator("object.ma_bsdf_to_fang",    text = "Convert BSDF")

        box = layout.box()
        box.label(text="Gamedata", icon='WORLD_DATA')
        col = box.column(align=True)
        col.operator("object.ma_copy_gamedata",   text = "Copy to Selected")
        col.operator("object.ma_gd_view",         text = "View in World Space")

        box = layout.box()
        row = box.row()
        row.prop(scene, "show_pasm_shaders", icon="SHADING_RENDERED", text="PASM Shaders", emboss=True)

        if scene.show_pasm_shaders:
            col = box.column(align=True)

            for i, shader in enumerate(shader_table.SHADER_INFO):
                row = col.row()

                name = shader["name"]
                deprecated = shader["deprecated"]
                fallback = shader["fallback"]

                label = f"{i}: {name}"

                if deprecated:
                    label += " (DEPRECATED)"
                    if fallback is not None:
                        label += f" -> {fallback}"

                    row.label(text=label, icon='ERROR')
                else:
                    row.label(text=label, icon='SHADING_RENDERED')