
import struct # For modifying vars into bytes

import mathutils # Need to work with matrix math

from . import file_def_mtx # Get our PASM file classes

from . import g_class # Get our global variables for the header data

from . import pasm_math  # PASM helper defs

import bpy # For working with Blender data

def ExportObjAnim(obj):
     # Validate we're working with animation data and not other stuff
    if obj.type != "ARMATURE":
        return

    print(obj.name, "is an armature object")

    TIME_TICKSPERSEC = 4800 # Constant ripped from Max SDK Docs
    
    # Find the animation info from the interface
    nTicksPerFrame = TIME_TICKSPERSEC / 30
    nFrameRate = bpy.context.scene.render.fps
    nStartTime = bpy.context.scene.frame_start
    nEndTime = bpy.context.scene.frame_end
    
    # Calculate the interval and number of keys
    nInterval = (nTicksPerFrame * nFrameRate) / 30;
    
    nKeys = (nEndTime - nStartTime) / nInterval;
    
    #print("nFrameRate: ", nFrameRate)
    #print("nStartTime: ", nStartTime)
    #print("nEndTime: ", nEndTime)
    #print("CurrentAction: ", obj.animation_data.action)
    
    mtxHeader = file_def_mtx.MTXHeader()
    
    # We need the store this data in an array to get offsets
    aMTXBones = []
    aMTXFrames = []
    
    for pbone in obj.pose.bones:
        mtxBone = file_def_mtx.MTXBone()
        mtxBone.szBoneName = pbone.name
        # We're exporting every frame rather than the individual keyframes
        mtxBone.nNumFrames = nEndTime - nStartTime
        aMTXBones.append(mtxBone)
        
        # Our bind pose is the first frame of animation
        bpy.context.scene.frame_set(nStartTime)
        bindPose = pasm_math.BObj2F43MtxBONE(pbone)
        # Our first frame of animation could also have a keyframe applied
        bindFrame = [0.0 for i in range(3)]
        bindPose[9] = bindPose[9] + pbone.location[0]
        bindPose[10] = bindPose[10] + pbone.location[2]
        bindPose[11] = bindPose[11] + pbone.location[1]
        bindFrame[0] = pbone.location[0]
        bindFrame[1] = pbone.location[1]
        bindFrame[2] = pbone.location[2]
        
        for curFrame in range(nStartTime, nEndTime):
            curFrameTick = curFrame * 160
            bpy.context.scene.frame_set(curFrame)
            testFrame = file_def_mtx.MTXFrame()
            number_of_ticks = float((curFrameTick - nStartTime)) * float((1.0/TIME_TICKSPERSEC))
            testFrame.fStartingSecs = number_of_ticks
            testFrame.mtxOrientation = pasm_math.BObj2F43MtxBONE(pbone)
            
            # The bones positions is an offset from inital frame
            # In addition to respecting offset from parent bone
            testFrame.mtxOrientation[9] = bindPose[9] + (bindFrame[0] - pbone.location[0])
            testFrame.mtxOrientation[10] = bindPose[10] + (bindFrame[2] - pbone.location[2])
            testFrame.mtxOrientation[11] = bindPose[11] + (bindFrame[1] - pbone.location[1])
            
            aMTXFrames.append(testFrame)
            
    #print(len(aMTXBones)) # Just number of bones
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
        
        
        
        