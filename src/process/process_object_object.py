# Module that processes an object object and returns byte data

# FANG TOOLKIT
from ..defs import file_def_ape_object
from . import g_class
from . import pasm_math
from ..star_commands.star_command_object import CObjectStringParser
from .process_gamedata import ProcessGamedata

def ExportObjObject(obj):
    if obj.name[:4].lower() == "off_": return # Doesn't matter it's off bail early
    if obj.name[:4].lower() != "obj_": return # No prefix no object

    if round(obj.scale.x, 5) != round(obj.scale.y, 5) != round(obj.scale.z, 5):
        if obj.empty_display_type != "CUBE":
            g_class.logError(f"OBJECT ERROR: The object object {obj.name} does not have a uniform scale! Found {obj.scale[0]:.3f}, {obj.scale[1]:.3f}, {obj.scale[2]:.3f}... Skipping")
            return
    
    outObject = file_def_ape_object.PASMObject()
    
    # Prepare object name by ripping off obj_ prefix and reading only up until first .
    outName = obj.name.lower()[4:]
    outName = outName.split(".",1)[0]
    
    outObject.header.szObjectName = outName
    
    # Parse object name for star commands
    objStrParser = CObjectStringParser()
    objStrParser.Parse(obj.name.lower())
    outObject.header.nFlags = objStrParser.m_ApeObjectFlag
    outObject.header.TintRGB[0] = objStrParser.m_TintRGB[0]
    outObject.header.TintRGB[1] = objStrParser.m_TintRGB[1]
    outObject.header.TintRGB[2] = objStrParser.m_TintRGB[2]
    
    outObject.header.mtxOrientation = pasm_math.BObj2F43Mtx(obj)
    
    ProcessGamedata(obj, "MeshEntity", outObject)

    # Go back and patch up userData length
    dataLen = 0
    for data in outObject.userData:
        if type(data) == float:
            dataLen = dataLen + 4
        else:
            dataLen = dataLen + len(data)
    outObject.header.nBytesOfUserData = dataLen
                        
    # Finally, write data to the file
    data = outObject.pack()
    g_class.g_FileOut.write(data)
    g_class.g_ApeHeader.fileSize += len(data)
    g_class.g_ApeHeader.nNumObjects += 1