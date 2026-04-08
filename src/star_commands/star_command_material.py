# Module for parsing Star Commands found in the names of Blender Materials

# FANG TOOLKIT
from .star_command_parser     import *
from ..defs.file_def_ape      import PASMCommands
from ..defs.file_def_ape_mesh import PASMMaterialFlag_e, PASMMatCollFlag_e, PASMLayerFlag_e
from ..defs.shader_table      import *

_AUTO_ID = -128 # Dont do this, shouldn't this be -1???

_COLL_FLAGS = [
    PASMMatCollFlag_e.APE_MAT_COLL_FLAGS_COLL_WITH_PLAYER,
    PASMMatCollFlag_e.APE_MAT_COLL_FLAGS_COLL_WITH_NPCS,
    PASMMatCollFlag_e.APE_MAT_COLL_FLAGS_OBSTRUCT_LINE_OF_SIGHT,
    PASMMatCollFlag_e.APE_MAT_COLL_FLAGS_COLL_WITH_THIN_PROJECTILES,
    PASMMatCollFlag_e.APE_MAT_COLL_FLAGS_COLL_WITH_THICK_PROJECTILTES,
    PASMMatCollFlag_e.APE_MAT_COLL_FLAGS_COLL_WITH_CAMERA,
    PASMMatCollFlag_e.APE_MAT_COLL_FLAGS_COLL_WITH_OBJECTS,
    PASMMatCollFlag_e.APE_MAT_COLL_FLAGS_WALKABLE,
    PASMMatCollFlag_e.APE_MAT_COLL_FLAGS_OBSTRUCT_SPLASH_DAMAGE,
    PASMMatCollFlag_e.APE_MAT_COLL_FLAGS_COLLIDE_WITH_DEBRIS,
    PASMMatCollFlag_e.APE_MAT_COLL_FLAGS_COLLIDE_WITH_VEHICLES,
    PASMMatCollFlag_e.APE_MAT_COLL_FLAGS_HOVER_COLLIDABLE,
]

