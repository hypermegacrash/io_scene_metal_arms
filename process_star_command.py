# Module that provides classes for processing Star Commands found in the name of Material, Object and Lights

from .pasm_file_def import PASMCommands # We only need the Star Commands struct

# Dont do this shit, come up with a cleaner solution
_AUTO_ID = -128

APE_MAT_FLAGS_NO_DRAW			= 0x01	# Polys with this material will not be drawn
APE_MAT_FLAGS_APPLY_TINT		= 0x02	# This tint is modulated into the texture color in the surface pass
APE_MAT_FLAGS_DO_NOT_LM			= 0x04	# These polys should not be light mapped, though they can obscure light
APE_MAT_FLAGS_ZWRITE_ON			= 0x08	# Relevant for translucent materials, only. When rendering this material, write to the zbuffer (default for translucent materials is not to)
APE_MAT_FLAGS_DO_NOT_TINT		= 0x10	# If tint is applied to the mesh, this material will not receive tint
APE_MAT_FLAGS_NO_LM_USE			= 0x20	# These polys should not be used in the lightmap phase (to receive or obscure light)
APE_MAT_FLAGS_DO_NOT_BLOCK_LM	= 0x40	# These polys will not block light during lightmap application
APE_MAT_FLAGS_VERT_RADIOSITY	= 0x80	# These polys will receive vertex radiosity

APE_MAT_FLAGS_NONE				= 0x00

class CMaterialStringParser:
    def __init__(self):
        self.m_ApeCommands = PASMCommands()
        self.Params = None

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
        self.m_ApeCommands.nCollMask = 255
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

        if(self._GetParamterString2(pszMatStr, "*sort")):
            self.m_ApeCommands.bSort = True
        
        if(self._GetParamterString2(pszMatStr, "*order")): 
            print("*order not implimented")
            
        if(self._GetParamterString2(pszMatStr, "*shader")):
            self.nParams[0] = int(self.nParams[0])
            
            self.m_ApeCommands.nShaderNum = max(0, self.nParams[0])
        
        if(self._GetParamterString2(pszMatStr, "*motif")): 
            print("*motif not implimented")
        
        if(self._GetParamterString2(pszMatStr, "*anim")):
            # Takes 2 arguments: (NumFrames, FramesPerSec)
            self.m_ApeCommands.nNumTexFrames = int(self.nParams[0])
            self.m_ApeCommands.fFramesPerSec = float(self.nParams[1])
            
            # AUTO ID
            if( self.m_ApeCommands.nID == -1 ):
                self.m_ApeCommands.nID = _AUTO_ID
        
        if(self._GetParamterString2(pszMatStr, "*rotate")):
            print("*rotate not implimented")
        
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
                  
        if(self._GetParamterString2(pszMatStr, "*nocoll")): 
            print("*nocoll not implimented")
        
        if(self._GetParamterString2(pszMatStr, "*coll")): 
            print("*coll not implimented")
        
        if(self._GetParamterString2(pszMatStr, "*noascroll")): 
            print("*noascroll not implimented")
        
        if(self._GetParamterString2(pszMatStr, "*tint")):
            self.m_ApeCommands.nFlags |= APE_MAT_FLAGS_APPLY_TINT
            
        if(self._GetParamterString2(pszMatStr, "*writez")): 
            print("*writez not implimented")
        
        if(self._GetParamterString2(pszMatStr, "*nomeshtint")): 
            print("*nomeshtint not implimented")
        
        if(self._GetParamterString2(pszMatStr, "*bumptile")): 
            print("*bumptile not implimented")
        
        if(self._GetParamterString2(pszMatStr, "*detailtile")): 
            print("*detailtile not implimented")
            
        if(self._GetParamterString2(pszMatStr, "*light")): 
            print("*light not implimented")
        
        if(self._GetParamterString2(pszMatStr, "*nodraw")): 
            print("*nodraw not implimented")
            
        if(self._GetParamterString2(pszMatStr, "*notinlm")): 
            print("*notinlm not implimented")
            
        if(self._GetParamterString2(pszMatStr, "*nolmblock")): 
            print("*nolmblock not implimented")
            
        if(self._GetParamterString2(pszMatStr, "*nolmuse")): 
            print("*nolmuse not implimented")
            
        if(self._GetParamterString2(pszMatStr, "*vertrad")): 
            print("*vertrad not implimented")
            
        if(self._GetParamterString2(pszMatStr, "*noshadows")): 
            print("*noshadows not implimented")
            
        if(self._GetParamterString2(pszMatStr, "*eangle")): 
            print("*eangle not implimented")
            
        if(self._GetParamterString2(pszMatStr, "*tangle")): 
            print("*tangle not implimented")
            
        if(self._GetParamterString2(pszMatStr, "*surf")): 
            print("*surf not implimented")
            
        if(self._GetParamterString2(pszMatStr, "*react")): 
            print("*react not implimented")  


APE_OB_FLAG_STATIC				= 0x00000001	# Object's bounding sphere has a static footprint in 3D space
APE_OB_FLAG_POSTER_Y			= 0x00000002	# Poster object around it's Y axis to always face the camera (neg-Z axis of object toward viewer)
APE_OB_FLAG_NO_COLL				= 0x00000004	# Don't collide with this object
                                               
APE_OB_FLAG_NO_LIGHT			= 0x00000010	# Don't light this object
                                               
