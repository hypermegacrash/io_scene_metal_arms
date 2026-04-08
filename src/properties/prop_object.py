# Module that adds new properties for shapes within the UI

import bpy

class MAObjectDataProperty(bpy.types.PropertyGroup):
    """Metal Arms Object Data Properties"""
    
    fCylinderHeight: bpy.props.FloatProperty( name="Cylinder Height", description="", default = 1.0 )
    fCylinderWidth:  bpy.props.FloatProperty( name="Cylinder Width",  description="", default = 1.0 )
    
    # UI VARS
    # Temp hack putting this in here, should be in its own class
    expandedMAObProps: bpy.props.BoolProperty( name="MA Shape Cylinder", description="", default=False )

def DrawMAObjectDataPanel(self, context):
    if context.object.empty_display_type == "CONE":
        layout = self.layout
        
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
        
        
        