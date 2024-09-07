# Module that allows for an external text editor to be used
# for writing Metal Arms Entity Gamedata

# BLENDER UI
import bpy # Blender Internal
import subprocess # Open up the external editor
import os # Operate on the host OS

# TODO: This is hardcoded for Windows as it relies on notepad.exe
        
class MAGD_External_Operator(bpy.types.Operator):
    """(Part of Metal Arms PASM Toolkit Add-on)
Expose an external editor to be used for editing multi line gamedata text"""
    bl_idname = "object.ma_ui_gamedata_external"
    bl_label = "MA Gamedata Notepad"
    bl_description = "External Editor for Metal Arms Entity Parameters"

    currentObj = None

    def invoke(self, context, event):

        self.currentObj = bpy.context.active_object

        tempFile = os.path.dirname(os.path.realpath(__file__)) + "\\" + self.currentObj.name + "_GD.txt"  # Path to the export file
            
        if "ma" not in bpy.data.objects[self.currentObj.name]:    
            bpy.data.objects[self.currentObj.name]["ma"] = ""

        with open(tempFile, "w") as f:  #open the file for writing
            f.write( self.currentObj["ma"] )       #write the memory into the file

        p = subprocess.Popen(['notepad.exe', tempFile])

        returncode = p.wait() # wait for notepad to exit

        with open(tempFile, "r") as f:  #open the file for writing
            self.currentObj["ma"] = f.read()
            
        os.remove(tempFile)
            
        return {'FINISHED'}
    

def MAGD_External_MenuFunc(self, context):
    self.layout.separator()
    col = self.layout.column()
    self.layout.operator_context = 'INVOKE_DEFAULT'
    col.operator(MAGD_External_Operator.bl_idname, icon="TEXT")