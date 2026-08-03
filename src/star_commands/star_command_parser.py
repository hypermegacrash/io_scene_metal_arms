"""
Star Command Parsing Module
---------------------------

This module provides a lightweight parsing system for "star commands",
a compact inline command syntax embedded in strings.

Star Command Format:
    Commands are prefixed with '*' and may optionally include arguments.

    Examples:
        "*flag"                 -> command with no arguments
        "*anim(2,3.0)"          -> command with arguments

Key Features:
- Regex-based parsing of inline command strings.
- Command dispatch via lookup table (name -> handler).
- Supports fixed or multiple valid argument counts.
- Built-in helpers for parsing ints, floats, and color values.
- Centralized error handling via g_class.logError.

Usage:
    Subclass BaseStarParser and implement `_build_command_table()`:

        class MyParser(BaseStarParser):
            def cmd_example(self, args):
                ...

            def _build_command_table(self):
                return {
                    "example": Command("example", 1, self.cmd_example),
                }

    Then call:
        parser.Parse("foo*example(123)")
"""

# BUILT IN
import re
from typing import Callable, Dict, List, Tuple
# FANG TOOLKIT
from ..process import g_class

# Matches:
#   *command
#   *command(args)
#   *command123   → treated as *command (numeric suffix ignored)
STAR_CMD_PATTERN = re.compile(r"\*([a-zA-Z]+)[0-9]*?(?:\((.*?)\))?")

class Command:
    """
    Represents a single star command definition.

    Attributes:
        name (str): Command name (without '*')
        arg_counts (List[int]): Allowed argument counts
        handler (Callable): Function to execute when command is parsed
    """
    def __init__(self, name: str, arg_counts, handler: Callable):
        self.name:       str       = name
        self.arg_counts: List[int] = ( arg_counts if isinstance(arg_counts, (list, tuple)) else [arg_counts] )
        self.handler:    Callable  = handler

class BaseStarParser:
    """
    Base class for all star command parsers.

    Responsibilities:
    - Extract commands from a string
    - Validate argument counts
    - Dispatch to registered handlers
    - Provide helper parsing utilities
    """

    ERROR_PREFIX = "STAR COMMAND ERROR"

    def __init__(self):
        self._commands: Dict[str, Command] = self._build_command_table()

    def _error_context(self) -> str:
        """Optional subclass context appended to errors."""
        return ""
    
    def _error(self, msg):
        context = self._error_context()

        if context:
            g_class.logError(f"{self.ERROR_PREFIX}: {context}: {msg}")
        else:
            g_class.logError(f"{self.ERROR_PREFIX}: {msg}")

    # Override in subclasses
    def _build_command_table(self) -> Dict[str, Command]:
        """Return dictionary mapping command names to Command objects."""
        return {}

    def _parse_int(self, val: str, min_v=None, max_v=None) -> int:
        v = int(float(val))
        if min_v is not None: v = max(min_v, v)
        if max_v is not None: v = min(max_v, v)
        return v

    def _parse_float(self, val: str, min_v=None, max_v=None) -> float:
        v = float(val)
        if min_v is not None: v = max(min_v, v)
        if max_v is not None: v = min(max_v, v)
        return v

    def _parse_color255(self, args: List[str]) -> List[float]:
        """Convert 0–255 RGB(A) values to normalized 0–1 floats."""
        return [ max(0.0, min(float(x), 255.0)) / 255.0 for x in args ]

    def _parse_commands(self, s: str) -> List[Tuple[str, List[str]]]:
        """
        Extract all star commands from a string.

        Returns:
            List of (command_name, args_list)
        """
        commands = []

        for match in STAR_CMD_PATTERN.finditer(s):
            name = match.group(1).lower()
            params = match.group(2)

            if params:
                params = [p.strip() for p in params.split(",")]
            else:
                params = []

            commands.append((name, params))

        return commands

    def Parse(self, s):
        """Parse a string and execute all contained star commands."""
        for name, args in self._parse_commands(s):
            cmd = self._commands.get(name)

            if not cmd:
                self._error(f"Unknown command '*{name}' in '{s}'")
                continue

            if len(args) not in cmd.arg_counts:
                self._error( f"Command '*{name}' expects {cmd.arg_counts} args but got {len(args)}" )
                continue

            try:
                cmd.handler(args)
            except Exception as e:
                self._error(f"Execution failed for '*{name}' in string {s}: {e}")