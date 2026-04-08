# Class Definitions for the PASM .cam file format

from .binary_writer import *

@binary_dataclass(slots=True)
class PASMCamHeader(BinaryStruct):
    """Shape in .wld, not standalone .cam file"""
    EXPECTED_SIZE = 16

    fRadius: float = bin_field("f", default=0.0)
    PAD:     bytes = bin_field("12s", default=b"\x00" * 12)

@binary_dataclass(slots=True)
class PASMCamInfo(BinaryStruct):
    EXPECTED_SIZE = 104

    _CAMERA_NAME_LEN = 16

    magic:             bytes = bin_field("4s", default=b"FANG")
    FVersion_Sub:      int   = bin_field("b", default=0)
    FVersion_Minor:    int   = bin_field("b", default=5)
    FVersion_Major:    int   = bin_field("b", default=1)
    FVersion_Platform: int   = bin_field("b", default=8)
    nBytesInFile:      int   = bin_field("i", default=0)
    szCameraName:      str   = str_field(_CAMERA_NAME_LEN, default="")
    nFrames:           int   = bin_field("i", default=0)
    nBytesOfUserData:  int   = bin_field("i", default=0)
    nOffsetToString:   int   = bin_field("i", default=0)
    PAD:               bytes = bin_field("64s", default=b"\x00" * 64)

@binary_dataclass(slots=True)
class PASMCamFrame(BinaryStruct):
    EXPECTED_SIZE = 56

    fSecsFromStart: float       = bin_field("f", default=0.0)
    fFOV:           float       = bin_field("f", default=0.0)
    mtxOrientation: list[float] = array_field("f", 12)
        
        
