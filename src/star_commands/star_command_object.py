# Module for parsing Star Commands found in the names of Blender Objects to be exported as a PASM Object

# FANG TOOLKIT
from .star_command_parser       import *
from ..defs.file_def_ape_object import PASMObjectFlag_e

class CObjectStringParser(BaseStarParser):

    ERROR_PREFIX = "OBJECT STAR COMMAND ERROR"

    def __init__(self):
        self.m_ApeObjectFlag = PASMObjectFlag_e.APE_OB_FLAG_STATIC
        self.m_fCullDist     = 0
        self.m_TintRGB       = [0.0, 0.0, 0.0]
        super().__init__()

    def _set_flag(self, flag):   self.m_ApeObjectFlag |= flag
    def _clear_flag(self, flag): self.m_ApeObjectFlag &= ~flag

    # Command Handlers
    def cmd_postery(self, args):  self._set_flag(PASMObjectFlag_e.APE_OB_FLAG_POSTER_Y)
    def cmd_posterx(self, args):  self._set_flag(PASMObjectFlag_e.APE_OB_FLAG_POSTER_X)
    def cmd_posterz(self, args):  self._set_flag(PASMObjectFlag_e.APE_OB_FLAG_POSTER_Z)
    def cmd_nocoll(self, args):   self._set_flag(PASMObjectFlag_e.APE_OB_FLAG_NO_COLL)
    def cmd_nolight(self, args):  self._set_flag(PASMObjectFlag_e.APE_OB_FLAG_NO_LIGHT)
    def cmd_culldist(self, args): self.m_fCullDist = float(args[0])

    def cmd_tint(self, args):
        r, g, b = [max(0.0, min(float(x), 255.0)) / 255.0 for x in args]
        self.m_TintRGB = [r, g, b]
        self._set_flag(PASMObjectFlag_e.APE_OB_FLAG_TINT)

    def cmd_nodraw(self, args):        self._set_flag(PASMObjectFlag_e.APE_OB_FLAG_NO_DRAW)
    def cmd_acceptlm(self, args):      self._set_flag(PASMObjectFlag_e.APE_OB_FLAG_LM)
    def cmd_vertrad(self, args):       self._set_flag(PASMObjectFlag_e.APE_OB_FLAG_VERT_RADIOSITY)
    def cmd_acceptshadows(self, args): self._set_flag(PASMObjectFlag_e.APE_OB_FLAG_ACCEPT_SHADOWS)
    def cmd_castshadows(self, args):   self._set_flag(PASMObjectFlag_e.APE_OB_FLAG_CAST_SHADOWS)

    def cmd_dynamic(self, args):
        self._clear_flag(PASMObjectFlag_e.APE_OB_FLAG_STATIC)
        self._clear_flag(PASMObjectFlag_e.APE_OB_FLAG_LM)
        self._clear_flag(PASMObjectFlag_e.APE_OB_FLAG_VERT_RADIOSITY)

    def cmd_nolmuse(self, args):
        self._set_flag(PASMObjectFlag_e.APE_OB_FLAG_NO_LM_USE)
        self._clear_flag(PASMObjectFlag_e.APE_OB_FLAG_LM)
        self._clear_flag(PASMObjectFlag_e.APE_OB_FLAG_VERT_RADIOSITY)

    def cmd_lightperpixel(self, args): self._set_flag(PASMObjectFlag_e.APE_OB_FLAG_PER_PIXEL)

    # ------------------------
    # Command Registry
    # ------------------------
    def _build_command_table(self):
        return {
            "postery":       Command("postery",       0, self.cmd_postery),
            "posterx":       Command("posterx",       0, self.cmd_posterx),
            "posterz":       Command("posterz",       0, self.cmd_posterz),
            "nocoll":        Command("nocoll",        0, self.cmd_nocoll),
            "nolight":       Command("nolight",       0, self.cmd_nolight),
            "culldist":      Command("culldist",      1, self.cmd_culldist),
            "tint":          Command("tint",          3, self.cmd_tint),
            "nodraw":        Command("nodraw",        0, self.cmd_nodraw),
            "acceptlm":      Command("acceptlm",      0, self.cmd_acceptlm),
            "vertrad":       Command("vertrad",       0, self.cmd_vertrad),
            "acceptshadows": Command("acceptshadows", 0, self.cmd_acceptshadows),
            "castshadows":   Command("castshadows",   0, self.cmd_castshadows),
            "dynamic":       Command("dynamic",       0, self.cmd_dynamic),
            "nolmuse":       Command("nolmuse",       0, self.cmd_nolmuse),
            "lightperpixel": Command("lightperpixel", 0, self.cmd_lightperpixel),
        }