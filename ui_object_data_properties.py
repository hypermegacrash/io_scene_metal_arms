# Module that exposes additional properties for shapes by adding new properties under the object > data window

# BLENDER
import bpy
from bpy.props import * # Property / UI Cheat Sheet https://docs.blender.org/api/current/bpy.props.html
from bpy.types import DATA_PT_empty # We need access to the object data struct
from bpy.types import Operator

class MAObjectDataProperty(bpy.types.PropertyGroup):
    """Metal Arms Object Data Properties"""
    
    fCylinderHeight:     FloatProperty(name="Cylinder Height",     description="", default = 1.0)
    fCylinderWidth:      FloatProperty(name="Cylinder Width",      description="", default = 1.0)
    
    # UI VARS
    # Temp hack putting this in here, should be in its own class
    expandedMAObProps:       BoolProperty( name="MA Shape Cylinder",  description="",                                default=False )

def DrawMAObjectDataPanel(self, context):
    if context.object.empty_display_type == "CONE":
        layout = self.layout
        #print(dir(context.object))
        #layout.use_property_split = True
        
        layout.use_property_split = False # Boxes look funky with this set to True
        mapropsbox = layout.box()
        mapropsbox.prop(context.object.ma_ob_props, "expandedMAObProps",
            icon="TRIA_DOWN" if context.object.ma_ob_props.expandedMAObProps else "TRIA_RIGHT",
            emboss = False
            )
        mapropsbox.use_property_split = True
        mapropsbox.use_property_decorate = False # Remove the diamond used for keyframing properties in animation
        if context.object.ma_ob_props.expandedMAObProps:
            mapropsbox.prop(context.object.ma_ob_props, "fCylinderHeight")
            mapropsbox.prop(context.object.ma_ob_props, "fCylinderWidth")
        
        
        