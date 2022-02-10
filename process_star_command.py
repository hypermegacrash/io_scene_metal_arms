# Module that provides classes for processing Star Commands found in the name of Material, Object and Lights

from .pasm_file_def import PASMCommands # We only need the Star Commands struct

# Dont do this shit, come up with a cleaner solution
_AUTO_ID = -128

def _GetParameterString(pszCmd):
    psz1stParenthesis = pszCmd.find("(")
    if(psz1stParenthesis == -1):
        print("Missing (")
        return False
    
    psz2ndParenthesis = pszCmd.find(")")
    if(psz2ndParenthesis == -1):
        print("Missing )")
        return False
    
    if(psz1stParenthesis > psz2ndParenthesis):
        print("Statement not enclosed in parenthesis")
        return False

    pszNextCmd = pszCmd.find("*")
    if(pszNextCmd != -1):
        if (psz2ndParenthesis > pszNextCmd):
            print("Found additional * command before )")
            return False

    nParams = pszCmd[psz1stParenthesis + 1:psz2ndParenthesis].split(",")
    return nParams

APE_MAT_FLAGS_NO_DRAW            = 0x01    # Polys with this material will not be drawn
APE_MAT_FLAGS_APPLY_TINT         = 0x02    # This tint is modulated into the texture color in the surface pass
APE_MAT_FLAGS_DO_NOT_LM          = 0x04    # These polys should not be light mapped, though they can obscure light
APE_MAT_FLAGS_ZWRITE_ON          = 0x08    # Relevant for translucent materials, only. When rendering this material, write to the zbuffer (default for translucent materials is not to)
APE_MAT_FLAGS_DO_NOT_TINT        = 0x10    # If tint is applied to the mesh, this material will not receive tint
APE_MAT_FLAGS_NO_LM_USE          = 0x20    # These polys should not be used in the lightmap phase (to receive or obscure light)
APE_MAT_FLAGS_DO_NOT_BLOCK_LM    = 0x40    # These polys will not block light during lightmap application
APE_MAT_FLAGS_VERT_RADIOSITY     = 0x80    # These polys will receive vertex radiosity

APE_MAT_FLAGS_NONE               = 0x00


APE_MAT_COLL_FLAGS_COLL_WITH_PLAYER              = 0x0001
APE_MAT_COLL_FLAGS_COLL_WITH_NPCS                = 0x0002
APE_MAT_COLL_FLAGS_OBSTRUCT_LINE_OF_SIGHT        = 0x0004
APE_MAT_COLL_FLAGS_COLL_WITH_THIN_PROJECTILES    = 0x0008
APE_MAT_COLL_FLAGS_COLL_WITH_THICK_PROJECTILTES  = 0x0010
APE_MAT_COLL_FLAGS_COLL_WITH_CAMERA              = 0x0020
APE_MAT_COLL_FLAGS_COLL_WITH_OBJECTS             = 0x0040
APE_MAT_COLL_FLAGS_WALKABLE                      = 0x0080
APE_MAT_COLL_FLAGS_OBSTRUCT_SPLASH_DAMAGE        = 0x0100
APE_MAT_COLL_FLAGS_COLLIDE_WITH_DEBRIS           = 0x0200
APE_MAT_COLL_FLAGS_COLLIDE_WITH_VEHICLES         = 0x0400
APE_MAT_COLL_FLAGS_HOVER_COLLIDABLE              = 0x0800

APE_MAT_COLL_FLAGS_COLL_WITH_NOTHING             = 0x0000
APE_MAT_COLL_FLAGS_COLL_WITH_EVERYTHING          = 0xFFFF


APE_LAYER_FLAGS_DO_NOT_CAST_SHADOWS              = 0x00000100
APE_LAYER_FLAGS_INVERT_EMISSIVE_MASK             = 0x00000200
APE_LAYER_FLAGS_ANGULAR_EMISSIVE                 = 0x00000400
APE_LAYER_FLAGS_ANGULAR_TRANSLUCENCY             = 0x00000800
APE_LAYER_FLAGS_NO_ALPHA_SCROLL                  = 0x00001000

APE_LAYER_FLAGS_NONE                             = 0x00000000