class CMaterialStringParser(BaseStarParser):
    def __init__(self):
        self.m_nMatFlags    = PASMMaterialFlag_e.APE_MAT_FLAGS_NONE
        self.m_nAffectAngle = 0
        self.ResetToDefaults()
        super().__init__()

    # This is run before EVERY Material is parsed, it's essentially the default PASMLight.PASMCommands
    def ResetToDefaults(self):
        self.m_TintRGB = [1.0, 1.0, 1.0]

        self.m_ApeCommands                      = PASMCommands()
        self.m_ApeCommands.bUseEmissiveColor    = 1
        self.m_ApeCommands.bUseSpecularColor    = 1
        self.m_ApeCommands.TintRGB              = [1.0, 1.0, 1.0]
        self.m_ApeCommands.nShaderNum           = -1
        self.m_ApeCommands.fBumpMapTileFactor   = 1
        self.m_ApeCommands.fDetailMapTileFactor = 4
        self.m_ApeCommands.nCollMask            = PASMMatCollFlag_e.APE_MAT_COLL_FLAGS_COLL_WITH_EVERYTHING
        self.m_ApeCommands.nReactType           = 0
        self.m_ApeCommands.nSurfaceType         = 0
        self.m_ApeCommands.nID                  = -1

    def cmd_id(self, args):
        val = self._parse_int(args[0])
        if val < 127:
            self.m_ApeCommands.nID = val

    def cmd_collid(self, args): self.m_ApeCommands.nCollID = self._parse_int(args[0], 1, 63)
    def cmd_sort(self, args):   self.m_ApeCommands.bSort = True
    def cmd_order(self, args):  self.m_ApeCommands.nOrderNum = self._parse_int(args[0], 1, 100)

    def cmd_shader(self, args):
        shaderIdx = self._parse_int(args[0])

        if 0 <= shaderIdx < len(SHADER_INFO):
            shader = SHADER_INFO[shaderIdx]

            name       = shader["name"]
            deprecated = shader["deprecated"]
            fallback   = shader["fallback"]

            if not deprecated:
                self.m_ApeCommands.nShaderNum = shaderIdx
            elif fallback is not None:
                fallback_shader = SHADER_INFO[fallback]
                self.m_ApeCommands.nShaderNum = fallback
                self._error( f"Shader {shaderIdx} ({name}) is deprecated. Falling back to {fallback} {fallback_shader['name']}." )
            else:
                self._error( f"Shader {shaderIdx} ({name}) is deprecated and has no fallback. Refer to shader list under MA Toolkit Tab" )
        else:
            self._error( f"Invalid shader index {shaderIdx}. Refer to shader list under MA Toolkit Tab" )

    def cmd_motif(self, args):
        # 6 in the original but only the emissive motif ID is ever actually used.
        val = self._parse_int(args[0])
        if 0 <= val < 65:
            self.m_ApeCommands.nEmissiveMotifID = val
        else:
            self._error("Motif must be between 0–64")

    def cmd_anim(self, args):
        self.m_ApeCommands.nNumTexFrames = self._parse_int(args[0])
        self.m_ApeCommands.fFramesPerSec = self._parse_float(args[1])
        
        # AUTO ID
        if( self.m_ApeCommands.nID == -1 ): self.m_ApeCommands.nID = _AUTO_ID

    def cmd_rotate(self, args):
        self.m_ApeCommands.fDeltaUVRotationPerSec = self._parse_float(args[0])
        self.m_ApeCommands.vRotateUVAround[0]     = self._parse_float(args[1])
        self.m_ApeCommands.vRotateUVAround[1]     = self._parse_float(args[2])

        # AUTO ID
        if( self.m_ApeCommands.nID == -1 ): self.m_ApeCommands.nID = _AUTO_ID

    def cmd_scroll(self, args):
        fXDirection, fXSpeed, fYDirection, fYSpeed = [float(x) for x in args]

        if fXDirection != 0.0 and fXSpeed != 0.0: self.m_ApeCommands.fDeltaUPerSec = fXDirection / fXSpeed
        if fYDirection != 0.0 and fYSpeed != 0.0: self.m_ApeCommands.fDeltaVPerSec = fYDirection / fYSpeed

        # AUTO ID
        if self.m_ApeCommands.nID == -1: self.m_ApeCommands.nID = _AUTO_ID

    def cmd_z(self, args):       self.m_ApeCommands.nZTugValue = self._parse_int(args[0], 1, 1000)
    def cmd_nocoll(self, args):  self.m_ApeCommands.bNoColl = True

    def cmd_coll(self, args):
        for i, flag in enumerate(_COLL_FLAGS):
            enabled = self._parse_int(args[i]) == 1
            if enabled:
                self.m_ApeCommands.nCollMask |= flag
            else:
                self.m_ApeCommands.nCollMask &= ~flag

    def cmd_noascroll(self, args):  self.m_nMatFlags          |= PASMLayerFlag_e.APE_LAYER_FLAGS_NO_ALPHA_SCROLL
    def cmd_tint(self, args):       self.m_ApeCommands.nFlags |= PASMMaterialFlag_e.APE_MAT_FLAGS_APPLY_TINT
    def cmd_writez(self, args):     self.m_ApeCommands.nFlags |= PASMMaterialFlag_e.APE_MAT_FLAGS_ZWRITE_ON
    def cmd_nomeshtint(self, args): self.m_ApeCommands.nFlags |= PASMMaterialFlag_e.APE_MAT_FLAGS_DO_NOT_TINT
    def cmd_bumptile(self, args):   self.m_ApeCommands.fBumpMapTileFactor   = self._parse_float(args[0])
    def cmd_detailtile(self, args): self.m_ApeCommands.fDetailMapTileFactor = self._parse_float(args[0])
    def cmd_light(self, args):      self.m_ApeCommands.LightRGBI = self._parse_color255(args)
    def cmd_nodraw(self, args):     self.m_ApeCommands.nFlags |= PASMMaterialFlag_e.APE_MAT_FLAGS_NO_DRAW  
    def cmd_notinlm(self, args):    self.m_ApeCommands.nFlags |= PASMMaterialFlag_e.APE_MAT_FLAGS_DO_NOT_LM  
    def cmd_nolmblock(self, args):  self.m_ApeCommands.nFlags |= PASMMaterialFlag_e.APE_MAT_FLAGS_DO_NOT_BLOCK_LM  
    def cmd_nolmuse(self, args):    self.m_ApeCommands.nFlags |= PASMMaterialFlag_e.APE_MAT_FLAGS_NO_LM_USE  
    def cmd_vertrad(self, args):    self.m_ApeCommands.nFlags |= PASMMaterialFlag_e.APE_MAT_FLAGS_VERT_RADIOSITY|PASMMaterialFlag_e.APE_MAT_FLAGS_DO_NOT_LM   
    def cmd_noshadows(self, args):  self.m_nMatFlags |= PASMLayerFlag_e.APE_LAYER_FLAGS_DO_NOT_CAST_SHADOWS

    def cmd_eangle(self, args):  
        self.m_nAffectAngle = self._parse_int(args[0], 0, 180)
        self.m_nMatFlags |= PASMLayerFlag_e.APE_LAYER_FLAGS_ANGULAR_EMISSIVE

    def cmd_tangle(self, args):  
        self.m_nAffectAngle = self._parse_int(args[0], 0, 180)
        self.m_nMatFlags |= PASMLayerFlag_e.APE_LAYER_FLAGS_ANGULAR_TRANSLUCENCY

    def cmd_surf(self, args):  self.m_ApeCommands.nSurfaceType = self._parse_int(args[0], 0, 15)
    def cmd_react(self, args): self.m_ApeCommands.nReactType   = self._parse_int(args[0], 0, 7)

    def _build_command_table(self):
        return {
            "id":         Command("id",         1,  self.cmd_id),
            "collid":     Command("collid",     1,  self.cmd_collid),
            "sort":       Command("sort",       0,  self.cmd_sort),
            "order":      Command("order",      1,  self.cmd_order),
            "shader":     Command("shader",     1,  self.cmd_shader),
            "motif":      Command("motif",      1,  self.cmd_motif),
            "anim":       Command("anim",       2,  self.cmd_anim),
            "rotate":     Command("rotate",     3,  self.cmd_rotate),
            "scroll":     Command("scroll",     4,  self.cmd_scroll),
            "z":          Command("z",          1,  self.cmd_z),
            "nocoll":     Command("nocoll",     0,  self.cmd_nocoll),
            "coll":       Command("coll",       12, self.cmd_coll),
            "noascroll":  Command("noascroll",  0,  self.cmd_noascroll),
            "tint":       Command("tint",       0,  self.cmd_tint),
            "writez":     Command("writez",     0,  self.cmd_writez),
            "nomeshtint": Command("nomeshtint", 0,  self.cmd_nomeshtint),
            "bumptile":   Command("bumptile",   1,  self.cmd_bumptile),
            "detailtile": Command("detailtile", 1,  self.cmd_detailtile),
            "light":      Command("light",      4,  self.cmd_light),
            "nodraw":     Command("nodraw",     0,  self.cmd_nodraw),
            "notinlm":    Command("notinlm",    0,  self.cmd_notinlm),
            "nolmblock":  Command("nolmblock",  0,  self.cmd_nolmblock),
            "nolmuse":    Command("nolmuse",    0,  self.cmd_nolmuse),
            "vertrad":    Command("vertrad",    0,  self.cmd_vertrad),
            "noshadows":  Command("noshadows",  0,  self.cmd_noshadows),
            "eangle":     Command("eangle",     1,  self.cmd_eangle),
            "tangle":     Command("tangle",     1,  self.cmd_tangle),
            "surf":       Command("surf",       1,  self.cmd_surf),
            "react":      Command("react",      1,  self.cmd_react), 
        }