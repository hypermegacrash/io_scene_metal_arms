# Module for processing the action of an armature for exporting

# BLENDER
import bpy
# FANG TOOLKIT
from ..defs import file_def_mtx
from . import g_class
from . import pasm_math

SKIP_EXTRA_BONES = True # Skip exporting non-deformation bones (off_, tack, etc...)
TIME_TICKSPERSEC = 4800 # Constant ripped from Max SDK Docs

# TODO: Currently we dont do any optimization on exporting bone frames
# If we find the delta between the current and last pose 
# we dont need to export every single frame

# Certain bones shouldn't be animated whether they are 
# off_, collision or physics related bones
def should_export_bone(inBone):
    if inBone.name[:4].lower() == "off_":    return False
    if inBone.name[:7].lower() == "cplane_": return False
    if inBone.name[:6].lower() == "ptack_":  return False
    if inBone.name[:6].lower() == "ctack_":  return False
    if inBone.name[:5].lower() == "tack_":   return False
        
    return True

def collect_bones(obj) -> list[bpy.types.PoseBone]:
    return [b for b in obj.pose.bones if not SKIP_EXTRA_BONES or should_export_bone(b)]

def calculate_offsets(header: file_def_mtx.MTXHeader, bones: list[file_def_mtx.MTXBone]) -> None:
    offset = file_def_mtx.MTXHeader().EXPECTED_SIZE + header.nNumBones * file_def_mtx.MTXBone().EXPECTED_SIZE

    for bone in bones:
        bone.nFrameArrayOffset = int(offset)
        offset += bone.nNumFrames * file_def_mtx.MTXFrame().EXPECTED_SIZE  

def ExportObjAnim(obj):
    if obj.type != "ARMATURE": 
        g_class.logError(
            f"ANIMATION ERROR: The selected object {obj.name} is not an armature! "
            "Please select an armature and retry exporting."
        )
        return

    # Find the animation info from the interface
    scene          = bpy.context.scene
    nStartTime     = scene.frame_start
    nEndTime       = scene.frame_end + 1 # +1 for looping
    nFrameRate     = scene.render.fps
    nTicksPerFrame = TIME_TICKSPERSEC / nFrameRate
    
    mtxHeader = file_def_mtx.MTXHeader()
    
    # Export Data
    export_bones = collect_bones(obj)
    mtx_bones    = []
    mtx_frames   = []
    bone_frames  = {}
    
    # Cache the bones once and create the mapping
    for pbone in export_bones:
        mtxBone = file_def_mtx.MTXBone()
        mtxBone.szBoneName = pbone.name

        mtx_bones.append(mtxBone)
        bone_frames[pbone.name] = []

    # Itterate frame by frame
    for frameIdx, curFrame in enumerate(range(nStartTime, nEndTime)):
        scene.frame_set(curFrame)

        if frameIdx == 0:
            number_of_ticks = 0.0
        else:
            curFrameTick = float(frameIdx * nTicksPerFrame)
            number_of_ticks = curFrameTick * float((1.0 / TIME_TICKSPERSEC))

        for pbone, mtxBone in zip(export_bones, mtx_bones):
            testFrame                = file_def_mtx.MTXFrame()
            testFrame.fStartingSecs  = number_of_ticks
            testFrame.mtxOrientation = pasm_math.BObj2F43MtxBONE(pbone)

            bone_frames[pbone.name].append(testFrame)
            mtxBone.nNumFrames += 1

    # Now we need to go back and write out corrsponding arrays for the bones
    for pbone in export_bones:
        frames = bone_frames[pbone.name]
        mtx_frames.extend(frames)
  
    # Now we can fix up our data
    mtxHeader.nNumBones = len(mtx_bones)
    
    calculate_offsets(mtxHeader, mtx_bones)

    # Finally, write data to the file
    g_class.g_FileOut.write( mtxHeader.pack() )
    for bone in mtx_bones:   g_class.g_FileOut.write( bone.pack()  )
    for frame in mtx_frames: g_class.g_FileOut.write( frame.pack() )