class CMaterialStringParser:
    def __init__(self):
        self.m_ApeCommands = PASMCommands()
        self.Params = None
        self.m_nMatFlags = APE_MAT_FLAGS_NONE
        self.m_nAffectAngle = 0

    def _GetParamterString2(self, inStr, Cmd):
        pszCmd = inStr.find(Cmd)            
        if(pszCmd != -1):
            if(_GetParameterString(inStr[pszCmd + 1:])):
                self.nParams = _GetParameterString(inStr[pszCmd + 1:])
                return True
        return False
    
    # This is run before EVERY Material is parsed, it's essentially the default PASMLight.PASMCommands
    def ResetToDefaults(self):
        self.Params = None

        self.m_ApeCommands = PASMCommands()
        self.m_ApeCommands.bUseDiffuseColor = 1
        self.m_ApeCommands.bUseSpecularColor = 1
        self.m_ApeCommands.TintRGB = [1.0, 1.0, 1.0]
        self.m_ApeCommands.nShaderNum = -1
        self.m_ApeCommands.fBumpMapTileFactor = 1
        self.m_ApeCommands.fDetailMapTileFactor = 4
        self.m_ApeCommands.nCollMask = APE_MAT_COLL_FLAGS_COLL_WITH_EVERYTHING
        self.m_ApeCommands.nReactType = 0
        self.m_ApeCommands.nSurfaceType = -1
        self.m_ApeCommands.nID = -1
    
    # The meat, takes a Material String Name as input formats the class's Star Command struct
    def Parse(self, pszMatStr):

        if(self._GetParamterString2(pszMatStr, "*id")):               
            self.nParams[0] = int(self.nParams[0])
                
            if(self.nParams[0] < 127):
                self.m_ApeCommands.nID = self.nParams[0]

        if(self._GetParamterString2(pszMatStr, "*collid")):         
            self.nParams[0] = int(self.nParams[0])
                
            self.m_ApeCommands.nCollID = max(1, min(self.nParams[0], 63))

        if( pszMatStr.find("*sort") != -1 ):
            self.m_ApeCommands.bSort = True
        
        if(self._GetParamterString2(pszMatStr, "*order")): 
            self.nParams[0] = int(self.nParams[0])
                
            self.m_ApeCommands.nOrderNum = max(1, min(self.nParams[0], 100))
            
        if(self._GetParamterString2(pszMatStr, "*shader")):
            self.nParams[0] = int(self.nParams[0])
            
            self.m_ApeCommands.nShaderNum = max(0, self.nParams[0])
        
        if(self._GetParamterString2(pszMatStr, "*motif")): 
            self.m_ApeCommands.nEmissiveMotifID  = int(self.nParams[0])
            self.m_ApeCommands.nDiffuseMotifID   = int(self.nParams[2])
            self.m_ApeCommands.nSpecularMotifID  = int(self.nParams[4])
            self.m_ApeCommands.bUseEmissiveColor = int(self.nParams[1])
            self.m_ApeCommands.bUseDiffuseColor  = int(self.nParams[3])
            self.m_ApeCommands.bUseSpecularColor = int(self.nParams[5])
        
        if(self._GetParamterString2(pszMatStr, "*anim")):
            # Takes 2 arguments: (NumFrames, FramesPerSec)
            self.m_ApeCommands.nNumTexFrames = int(self.nParams[0])
            self.m_ApeCommands.fFramesPerSec = float(self.nParams[1])
            
            # AUTO ID
            if( self.m_ApeCommands.nID == -1 ):
                self.m_ApeCommands.nID = _AUTO_ID
        
        if(self._GetParamterString2(pszMatStr, "*rotate")):
            self.m_ApeCommands.fDeltaUVRotationPerSec = float(self.nParams[0])
            self.m_ApeCommands.vRotateUVAround.Set[0] = float(self.nParams[1])
            self.m_ApeCommands.vRotateUVAround.Set[1] = float(self.nParams[2])
            
            # AUTO ID
            if( self.m_ApeCommands.nID == -1 ):
                self.m_ApeCommands.nID = _AUTO_ID
        
        if(self._GetParamterString2(pszMatStr, "*scroll")):
            self.nParams[0] = float(self.nParams[0])
            self.nParams[1] = float(self.nParams[1])
            self.nParams[2] = float(self.nParams[2])
            self.nParams[3] = float(self.nParams[3])
            
            self.m_ApeCommands.fDeltaUPerSec = self.nParams[0] / self.nParams[1]
            self.m_ApeCommands.fDeltaVPerSec = self.nParams[2] / self.nParams[3]
            
            # AUTO ID
            if( self.m_ApeCommands.nID == -1 ):
                self.m_ApeCommands.nID = _AUTO_ID
        
        if(self._GetParamterString2(pszMatStr, "*z")): 
            self.nParams[0] = int( float( self.nParams[0] ) )                
            self.m_ApeCommands.nZTugValue = max(1, min(self.nParams[0], 1000))
        
        if( pszMatStr.find("*nocoll") != -1 ): 
            self.m_ApeCommands.bNoColl = True
        
        if(self._GetParamterString2(pszMatStr, "*coll")): 
            if( self.nParams[0] == 1 ):
                self.m_ApeCommands.nCollMask |= APE_MAT_COLL_FLAGS_COLL_WITH_PLAYER
            else:
                self.m_ApeCommands.nCollMask &= ~APE_MAT_COLL_FLAGS_COLL_WITH_PLAYER
            if( self.nParams[1] == 1 ):
                self.m_ApeCommands.nCollMask |= APE_MAT_COLL_FLAGS_COLL_WITH_NPCS
            else:
                self.m_ApeCommands.nCollMask &= ~APE_MAT_COLL_FLAGS_COLL_WITH_NPCS
            if( self.nParams[2] == 1 ):
                self.m_ApeCommands.nCollMask |= APE_MAT_COLL_FLAGS_OBSTRUCT_LINE_OF_SIGHT
            else:
                self.m_ApeCommands.nCollMask &= ~APE_MAT_COLL_FLAGS_OBSTRUCT_LINE_OF_SIGHT
            if( self.nParams[3] == 1 ):
                self.m_ApeCommands.nCollMask |= APE_MAT_COLL_FLAGS_COLL_WITH_THIN_PROJECTILES
            else:
                self.m_ApeCommands.nCollMask &= ~APE_MAT_COLL_FLAGS_COLL_WITH_THIN_PROJECTILES
            if( self.nParams[4] == 1 ):
                self.m_ApeCommands.nCollMask |= APE_MAT_COLL_FLAGS_COLL_WITH_THICK_PROJECTILTES
            else:
                self.m_ApeCommands.nCollMask &= ~APE_MAT_COLL_FLAGS_COLL_WITH_THICK_PROJECTILTES
            if( self.nParams[5] == 1 ):
                self.m_ApeCommands.nCollMask |= APE_MAT_COLL_FLAGS_COLL_WITH_CAMERA
            else:
                self.m_ApeCommands.nCollMask &= ~APE_MAT_COLL_FLAGS_COLL_WITH_CAMERA
            if( self.nParams[6] == 1 ):
                self.m_ApeCommands.nCollMask |= APE_MAT_COLL_FLAGS_COLL_WITH_OBJECTS
            else:
                self.m_ApeCommands.nCollMask &= ~APE_MAT_COLL_FLAGS_COLL_WITH_OBJECTS
            if( self.nParams[7] == 1 ):
                self.m_ApeCommands.nCollMask |= APE_MAT_COLL_FLAGS_WALKABLE
            else:
                self.m_ApeCommands.nCollMask &= ~APE_MAT_COLL_FLAGS_WALKABLE        
            if( self.nParams[8] == 1 ):
                self.m_ApeCommands.nCollMask |= APE_MAT_COLL_FLAGS_OBSTRUCT_SPLASH_DAMAGE
            else:
                self.m_ApeCommands.nCollMask &= ~APE_MAT_COLL_FLAGS_OBSTRUCT_SPLASH_DAMAGE
            if( self.nParams[9] == 1 ):
                self.m_ApeCommands.nCollMask |= APE_MAT_COLL_FLAGS_COLLIDE_WITH_DEBRIS
            else:
                self.m_ApeCommands.nCollMask &= ~APE_MAT_COLL_FLAGS_COLLIDE_WITH_DEBRIS     
            if( self.nParams[10] == 1 ):
                self.m_ApeCommands.nCollMask |= APE_MAT_COLL_FLAGS_COLLIDE_WITH_VEHICLES
            else:
                self.m_ApeCommands.nCollMask &= ~APE_MAT_COLL_FLAGS_COLLIDE_WITH_VEHICLES
            if( self.nParams[11] == 1 ):
                self.m_ApeCommands.nCollMask |= APE_MAT_COLL_FLAGS_HOVER_COLLIDABLE
            else:
                self.m_ApeCommands.nCollMask &= ~APE_MAT_COLL_FLAGS_HOVER_COLLIDABLE
        
        if( pszMatStr.find("*noascroll") != -1 ):
            self.m_nMatFlags |= APE_LAYER_FLAGS_NO_ALPHA_SCROLL
        
        if( pszMatStr.find("*tint") != -1 ):
            self.m_ApeCommands.nFlags |= APE_MAT_FLAGS_APPLY_TINT
            
        if( pszMatStr.find("*writez") != -1 ): 
            self.m_ApeCommands.nFlags |= APE_MAT_FLAGS_ZWRITE_ON
        
        if( pszMatStr.find("*nomeshtint") != -1 ): 
            self.m_ApeCommands.nFlags |= APE_MAT_FLAGS_DO_NOT_TINT
        
        if(self._GetParamterString2(pszMatStr, "*bumptile")): 
            self.m_ApeCommands.fBumpMapTileFactor = float(self.nParams[0])
        
        if(self._GetParamterString2(pszMatStr, "*detailtile")): 
            self.m_ApeCommands.fDetailMapTileFactor = float(self.nParams[0])
            
        if(self._GetParamterString2(pszMatStr, "*light")):
            self.m_ApeCommands.LightRGBI[0] =  ( max(0.0, min(float(self.nParams[0]), 255.0)) ) / 255.0
            self.m_ApeCommands.LightRGBI[1] =  ( max(0.0, min(float(self.nParams[1]), 255.0)) ) / 255.0
            self.m_ApeCommands.LightRGBI[2] =  ( max(0.0, min(float(self.nParams[2]), 255.0)) ) / 255.0
            self.m_ApeCommands.LightRGBI[3] =  ( max(0.0, min(float(self.nParams[3]), 255.0)) ) / 255.0
        
        if( pszMatStr.find("*nodraw") != -1 ): 
            self.m_ApeCommands.nFlags |= APE_MAT_FLAGS_NO_DRAW
            
        if( pszMatStr.find("*notinlm") != -1 ): 
            self.m_ApeCommands.nFlags |= APE_MAT_FLAGS_DO_NOT_LM
            
        if( pszMatStr.find("*nolmblock") != -1 ): 
            self.m_ApeCommands.nFlags |= APE_MAT_FLAGS_DO_NOT_BLOCK_LM
            
        if( pszMatStr.find("*nolmuse") != -1 ): 
            self.m_ApeCommands.nFlags |= APE_MAT_FLAGS_NO_LM_USE
            
        if( pszMatStr.find("*vertrad") != -1 ): 
            self.m_ApeCommands.nFlags |= APE_MAT_FLAGS_VERT_RADIOSITY|APE_MAT_FLAGS_DO_NOT_LM
            
        if( pszMatStr.find("*noshadows") != -1 ): 
            self.m_nMatFlags |= APE_LAYER_FLAGS_DO_NOT_CAST_SHADOWS
            
        if(self._GetParamterString2(pszMatStr, "*eangle")):
            self.m_nAffectAngle = max ( 0, min( int(self.nParams[0]), 180) )
            self.m_nMatFlags |= APE_LAYER_FLAGS_ANGULAR_EMISSIVE
            
        if(self._GetParamterString2(pszMatStr, "*tangle")): 
            self.m_nAffectAngle = max ( 0, min( int(self.nParams[0]), 180) )
            self.m_nMatFlags |= APE_LAYER_FLAGS_ANGULAR_TRANSLUCENCY
            
        if(self._GetParamterString2(pszMatStr, "*surf")): 
            self.m_ApeCommands.nSurfaceType = max ( 0, min( int(self.nParams[0]), 15) )
            
        if(self._GetParamterString2(pszMatStr, "*react")): 
            self.m_ApeCommands.nReactType = max ( 0, min( int(self.nParams[0]), 7) )


