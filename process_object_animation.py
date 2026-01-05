# Module for processing the action of an armature for exporting

# FANG TOOLKIT
from . import file_def_mtx # Get our PASM file classes
from . import g_class      # Get our global variables for the header data
from . import pasm_math    # PASM helper defs
# BLENDER
import bpy                 # For working with Blender data

SKIP_EXTRA_BONES = True # Skip exporting non-deformation bones (off_, tack, etc...)

# TODO: Currently we dont do any optimization on exporting bone frames
# If we find the delta between the current and last pose we dont need to export
# every single frame

# Certain bones shouldn't be animated whether they are 
# off_, collision or physics related bones
def shouldExportBone(inBone):
    if inBone.name[:4].lower() == "off_":    return False
    if inBone.name[:7].lower() == "cplane_": return False
    if inBone.name[:6].lower() == "ptack_":  return False
    if inBone.name[:6].lower() == "ctack_":  return False
    if inBone.name[:5].lower() == "tack_":   return False
        
    return True

def ExportObjAnim(obj):
    if obj.type != "ARMATURE": return # Validate we're working with armature animation data

    # print(obj.name, "is an armature object")

    TIME_TICKSPERSEC = 4800 # Constant ripped from Max SDK Docs
    
    # Find the animation info from the interface
    nStartTime = bpy.context.scene.frame_start
    nEndTime   = bpy.context.scene.frame_end
    nEndTime += 1 # Support for looping
    nFrameRate = bpy.context.scene.render.fps
    nTicksPerFrame = TIME_TICKSPERSEC / nFrameRate
    
    mtxHeader = file_def_mtx.MTXHeader()
    
    # We need the store this data in an array to get offsets
    aMTXBones  = []
    aMTXFrames = []
    
    for pbone in obj.pose.bones:
        if SKIP_EXTRA_BONES:
            if not shouldExportBone(pbone): continue

        mtxBone = file_def_mtx.MTXBone()
        mtxBone.szBoneName = pbone.name

        for frameIdx, curFrame in enumerate(range(nStartTime, nEndTime)):
            # Navigate to the frame
            bpy.context.scene.frame_set(curFrame)
            
            # Fill out the struct
            testFrame = file_def_mtx.MTXFrame()

            if frameIdx == 0:
                number_of_ticks = 0.0
            else:
                curFrameTick = float(frameIdx * nTicksPerFrame)
                number_of_ticks = curFrameTick * float( (1.0 / TIME_TICKSPERSEC) )

            testFrame.fStartingSecs = number_of_ticks
            testFrame.mtxOrientation = pasm_math.BObj2F43MtxBONE(pbone)
            
            # Add it to the list
            aMTXFrames.append(testFrame)

            mtxBone.nNumFrames += 1

        aMTXBones.append(mtxBone)
    
    # Now we can fix up our data
    mtxHeader.nNumBones = len(aMTXBones)
    
    # This gets us to the start of the frame data... Length of bytes needs to be divided by 2
    lenHeader = len(file_def_mtx.MTXHeader().packBytes().hex()) / 2
    lenBone   = len(file_def_mtx.MTXBone().packBytes().hex())   / 2
    lenFrame  = len(file_def_mtx.MTXFrame().packBytes().hex())  / 2
    
    offset = lenHeader + mtxHeader.nNumBones * lenBone
    for bone in aMTXBones:
        bone.nFrameArrayOffset = int(offset)

        # Get the offset for the next bone
        offset = offset + (mtxBone.nNumFrames * lenFrame)
        
    # Finally, write data to the file
    g_class.file.write( mtxHeader.packBytes() )
    for bone in aMTXBones:   g_class.file.write( bone.packBytes()  )
    for frame in aMTXFrames: g_class.file.write( frame.packBytes() )
