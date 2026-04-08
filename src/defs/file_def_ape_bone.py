# Class Definitions for the PASM Bone Structures within the .ape file format

from .binary_writer import *

@binary_dataclass(slots=True)
class PASMBone(BinaryStruct):
    EXPECTED_SIZE = 176

    _BONE_NAME_LEN          = 32
    _BONE_MAX_CHILD_INDICES = 64

    szBoneName:     str         = str_field(_BONE_NAME_LEN)
    nFlags:         int         = bin_field("i", default=0)
    nBoneIndex:     int         = bin_field("i", default=0)
    nParentIndex:   int         = bin_field("i", default=-1)
    mtxOrientation: list[float] = array_field("f", 12)
    nNumChildren:   int         = bin_field("i", default=0)
    auChildIndices: list[int]   = array_field("b", _BONE_MAX_CHILD_INDICES)
    PAD:            bytes       = bin_field("16s", default=b"\x00" * 16)