# Module that adds new properties for bones within the UI

import bpy

class MABoneDataProperty(bpy.types.PropertyGroup):
    """Metal Arms Bone Data Properties"""
    
    fBoneScale: bpy.props.FloatProperty( name="Bone Scale", description="", default = 1.0 )
    
    # UI VARS
    # Temp hack putting this in here, should be in its own class
    expandedMABoneProps: bpy.props.BoolProperty( name="MA Bone",  description="", default=False )

def DrawMABoneDataPanel(self, context):
    layout = self.layout
    
    layout.use_property_split = False # Boxes look funky with this set to True
    mapropsbox = layout.box()
    mapropsbox.prop(context.bone.ma_bone_props, "expandedMABoneProps",
        icon="TRIA_DOWN" if context.bone.ma_bone_props.expandedMABoneProps else "TRIA_RIGHT",
        emboss = False
        )
    mapropsbox.use_property_split = True
    mapropsbox.use_property_decorate = False # Remove the diamond used for keyframing properties in animation
    if context.bone.ma_bone_props.expandedMABoneProps:
        mapropsbox.prop(context.bone.ma_bone_props, "fBoneScale")
