# Module that processes an object object and returns byte data

# FANG TOOLKIT
from . import file_def_ape  # Get our PASM file classes
from . import g_class       # Get our global variables for the header data
from . import pasm_math     # PASM helper defs
from .process_star_command import CObjectStringParser # Import just the Material Star Command Parser
from .process_gamedata     import ProcessGamedata     # Import just the Gmaedata Parser

def ExportObjObject(obj):
    if obj.name[:4].lower() == "off_": return # Doesn't matter it's off bail early
    if obj.name[:4].lower() != "obj_": return # No prefix no object
        
    print(obj.name, "is a object object")
    
    outObject = file_def_ape.PASMObject()
    
    # Prepare object name by ripping off obj_ prefix and reading only up until first .
    outName = obj.name.lower()[4:]
    outName = outName.split(".",1)[0]
    
    outObject.szObjectName = outName
    
    # Parse object name for star commands
    objStrParser = CObjectStringParser()
    objStrParser.Parse(obj.name.lower())
    outObject.nFlags = objStrParser.m_ApeObjectFlag
    outObject.TintRGB[0] = objStrParser.m_TintRGB[0]
    outObject.TintRGB[1] = objStrParser.m_TintRGB[1]
    outObject.TintRGB[2] = objStrParser.m_TintRGB[2]
    
    outObject.mtxOrientation = pasm_math.BObj2F43Mtx(obj)
    
    ProcessGamedata(obj, outObject)
                        
    # Finally, write data to the file, and our header
    g_class.file.write(outObject.packBytes())
    g_class.gApeHeader.fileSize += len(outObject.packBytes())
    g_class.gApeHeader.nNumObjects += 1