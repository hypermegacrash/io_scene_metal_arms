# Blender runs this module on bootup / addon enable calling register to add all the classes and UI updates, unregister is called when this addon is disabled

# BLENDER
import bpy # Registering / Unregistering classes
# Blender looks for this Dictionary for info about this Add-on, viewable in the Add-ons category within Preferences
bl_info = {
        "name": "Metal Arms PASM Toolkit",
        "author": "Crashz",
        "version": (0, 17, 0),
        "blender": (4, 2, 0),
        "category": "Import-Export",
        "location": "File > Import-Export",
        "description": "Rewrite of the Ape Exporter plugin from 3DS MAX 5 for Blender 4.2+. This is a tool for exporting files to then be compiled into an MST using PASM",
        "support": "COMMUNITY"
}

# FANG TOOLKIT
# Import the classes that do the magic
from .export_wld import *
from .export_ape import *
from .export_cam import *
from .export_mtx import *
# Classes that expose more Metal Arms functionality
from .ui_gamedata               import *
from .ui_object_data_properties import *
from .ui_sidebar_helpers        import *
from .process_gamedata          import setupgdkeys

# The list of classes we are registering within Blender
classes = (
    # File Export Logic
    ExportWLD,
    ExportAPE,
    ExportCAM,
    ExportMTX,
    
    # Gamedata Editor UI
    MAGD_Operator,
    
    # Object Data UI
    MAObjectDataProperty,
    
    # Sidebar general help functions
    MASidePanel,
    MAUpdateFangMaterial,
    MABSDF2FM,
    MA_OpenGDKeys,
    MA_CopyGamedata,
    MAGDVIEW,
)

aExportUI = (
    exportAPE_MenuFunc,
    exportWLD_MenuFunc,
    exportCAM_MenuFunc,
    exportMTX_MenuFunc,
)

# When this add-on is enabled in Edit>Preferences>Add-ons, this function is called
def register():    
    #print("Metal Arms Toolbox Add-On enabled!")
    # Registering classes
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Update UI in File > Export 
    for func in aExportUI:
        bpy.types.TOPBAR_MT_file_export.append(func)
    
    # Update UI in Right Click > Object Context Menu
    bpy.types.VIEW3D_MT_object_context_menu.append(MAGD_MenuFunc)
    
    bpy.types.Object.ma_ob_props = bpy.props.PointerProperty(type = MAObjectDataProperty)
    
    # Update UI in Object > Data
    DATA_PT_empty.append(DrawMAObjectDataPanel)
    
    setupgdkeys()
    

# When this add-on is disabled in Edit>Preferences>Add-ons, this function is called
def unregister():
    #print("Metal Arms Toolbox Add-On disabled!")
    # We unregister in reverse order because systems initialized latter may rely on systems initalized earlier
    
    # Update UI in Right Click > Object Context Menu
    bpy.types.VIEW3D_MT_object_context_menu.remove(MAGD_MenuFunc)
    
    del bpy.types.Object.ma_ob_props
    
    # Update UI in Object > Data
    DATA_PT_empty.remove(DrawMAObjectDataPanel)
    
    # Update UI in File > Export in reverse order
    for func in reversed(aExportUI):
        bpy.types.TOPBAR_MT_file_export.append(func)
    
    # Unregistering classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