APE_OB_FLAG_STATIC              = 0x00000001    # Object's bounding sphere has a static footprint in 3D space
APE_OB_FLAG_POSTER_Y            = 0x00000002    # Poster object around it's Y axis to always face the camera (neg-Z axis of object toward viewer)
APE_OB_FLAG_NO_COLL             = 0x00000004    # Don't collide with this object
                                               
APE_OB_FLAG_NO_LIGHT            = 0x00000010    # Don't light this object
                                               
APE_OB_FLAG_POSTER_X            = 0x00000040    # Poster object around it's X axis
APE_OB_FLAG_POSTER_Z            = 0x00000080    # Poster object around it's Z axis
APE_OB_FLAG_NO_DRAW             = 0x00000100   
APE_OB_FLAG_LM                  = 0x00000200    # This (static) object will receive light maps
APE_OB_FLAG_PER_PIXEL           = 0x00000400   
APE_OB_FLAG_VERT_RADIOSITY      = 0x00000800    # This (static) object will receive vertex radiosity
APE_OB_FLAG_ACCEPT_SHADOWS      = 0x00001000    # This object will receive shadows
APE_OB_FLAG_CAST_SHADOWS        = 0x00002000    # This object will cast shadows
APE_OB_FLAG_TINT                = 0x00004000    # This object will be tinted
APE_OB_FLAG_NO_LM_USE           = 0x00008000    # This object will not be considered when generating lightmaps (even if static)

