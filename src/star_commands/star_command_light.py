# Module for parsing Star Commands found in the names of Blender Objects to be exported as a PASM Light

# FANG TOOLKIT
from .star_command_parser     import *
from..defs.file_def_ape_light import PASMLightFlag_e

class CLightStringParser(BaseStarParser):

    ERROR_PREFIX = "LIGHT STAR COMMAND ERROR"

    def __init__(self):
        self.m_ApeLightFlag      = 0
        self.m_fCoronaScale      = 1.0
        self.m_szCoronaTexture   = ""
        self.m_szPerPixelTexture = ""
        self.m_nLightID          = -1
        self.m_nMotifID          = 0
        super().__init__()

    def _set_flag(self, flag):   self.m_ApeLightFlag |= flag
    def _clear_flag(self, flag): self.m_ApeLightFlag &= ~flag

    def cmd_self(self, args):        self._set_flag(PASMLightFlag_e.APE_LIGHT_FLAG_LIGHT_SELF)
    def cmd_castshadows(self, args): self._set_flag(PASMLightFlag_e.APE_LIGHT_FLAG_CAST_SHADOWS)
    def cmd_scalecorona(self, args): self.m_fCoronaScale = self._parse_float(args[0])

    def cmd_fadingcorona(self, args):
        self._set_flag(PASMLightFlag_e.APE_LIGHT_FLAG_CORONA | PASMLightFlag_e.APE_LIGHT_FLAG_CORONA_PROXFADE)
        self.m_szCoronaTexture = args[0]

    def cmd_corona(self, args):
        self._set_flag(PASMLightFlag_e.APE_LIGHT_FLAG_CORONA)
        self.m_szCoronaTexture = args[0]

    def cmd_perpixel(self, args):
        self._set_flag(PASMLightFlag_e.APE_LIGHT_FLAG_PER_PIXEL)

        if len(args) == 1:
            self.m_szPerPixelTexture = args[0]

    def cmd_onlyppmesh(self, args):  self._set_flag(PASMLightFlag_e.APE_LIGHT_FLAG_MESH_MUST_BE_PER_PIXEL)
    def cmd_onlydynamic(self, args): self._set_flag(PASMLightFlag_e.APE_LIGHT_FLAG_DYNAMIC_ONLY)
    def cmd_lm(self, args):          self._set_flag(PASMLightFlag_e.APE_LIGHT_FLAG_LIGHTMAP_LIGHT)

    def cmd_uniquelm(self, args):
        self._clear_flag(PASMLightFlag_e.APE_LIGHT_FLAG_DYNAMIC_ONLY)
        self._set_flag(PASMLightFlag_e.APE_LIGHT_FLAG_UNIQUE_LIGHTMAP | PASMLightFlag_e.APE_LIGHT_FLAG_LIGHTMAP_LIGHT)

    def cmd_onlylm(self, args):
        self._clear_flag(PASMLightFlag_e.APE_LIGHT_FLAG_DYNAMIC_ONLY)
        self._set_flag(PASMLightFlag_e.APE_LIGHT_FLAG_LIGHTMAP_ONLY_LIGHT | PASMLightFlag_e.APE_LIGHT_FLAG_LIGHTMAP_LIGHT)

    def cmd_noterrain(self, args): self._set_flag(PASMLightFlag_e.APE_LIGHT_FLAG_OBJ_DONT_LIGHT_TERRAIN)
    def cmd_id(self, args): self.m_nLightID = self._parse_int(args[0], 0, 0xFFFF)

    def cmd_motif(self, args):
        val = self._parse_int(args[0])
        self.m_nMotifID = val

        if val != 0:
            self._set_flag(PASMLightFlag_e.APE_LIGHT_FLAG_DONT_USE_RGB)

    # ------------------------
    # Command Table
    # ------------------------
    def _build_command_table(self):
        return {
            "self":         Command("self",         0,      self.cmd_self),
            "castshadows":  Command("castshadows",  0,      self.cmd_castshadows),
            "scalecorona":  Command("scalecorona",  1,      self.cmd_scalecorona),
            "fadingcorona": Command("fadingcorona", 1,      self.cmd_fadingcorona),
            "corona":       Command("corona",       1,      self.cmd_corona),
            "perpixel":     Command("perpixel",     [0, 1], self.cmd_perpixel),
            "onlyppmesh":   Command("onlyppmesh",   0,      self.cmd_onlyppmesh),
            "onlydynamic":  Command("onlydynamic",  0,      self.cmd_onlydynamic),
            "lm":           Command("lm",           0,      self.cmd_lm),
            "uniquelm":     Command("uniquelm",     0,      self.cmd_uniquelm),
            "onlylm":       Command("onlylm",       0,      self.cmd_onlylm),
            "noterrain":    Command("noterrain",    0,      self.cmd_noterrain),
            "id":           Command("id",           1,      self.cmd_id),
            "motif":        Command("motif",        1,      self.cmd_motif),
        }