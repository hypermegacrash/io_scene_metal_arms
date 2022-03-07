# Module that processes a fog object and returns byte data

from . import pasm_file_def # Get our PASM file classes

from . import g_class # Get our global variables for the header data

def ExportObjFog(obj):
    if obj.type != "EMPTY":
        return
    # Enforce the user to follow naming scheme
    if obj.name[:4].lower() != "fog_":
        return
        
    print(obj.name, "is a fog object")
    return None