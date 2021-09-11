# Module that processes a shape object and returns byte data

import struct # Work with bytes

import bpy # Work with Blender data types
import bmesh # Work with Blender mesh data
import math # Do we use this again?

from . import pasm_file_def # Get our PASM file classes

from . import g_class # Get our global variables for the header data

from . import pasm_math # Need this for the rotation matrix math

def ExportObjShape(obj):
    if obj.type != "EMPTY":
        return
        
    print(obj.name, "is a shape object")
    
    testShape = pasm_file_def.PASMShape()
    
    if obj.empty_display_type == "CUBE":
        testShape.nType = pasm_file_def.PASMShapeType_e.APE_SHAPE_TYPE_START_POINT
        
    # Rotation Matrix fun
    testShape.mtxOrientation = pasm_math.BRot2FRot(obj)
    
    # Grab custom properties from the object
    if len(obj.keys()) > 1:
        # First item is _RNA_UI
        #print(obj.name,"Custom Properties:")
        for K in obj.keys():
            if K not in '_RNA_UI':
                testShape.userData.append(str(K) + "=" + str(obj[K]))
                #print( K , "=" ,obj[K] )
    
    #print(testShape.userData)
    dataLen = 0
    for data in testShape.userData:
        dataLen = dataLen + len(data)
    #print(dataLen)
    
    testShape.nBytesOfUserData = dataLen
    
    # Finally, write data to the file, and our header
    g_class.file.write(testShape.packBytes())
    g_class.gWldHeader.fileSize += len(testShape.packBytes())
    g_class.gWldHeader.nNumShapes += 1