# Module that defines Metal Arms Material Flags + UI

# BLENDER
import bpy              # For working with Blender data
from bpy.props import * # Property / UI Cheat Sheet https://docs.blender.org/api/current/bpy.props.html
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )
                       
class MAMaterialProperty(bpy.types.PropertyGroup):
    """Metal Arms material data / surface flags attached to a material"""
    
    materialType: EnumProperty(
        name = "Material Type",
        description = "A Material is a container for layers, you can have 1 layer (Standard) or 2 (Composite)",
        items = ( ('STD',  "Standard",  "Material with only base layer"),
                  ('COMP', "Composite", "Material with base layer & layer 1"),
                ),
        default = 'STD'
        )

    # COMMON MATERIAL PROPERTIES
    tintColor:         FloatVectorProperty(name="Tint Color", subtype='COLOR', default=(1.0, 1.0, 1.0), min=0.0, max=1.0, description="Color to tint material") 
    is2Sided:          BoolProperty       (name="Is 2-Sided", description="Set to True if this material should render on both sides of the polygon", default = False)
    # STAR COMMANDS
    ID:                IntProperty (name="ID",                    description="", default = 127, min = 0, max = 127)
    collID:            IntProperty (name="collID",                description="", default = 1,   min = 1, max = 63)
    sort:              BoolProperty(name="Sort",                  description="", default = False)
    order:             IntProperty (name="Order",                 description="", default = 1,   min = 1, max = 100)
    shader:            IntProperty (name="Shader",                description="", default = 0,   min = 0, max = 100) # We actually dont know the total shaders available, cap at 100                                                       
    # *motif                                                      
    nEmissiveMotifID:  IntProperty (name="Emissive Motif ID",     description="", default = 0)
    nDiffuseMotifID:   IntProperty (name="Diffuse Motif ID",      description="", default = 0)
    nSpecularMotifID:  IntProperty (name="Specular Motif ID",     description="", default = 0)
    bUseEmissiveColor: BoolProperty(name="Use Emissive Color",    description="", default = False)
    bUseDiffuseColor:  BoolProperty(name="Use Diffuse Color",     description="", default = False)
    bUseSpecularColor: BoolProperty(name="Use Specular Color",    description="", default = False)
    # *anim
    nNumTexFrames:     IntProperty  (name="Number Texture Frames", description="", default = 0)
    fFramesPerSec:     FloatProperty(name="Frames Per Second",     description="", default = 0)
    # *rotate

    # *scroll

    # CLARIFY
    z:                 IntProperty (name="Z",                   description="", default = 0, min = 0, max = 1000)
    nocoll:            BoolProperty(name="No Collision",        description="", default = False)
    # *coll
    APE_MAT_COLL_FLAGS_COLL_WITH_PLAYER:             BoolProperty(name="Player",            description="", default = True)
    APE_MAT_COLL_FLAGS_COLL_WITH_NPCS:               BoolProperty(name="NPC",               description="", default = True)
    APE_MAT_COLL_FLAGS_OBSTRUCT_LINE_OF_SIGHT:       BoolProperty(name="Line of Sight",     description="", default = True)
    APE_MAT_COLL_FLAGS_COLL_WITH_THIN_PROJECTILES:   BoolProperty(name="Thin Projectiles",  description="", default = True)
    APE_MAT_COLL_FLAGS_COLL_WITH_THICK_PROJECTILTES: BoolProperty(name="Thick Projectiles", description="", default = True)
    APE_MAT_COLL_FLAGS_COLL_WITH_CAMERA:             BoolProperty(name="Camera",            description="", default = True)
    APE_MAT_COLL_FLAGS_COLL_WITH_OBJECTS:            BoolProperty(name="Objects",           description="", default = True)
    APE_MAT_COLL_FLAGS_WALKABLE:                     BoolProperty(name="Walkable",          description="", default = True)
    APE_MAT_COLL_FLAGS_OBSTRUCT_SPLASH_DAMAGE:       BoolProperty(name="Splash Damage",     description="", default = True)
    APE_MAT_COLL_FLAGS_COLLIDE_WITH_DEBRIS:          BoolProperty(name="Debris",            description="", default = True)
    APE_MAT_COLL_FLAGS_COLLIDE_WITH_VEHICLES:        BoolProperty(name="Vehicles",          description="", default = True)
    APE_MAT_COLL_FLAGS_HOVER_COLLIDABLE:             BoolProperty(name="Hover",             description="", default = True)
    # MISC
    noascroll:  BoolProperty       (name="noascroll",            description="", default = False)
    tint:       BoolProperty       (name="Tint",                 description="", default = False)
    writez:     BoolProperty       (name="Write Z",              description="", default = False)
    nomeshtint: BoolProperty       (name="No Mesh Tint",         description="", default = False)
    bumptile:   FloatProperty      (name="Bump Tile",            description="", default = 1)
    detailtile: FloatProperty      (name="Detail Tile",          description="", default = 4)
    light:      FloatVectorProperty(name="Light",                description="", subtype='COLOR', min=0.0, max=1.0, size=4)      
    nodraw:     BoolProperty       (name="No Draw",              description="", default = False)
    notinlm:    BoolProperty       (name="Not in Lightmap",      description="", default = False)
    nolmblock:  BoolProperty       (name="No Lightmap Block",    description="", default = False)
    nolmuse:    BoolProperty       (name="No Lightmap Use",      description="", default = False)
    vertrad:    BoolProperty       (name="Vertex Radiosity",     description="", default = False)
    noshadows:  BoolProperty       (name="Don't Cast Shadows",   description="", default = False)                           
    eangle:     IntProperty        (name="Angular Emissive",     description="", default = 0, min = 0, max = 100)
    tangle:     IntProperty        (name="Angular Transparancy", description="", default = 0, min = 0, max = 100)
        
    surf: EnumProperty(
        name = "Surface Type",
        description = "How the material reacts",
        items = ( ('0',   "0 - Default",     "*surf(0)"),
                  ('1',   "1 - Concrete",    "*surf(1)"),
                  ('2',   "2 - Metal",       "*surf(2)"),
                  ('3',   "3 - Metal Grate", "*surf(3)"),
                  ('4',   "4 - Dirt",        "*surf(4)"),
                  ('5',   "5 - Rock",        "*surf(5)"),
                  ('6',   "5 - Glass",       "*surf(6)"),
                  ('7',   "7 - ???",         "*surf(7)"),
                  ('8',   "8 - Electronics", "*surf(8)"),
                  ('9',   "9 - Junk",        "*surf(9)"),
                  ('10', "10 - Water",       "*surf(10)"),
                  ('11', "11 - Goop",        "*surf(11)"),
                  ('12', "12 - Acid",        "*surf(12)"),
                  ('13', "13 - Force Field", "*surf(13)"),
                  ('14', "14 - ???",         "*surf(14)"),
                  ('15', "15 - ???",         "*surf(15)"),
                ),
        default = '0'
        )
        
    react: EnumProperty(
        name = "React Type",
        description = "Whether the material will be slippery or not",
        items = ( ('0', "0 - Normal",   "*react(0)\nWalkable surface"),
                  ('1', "1 - Slippery", "*react(1)\nSlide around the surface, similar to ice"),
                  ('2', "2 - ???",   ""),
                  ('3', "3 - ???",   ""),
                  ('4', "4 - ???",   ""),
                  ('5', "5 - ???",   ""),
                  ('6', "6 - ???",   ""),
                  ('7', "7 - ???",   ""),
                ),
        default = '0'
        )
    
    # UI VARS
    # Temp hack putting this in here, should be in its own class
    expandedBCollision:       BoolProperty( name="Collision Properties",  description="What this material is allowed to collide with",                                default=False )
    expandedBLayerBase:       BoolProperty( name="Base Layer Properties", description="Flags that influence the look of the surface",                                 default=False )
    expandedBLayer1:          BoolProperty( name="Layer 1 Properties",    description="Flags that influence the look of the surface over the base layer",             default=False )
    expandedBStarCmdOverride: BoolProperty( name="Material Overrides",    description="Flags that will be used in place of properties those in Base Layer & Layer 1", default=False )
    
    # COMPOSITE VARS
    # Composite Materials point to these materials as the layers
    layerBase:  PointerProperty(name="Base Layer", type=bpy.types.Material)
    layer1:     PointerProperty(name="Layer 1",    type=bpy.types.Material)
    # We will construct a special column dubbed the override column
    # for each bool checked that value will override a every instance of that value within it's scope
    bOVERtint:       BoolProperty (name = "bOVERtint",      default = False)
    bOVERtintColor:  BoolProperty (name = "bOVERtintColor", default = False)
    bOVERsurf:       BoolProperty (name = "bOVERsurf",      default = False)
    bOVERreact:      BoolProperty (name = "bOVERreact",     default = False)
    bOVERID:         BoolProperty (name = "bOVERID",        default = False)
    bOVERcollID:     BoolProperty (name = "bOVERcollID",    default = False)
    bOVERsort:       BoolProperty (name = "bOVERsort",      default = False)
    bOVERorder:      BoolProperty (name = "bOVERorder",     default = False)
    bOVERshader:     BoolProperty (name = "bOVERshader",    default = False)
    bOVERis2Sided:   BoolProperty (name = "bOVERis2Sided",  default = False)
    bOVERcoll:       BoolProperty (name = "bOVERcoll",      default = False)
    
