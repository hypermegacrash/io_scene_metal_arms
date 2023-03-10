# Module that processes a fog object and returns byte data
# NOTE: This module is outdated, fog was moved from .wld to level .csv file and deprecated in the PASM2 compiler

# FANG TOOLKIT
from . import file_def_ape  # Get our PASM file classes
from . import g_class       # Get our global variables for the header data

def ExportObjFog(obj):
    if obj.name[:4].lower() == "off_":  return # Doesn't matter it's off bail early
    if obj.type             != "EMPTY": return
    if obj.name[:4].lower() != "fog_":  return # Enforce the user to follow naming scheme
        
    print(obj.name, "is a fog object")
    return None