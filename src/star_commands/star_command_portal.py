# Module for parsing Star Commands found in the names of Portal Blender Objects

# FANG TOOLKIT
from .star_command_parser       import *
from ..defs.file_def_ape_volume import PASMPortalFlag_e
    
class CPortalStringParser:
    def __init__(self):
        self.m_ApePortalFlag = 0

    def _set_flag(self, flag):   self.m_ApePortalFlag |= flag
    def _clear_flag(self, flag): self.m_ApePortalFlag &= ~flag

    def cmd_mirror(self, args): self._set_flag(PASMPortalFlag_e.APE_PORTAL_FLAG_MIRROR)
    def cmd_sound(self, args):  self._set_flag(PASMPortalFlag_e.APE_PORTAL_FLAG_SOUND_ONLY)
    def cmd_oneway(self, args): self._set_flag(PASMPortalFlag_e.APE_PORTAL_FLAG_ONE_WAY)
    def cmd_anti(self, args):   self._set_flag(PASMPortalFlag_e.APE_PORTAL_FLAG_ANTI)
    
    def _build_command_table(self):
        return {
            "mirror": Command("mirror", 0, self.cmd_mirror),
            "sound":  Command("sound",  0, self.cmd_sound),
            "oneway": Command("oneway", 0, self.cmd_oneway),
            "anti":   Command("anti",   0, self.cmd_anti),
        }