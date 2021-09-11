# This module is for sharing a single instance of data between modules

# . is the add-on folder directory
from . import pasm_file_def

gWldHeader = pasm_file_def.PASMHeader()

gApeHeader = pasm_file_def.PASMHeader()

# An empty var which will become a output file
file = None