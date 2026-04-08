# Class Definitions for the PASM .ape / .wld file format

from .binary_writer import *

from .file_def_ape_bone   import *
from .file_def_ape_light  import *
from .file_def_ape_mesh   import *
from .file_def_ape_object import *
from .file_def_ape_shape  import *
from .file_def_ape_volume import *

@binary_dataclass(slots=True)
class PASMHeader(BinaryStruct):
    EXPECTED_SIZE = 132

    _HEADER_SCENE_NAME_LEN = 16

    magic:                  bytes = bin_field("4s", default=b"FANG")
    FVersion_Sub:           int   = bin_field("b", default=0)
    FVersion_Minor:         int   = bin_field("b", default=5)
    FVersion_Major:         int   = bin_field("b", default=1)
    FVersion_Platform:      int   = bin_field("b", default=8)
    fileSize:               int   = bin_field("I", default=EXPECTED_SIZE)
    sceneName:              str   = str_field(_HEADER_SCENE_NAME_LEN, default="")
    bWld:                   int   = bin_field("i", default=0)
    nNumBones:              int   = bin_field("h", default=0)
    nNumCells:              int   = bin_field("h", default=0)
    nNumLights:             int   = bin_field("h", default=0)
    nNumVisPortals:         int   = bin_field("h", default=0)
    nNumObjects:            int   = bin_field("h", default=0)
    nNumFogs:               int   = bin_field("h", default=0)
    nNumSegments:           int   = bin_field("h", default=0)
    nNumShapes:             int   = bin_field("h", default=0)
    nSizeOfBoneStruct:      int   = bin_field("h", default=PASMBone.EXPECTED_SIZE)
    nSizeOfLightStruct:     int   = bin_field("h", default=PASMLight.EXPECTED_SIZE)
    nSizeOfObjectStruct:    int   = bin_field("h", default=PASMObjectHeader.EXPECTED_SIZE)
    nSizeOfFogStruct:       int   = bin_field("h", default=44) # Legacy
    nSizeOfSegmentStruct:   int   = bin_field("h", default=PASMSegmentHeader.EXPECTED_SIZE)
    nSizeOfMaterialStruct:  int   = bin_field("h", default=PASMMaterial.EXPECTED_SIZE)
    nSizeOfVertStruct:      int   = bin_field("h", default=PASMVert.EXPECTED_SIZE)
    nSizeOfVertIndexStruct: int   = bin_field("h", default=PASMVertIndex.EXPECTED_SIZE)
    nSizeOfShapeStruct:     int   = bin_field("h", default=PASMShape.EXPECTED_SIZE)
    PAD:                    bytes = bin_field("66s", default=b"\x00" * 66)