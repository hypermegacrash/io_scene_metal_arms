# Module that processes an object object and returns byte data

# FANG TOOLKIT
from . import pasm_file_def # Get our PASM file classes
from . import g_class       # Get our global variables for the header data
from . import pasm_math     # PASM helper defs
from .process_star_command import CObjectStringParser # Import just the Material Star Command Parser

def ExportObjObject(obj):
    if obj.name[:4].lower() == "off_": return # Doesn't matter it's off bail early
    if obj.name[:4].lower() != "obj_": return # No prefix no object
        
    print(obj.name, "is a object object")
    
    outObject = pasm_file_def.PASMObject()
    
    # Prepare object name by ripping off obj_ prefix and reading only up until first .
    outName = obj.name.lower()[4:]
    outName = outName.split(".",1)[0]
    
    outObject.szObjectName = outName
    
    # Hard coded flag to this but there are alot more to consider in the future
    outObject.nFlags = 1
    
    # Parse object name for star commands
    objStrParser = CObjectStringParser()       
    objStrParser.Parse(obj.name.lower())
    outObject.nFlags += objStrParser.m_ApeObjectFlag
    
    outObject.mtxOrientation = pasm_math.BObj2F43MtxSCALE(obj)
    
    # Grab custom properties from the object
    try:
        cmds = obj["ma"].split('\n')
        x = 0
        for index in cmds: 
            x += 1
            a = index.find("=")
            i = a - 1
            j = a + 1
            while index[i] == " ":
                i = i - 1
            while index[j] == " ":
                j = j + 1
            outObject.userData.append(index[:i + 1] + "=" + index[j:])
            if x < len(cmds):
                outObject.userData.append(str('\x0D\x0A'))
    except:
        print("No Custom Properties")
     
    # Go back and patch up userData length
    dataLen = 0
    for data in outObject.userData:
        dataLen = dataLen + len(data)
    outObject.nBytesOfUserData = dataLen
                        
    # Finally, write data to the file, and our header
    g_class.file.write(outObject.packBytes())
    g_class.gWldHeader.fileSize += len(outObject.packBytes())
    g_class.gWldHeader.nNumObjects += 1