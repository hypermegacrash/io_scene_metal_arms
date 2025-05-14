# Module that defines a sidebar panel containing useful QOL buttons that ease development

import bpy
import os

class MABSDF2FM(bpy.types.Operator):
    """Replace all Principaled BDSF Surfaces with FANG Material NodeTrees"""
    bl_label  = "Update FANG Material"
    bl_idname = "object.ma_bsdf_to_fang"
    
    def execute(self, context):
        for mat in bpy.data.materials:
            #print(mat.name)
            
            matOut = None
            
            if mat.name == "Dots Stroke":
                #print("No material!")
                continue
        
            # Get the material output
            for node in mat.node_tree.nodes:
                if node.type == "OUTPUT_MATERIAL" and node.is_active_output:
                    matOut = node
                    continue
                
            if matOut == None:
                #print("No output material!")
                continue
            
            try:
                surface = matOut.inputs["Surface"].links[0].from_node # Get the Node connected to it
            except:
                #print("No Surface Node Group!")
                continue
                
            print(surface)
        
            if surface.type == "BSDF_PRINCIPLED":
                #print("We gonna mod this one!")
                fangNodeGroup = mat.node_tree.nodes.new("ShaderNodeGroup")
                fangNodeGroup.node_tree = bpy.data.node_groups[bpy.data.node_groups.find("FANG Material")]
                fangNodeGroup.location = surface.location
                
                try:
                    basecolor = surface.inputs["Base Color"].links[0].from_node
                    mat.node_tree.links.new(fangNodeGroup.inputs["Diffuse Color"], basecolor.outputs[0])
                except:
                    #print("No Texture connected, probably shouldn't touch this one")
                    continue
                
                mat.node_tree.nodes.remove(surface)
                mat.node_tree.links.new(fangNodeGroup.outputs[0], matOut.inputs[0])
    
        return {'FINISHED'}
        
class MAUpdateFangMaterial(bpy.types.Operator):
    """Add / Update the FANG Materials in the scene"""
    bl_label = "Update FANG Material / Composite"
    bl_idname = "object.ma_update_material"
    
    def execute(self, context):
        # First we grab the updated NodeTree
        directory = os.path.dirname(os.path.realpath(__file__)) + "\\FangMasterShader.blend\\NodeTree\\"
        
        # FANG COMPOSITE FIRST
        
        # Remove the old nodetree
        ng = bpy.data.node_groups
        for node in ng:
            if (node.name.lower().split(".",1)[0] == "fang composite"):
                n = ng.find(node.name)
                ng.remove(ng[n])
        
        # Add the new nodetree
        # We do this AFTER removing old nodetree so we dont get the .001
        bpy.ops.wm.append(filename="FANG Composite", directory=directory)
        
        # Now we itterate through all materials to repair the broken data-blocks
        for mat in bpy.data.materials:   
            matOut = None
            
            # Skip the mysterious "Dots Stroke" material
            if mat.name == "Dots Stroke":
                print("Skip this material!")
                continue
        
            # Get the material output
            for node in mat.node_tree.nodes:
                if node.type == "OUTPUT_MATERIAL" and node.is_active_output:
                    matOut = node
                    continue
            
            # Does it have a Material Output?  
            if matOut == None:
                print("No output material!")
                continue
            
            # Does it have a surface connected to it?
            try:
                surface = matOut.inputs["Surface"].links[0].from_node # Get the Node connected to it
            except:
                print("No Surface Node Group!")
                continue
            
            # If it's a group... is this node tree broken?
            # Hypothetically the scene could already have a bad node tree that wasn't
            # broken by us running this script...
            if surface.type == "GROUP":
                if surface.node_tree == None:
                    print("Assume this is a broken Data-Block from being replaced")
                    surface.node_tree = bpy.data.node_groups[bpy.data.node_groups.find("FANG Composite")]
        
        # THEN FANG MATERIAL
        
        # Remove the old nodetree
        ng = bpy.data.node_groups
        for node in ng:
            if (node.name.lower().split(".",1)[0] == "fang material"):
                n = ng.find(node.name)
                ng.remove(ng[n])
        
        # Add the new nodetree
        # We do this AFTER removing old nodetree so we dont get the .001
        bpy.ops.wm.append(filename="FANG Material",  directory=directory)
        
        # Now we itterate through all materials to repair the broken data-blocks for FANG Material
        for mat in bpy.data.materials:
            matOut = None
            
            # Skip the mysterious "Dots Stroke" material
            if mat.name == "Dots Stroke":
                print("Skip this material!")
                continue
        
            # Get the material output
            for node in mat.node_tree.nodes:
                if node.type == "OUTPUT_MATERIAL" and node.is_active_output:
                    matOut = node
                    continue
            
            # Does it have a Material Output?  
            if matOut == None:
                print("No output material!")
                continue
            
            # Does it have a surface connected to it?
            try:
                surface = matOut.inputs["Surface"].links[0].from_node # Get the Node connected to it
            except:
                print("No Surface Node Group!")
                continue
            
            # If it's a group... is this node tree broken?
            # Hypothetically the scene could already have a bad node tree that wasn't
            # broken by us running this script...
            if surface.type == "GROUP":
                if surface.node_tree == None:
                    print("Assume this is a broken Data-Block from being replaced")
                    surface.node_tree = bpy.data.node_groups[bpy.data.node_groups.find("FANG Material")]
                elif surface.node_tree.name == "FANG Composite":
                    flayer0 = surface.inputs["Base"].links[0].from_node    # Get the Node connected to it
                    flayer1 = surface.inputs["Layer 1"].links[0].from_node # Get the Node connected to it
                    
                    flayer0.node_tree = bpy.data.node_groups[bpy.data.node_groups.find("FANG Material")]
                    flayer1.node_tree = bpy.data.node_groups[bpy.data.node_groups.find("FANG Material")]

        return {'FINISHED'}
        
