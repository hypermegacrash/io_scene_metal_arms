# Module for processing the bone hierarchy of a model for exporting

from . import pasm_file_def # Get our PASM file classes
from . import g_class       # Get our global variables for the header data
from . import pasm_math     # PASM helper defs
import bpy                  # Force a scene update when we change bone pose to REST
from math import pi

def ExportObjBone(obj): 
    if obj.type != "ARMATURE": return # Validate we're working with an armature
        
    print(obj.name, "is an armature / hierarchy object")
    
    # Bone Index https://stackoverflow.com/questions/53440205/different-ordering-of-bones-in-blender-than-in-python
    # Rest Pose https://blender.stackexchange.com/questions/26395/python-exporter-set-armature-to-rest-pose-while-exporting-meshes
    # Rest Pose Change https://blenderartists.org/t/cannot-change-pose-when-rest-position-is-enabled/637989

    obj.data.pose_position = "REST"
    bpy.context.view_layer.update()
    
    # We store all bones in a list then write out at the end
    aBones = []
    
    for pBoneInst in obj.pose.bones:
        print("BONE:", pBoneInst.name)
        apeBone = pasm_file_def.PASMBone()
        
        boneInst = pBoneInst.bone
        
        apeBone.szBoneName = pBoneInst.name
        apeBone.mtxOrientation = pasm_math.BObj2F43MtxHIERARCHY(pBoneInst)
        apeBone.nBoneIndex = obj.pose.bones.find(pBoneInst.name)
        apeBone.nNumChildren = len(boneInst.children)
        if boneInst.parent == None: apeBone.nParentIndex = -1
        else:                       apeBone.nParentIndex = obj.pose.bones.find(boneInst.parent.name)
        
        index = 0
        for child in boneInst.children:
            apeBone.auChildIndices[index] = obj.pose.bones.find(child.name)
            index = index + 1
           
        aBones.append(apeBone)

    # Finally, write data to the file, and our header
    for bone in aBones:
        #print(bone.szBoneName, bone.mtxOrientation[9], bone.mtxOrientation[10], bone.mtxOrientation[11])
        g_class.file.write(bone.packBytes())
        g_class.gWldHeader.fileSize += len(bone.packBytes())
        g_class.gWldHeader.nNumBones += 1
