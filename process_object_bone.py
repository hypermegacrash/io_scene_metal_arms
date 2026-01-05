# Module for processing the bone hierarchy of a model for exporting

# FANG TOOLKIT
from . import file_def_ape # Get our PASM file classes
from . import g_class       # Get our global variables for the header data
from . import pasm_math     # PASM helper defs
# BLENDER
import bpy                  # Force a scene update when we change bone pose to REST

from mathutils import Matrix

def ExportObjBone(obj):
    if obj.type != "ARMATURE": return # Validate we're working with an armature
        
    # print(obj.name, "is an armature / hierarchy object")
    
    # Bone Index https://stackoverflow.com/questions/53440205/different-ordering-of-bones-in-blender-than-in-python
    # Rest Pose https://blender.stackexchange.com/questions/26395/python-exporter-set-armature-to-rest-pose-while-exporting-meshes
    # Rest Pose Change https://blenderartists.org/t/cannot-change-pose-when-rest-position-is-enabled/637989

    # Reset bones positions    
    for pb in obj.pose.bones:
        pb.matrix_basis = Matrix()
    
    # Scale the armature according to the bone scale
    for pb in obj.pose.bones:
        pb.scale[0] = pb.bone.ma_bone_props.fBoneScale
        pb.scale[1] = pb.bone.ma_bone_props.fBoneScale
        pb.scale[2] = pb.bone.ma_bone_props.fBoneScale

    bpy.context.view_layer.update()
    
    # We store all bones in a list then write out at the end
    aBones = []

    # Write out the Scene Root bone
    apeBone = file_def_ape.PASMBone()
    
    apeBone.szBoneName = "Scene Root"
    apeBone.mtxOrientation = [1.0, 0.0, 0.0,
                              0.0, 1.0, 0.0,
                              0.0, 0.0, 1.0,
                              0.0, 0.0, 0.0]
    apeBone.nBoneIndex = 0
    apeBone.nParentIndex = -1
       
    aBones.append(apeBone)

    for pBoneInst in obj.pose.bones:
        apeBone = file_def_ape.PASMBone()
        
        boneInst = pBoneInst.bone
        
        apeBone.szBoneName = pBoneInst.name
        apeBone.mtxOrientation = pasm_math.BObj2F43MtxHIERARCHY(pBoneInst)
        apeBone.nBoneIndex = obj.pose.bones.find(pBoneInst.name) + 1
        apeBone.nNumChildren = len(boneInst.children)
        if boneInst.parent == None: apeBone.nParentIndex = 0
        else:                       apeBone.nParentIndex = obj.pose.bones.find(boneInst.parent.name) + 1
        
        index = 0
        for child in boneInst.children:
            apeBone.auChildIndices[index] = obj.pose.bones.find(child.name) + 1
            index = index + 1
           
        aBones.append(apeBone)

    # Fix up children for Scene Root bone
    index = 0
    for bone in aBones[1:]:
        if bone.nParentIndex == 0:
            aBones[0].nNumChildren = aBones[0].nNumChildren + 1
            aBones[0].auChildIndices[index] = bone.nBoneIndex
            index = index + 1

    # Finally, write data to the file, and our header
    for bone in aBones:
        #print(bone.szBoneName, bone.mtxOrientation[9], bone.mtxOrientation[10], bone.mtxOrientation[11])
        g_class.file.write(bone.packBytes())
        g_class.gApeHeader.fileSize += len(bone.packBytes())
        g_class.gApeHeader.nNumBones += 1
