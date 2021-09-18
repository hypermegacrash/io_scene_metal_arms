# Module that processes an object object and returns byte data

from . import pasm_file_def # Get our PASM file classes

from . import g_class # Get our global variables for the header data

from . import pasm_math # PASM helper defs

def ExportObjObject(obj):
    if(obj.name.find("obj_", 0, 4) == -1):
        return
        
    print(obj.name, "is a object object")
    
    outObject = pasm_file_def.PASMObject()
    
    # Prepare object name by ripping off obj_ prefix and reading only up until first .
    outName = obj.name.lower()[4:]
    outName = outName.split(".",1)[0]
    
    outObject.szObjectName = outName
    
    # Hard coded flag to this but there are alot more to consider in the future
    outObject.nFlags = 1
    
    outObject.mtxOrientation = pasm_math.BObj2F43Mtx(obj)
          
    # Grab custom properties from the object
    if len(obj.keys()) > 1:
        # First item is _RNA_UI
        index = 2
        for K in obj.keys():        
            if K not in '_RNA_UI':
                outObject.userData.append(str(K) + "=" + str(obj[K]))
                if index < len(obj.keys()):
                    index += 1
                    outObject.userData.append(str('\x0D\x0A'))
     
    # Go back and patch up userData length
    dataLen = 0
    for data in outObject.userData:
        dataLen = dataLen + len(data)
    outObject.nBytesOfUserData = dataLen
                        
    # Finally, write data to the file, and our header
    g_class.file.write(outObject.packBytes())
    g_class.gWldHeader.fileSize += len(outObject.packBytes())
    g_class.gWldHeader.nNumObjects += 1