def DrawMetalArmsProperties(layout, material):
    layout.use_property_split    = True  # Split the property into 2 columns, Name in first column, Value in second
    layout.use_property_decorate = False # Remove the diamond used for keyframing properties in animation
    
    layout.prop(material, "tint")
    # Only enable modifiying the value if tint box is checked
    subtint = layout.row()
    subtint.enabled = material.tint
    subtint.prop(material, "tintColor")
    
    layout.prop(material, "surf")
    layout.prop(material, "react")
    layout.prop(material, "ID")
    layout.prop(material, "collID")
    layout.prop(material, "sort")
    layout.prop(material, "order")
    layout.prop(material, "shader")
    layout.prop(material, "is2Sided")
    
    layout.use_property_split = False # Boxes look funky with this set to True
    
    # Drop down box for Collision Properties
    box = layout.box()
    box.prop(material, "expandedBCollision",
        icon="TRIA_DOWN" if material.expandedBCollision else "TRIA_RIGHT",
        emboss = False
        )
    
    # When the User has clicked on the Collision Properties box, show this
    if material.expandedBCollision:
        grid = box.grid_flow(columns=2, align=True)
        grid.prop(material, "APE_MAT_COLL_FLAGS_COLL_WITH_PLAYER")
        grid.prop(material, "APE_MAT_COLL_FLAGS_COLL_WITH_NPCS")
        grid.prop(material, "APE_MAT_COLL_FLAGS_OBSTRUCT_LINE_OF_SIGHT")
        grid.prop(material, "APE_MAT_COLL_FLAGS_COLL_WITH_THIN_PROJECTILES")
        grid.prop(material, "APE_MAT_COLL_FLAGS_COLL_WITH_THICK_PROJECTILTES")
        grid.prop(material, "APE_MAT_COLL_FLAGS_COLL_WITH_CAMERA")
        grid.prop(material, "APE_MAT_COLL_FLAGS_COLL_WITH_OBJECTS")
        grid.prop(material, "APE_MAT_COLL_FLAGS_WALKABLE")
        grid.prop(material, "APE_MAT_COLL_FLAGS_OBSTRUCT_SPLASH_DAMAGE")
        grid.prop(material, "APE_MAT_COLL_FLAGS_COLLIDE_WITH_DEBRIS")
        grid.prop(material, "APE_MAT_COLL_FLAGS_COLLIDE_WITH_VEHICLES")
        grid.prop(material, "APE_MAT_COLL_FLAGS_HOVER_COLLIDABLE")
    
