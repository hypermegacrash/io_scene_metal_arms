# Module that processes a object object and returns byte data

import struct # Work with bytes

import bpy # Work with Blender data types
import bmesh # Work with Blender mesh data
import math # Do we use this again?

from . import pasm_file_def # Get our PASM file classes

from . import g_class # Get our global variables for the header data

def ExportObjObject(obj):
    if(obj.name.find("obj_", 0, 4) != -1):
        return None
        
    print(obj.name, "is a object object")
    return None