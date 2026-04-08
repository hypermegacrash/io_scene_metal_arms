# This module is for sharing a single instance of data between modules

# BUILT IN
import datetime
import pathlib
# BLENDER
import bpy
import toml
# FANG TOOLKIT
from ..defs import file_def_ape

# ADD ON
g_SrcDir        = pathlib.Path(__file__).resolve().parent.parent.parent
g_FileLogPath   = g_SrcDir / "blender_ma_error_log.txt"
g_AddonInfoPath = g_SrcDir / "blender_manifest.toml"
g_AddonInfo     = toml.load(g_AddonInfoPath)
# LOGGING
g_FileLog       = None  # The error log file that we write errors to from different process_object* modules
g_ShowErrorLog  = False # We set this variable when an error occured and we should bring up the .txt file
# FANG TOOLKIT
g_FileOut       = None                      # The output file that is adjusted by different process_object* modules
g_GDSchema      = []                        # Gamedata schema
g_ApeHeader     = file_def_ape.PASMHeader() # The header we need to modify by different process_object* modules
g_ApeSegments   = []                        # Ape segments need a copy writting to file for LOD support

# Function for writting a error with metadata to the error log
def logError(str):
    global g_ShowErrorLog # Grab from the global scope of this file
    g_ShowErrorLog = True
    g_FileLog.write("\n")
    g_FileLog.write("BLENDER FANG FILE EXPORTER " + bpy.data.filepath + "\n")
    g_FileLog.write("Occured - " + datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y") + "\n")
    g_FileLog.write(str + "\n")

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