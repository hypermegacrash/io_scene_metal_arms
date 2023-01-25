# Module for processing the action of an armature for exporting

# FANG TOOLKIT
from . import file_def_mtx # Get our PASM file classes
from . import g_class      # Get our global variables for the header data
from . import pasm_math    # PASM helper defs
# BLENDER
import struct              # For modifying vars into bytes
import mathutils           # Need to work with matrix math
import bpy                 # For working with Blender data

def ExportObjAnim(obj):
    # NOTE: Shhhhhh, we're gonna export bones with off_ for the moment b/c bone hierarchy hard
    #if obj.name[:4].lower() == "off_":     return # Doesn't matter it's off bail early
    if obj.type             != "ARMATURE": return # Validate we're working with armature animation data

    print(obj.name, "is an armature object")

    TIME_TICKSPERSEC = 4800 # Constant ripped from Max SDK Docs
    
    # Find the animation info from the interface
    nStartTime = bpy.context.scene.frame_start
    nEndTime   = bpy.context.scene.frame_end
    nFrameRate = bpy.context.scene.render.fps
    nTicksPerFrame = TIME_TICKSPERSEC / nFrameRate #nTicksPerFrame = TIME_TICKSPERSEC / 30
    
    # Calculate the interval and number of keys
    nInterval = (nTicksPerFrame * nFrameRate) / 30;
    
    nKeys = (nEndTime - nStartTime) / nInterval;
    
    #print("nFrameRate: ", nFrameRate)
    #print("nStartTime: ", nStartTime)
    #print("nEndTime: ", nEndTime)
    #print("CurrentAction: ", obj.animation_data.action)
    
    mtxHeader = file_def_mtx.MTXHeader()
    
    # We need the store this data in an array to get offsets
    aMTXBones  = []
    aMTXFrames = []
    
    for pbone in obj.pose.bones:
        mtxBone = file_def_mtx.MTXBone()
        mtxBone.szBoneName = pbone.name
        # We're exporting every frame rather than the individual keyframes
        mtxBone.nNumFrames = nEndTime - nStartTime
        aMTXBones.append(mtxBone)
        
        for curFrame in range(nStartTime, nEndTime):
            # Navigate to the frame
            curFrameTick = curFrame * nTicksPerFrame #curFrameTick = curFrame * 160
            bpy.context.scene.frame_set(curFrame)
            
            # Fill out the struct
            testFrame = file_def_mtx.MTXFrame()
            if curFrame == nStartTime:
                number_of_ticks = 0.0
            else:
                number_of_ticks = float((curFrameTick - nStartTime) - (1 * nTicksPerFrame)) * float((1.0/TIME_TICKSPERSEC)) #number_of_ticks = float((curFrameTick - nStartTime)) * float((1.0/TIME_TICKSPERSEC))
            testFrame.fStartingSecs = number_of_ticks
            testFrame.mtxOrientation = pasm_math.BObj2F43MtxBONE(pbone)
            
            # Add it to the list
            aMTXFrames.append(testFrame)
            
    #print(len(aMTXBones))  # Just number of bones
    #print(len(aMTXFrames)) # (Frames + 1) * number of bones
    
    # Now we can fix up our data
    mtxHeader.nNumBones = len(aMTXBones)
    
    index = 0
    for bone in aMTXBones:
        # This gets us to the start of the frame data... Length of bytes needs to be divided by 2
        offset = (len(mtxHeader.packBytes().hex()) / 2) + len(aMTXBones) * (len(mtxBone.packBytes().hex()) / 2)
        # WTF is this??? We should be itterating over the bones and getting the length of their frames not
        #assuming the length is always the length of the animation!!!
        offset = offset + (((nEndTime - nStartTime) * index) * (len(testFrame.packBytes().hex()) / 2))
        offset = int(offset)
        bone.nFrameArrayOffset = offset
        index += 1
    
    # Finally, write data to the file
    g_class.file.write( mtxHeader.packBytes() )
    for x in aMTXBones:
        g_class.file.write( x.packBytes() )
    for x in aMTXFrames:
        g_class.file.write( x.packBytes() )