def DrawCompositeMaterialPanel(layout, material):

    # BASE LAYER
    layout.use_property_split = True # Boxes look funky with this set to True
    layout.prop_search(material, "layerBase", bpy.data, "materials")
    # This creates a "dirty" material where it is inheriting properties from this material causing issues
    #layout.template_ID(material, "layerBase", new = "material.new", text = "Base Layer")
                                   
    # Drop down box for Base Layer Star Commands
    layout.use_property_split = False # Boxes look funky with this set to True
    layerBaseBox = layout.box()
    layerBaseBox.prop(material, "expandedBLayerBase",
        icon="TRIA_DOWN" if material.expandedBLayerBase and material.layerBase != None else "TRIA_RIGHT",
        emboss = False
        )
    
    if material.expandedBLayerBase and material.layerBase != None:
        DrawMetalArmsProperties(layerBaseBox, material.layerBase.ma_mat)
        
    # LAYER 1
    layout.use_property_split = True # Boxes look funky with this set to True
    layout.prop_search(material, "layer1", bpy.data, "materials")
     
    # Drop down box for Layer 1 Star Commands
    layout.use_property_split = False # Boxes look funky with this set to True
    layer1Box = layout.box()
    layer1Box.prop(material, "expandedBLayer1",
        icon="TRIA_DOWN" if material.expandedBLayer1 and material.layer1 != None else "TRIA_RIGHT",
        emboss = False
        )
    
    if material.expandedBLayer1 and material.layer1 != None:
        DrawMetalArmsProperties(layer1Box, material.layer1.ma_mat)
    
