# Module for exporting a .cam file and adding UI to execute

# BUILT IN
import os
# BLENDER
import bpy
from bpy_extras.io_utils import ExportHelper
# FANG TOOLKIT
from ..process import g_class
from ..process.process_object_animation import ExportObjAnim
from .help_footer import writeFooterInfo

class ExportMTX(bpy.types.Operator, ExportHelper):
    """Export scene to a Pasm compatible .mtx file"""
    bl_idname    = 'export_scene.mtx'
    bl_label     = 'Export MTX'
    filename_ext = '.mtx'

    # Draw the export properties which are then stored in self to be accessed later
    def draw(self, context):
        layout = self.layout
        
        boxHeader = layout.box()
        boxHeader.label(text="Mtx File Exporter")
        
        writeFooterInfo(layout)
                
    # The Blender Python API's equivalent of C/C++ main()
    def execute(self, context):
        # Init our out file and error log in the global g_class for other modules to access
        with open(self.filepath, 'wb')     as g_class.g_FileOut, \
                open(g_class.g_FileLogPath, 'a') as g_class.g_FileLog:

            g_class.g_ShowErrorLog = False
    
            # The data we want from the scene are the "objects"
            # Objects are generic containers that contain "data"
            # Data for an Object can be a mesh, light, empty etc
            
            objects = [obj for obj in context.selected_objects]
                
            if(len(objects) == 0):
                self.report({'ERROR'}, 'No Animated Object selected!')
                return {'CANCELLED'}
            elif(len(objects) != 1):
                self.report({'ERROR'}, 'Can only export 1 mtx at a time!')
                return {'CANCELLED'}
    
            # We export one animation per export
            ExportObjAnim(objects[0])

        # Did we encounter any errors?
        if(g_class.g_ShowErrorLog): os.startfile(g_class.g_FileLogPath)
                        
        self.report({'INFO'}, "MTX Export Finished!")
    
        return {'FINISHED'}
                
def exportMTX_MenuFunc(self, context):
    self.layout.operator(
        ExportMTX.bl_idname, text="Metal Arms Pasm Mtx (.mtx)")