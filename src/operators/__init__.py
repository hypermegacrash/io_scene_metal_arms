
# BLENDER
import bpy
# FANG TOOLKIT
from .op_fmat_convert    import MA_FMat_Convert
from .op_fmat_update     import MA_FMat_Update
from .op_gamedata_copy   import MA_Gamedata_Copy
from .op_gamedata_edit   import MA_Gamedata_Edit, MA_Gamedata_Edit_MenuFunc
from .op_gamedata_draw   import MA_Gamedata_Draw
from .ui_sidebar_helpers import MA_Panel_Helpers

classes = (
    MA_FMat_Convert,
    MA_FMat_Update,
    MA_Gamedata_Copy,
    MA_Panel_Helpers,
)

background_classes = (
    MA_Gamedata_Edit,
    MA_Gamedata_Draw,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    if not bpy.app.background:
        for cls in background_classes:
            bpy.utils.register_class(cls)

        bpy.types.VIEW3D_MT_object_context_menu.append(MA_Gamedata_Edit_MenuFunc)


def unregister():
    if not bpy.app.background:
        bpy.types.VIEW3D_MT_object_context_menu.remove(MA_Gamedata_Edit_MenuFunc)

        for cls in reversed(background_classes):
            bpy.utils.unregister_class(cls)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)