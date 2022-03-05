# Module for exporting a .cam file and adding UI to execute

# For grabbing the Add-On version so we can print it in the exporter menu
from . import bl_info

# For working with Blender data
import bpy

# We need these properties for the export settings config
from bpy.props import (
        BoolProperty,
        #BoolVectorProperty,
        #CollectionProperty,
        #EnumProperty,
        #FloatProperty,
        #FloatVectorProperty,
        #IntProperty,
        #IntVectorProperty,
        #PointerProperty,
        #StringProperty
        )

# Operator allows a class to interface with the rest of Blender essentially
# Exposes the use of the execute() function and directing bl_ data
from bpy.types import Operator
        
# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper

# . is the add-on folder directory
from . import file_def_cam

# Get our global variables like header data & I/O file
from . import g_class

# Grab all our defs for exporting Blender data to PASM formatted data
from .process_object_camera import ExportObjCam

# We need this for accessing filepath functions
import os

# The MEAT, when this class is executed it returns a PASM compatible .cam file
class ExportCAM(Operator, ExportHelper):
        """Export scene to a Pasm compatible .cam file"""
        # Should this stuff be in the menu_func func? something to consider
        bl_idname = 'export_scene.cam'
        bl_label = 'Export CAM'
        filename_ext = '.cam'

        # Draw the export properties which are then stored in self to be accessed later
        def draw(self, context):
            layout = self.layout
            
            box = layout.box()
            box.label(text="Cam File Exporter")
            
            fileRevision = layout.row()
            fileRevision.label(text = "PASM File Version # 1.5.0")
                      
            # This might be the worst thing I've ever wrote
            toolRevision = layout.row()
            strToolRevision = str(bl_info["version"])
            strToolRevision = strToolRevision[1:-1]
            strToolRevision = strToolRevision.replace(",", ".")
            strToolRevision = strToolRevision.replace(" ", "")
            strToolRevision = "MA Toolkit Version # " + strToolRevision
            toolRevision.label(text = strToolRevision)
                    
        # The Blender Python API's equivalent of C/C++ main()
        def execute(self, context):
        
            # Init our exported cam file          
            filename = os.path.basename(self.filepath)
            filename = filename[:len(filename)-4]                    
            g_class.file = open(self.filepath, 'wb') # Init our none var in the global g_class
       
            # The data we want from the scene are the "objects"
            # Objects are generic containers that contain "data"
            # Data for an Object can be a mesh, light, empty etc
            
            objects = context.selected_objects
            if(len(objects) == 0):
                print("No Camera Object selected!")
                return {'FINISHED'}
            elif(len(objects) != 1):
                print("Can only export 1 cam at a time!")
                return {'FINISHED'}

            # To mimic the original exporter as closely as possible
            # We itterate over the entire scene for each section of the PASM file
            # One loop for lights, one for geo, one for cells, and so on
	
            for obj in objects:
                ExportObjCam(obj)
                
            g_class.file.close() # Remember folks, always close your files when your done playing with them
                         
            print("CAM Export Finished!")
            self.report({'INFO'}, "CAM Export Finished!")
        
            return {'FINISHED'}
                
def exportCAM_MenuFunc(self, context):
    self.layout.operator(
        ExportCAM.bl_idname, text="Metal Arms Pasm Cam (.cam)")