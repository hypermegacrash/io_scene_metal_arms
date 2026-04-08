# Module that adds new properties for lights within the UI

import bpy

class MALightDataProperty(bpy.types.PropertyGroup):
    """Metal Arms Light Data Properties"""
    
    fRadius:    bpy.props.FloatProperty( name="Radius",    description="How far this Light will travel", default = 100.0 )
    fIntensity: bpy.props.FloatProperty( name="Intensity", description="Brightness of this light",       default = 1.0 )
    
    # UI VARS
    # Temp hack putting this in here, should be in its own class
    expandedMALightProps: bpy.props.BoolProperty( name="MA Light", description="", default=False )

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
        
        
        