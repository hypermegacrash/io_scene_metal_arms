"""
BinaryStruct Export Module
--------------------------

Module for defining dataclasses that can be
converted into packed binary data.

Usage:
    @binary_dataclass(slots=True)
    class Header(BinaryStruct):
        magic: bytes = bin_field("4s", default=b"DATA")
        version: int = bin_field("I", default=1)

    header = Header()
    binary_data = header.pack()
"""

# BUILT IN
from dataclasses import dataclass, field, fields
import struct

# Field Descriptors - factory functions that create dataclass fields with metadata describing how to pack them

def bin_field(fmt: str, *, encoder=None, default=0):
    return field(default=default, metadata={
        "fmt": fmt,
        "encoder": encoder,
    })

# Encode a string as UTF-8, truncate to size-1 bytes and null pad to exactly `size` bytes.
def _padded_utf8_encoder(size: int):
    def encode(val: str) -> bytes:
        return val.encode("utf-8")[: size - 1].ljust(size, b"\x00")

    return encode

def str_field(size: int, default: str = ""):
    return bin_field(
        f"{size}s",
        encoder=_padded_utf8_encoder(size),
        default=default,
    )

def fixed_str_array_field(count: int, size: int):
    encode_one = _padded_utf8_encoder(size)

    def encoder(vals: list[str]) -> bytes:
        if len(vals) != count:
            raise ValueError(f"Expected {count} strings, got {len(vals)}")

        return b"".join(encode_one(s) for s in vals)

    total_size = count * size

    return field(
        default_factory=lambda: [""] * count,
        metadata={
            "fmt": f"{total_size}s",
            "encoder": encoder,
        },
    )

def vec2_array_field(count: int):
    def encoder(vals):
        if len(vals) != count:
            raise ValueError(f"Expected {count} vec2s, got {len(vals)}")

        flat = []
        for v in vals:
            if len(v) != 2:
                raise ValueError("Each vec2 must have 2 components")
            flat.extend(v)

        return struct.pack(f"<{count * 2}f", *flat)

    return field(default_factory=lambda: [[0.0, 0.0] for _ in range(count)], metadata={
        "fmt": f"{count * 2 * 4}s",  # 4 bytes per float
        "encoder": encoder,
    })

def struct_field(struct_cls):
    def encode(val):
        if not isinstance(val, struct_cls):
            raise TypeError(f"Expected {struct_cls.__name__}, got {type(val).__name__}")
        return val.pack()

    return field(default_factory=struct_cls, metadata={
        "fmt": None,
        "encoder": encode,
        "nested": struct_cls,
    })

def array_field(fmt: str, count: int, *, default=None):
    full_fmt = f"{count}{fmt}"

    def encoder(vals):
        if len(vals) != count:
            raise ValueError(f"Expected {count} items, got {len(vals)}")

        packed = struct.pack(f"<{full_fmt}", *vals)

        return bytes(packed)

    if default is None:
        default = lambda: [0] * count

    return field(default_factory=default, metadata={
        "fmt": full_fmt,
        "encoder": None,
        "array_encoder": encoder,
    })

def struct_array_field(struct_cls, count: int, *, zero_bytes: bytes):
    def encoder(vals):
        if len(vals) != count:
            raise ValueError(f"Expected {count} items, got {len(vals)}")

        out = bytearray()

        for v in vals:
            if v is None:
                out += zero_bytes
            else:
                if not isinstance(v, struct_cls):
                    raise TypeError(
                        f"Expected {struct_cls.__name__}, got {type(v).__name__}"
                    )
                out += v.pack()

        return bytes(out)

    return field(default_factory=lambda: [None] * count, metadata={
        "fmt":          None,
        "encoder":      encoder,
        "struct_array": struct_cls,
        "count":        count,
        "zero":         zero_bytes,
    })

# Base Class - All binary-exporting classes inherit from it.

class BinaryStruct:
    __slots__     = ()   # Slots so we don't accidentally write non defined struct data
    _STRUCT       = None # Cached struct.Struct object for packing
    _ENDIAN       = "<"  # Default little-endian
    EXPECTED_SIZE = None # Set by inherited classes to validate structure size

    @classmethod
    def _build_struct(cls):
        """Build a struct.Struct object based on the dataclass fields."""
        fmt = [cls._ENDIAN]

        for f in fields(cls):
            field_fmt = f.metadata["fmt"]

            # nested struct
            if field_fmt is None and "nested" in f.metadata:
                nested = f.metadata["nested"]

                if nested._STRUCT is None:
                    nested._validate_and_cache_struct()

                field_fmt = f"{nested._STRUCT.size}s"

            # struct array
            elif field_fmt is None and "struct_array" in f.metadata:
                struct_cls = f.metadata["struct_array"]
                count = f.metadata["count"]

                if struct_cls._STRUCT is None:
                    struct_cls._validate_and_cache_struct()

                size = struct_cls._STRUCT.size * count
                field_fmt = f"{size}s"

            # array field
            elif "array_encoder" in f.metadata:
                size = struct.calcsize(cls._ENDIAN + field_fmt)
                field_fmt = f"{size}s"

            # error
            elif field_fmt is None:
                raise ValueError(f"{f.name} missing fmt")

            fmt.append(field_fmt)

        return struct.Struct("".join(fmt))

    @classmethod
    def _validate_and_cache_struct(cls):
        """
        Builds and caches the struct.
        Validates against EXPECTED_SIZE if provided.
        """
        s = cls._build_struct()

        if cls.EXPECTED_SIZE is not None and s.size != cls.EXPECTED_SIZE:
            raise ValueError(
                f"{cls.__name__} size mismatch:\n"
                f"  expected: {cls.EXPECTED_SIZE}\n"
                f"  actual:   {s.size}\n"
                f"  format:   {s.format}"
            )

        cls._STRUCT = s
    
    def pack(self) -> bytes:
        """
        Converts the instance into a packed byte array.
        Uses encoders for nested structs and arrays.
        """
        if self._STRUCT is None:
            raise RuntimeError( f"{type(self).__name__} is not initialized (missing @binary_dataclass?)" )

        values = []

        for f in fields(self):
            val = getattr(self, f.name)

            array_encoder = f.metadata.get("array_encoder")
            if array_encoder:
                values.append(array_encoder(val))
                continue

            encoder = f.metadata.get("encoder")
            if encoder:
                val = encoder(val)

            values.append(val)

        return self._STRUCT.pack(*values)

def binary_dataclass(*args, **kwargs):
    """
    Wraps @dataclass and validates BinaryStructs.
    Ensures _STRUCT is initialized immediately.
    """
    def wrapper(cls):
        cls = dataclass(*args, **kwargs)(cls)

        if issubclass(cls, BinaryStruct):
            cls._validate_and_cache_struct()

        return cls

    return wrapper