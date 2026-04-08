# Module for processing the bone hierarchy of a model for exporting

# BLENDER
import bpy
from mathutils import Matrix
# FANG TOOLKIT
from ..defs import file_def_ape_bone
from . import g_class
from . import pasm_math

IDENTITY_F43 = [
    1.0, 0.0, 0.0,
    0.0, 1.0, 0.0,
    0.0, 0.0, 1.0,
    0.0, 0.0, 0.0
]

def ExportObjBone(obj):
    if obj.type != "ARMATURE": return # Validate we're working with an armature

    pose_bones = list(obj.pose.bones)
    bone_index = {pb.name: i + 1 for i, pb in enumerate(pose_bones)} # Precompute indices (scene root occupies 0)

    # Reset pose + apply scale
    for pb in pose_bones:
        pb.matrix_basis = Matrix()
        s = pb.bone.ma_bone_props.fBoneScale
        pb.scale[:] = (s, s, s)

    bpy.context.view_layer.update()
    
    # We store all bones in a list then write out at the end
    aBones = []

    # Write out the Scene Root bone
    rootBone                = file_def_ape_bone.PASMBone()
    rootBone.szBoneName     = "Scene Root"
    rootBone.mtxOrientation = IDENTITY_F43
    rootBone.nBoneIndex     = 0
    rootBone.nParentIndex   = -1  
    aBones.append(rootBone)

    for pBoneInst in obj.pose.bones:

        apeBone = file_def_ape_bone.PASMBone()
        bone    = pBoneInst.bone
        parent  = bone.parent
        
        apeBone.szBoneName     = pBoneInst.name
        apeBone.mtxOrientation = pasm_math.BObj2F43MtxHIERARCHY(pBoneInst)
        apeBone.nBoneIndex     = bone_index[pBoneInst.name]
        apeBone.nNumChildren   = len(bone.children)
        apeBone.nParentIndex   = 0 if parent is None else bone_index[parent.name]
        
        for i, child in enumerate(bone.children):
            apeBone.auChildIndices[i] = bone_index[child.name]
           
        aBones.append(apeBone)

    # Populate scene root children
    root_children = [b.nBoneIndex for b in aBones[1:] if b.nParentIndex == 0]
    rootBone.nNumChildren = len(root_children)

    for i, idx in enumerate(root_children):
        rootBone.auChildIndices[i] = idx

    # Finally, write data to the file
    for bone in aBones:
        g_class.g_FileOut.write(bone.pack())
        g_class.g_ApeHeader.fileSize  += file_def_ape_bone.PASMBone.EXPECTED_SIZE
        g_class.g_ApeHeader.nNumBones += 1