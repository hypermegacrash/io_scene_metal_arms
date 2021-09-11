# Blender looks for this Dictionary for info about this add-on, viewable in the Add-ons category within Preferences
bl_info = {
        "name": "Metal Arms PASM Toolkit",
        "author": "Crashz",
        "version": (0, 0, 1),
        "blender": (2, 80, 0),
        "category": "Import-Export",
        "location": "File > Import-Export",
        "description": "Rewrite of the Ape Exporter plugin from 3DS MAX 5, This is a tool for exporting .wld files to then be compiled into an MST using PASM",
        "support": "TESTING"
}

# For working with Blender data
import bpy

# We use this when exporting but I have no idea what this does, darn
from bpy_extras.io_utils import (
        ExportHelper
        )

# Needed for exporting? what does this do again?
from bpy.types import (
        Operator,
        )

# . is the add-on folder directory
from . import pasm_file_def

from . import g_class # Get our global variables like header data & I/O file

from .process_object_geo import ExportObjGeo
from .process_object_light import ExportObjLight
from .process_object_object import ExportObjObject
from .process_object_shape import ExportObjShape
from .process_object_volume import ExportObjVolume
from .process_object_fog import ExportObjFog

# Need for getting filepath bs, eventually we get rid of this and use some Blender exposed var we don't know exists, hopefully
import os

# The MEAT, when this class is executed it reutns a PASM compatible .wld file
class ExportWLD(Operator, ExportHelper):
        """Export scene to a Pasm compatible .wld file"""
        # Should this stuff be in the menu_func func? something to consider
        bl_idname = 'export_scene.wld'
        bl_label = 'Export WLD'
        filename_ext = '.wld'

        # The Blender Python API's equivalent of C/C++ main()
        def execute(self, context):
        
                # Make sure we're dealing w a fresh header
                g_class.gWldHeader = pasm_file_def.PASMHeader()
                
                filename = os.path.basename(self.filepath)
                filename = filename[:len(filename)-4]
                g_class.gWldHeader.sceneName = filename
                
                g_class.gWldHeader.bWld = 1
                
                g_class.file = open(self.filepath, 'wb')
                # This will be overwritten at the very end with the correct data
                g_class.file.write(g_class.gWldHeader.packBytes())
                
                # The data we want from the scene are the "objects"
                # Objects are generic containers that contain "data"
                # Data for an Object can be a mesh, light, empty etc

                # To mimic the original exporter as closely as possible
                # We itterate over the entire scene for each section of the PASM file
                # One loop for lights, one for geo, one for cells, and so on
	       
                for obj in bpy.context.scene.objects:
                    ExportObjLight(obj)

                for obj in bpy.context.scene.objects:
                    ExportObjObject(obj)
	
                for obj in bpy.context.scene.objects:
                    ExportObjFog(obj)
	
                for obj in bpy.context.scene.objects:
                    ExportObjShape(obj)

                for obj in bpy.context.scene.objects:
                    ExportObjVolume(obj)
                    
                for obj in bpy.context.scene.objects:
                    ExportObjGeo(obj)
                
                g_class.file.seek(0)
                g_class.file.write(g_class.gWldHeader.packBytes())
                
                # Remember folks, always close your files when your done playing with them
                g_class.file.close()
        
                return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(
        ExportWLD.bl_idname, text="Metal Arms Pasm Wld (.wld)")

# When this add-on is enabled in Edit>Preferences>Add-ons, this function is called
# Additionally, after this add-on is enabled, this function will be called on Blender bootup
def register():
        print("Metal Arms Toolbox Add-On enabled!")
        bpy.utils.register_class(ExportWLD)
        bpy.types.TOPBAR_MT_file_export.append(menu_func)

# When this add-on is disabled in Edit>Preferences>Add-ons, this function is called
def unregister():
        print("Metal Arms Toolbox Add-On disabled!")
        bpy.utils.unregister_class(ExportWLD)
        bpy.types.TOPBAR_MT_file_export.remove(menu_func)