class MAMaterialPanel(bpy.types.Panel):
    """The panel drawn in the "Material Properties" tab to modify MAMaterialProperty"""
    bl_idname = "MATERIAL_PT_maProperties"
    bl_label = "MA Material Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    
    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        material = context.material.ma_mat

        layout.use_property_split    = True  # Split the property into 2 columns, Name in first column, Value in second
        layout.use_property_decorate = False # Remove the diamond used for keyframing properties in animation
        
        layout.prop(material, "materialType")
        
        # If this is a composite material this material is a container for 2 different materials
        if material.materialType == "COMP":
            DrawCompositeMaterialPanel(layout, material)
            
            # Drop down box for Star Command Overrides
            layout.use_property_split = False # Boxes look funky with this set to True
            starCmdOverrideBox = layout.box()
            starCmdOverrideBox.prop(material, "expandedBStarCmdOverride",
                icon="TRIA_DOWN" if material.expandedBStarCmdOverride else "TRIA_RIGHT",
                emboss = False
                )
            
            if material.expandedBStarCmdOverride:
                split = starCmdOverrideBox.split(factor = 0.05)
                col   = split.column(align = True)
                
                col.prop(material, "bOVERtint"      )
                col.prop(material, "bOVERtintColor" )
                col.prop(material, "bOVERsurf"      )
                col.prop(material, "bOVERreact"     )
                col.prop(material, "bOVERID"        )
                col.prop(material, "bOVERcollID"    )
                col.prop(material, "bOVERsort"      )
                col.prop(material, "bOVERorder"     )
                col.prop(material, "bOVERshader"    )
                col.prop(material, "bOVERis2Sided"  )
                col.prop(material, "bOVERcoll"      )
                
                col = split.column(align = True)
                DrawMetalArmsProperties(col, material)
        else:
            # Draw the properties, these flags used differently depending on context
            # Standard materials use these flags as usual
            # Composite materials use these flags to override flags set in the base layer and layer 1
            DrawMetalArmsProperties(layout, material)