APE_OB_FLAG_NONE                = 0x00000000

class CObjectStringParser:
    def __init__(self):
        self.m_ApeObjectFlag = 0
        self.m_fCullDist = 0
        self.m_TintRGB = [0.0, 0.0, 0.0]
        self.Params = None
        
    def _GetParamterString2(self, inStr, Cmd):
        pszCmd = inStr.find(Cmd)            
        if(pszCmd != -1):
            if(_GetParameterString(inStr[pszCmd + 1:])):
                self.nParams = _GetParameterString(inStr[pszCmd + 1:])
                return True
        return False
        
    def Parse(self, pszObjectStr):
        
        if( pszObjectStr.find("*postery") != -1 ):
            self.m_ApeObjectFlag |= APE_OB_FLAG_POSTER_Y
            
        if( pszObjectStr.find("*posterx") != -1 ):
            self.m_ApeObjectFlag |= APE_OB_FLAG_POSTER_X
            
        if( pszObjectStr.find("*posterz") != -1 ):
            self.m_ApeObjectFlag |= APE_OB_FLAG_POSTER_Z
            
        if( pszObjectStr.find("*nocoll") != -1 ):
            self.m_ApeObjectFlag |= APE_OB_FLAG_NO_COLL
        # LEGACY / UNUSED?    
        if( pszObjectStr.find("nofog") != -1 ):
            print("*nofog not implimented")
            
        if( pszObjectStr.find("*nolight") != -1 ): 
            self.m_ApeObjectFlag |= APE_OB_FLAG_NO_LIGHT
        
        if(self._GetParamterString2(pszObjectStr, "*culldist")): 
            self.m_fCullDist = float(self.nParams[0])
            
        if(self._GetParamterString2(pszObjectStr, "*tint")): 
            self.m_ApeCommands.TintRGB[0] =  ( max(0.0, min(float(self.nParams[0]), 255.0)) ) / 255.0
            self.m_ApeCommands.TintRGB[1] =  ( max(0.0, min(float(self.nParams[1]), 255.0)) ) / 255.0
            self.m_ApeCommands.TintRGB[2] =  ( max(0.0, min(float(self.nParams[2]), 255.0)) ) / 255.0
            
        # LEGACY / UNUSED?    
        if( pszObjectStr.find("*sort") != -1 ):
            print("*sort not implimented")
            
        if( pszObjectStr.find("*nodraw") != -1 ): 
            self.m_ApeObjectFlag |= APE_OB_FLAG_NO_DRAW
            
        if( pszObjectStr.find("*acceptlm") != -1 ): 
            self.m_ApeObjectFlag |= APE_OB_FLAG_LM
            
        if( pszObjectStr.find("*vertrad") != -1 ):
            self.m_ApeObjectFlag |= APE_OB_FLAG_VERT_RADIOSITY
        
        if( pszObjectStr.find("acceptshadows") != -1 ):
            self.m_ApeObjectFlag |= APE_OB_FLAG_ACCEPT_SHADOWS
            
        if( pszObjectStr.find("*castshadows") != -1 ): 
            self.m_ApeObjectFlag |= APE_OB_FLAG_CAST_SHADOWS
            
        if( pszObjectStr.find("*dynamic") != -1 ): 
            self.m_ApeObjectFlag &= ~(APE_OB_FLAG_STATIC|APE_OB_FLAG_LM|APE_OB_FLAG_VERT_RADIOSITY)
            
        if( pszObjectStr.find("*nolmuse") != -1 ): 
            self.m_ApeObjectFlag |= APE_OB_FLAG_NO_LM_USE
            self.m_ApeObjectFlag &= ~(APE_OB_FLAG_LM|APE_OB_FLAG_VERT_RADIOSITY)
            
        if( pszObjectStr.find("*lightperpixel") != -1 ): 
            self.m_ApeObjectFlag |= APE_OB_FLAG_PER_PIXEL
   
