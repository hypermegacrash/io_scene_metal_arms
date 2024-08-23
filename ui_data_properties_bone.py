# Module that exposes additional properties for shapes by adding new properties under the...

# BLENDER
import bpy
from bpy.props import * # Property / UI Cheat Sheet https://docs.blender.org/api/current/bpy.props.html

class MABoneDataProperty(bpy.types.PropertyGroup):
    """Metal Arms Bone Data Properties"""
    
    fBoneScale:     FloatProperty(name="Bone Scale",     description="", default = 1.0)
    
    # UI VARS
    # Temp hack putting this in here, should be in its own class
    expandedMABoneProps:       BoolProperty( name="MA Bone",  description="",                                default=False )

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
        
        
        