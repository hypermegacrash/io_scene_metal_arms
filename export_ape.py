# Module for exporting a .ape file and adding UI to execute

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
from . import pasm_file_def

# Get our global variables like header data & I/O file
from . import g_class

# Grab all our defs for exporting Blender data to PASM formatted data
from .process_object_geo3  import ExportObjGeo
from .process_object_light import ExportObjLight
from .process_object_bone  import ExportObjBone

# We need this for accessing filepath functions
import os

class ExportAPE(Operator, ExportHelper):
        """Export scene to a Pasm compatible .ape file"""
        # Should this stuff be in the menu_func func? something to consider
        bl_idname = 'export_scene.ape'
        bl_label = 'Export APE'
        filename_ext = '.ape'
        
        m_bUseSelection: BoolProperty(
            name="Selection Only",
            description="Export selected objects only",
            default=False,
            )
            
        m_bExportLights: BoolProperty(
            name="Export Light Data",
            description="Export all lights from the scene",
            default=True,
            )
            
        m_bExportGeo: BoolProperty(
            name="Export Geometry Data",
            description="Export all geometry from the scene",
            default=True,
            )
          
        m_bExportHierarchy: BoolProperty(
            name="Export Hierarchy",
            #description="Create a bone for every object",
            description="Export the armature from the scene",
            default=True,
            )

        # Draw the export properties which are then stored in self to be accessed later
        def draw(self, context):
            layout = self.layout
            
            box = layout.box()
            box.label(text="Ape File Exporter")
        
            layout.prop(self, "m_bUseSelection")
            
            testA = layout.box()
            
            testA.prop(self, "m_bExportLights")
            testA.prop(self, "m_bExportGeo")
            testA.prop(self, "m_bExportHierarchy")
            
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
              
                # Init and dress a fresh header
                g_class.gWldHeader = pasm_file_def.PASMHeader() 
                
                filename = os.path.basename(self.filepath)
                filename = filename[:len(filename)-4]
                g_class.gWldHeader.sceneName = filename
                
                g_class.gWldHeader.bWld = 0
                           
                g_class.file = open(self.filepath, 'wb') # Init our none var in the global g_class
                g_class.file.write(g_class.gWldHeader.packBytes()) # This will be overwritten at the very end with the correct data
                
                # The data we want from the scene are the "objects"
                # Objects are generic containers that contain "data"
                # Data for an Object can be a mesh, light, empty etc
                
                if (self.m_bUseSelection):
                    objects = context.selected_objects
                else:
                    objects = context.scene.objects

                # To mimic the original exporter as closely as possible
                # We itterate over the entire scene for each section of the PASM file
                # One loop for lights, one for geo, one for cells, and so on
	       
                if(self.m_bExportHierarchy):
                    for obj in objects:
                        ExportObjBone(obj)
                        
                if(self.m_bExportLights):
                    for obj in objects:
                        ExportObjLight(obj)
                
                if(self.m_bExportGeo):                
                    for obj in objects:
                        ExportObjGeo(obj)
                
                # Go back to the start and rewrite the header with correct data
                g_class.file.seek(0)
                g_class.file.write(g_class.gWldHeader.packBytes())
                             
                g_class.file.close() # Remember folks, always close your files when your done playing with them
                
                print("APE Export Finished!")
                self.report({'INFO'}, "APE Export Finished!")
        
                return {'FINISHED'}
                
def exportAPE_MenuFunc(self, context):
    self.layout.operator(
    ExportAPE.bl_idname, text="Metal Arms Pasm Ape (.ape)")