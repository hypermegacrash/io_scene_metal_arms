# Module that exposes additional properties for shapes by adding new properties under the object > data window

# BLENDER
import bpy
from bpy.props import * # Property / UI Cheat Sheet https://docs.blender.org/api/current/bpy.props.html

class MALightDataProperty(bpy.types.PropertyGroup):
    """Metal Arms Light Data Properties"""
    
    fRadius:             FloatProperty(name="Radius",     description="How far this Light will travel", default = 100.0)
    fIntensity:          FloatProperty(name="Intensity",  description="Brightness of this light",       default = 1.0)
    
    # UI VARS
    # Temp hack putting this in here, should be in its own class
    expandedMALightProps:       BoolProperty( name="MA Light",  description="",                                default=False )

def DrawMALightDataPanel(self, context):
    layout = self.layout
    
    layout.use_property_split = False # Boxes look funky with this set to True
    mapropsbox = layout.box()
    mapropsbox.prop(context.object.data.ma_light_props, "expandedMALightProps",
        icon="TRIA_DOWN" if context.object.data.ma_light_props.expandedMALightProps else "TRIA_RIGHT",
        emboss = False
        )
    mapropsbox.use_property_split = True
    mapropsbox.use_property_decorate = False # Remove the diamond used for keyframing properties in animation
    if context.object.data.ma_light_props.expandedMALightProps:
        mapropsbox.prop(context.object.data.ma_light_props, "fRadius")
        mapropsbox.prop(context.object.data.ma_light_props, "fIntensity")
        
        
        