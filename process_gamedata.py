# Module that processes gamedata attached to an object

# PYTHON BUILT IN
from difflib import SequenceMatcher
# FANG TOOLKIT
from . import g_class       # Get our global variables like header data & I/O file
import os

def setupgdkeys():
    path = os.path.dirname(os.path.realpath(__file__))
    path = path + "\gdkeys.txt"
    gdkeysfile = open(path)
    cmds = gdkeysfile.read();
    gdkeysfile.close()
    cmds = cmds.split('\n')
    for index in cmds:
        if index == "" or index.isspace(): continue # Check if string is empty
        if index[0] == "#":                continue # Check if comment line
        g_class.gdkeys.append(index.strip())
    #print(g_class.gdkeys)

# Grab custom properties from the object
def ProcessGamedata(obj, outObj):
    try:
        cmds = obj["ma"].split('\n')
        lc = [x.lower() for x in g_class.gdkeys]
        x = 0
        for index in cmds: 
            if index == "" or index.isspace(): continue # Check if string is empty
            if index[0] == "#":                continue # Check if comment line
            x += 1
            a = index.find("=")
            i = a - 1
            j = a + 1
            while index[i] == " ":
                i = i - 1
            while index[j] == " ":
                j = j + 1
                
            if index[:i + 1].lower() not in lc:
                for idx, y in enumerate(lc):
                    if SequenceMatcher(None, index[:i + 1].lower(), y).ratio() > 0.7:
                        g_class.logError("GAMEDATA ERROR: Unknown gamedata key " + index[:i + 1] + " found in " + obj.name + ". Did you mean " + g_class.gdkeys[idx] + " ?")
                        break
                else:
                    g_class.logError("GAMEDATA ERROR: Unknown gamedata key " + index[:i + 1] + " found in " + obj.name + ". No potential matches found.")
                continue

            outObj.userData.append(index[:i + 1] + "=" + index[j:])
            if x < len(cmds):
                outObj.userData.append(str('\x0D\x0A'))
    except:
        print("No Custom Properties") 
    
    # Go back and patch up userData length
    dataLen = 0
    for data in outObj.userData:
        if type(data) == float:
            dataLen = dataLen + 4
        else:
            dataLen = dataLen + len(data)
    outObj.nBytesOfUserData = dataLen