APE_LIGHT_FLAG_DONT_USE_RGB              = 0x00000001    # Disregard the light's rgb and only use the motif's color (default = off)
APE_LIGHT_FLAG_LIGHT_SELF                = 0x00000002    # Light the object that the light is attached to (default = off)
APE_LIGHT_FLAG_OBJ_DONT_LIGHT_TERRAIN    = 0x00000004    # Lights attached to this object don't light the terrain (default = off)

APE_LIGHT_FLAG_PER_PIXEL                 = 0x00000008    # This light casts a projection on the environment (may or may not have a texture)

APE_LIGHT_FLAG_LIGHTMAP_ONLY_LIGHT       = 0x00000010    # This light will only be used in the lightmap portion of PASM and will not be exported to the engine.
APE_LIGHT_FLAG_LIGHTMAP_LIGHT            = 0x00000020    # This light is to be used for generating lightmaps (If it is not dynamic, it can be discarded prior to the engine)
APE_LIGHT_FLAG_UNIQUE_LIGHTMAP           = 0x00000040    # This light will generate its own unique lightmap in the lightmapping phase (it must also have a unique m_nLightID)

APE_LIGHT_FLAG_CORONA                    = 0x00000080    # This light has a corona
APE_LIGHT_FLAG_CORONA_PROXFADE           = 0x00000100    # Fade the corona as the camera gets closer.

