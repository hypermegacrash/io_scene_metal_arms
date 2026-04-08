# Class Definitions for the PASM .mtx file format

from .binary_writer import *

@binary_dataclass(slots=True)
class MTXHeader(BinaryStruct):
    EXPECTED_SIZE = 8

    nNumBones: int = bin_field("i", default=0)
    nDataType: int = bin_field("i", default=0)

@binary_dataclass(slots=True)
class MTXBone(BinaryStruct):
    """Bone with all offsets to their orientations"""
    EXPECTED_SIZE = 40

    szBoneName:        str = str_field(32, default="")
    nNumFrames:        int = bin_field("i", default=0)
    nFrameArrayOffset: int = bin_field("i", default=0)

@binary_dataclass(slots=True)
class MTXFrame(BinaryStruct):
    """Matrix data for x bone at y time from first frame"""
    EXPECTED_SIZE = 52

    fStartingSecs:  float       = bin_field("f", default=0.0)
    mtxOrientation: list[float] = array_field("f", 12)