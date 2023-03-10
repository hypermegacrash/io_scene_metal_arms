# Module that processes a camera object and returns byte data

# FANG TOOLKIT
from . import file_def_cam # Get our PASM file classes
from . import g_class      # Get our global variables for the header data
from . import pasm_math    # PASM helper defs
# BLENDER
import bpy # For working with Blender data

def ExportObjCam(obj):
    if obj.name[:4].lower() == "off_":   return # Doesn't matter it's off bail early
    if obj.type             != "CAMERA": # Validate we're working with camera data and not other stuff
        g_class.logError("CAMERA ERROR: The selected object " + obj.name + " is not a camera! Please select a camera and retry exporting.")
        return 
    if obj.name[:4].lower() != "cam_": # Enforce the user to follow naming scheme
        g_class.logError("CAMERA ERROR: The selected camera " + obj.name + " does not contain the cam_ prefix! Please fix and retry exporting.")
        return 
        
    print(obj.name, "is a camera object")

    TIME_TICKSPERSEC = 4800
    
    # Find the animation info from the interface
    nTicksPerFrame = TIME_TICKSPERSEC / 30
    nFrameRate     = bpy.context.scene.render.fps
    nStartTime     = bpy.context.scene.frame_start
    nEndTime       = bpy.context.scene.frame_end
    
    # Calculate the interval and number of keys
    nInterval = (nTicksPerFrame * nFrameRate) / 30;
    
    nKeys = (nEndTime - nStartTime) / nInterval;
    
    camHeader = file_def_cam.PASMCamInfo()
    camHeader.szCameraName = obj.name[4:]
    aFrames = []
    
    # Scrub through the timeline for snapshots we want
    for curFrame in range(nStartTime, nEndTime):
        curFrameTick = curFrame * 160
        bpy.context.scene.frame_set(curFrame)
        testFrame = file_def_cam.PASMCamFrame()
        number_of_ticks = float((curFrameTick - nStartTime)) * float((1.0/TIME_TICKSPERSEC))
        testFrame.fSecsFromStart = number_of_ticks
        testFrame.fFOV = obj.data.angle
        testFrame.mtxOrientation = pasm_math.BObj2F43MtxLIGHT(obj)
        aFrames.append(testFrame)
        
        camHeader.nFrames += 1
        camHeader.nBytesOfUserData += 56
        camHeader.nOffsetToString = camHeader.nBytesOfUserData
    
    # Finally, write data to the file
    g_class.file.write(camHeader.packBytes())
    for frame in aFrames:
        g_class.file.write(frame.packBytes())
    
    
    
    
    