APE_LIGHT_FLAG_CAST_SHADOWS              = 0x00000200    # This light will cast shadows (only relevant for engine lights)

APE_LIGHT_FLAG_DYNAMIC_ONLY              = 0x00000400    # This light will not affect static objects

APE_LIGHT_FLAG_MESH_MUST_BE_PER_PIXEL    = 0x00000800    # For per-pixel lights that have a projected texture.  If this flag is set, only objects that are flagged
                                                            # as per pixel lit will have the texture projected on them.  Others will just apply as a dynamic vertex light
   
class CLightStringParser:
    def __init__(self):
        self.m_ApeLightFlag = 0
        self.Params = None
        self.m_fCoronaScale = 1.0
        self.m_szCoronaTexture = ""
        self.m_szPerPixelTexture = ""
        self.m_nLightID = -1
        
    def _GetParamterString2(self, inStr, Cmd):
        pszCmd = inStr.find(Cmd)            
        if(pszCmd != -1):
            if(_GetParameterString(inStr[pszCmd + 1:])):
                self.nParams = _GetParameterString(inStr[pszCmd + 1:])
                return True
        return False
        
    def Parse(self, pszLightStr):
    
        if( pszLightStr.find("*self") != -1 ):
            self.m_ApeLightFlag |= APE_LIGHT_FLAG_LIGHT_SELF
            
        if( pszLightStr.find("*castshadows") != -1 ):
            self.m_ApeLightFlag |= APE_LIGHT_FLAG_CAST_SHADOWS
            
        if(self._GetParamterString2(pszLightStr, "*scalecorona")): 
            self.m_fCoronaScale = float(self.nParams[0])
            
        if(self._GetParamterString2(pszLightStr, "*fadingcorona")): 
            self.m_ApeLightFlag |= APE_LIGHT_FLAG_CORONA|APE_LIGHT_FLAG_CORONA_PROXFADE
            self.m_szCoronaTexture = self.nParams[0]
            
        if(self._GetParamterString2(pszLightStr, "*corona")): 
            self.m_ApeLightFlag |= APE_LIGHT_FLAG_CORONA
            self.m_szCoronaTexture = self.nParams[0]
            
        if(self._GetParamterString2(pszLightStr, "*perpixel")): 
            self.m_ApeLightFlag |= APE_LIGHT_FLAG_PER_PIXEL
            self.m_szPerPixelTexture = self.nParams[0]
        
        if( pszLightStr.find("*onlyppmesh") != -1 ):
            self.m_ApeLightFlag |= APE_LIGHT_FLAG_MESH_MUST_BE_PER_PIXEL
        
        if( pszLightStr.find("*onlydynamic") != -1 ):
            self.m_ApeLightFlag |= APE_LIGHT_FLAG_DYNAMIC_ONLY
        
        if( pszLightStr.find("*lm") != -1 ):
            self.m_ApeLightFlag |= APE_LIGHT_FLAG_LIGHTMAP_LIGHT
        
        if( pszLightStr.find("*uniquelm") != -1 ):
            self.m_ApeLightFlag &= ~APE_LIGHT_FLAG_DYNAMIC_ONLY
            self.m_ApeLightFlag |= APE_LIGHT_FLAG_UNIQUE_LIGHTMAP | APE_LIGHT_FLAG_LIGHTMAP_LIGHT
            
        if( pszLightStr.find("*onlylm") != -1 ): 
            self.m_ApeLightFlag &= ~APE_LIGHT_FLAG_DYNAMIC_ONLY
            self.m_ApeLightFlag |= APE_LIGHT_FLAG_LIGHTMAP_ONLY_LIGHT|APE_LIGHT_FLAG_LIGHTMAP_LIGHT
        
        if( pszLightStr.find("*noterrain") != -1 ):
            self.m_ApeLightFlag |= APE_LIGHT_FLAG_OBJ_DONT_LIGHT_TERRAIN
            
        if(self._GetParamterString2(pszLightStr, "*id")): 
            self.m_nLightID = max(0, min( int(self.nParams[0]), 0xffff))
            
        if(self._GetParamterString2(pszLightStr, "*motif")): 
            self.m_nMotifID = int(self.nParams[0])
            if(int(self.nParams[1]) != 0):
                self.m_ApeLightFlag |= APE_LIGHT_FLAG_DONT_USE_RGB
       
