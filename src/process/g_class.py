# This module is for sharing a single instance of data between modules

# BUILT IN
import pathlib
# BLENDER
import tomllib
# FANG TOOLKIT
from ..defs import file_def_ape

# ADD ON
g_SrcDir        = pathlib.Path(__file__).resolve().parent.parent.parent
g_AddonInfoPath = g_SrcDir / "blender_manifest.toml"
with open(g_AddonInfoPath, "rb") as f:
    g_AddonInfo = tomllib.load(f)
# FANG TOOLKIT
g_FileOut       = None                      # The output file that is adjusted by different process_object* modules
g_GDSchema      = []                        # Gamedata schema
g_ApeHeader     = file_def_ape.PASMHeader() # The header we need to modify by different process_object* modules
g_ApeSegments   = []                        # Ape segments need a copy writting to file for LOD support

# LOGGING
g_Logger        = None

def logError(message: str):
    g_Logger.log_error(message)