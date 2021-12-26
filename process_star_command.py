# Module that provides classes for processing Star Commands found in the name of Material, Object and Lights

from .pasm_file_def import PASMCommands # We only need The Star Commands struct

class CMatStringParser:
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
            print("*scroll not implimented")
            
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

    def ResetRoDefaults():
        self.m_ApeCommands = PASMCommands()
        self.Params = None

class CObjStringParser:
    def __init__(self):
        self.m_ApeCommands = PASMCommands()
        self.Params = None
        
class CLightStringParser:
    def __init__(self):
        self.m_ApeCommands = PASMCommands()
        self.Params = None

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