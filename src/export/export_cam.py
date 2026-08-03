# Module for exporting a .cam file and adding UI to execute

# BUILT IN
import os
# BLENDER
import bpy
from bpy_extras.io_utils import ExportHelper
# FANG TOOLKIT
from ..process import g_class
from ..process.process_logger        import ErrorLogger
from ..process.process_object_camera import ExportObjCam
from .help_footer import writeFooterInfo

class ExportCAM(bpy.types.Operator, ExportHelper):
    """Export scene to a Pasm compatible .cam file"""
    bl_idname    = 'export_scene.cam'
    bl_label     = 'Export CAM'
    filename_ext = '.cam'

    # Draw the export properties which are then stored in self to be accessed later
    def draw(self, context):
        layout = self.layout
        
        boxHeader = layout.box()
        boxHeader.label(text="Cam File Exporter")
        
        writeFooterInfo(layout)
                
    # The Blender Python API's equivalent of C/C++ main()
    def execute(self, context):
        # Init our out file and error log in the global g_class for other modules to access
        with open(self.filepath, 'wb')     as g_class.g_FileOut, \
                ErrorLogger() as g_class.g_Logger:
                            
            g_class.g_ShowErrorLog = False
    
            # The data we want from the scene are the "objects"
            # Objects are generic containers that contain "data"
            # Data for an Object can be a mesh, light, empty etc
            
            objects = [obj for obj in context.selected_objects]
                
            if(len(objects) == 0):
                self.report({'ERROR'}, "No Camera Object selected!")
                return {'CANCELLED'}
            elif(len(objects) != 1):
                self.report({'ERROR'}, "Can only export 1 cam at a time!")
                return {'CANCELLED'}

            # We export one camera per export
            ExportObjCam(objects[0])
                        
        self.report({'INFO'}, "CAM Export Finished!")
    
        return {'FINISHED'}
                
def exportCAM_MenuFunc(self, context):
    self.layout.operator(
        ExportCAM.bl_idname, text="Metal Arms Pasm Cam (.cam)")