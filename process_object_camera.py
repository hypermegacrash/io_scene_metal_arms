# Module that processes a camera object and returns byte data

from . import pasm_file_def # Get our PASM file classes

from . import g_class # Get our global variables for the header data

def ExportObjCam(obj):
    # Validate we're working with camera data and not other stuff
    if obj.type != "MESH":
        return
        
    print(obj.name, "is a camera object")
    
    # Finally, write data to the file, and our header
    g_class.file.write(outSegment.packBytes())
    g_class.gWldHeader.fileSize += len(outSegment.packBytes())
    g_class.gWldHeader.nNumSegments += 1