class MA_OpenGDKeys(bpy.types.Operator):
    """Open the GDKeys.txt file"""
    bl_label  = "Open gdkeys.txt"
    bl_idname = "object.ma_open_gdkeys"
    
    def execute(self, context):
        path = os.path.dirname(os.path.realpath(__file__))
        path = path + "\gdkeys.txt"
        os.startfile(path)
        return {'FINISHED'}
        
class MA_CopyGamedata(bpy.types.Operator):
    """Copy the selected object's gamedata to the other highlighted objects"""
    bl_label  = "Copy GameData to Selected"
    bl_idname = "object.ma_copy_gamedata"
    
    def execute(self, context):
        # Get what we want to modify
        selectionObjs = bpy.context.selected_objects
        active_object = bpy.context.view_layer.objects.active
        inGameData = None
        
        # Error checking for sanity
        if(len(selectionObjs)  < 2):
            self.report({'ERROR'}, "Must select at least 2 objects! Aborting")
            return {'CANCELLED'}
            
        try:
            inGameData = active_object["ma"]
        except:
            self.report({'ERROR'}, f"Unable to get gamedata from {active_object.name}! Aborting")
            return {'CANCELLED'}
            
        if inGameData == "":
            self.report({'ERROR'}, f"Empty gamedata in {active_object.name}? Aborting")
            return {'CANCELLED'}

        for obj in selectionObjs:
            obj["ma"] = active_object["ma"]
        
        self.report({'INFO'}, f"Copied gamedata from {active_object.name} to {len(selectionObjs) - 1} object(s)!")
        return {'FINISHED'}

import blf
from bpy_extras.view3d_utils import location_3d_to_region_2d

class MAGDVIEW_INST(bpy.types.PropertyGroup):
    isEnabled = False
    handler = None
    drawDist = 500

# TODO: Draw Distance should be a property exposed in the UI
# TODO: Filtering should be able to be done based on type (Draw only doors, bots, etc)
# TODO: Color code option by type (Bot, Door, Generic, etc)
# TODO: UI Colors and Size should be exposed in the UI
# TODO: Only draw gamedata of selected objects
class MAGDVIEW(bpy.types.Operator):
    """Replace all Principaled BDSF Surfaces with FANG Material NodeTrees"""
    bl_label  = "View Gamedata in World Space"
    bl_idname = "object.ma_gd_view"
    
    def draw_callback_magd3dview_px(self, context, extra):
        """Draw on the viewports"""
        # BLF drawing routine
        font_id = 0
        blf.color(font_id, 1.0, 1.0, 1.0, 1.0)
        blf.size(font_id, 16)
        blf.enable(font_id, 4)
        blf.shadow_offset(font_id, 1, -1)
        
        region = bpy.context.region
        rv3d = bpy.context.space_data.region_3d
        
        for obj in bpy.context.view_layer.objects:
            if not obj.visible_get(): continue # Is this object currently rendering in the scene?
            if "ma" not in obj:       continue # Does this object have any gamedata to preview?

            # Don't draw stuff too far away
            view_mat_inv = rv3d.view_matrix
            
            if rv3d.is_perspective:
                dist = (view_mat_inv@obj.location).length
            else:
                dist = -(view_mat_inv@obj.location).z
                
            if dist > MAGDVIEW_INST.drawDist:
                continue
            
            vector2d = location_3d_to_region_2d(region, rv3d, obj.location)
            
            if vector2d == None:
                continue
            
            lines = bpy.data.objects[obj.name]["ma"].split("\n")
            
            for line in lines:
                blf.position(font_id, vector2d[0], vector2d[1], 0)
                if line[:4].lower() == "name":
                    blf.color(font_id, 0.4, 0.4, 1.0, 1.0)
                elif line[:1].lower() == "#":
                    blf.color(font_id, 0.4, 1.0, 1.0, 1.0)
                else:
                    blf.color(font_id, 1.0, 1.0, 1.0, 1.0)
                
                blf.draw(font_id, line)
                vector2d[1] -= 18
    
    def execute(self, context):
        if MAGDVIEW_INST.isEnabled == False:
            print("Adding draw handler!")
            MAGDVIEW_INST.handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_magd3dview_px, (None, None), 'WINDOW', 'POST_PIXEL')
            MAGDVIEW_INST.isEnabled = True
        elif MAGDVIEW_INST.isEnabled == True:
            print("Removing draw handler!")
            bpy.types.SpaceView3D.draw_handler_remove(MAGDVIEW_INST.handler, 'WINDOW')
            MAGDVIEW_INST.isEnabled = False
    
        return {'FINISHED'}


class MASidePanel(bpy.types.Panel):
    """Helper Side Panel for MA Toolkit containing QOL features for development"""
    bl_label = "MA Toolkit"
    bl_idname = "OBJECT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MA Toolkit"
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.column()
        row.operator("object.ma_update_material", text = "Add / Update FANG Material")
        row.operator("object.ma_bsdf_to_fang",    text = "Convert BSDF to FANG")
        row.operator("object.ma_open_gdkeys",     text = "Open gdkeys")
        row.operator("object.ma_copy_gamedata",   text = "Copy Gamedata to Selected")
        row.operator("object.ma_gd_view",         text = "View Gamedata in World Space")
        
        
        
        
        
        
        
        