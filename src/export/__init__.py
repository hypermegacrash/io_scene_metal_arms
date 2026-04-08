
# BLENDER
import bpy
# FANG TOOLKIT
from .export_ape import ExportAPE, exportAPE_MenuFunc
from .export_wld import ExportWLD, exportWLD_MenuFunc
from .export_mtx import ExportMTX, exportMTX_MenuFunc
from .export_cam import ExportCAM, exportCAM_MenuFunc

classes = (
    ExportAPE,
    ExportWLD,
    ExportMTX,
    ExportCAM,
)

menu_funcs = (
    exportAPE_MenuFunc,
    exportWLD_MenuFunc,
    exportMTX_MenuFunc,
    exportCAM_MenuFunc,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    for func in menu_funcs:
        bpy.types.TOPBAR_MT_file_export.append(func)


def unregister():
    for func in reversed(menu_funcs):
        bpy.types.TOPBAR_MT_file_export.remove(func)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)