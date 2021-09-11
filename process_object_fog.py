# Module that processes a fog object and returns byte data

import struct # Work with bytes

import bpy # Work with Blender data types
import bmesh # Work with Blender mesh data
import math # Do we use this again?

from . import pasm_file_def # Get our PASM file classes

from . import g_class # Get our global variables for the header data

def ExportObjFog(obj):
    if obj.type != "EMPTY":
        return
    if(obj.name.find("fog_", 0, 4) == -1):
        return None
        
    print(obj.name, "is a fog object")
    return None