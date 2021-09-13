# Module that processes a light object and returns byte data

import struct # Work with bytes

import bpy # Work with Blender data types
import bmesh # Work with Blender mesh data
import math # Do we use this again?

# Light stuff
from mathutils import Euler
from math import radians

from . import pasm_file_def # Get our PASM file classes

from . import g_class # Get our global variables for the header data

from . import pasm_math # Need this for the rotation matrix math

def ExportObjLight(obj):
    if obj.type != "LIGHT":
        return
        
    print(obj.name, "is a light object")

    outLight = pasm_file_def.PASMLight()
    
    if obj.data.type == "SUN":
        outLight.nApeLightType = pasm_file_def.PASMLightType_e.APE_LIGHT_TYPE_DIR
        # Sphere is only filled out for point lights
    elif obj.data.type == "POINT":
        outLight.nApeLightType = pasm_file_def.PASMLightType_e.APE_LIGHT_TYPE_OMNI
    else:
        print("Unsupported or Unknown Light detected")
        return
        
    outLight.szLightName = obj.name
    
    outLight.Color[0] = obj.data.color[0]
    outLight.Color[1] = obj.data.color[1]
    outLight.Color[2] = obj.data.color[2]
    
    #outLight.Intensity = obj.data.energy
    #outLight.Intensity = 1
    outLight.Intensity = obj.data.diffuse_factor
    
    # Flag stuff, this needs to be better
    if obj.name.find("*lm") != -1:
        outLight.nFlags |= pasm_file_def.PASMLightFlag_e.APE_LIGHT_FLAG_LIGHTMAP_LIGHT
    if obj.name.find("*castshadows") != -1:
        outLight.nFlags |= pasm_file_def.PASMLightFlag_e.APE_LIGHT_FLAG_CAST_SHADOWS
    if obj.name.find("*onlylm") != -1:
        #outLight.nFlags |= pasm_file_def.PASMLightFlag_e.APE_LIGHT_FLAG_LIGHTMAP_ONLY_LIGHT
        outLight.nFlags = 48
    
    # Rotation Matrix fun
    outLight.mtxOrientation = pasm_math.BRot2FRot(obj)
    
    if outLight.nApeLightType == pasm_file_def.PASMLightType_e.APE_LIGHT_TYPE_DIR:
        # This is the 3rd row of the rotation matrix
        outLight.Direction[0] =  outLight.mtxOrientation[6]
        outLight.Direction[1] =  outLight.mtxOrientation[7]
        outLight.Direction[2] =  outLight.mtxOrientation[8]
    
    if outLight.nApeLightType == pasm_file_def.PASMLightType_e.APE_LIGHT_TYPE_OMNI:
        # Blender doesn't give a radius of light
        # So we're gonna calculate inverse square law to try and approximate one
        radius = math.sqrt((( obj.data.energy / 0.02) / ( 4 * math.pi )))
        outLight.Sphere[0] = radius
        outLight.Sphere[1] = outLight.mtxOrientation[9]
        outLight.Sphere[2] = outLight.mtxOrientation[10]
        outLight.Sphere[3] = outLight.mtxOrientation[11]

    
    # Finally, write data to the file, and our header
    g_class.file.write(outLight.packBytes())
    g_class.gWldHeader.fileSize += len(outLight.packBytes())
    g_class.gWldHeader.nNumLights += 1
    



