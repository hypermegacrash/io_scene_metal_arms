# Module for copying gamedata parameters from a source object to all of the selected.

# BLENDER
import bpy

class MA_Gamedata_Copy(bpy.types.Operator):
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