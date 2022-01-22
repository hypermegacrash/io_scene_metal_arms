# Module that provides classes for processing Star Commands found in the name of Material, Object and Lights

from .pasm_file_def import PASMCommands # We only need the Star Commands struct

_AUTO_ID = 128

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
        self.m_ApeCommands.nMatFlags = 0
        self.m_ApeCommands.nAffectAngle = 0
        self.m_ApeCommands.bSort = False
        self.m_ApeCommands.nOrderNum = 0
        self.m_ApeCommands.nShaderNum = -1
        self.m_ApeCommands.nEmissiveMotifID = 0
        self.m_ApeCommands.nSpecularMotifID = 0
        self.m_ApeCommands.nDiffuseMotifID = 0
        self.m_ApeCommands.bUseEmissiveColor = True
        self.m_ApeCommands.bUseSpecularColor = True
        self.m_ApeCommands.bUseDiffuseColor = False
        self.m_ApeCommands.nNumTexFrames = 0
        self.m_ApeCommands.fFramesPerSecs = 0.0
        self.m_ApeCommands.fDeltaUPerSec = 0.0
        self.m_ApeCommands.fDeltaVPerSec = 0.0
        self.m_ApeCommands.fDeltaUVRotationPerSec = 0.0
        self.m_ApeCommands.nZTugValue = 0
        #self.m_ApeCommands.nID = 255
        self.m_ApeCommands.bNoColl = False
        self.m_ApeCommands.nCollID = 0
        self.m_ApeCommands.nFlags = 0
        #self.m_ApeCommands.nCollMask = 255
        self.m_ApeCommands.nReactType = 0
        self.m_ApeCommands.nSurfaceType = 0
        self.m_ApeCommands.TintRGB  = [1.0, 1.0, 1.0]
        self.m_ApeCommands.LightRGBI = [0.0, 0.0, 0.0, 0.0]
        self.m_ApeCommands.fBumpMapTileFactor = 1.0
        self.m_ApeCommands.fDetailMapTileFactor = 4.0
        
    
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
            
            self.m_ApeCommands.nShaderID = max(0, self.nParams[0])
        
        if(self._GetParamterString2(pszMatStr, "*motif")): 
            print("*motif not implimented")
        
        if(self._GetParamterString2(pszMatStr, "*anim")):
            print("*anim not implimented")
        
        if(self._GetParamterString2(pszMatStr, "*rotate")): 
            print("*rotate not implimented")
        
        if(self._GetParamterString2(pszMatStr, "*scroll")):
            self.nParams[0] = float(self.nParams[0])
            self.nParams[1] = float(self.nParams[1])
            
            self.m_ApeCommands.fDeltaUPerSec = self.nParams[0]
            self.m_ApeCommands.fDeltaVPerSec = self.nParams[1]
            self.m_ApeCommands.nID = _AUTO_ID
                  
        if(self._GetParamterString2(pszMatStr, "*nocoll")): 
            print("*nocoll not implimented")
        
        if(self._GetParamterString2(pszMatStr, "*coll")): 
            print("*coll not implimented")
        
        if(self._GetParamterString2(pszMatStr, "*noascroll")): 
            print("*noascroll not implimented")
        
        if(self._GetParamterString2(pszMatStr, "*tint")): 
            print("*tint not implimented")
            
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
            print("*castshadows not implimented")
            
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