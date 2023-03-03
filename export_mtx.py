# Module for exporting a .cam file and adding UI to execute

# FANG TOOLKIT
from . import g_class      # Get our global variables like header data & I/O file
# Grab all our defs for exporting Blender data to PASM formatted data
from . import file_def_mtx # . is the add-on folder directory
from .process_object_animation import ExportObjAnim

# BLENDER
import bpy              # For working with Blender data
import os               # We need this for accessing filepath functions
from bpy.props import ( # We need these properties for the export settings config
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

# The MEAT, when this class is executed it returns a PASM compatible .mtx file
class ExportMTX(Operator, ExportHelper):
        """Export scene to a Pasm compatible .mtx file"""
        # Should this stuff be in the menu_func func? something to consider
        bl_idname    = 'export_scene.mtx'
        bl_label     = 'Export MTX'
        filename_ext = '.mtx'

        # Draw the export properties which are then stored in self to be accessed later
        def draw(self, context):
            layout = self.layout
            
            boxHeader = layout.box()
            boxHeader.label(text="Mtx File Exporter")
            
            g_class.writeFooterInfo(layout)
                    
        # The Blender Python API's equivalent of C/C++ main()
        def execute(self, context):
            # Init our out file and error log in the global g_class for other modules to access
            with open(self.filepath, 'wb')     as g_class.file, \
                 open(g_class.fpErrorLog, 'a') as g_class.errorLogFile:

                g_class.bShowErrorLog = False
        
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
            if(g_class.bShowErrorLog): os.startfile(g_class.fpErrorLog)
                         
            print("MTX Export Finished!")
            self.report({'INFO'}, "MTX Export Finished!")
        
            return {'FINISHED'}
                
def exportMTX_MenuFunc(self, context):
    self.layout.operator(
        ExportMTX.bl_idname, text="Metal Arms Pasm Mtx (.mtx)")