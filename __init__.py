# Blender runs this module on bootup / addon enable calling register to add all the classes and UI updates, unregister is called when this addon is disabled

# Blender looks for this Dictionary for info about this Add-on, viewable in the Add-ons category within Preferences
bl_info = {
        "name": "Metal Arms PASM Toolkit",
        "author": "Crashz",
        "version": (0, 4, 25),
        "blender": (2, 93, 0),
        "category": "Import-Export",
        "location": "File > Import-Export",
        "description": "Rewrite of the Ape Exporter plugin from 3DS MAX 5 for Blender 2.93+. This is a tool for exporting .wld files to then be compiled into an MST using PASM",
        "support": "TESTING"
}

import bpy # Registering / Unregistering classes

# Import the classes that do the magic
from .ui_custom_properties import *
from .export_wld import *
from .export_ape import *

# The list of classes we are registering within Blender
classes = (
    ExportWLD,
    ExportAPE,
    MAImgui
)

# When this add-on is enabled in Edit>Preferences>Add-ons, this function is called
def register():    
    print("Metal Arms Toolbox Add-On enabled!")
    # Registering classes
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Update UI
    bpy.types.TOPBAR_MT_file_export.append(exportAPE_MenuFunc)
    bpy.types.TOPBAR_MT_file_export.append(exportWLD_MenuFunc)
    VIEW3D_MT_object_context_menu.append(MAGUI_MenuFunc)

# When this add-on is disabled in Edit>Preferences>Add-ons, this function is called
def unregister():
    print("Metal Arms Toolbox Add-On disabled!")
    # Unregistering classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Update UI
    bpy.types.TOPBAR_MT_file_export.remove(exportAPE_MenuFunc)
    bpy.types.TOPBAR_MT_file_export.remove(exportWLD_MenuFunc)
    VIEW3D_MT_object_context_menu.remove(MAGUI_MenuFunc)