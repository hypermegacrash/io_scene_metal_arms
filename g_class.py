# This module is for sharing a single instance of data between modules

# FANG TOOLKIT
from . import file_def_ape  # . is the add-on folder directory
from . import bl_info       # For grabbing the Add-On version so we can print it in the exporter menu
# BLENDER
import bpy # We write the filename when writting out the error
# PYTHON
import datetime # We write the time the error occured
import os       # Need the filepath of this file

# GLOBAL VARIABLES
gApeHeader = file_def_ape.PASMHeader() # The header we need to modify by different process_object* modules
file          = None  # The output file that is adjusted by different process_object* modules
errorLogFile  = None  # The error log file that we write errors to from different process_object* modules
fpErrorLog    = os.path.dirname(os.path.realpath(__file__)) + "\\blender_ma_error_log.txt"  # Path to the export file
bShowErrorLog = False # We set this variable when an error occured and we should bring up the .txt file
gd_schema = [] # Gamedata schema

gApeSegments = [] # Ape segments need a copy writting to file for LOD support

# Function for writting a error with metadata to the error log
def logError(str):
    global bShowErrorLog # Grab from the global scope of this file
    bShowErrorLog = True
    errorLogFile.write("\n")
    errorLogFile.write("BLENDER FANG FILE EXPORTER " + bpy.data.filepath + "\n")
    errorLogFile.write("Occured - " + datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y") + "\n")
    errorLogFile.write(str + "\n")
    
# https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
class bcolors:
    HEADER    = '\033[95m'
    OKBLUE    = '\033[94m'
    OKCYAN    = '\033[96m'
    OKGREEN   = '\033[92m'
    WARNING   = '\033[93m'
    FAIL      = '\033[91m'
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'
    
# Special functions for printing colored text to the output terminal
def printOK     (str): print(f"{bcolors.OKBLUE}%s{bcolors.ENDC}"  % (str))
def printWARNING(str): print(f"{bcolors.WARNING}%s{bcolors.ENDC}" % (str))
def printFAIL   (str): print(f"{bcolors.FAIL}%s{bcolors.ENDC}"    % (str))
def printDEBUG  (str): print(f"{bcolors.OKGREEN}%s{bcolors.ENDC}" % (str))

# Footer info we write in the description of every exporter dialog
def writeFooterInfo(layout):
    fileRevision = layout.row()
    fileRevision.label(text = "PASM File Version # 1.5.0")
              
    # This might be the worst thing I've ever wrote
    toolRevision = layout.row()
    strToolRevision = str(bl_info["version"])
    strToolRevision = strToolRevision[1:-1]
    strToolRevision = strToolRevision.replace(",", ".")
    strToolRevision = strToolRevision.replace(" ", "")
    strToolRevision = "MA Toolkit Version # " + strToolRevision
    toolRevision.label(text = strToolRevision)

def getLayerCollection(collection, view_layer=None):
    '''Returns the view layer LayerCollection for a specificied Collection'''
    def scan_children(lc, result=None):
        for c in lc.children:
            if c.collection == collection:
                return c
            result = scan_children(c, result)
        return result

    if view_layer is None:
        view_layer = bpy.context.view_layer
    return scan_children(view_layer.layer_collection)

restoreState = []
vl_colls     = []

def PrepareCollections():
    restoreState.clear()
    vl_colls.clear()
    for coll in bpy.data.collections:
        vl_colls.append(getLayerCollection(coll))

    for coll in vl_colls:
        restoreState.append([coll.exclude, coll.hide_viewport])
        coll.exclude = False
        coll.hide_viewport = False

    bpy.context.evaluated_depsgraph_get().update()

def RestoreCollections():
    for idx, x in enumerate(restoreState):
        vl_colls[idx].exclude = x[0]
        vl_colls[idx].hide_viewport = x[1]