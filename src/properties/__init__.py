import bpy

from .prop_object import MAObjectDataProperty, DrawMAObjectDataPanel
from .prop_light  import MALightDataProperty,  DrawMALightDataPanel
from .prop_bone   import MABoneDataProperty,   DrawMABoneDataPanel

classes = (
    MAObjectDataProperty,
    MALightDataProperty,
    MABoneDataProperty,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.ma_ob_props   = bpy.props.PointerProperty(type=MAObjectDataProperty)
    bpy.types.Light.ma_light_props = bpy.props.PointerProperty(type=MALightDataProperty)
    bpy.types.Bone.ma_bone_props   = bpy.props.PointerProperty(type=MABoneDataProperty)

    bpy.types.DATA_PT_empty.append(DrawMAObjectDataPanel)
    bpy.types.DATA_PT_context_light.append(DrawMALightDataPanel)
    bpy.types.BONE_PT_context_bone.append(DrawMABoneDataPanel)


def unregister():
    bpy.types.BONE_PT_context_bone.remove(DrawMABoneDataPanel)
    bpy.types.DATA_PT_context_light.remove(DrawMALightDataPanel)
    bpy.types.DATA_PT_empty.remove(DrawMAObjectDataPanel)

    del bpy.types.Bone.ma_bone_props
    del bpy.types.Light.ma_light_props
    del bpy.types.Object.ma_ob_props

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)