APE_OB_FLAG_POSTER_X			= 0x00000040	# Poster object around it's X axis
APE_OB_FLAG_POSTER_Z			= 0x00000080	# Poster object around it's Z axis
APE_OB_FLAG_NO_DRAW				= 0x00000100   
APE_OB_FLAG_LM					= 0x00000200	# This (static) object will receive light maps
APE_OB_FLAG_PER_PIXEL			= 0x00000400   
APE_OB_FLAG_VERT_RADIOSITY		= 0x00000800	# This (static) object will receive vertex radiosity
APE_OB_FLAG_ACCEPT_SHADOWS		= 0x00001000	# This object will receive shadows
APE_OB_FLAG_CAST_SHADOWS		= 0x00002000	# This object will cast shadows
APE_OB_FLAG_TINT				= 0x00004000	# This object will be tinted
APE_OB_FLAG_NO_LM_USE			= 0x00008000	# This object will not be considered when generating lightmaps (even if static)

APE_OB_FLAG_NONE				= 0x00000000

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
        
        if(self._GetParamterString2(pszObjectStr, "*postery")): 
            print("*postery not implimented")
            
        if(self._GetParamterString2(pszObjectStr, "*posterx")): 
            print("*posterx not implimented")
            
        if(self._GetParamterString2(pszObjectStr, "*posterz")): 
            print("*posterz not implimented")
            
        if(self._GetParamterString2(pszObjectStr, "*nocoll")): 
            print("*nocoll not implimented")
            
        if(self._GetParamterString2(pszObjectStr, "*nofog")): 
            print("*nofog not implimented")
            
        if(self._GetParamterString2(pszObjectStr, "*nolight")): 
            print("*nolight not implimented")
        
        if(self._GetParamterString2(pszObjectStr, "*culldist")): 
            print("*culldist not implimented")
            
        if(self._GetParamterString2(pszObjectStr, "*tint")): 
            print("*tint not implimented")
            
        if(self._GetParamterString2(pszObjectStr, "*sort")): 
            print("*sort not implimented")
            
        if(self._GetParamterString2(pszObjectStr, "*nodraw")): 
            print("*nodraw not implimented")
            
        if(self._GetParamterString2(pszObjectStr, "*acceptlm")): 
            print("*acceptlm not implimented")
            
        if(self._GetParamterString2(pszObjectStr, "*vertrad")): 
            print("*vertrad not implimented")
        
        if(self._GetParamterString2(pszObjectStr, "*acceptshadows")): 
            print("*acceptshadows not implimented")
            
        if(self._GetParamterString2(pszObjectStr, "*castshadows")): 
            self.m_ApeObjectFlag |= APE_OB_FLAG_CAST_SHADOWS
            
        if(self._GetParamterString2(pszObjectStr, "*dynamic")): 
            print("*dynamic not implimented")
            
        if(self._GetParamterString2(pszObjectStr, "*nolmuse")): 
            print("*nolmuse not implimented")
            
        if(self._GetParamterString2(pszObjectStr, "*lightperpixel")): 
            print("*lightperpixel not implimented")
        
class CLightStringParser:
    def __init__(self):
        self.m_ApeLightFlag = 0
        self.Params = None
        
    def _GetParamterString2(self, inStr, Cmd):
        pszCmd = inStr.find(Cmd)            
        if(pszCmd != -1):
            if(_GetParameterString(inStr[pszCmd + 1:])):
                self.nParams = _GetParameterString(inStr[pszCmd + 1:])
                return True
        return False
        
    def Parse(self, pszLightStr):
    
        if(self._GetParamterString2(pszLightStr, "*self")): 
            print("*self not implimented")
            
        if(self._GetParamterString2(pszLightStr, "*castshadows")): 
            print("*castshadows not implimented")
            
        if(self._GetParamterString2(pszLightStr, "*scalecorona")): 
            print("*scalecorona not implimented")
            
        if(self._GetParamterString2(pszLightStr, "*fadingcorona")): 
            print("*fadingcorona not implimented")
            
        if(self._GetParamterString2(pszLightStr, "*corona")): 
            print("*corona not implimented")
            
        if(self._GetParamterString2(pszLightStr, "*perpixel")): 
            print("*perpixel not implimented")
            
        if(self._GetParamterString2(pszLightStr, "*onlyppmesh")): 
            print("*onlyppmesh not implimented")
            
        if(self._GetParamterString2(pszLightStr, "*onlydynamic")): 
            print("*onlydynamic not implimented")
            
        if(self._GetParamterString2(pszLightStr, "*lm")): 
            print("*lm not implimented")
            
        if(self._GetParamterString2(pszLightStr, "*uniquelm")): 
            print("*uniquelm not implimented")
            
        if(self._GetParamterString2(pszLightStr, "*onlylm")): 
            print("*onlylm not implimented")
            
        if(self._GetParamterString2(pszLightStr, "*noterrain")): 
            print("*noterrain not implimented")
            
        if(self._GetParamterString2(pszLightStr, "*id")): 
            print("*id not implimented")
            
        if(self._GetParamterString2(pszLightStr, "*motif")): 
            print("*motif not implimented")
        
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
    
        if(self._GetParamterString2(pszPortalStr, "*mirror")): 
            print("*mirror not implimented")
            
        if(self._GetParamterString2(pszPortalStr, "*sound")): 
            print("*sound not implimented")
            
        if(self._GetParamterString2(pszPortalStr, "*oneway")): 
            print("*oneway not implimented")
            
        if(self._GetParamterString2(pszPortalStr, "*anti")): 
            print("*anti not implimented")  
        
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