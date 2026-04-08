# Module that processes a camera object and returns byte data

# FANG TOOLKIT
from ..defs import file_def_cam
from . import g_class
from . import pasm_math
# BLENDER
import bpy

TIME_TICKSPERSEC     = 4800
FRAME_USERDATA_BYTES = 56

def ExportObjCam(obj):
    if obj.name[:4].lower() == "off_": return # Doesn't matter it's off bail early
    if obj.type             != "CAMERA": # Validate we're working with camera data and not other stuff
        g_class.logError(
            f"CAMERA ERROR: The selected object {obj.name} is not a camera! "
            "Please select a camera and retry exporting."
        )
        return 
    if obj.name[:4].lower() != "cam_": # Enforce the user to follow naming scheme
        g_class.logError(
            f"CAMERA ERROR: The selected camera {obj.name} does not contain the cam_ prefix! "
            "Please fix and retry exporting."
        )
        return 
    
    # Find the animation info from the interface
    scene            = bpy.context.scene
    start_frame      = scene.frame_start
    end_frame        = scene.frame_end
    fps              = scene.render.fps
    seconds_per_tick = float( (1.0 / TIME_TICKSPERSEC ) )
    ticks_per_frame  = TIME_TICKSPERSEC / fps
    start_tick       = start_frame * ticks_per_frame
    
    camHeader              = file_def_cam.PASMCamInfo()
    camHeader.szCameraName = obj.name[4:]
    aFrames                = []
    
    # Scrub through the timeline for snapshots we want
    for frame in range(start_frame, end_frame):
        # Navigate to the frame
        scene.frame_set(frame)

        frame_tick = frame * ticks_per_frame

        # Fill out the struct
        camFrame = file_def_cam.PASMCamFrame()
        if frame == start_frame: secs_from_start = 0.0
        else:                    secs_from_start = (frame_tick - start_tick) * seconds_per_tick

        camFrame.fSecsFromStart = secs_from_start
        camFrame.fFOV           = obj.data.angle
        camFrame.mtxOrientation = pasm_math.BObj2F43MtxLIGHT(obj)

        aFrames.append(camFrame)
        
    camHeader.nFrames = len(aFrames)
    camHeader.nBytesOfUserData = FRAME_USERDATA_BYTES * camHeader.nFrames
    camHeader.nOffsetToString = camHeader.nBytesOfUserData
    
    # Finally, write data to the file
    g_class.g_FileOut.write(camHeader.pack())
    for frame in aFrames:
        g_class.g_FileOut.write(frame.pack())