APE_PORTAL_FLAG_MIRROR            = 0x00000001    # the portal is a mirror
APE_PORTAL_FLAG_SOUND_ONLY        = 0x00000002    # the portal is for sound only
APE_PORTAL_FLAG_ONE_WAY           = 0x00000004    # the portal is 1 way
APE_PORTAL_FLAG_ANTI              = 0x00000008    # the portal is an anti portal

APE_PORTAL_FLAG_NONE              = 0x00000000
       
class CPortalStringParser:
    def __init__(self):
        self.m_ApePortalFlag = 0
        self.Params = None
        
    def _GetParamterString2(self, inStr, Cmd):
        pszCmd = inStr.find(Cmd)            
        if(pszCmd != -1):
            if(_GetParameterString(inStr[pszCmd + 1:])):
                self.nParams = _GetParameterString(inStr[pszCmd + 1:])
                return True
        return False
    
    def ResetRoDefaults():
        self.m_ApePortalFlag = 0
        self.Params = None
    
    def Parse(self, pszPortalStr):
    
        if( pszPortalStr.find("*mirror") != -1 ):
            self.m_ApePortalFlag |= APE_PORTAL_FLAG_MIRROR
            
        if( pszPortalStr.find("*sound") != -1 ): 
            self.m_ApePortalFlag |= APE_PORTAL_FLAG_SOUND_ONLY
            
        if( pszPortalStr.find("*oneway") != -1 ):
            self.m_ApePortalFlag |= APE_PORTAL_FLAG_ONE_WAY
            
        if( pszPortalStr.find("*anti") != -1 ):
            self.m_ApePortalFlag |= APE_PORTAL_FLAG_ANTI
       
       
       