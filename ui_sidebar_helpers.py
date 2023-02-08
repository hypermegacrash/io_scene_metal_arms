import bpy
import os

class MABSDF2FM(bpy.types.Operator):
    """Replace all Principaled BDSF Surfaces with FANG Material NodeTrees"""
    bl_label = "Update FANG Material"
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
        
# Class to update all FANG Materials to the one currently used in the Add-On
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
        n = ng.find("FANG Composite")
        if n > -1:
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
            
            surface = matOut.inputs["Surface"].links[0].from_node # Get the Node connected to it
            
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
        n = ng.find("FANG Material")
        if n > -1:
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

        return {'FINISHED'}

#PANEL UI PART 1 DRAW
class MASidePanel(bpy.types.Panel):
    """Helper Side Panel for MA Toolkit"""
    bl_label = "MA Toolkit"
    bl_idname = "OBJECT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MA Toolkit"
    
    def draw(self, context):
        
        #variables
        layout = self.layout
        
        #add CUSTOM BUTTON
        row = layout.column()
        row.operator("object.ma_update_material", text = "Add / Update FANG Material")
        row.operator("object.ma_bsdf_to_fang",    text = "Convert BSDF to FANG")