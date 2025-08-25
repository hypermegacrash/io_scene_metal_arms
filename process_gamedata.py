# Module that processes gamedata attached to an object

# PYTHON BUILT IN
from difflib import SequenceMatcher
import re
import xml.etree.ElementTree as ET
# FANG TOOLKIT
from . import g_class       # Get our global variables like header data & I/O file
import os

_XML_DATABASE_NAME = "madb.xml"

def setupgdkeys():
    # Setup path to xml database...
    path = os.path.dirname(os.path.realpath(__file__))
    path = path + os.sep + _XML_DATABASE_NAME

    # Read in the contents...
    inXML = None
    with open(path, 'r', encoding='utf-8') as file:
        inXML = file.read()

    # Extract from <body> to </body>...
    match = re.search(r'<body>.*?</body>', inXML, re.DOTALL)
    if match:
        body_content = match.group(0)
    else:
        print("No <body> tag found")
        return False
    
    # Extract param fields...
    param_fields = []
    param_fields_obsolete = []
    root = ET.fromstring(body_content)
    for param in root.findall('.//param'):
        bIsDeprecated = int(param.attrib['deprecated'])
        bIsUnimplemented = int(param.attrib['unimplemented'])
        
        if(bIsDeprecated):
            #print(f"{param.attrib['name']} is deprecated!")
            param_fields_obsolete.append(param.attrib)
            continue
            
        if(bIsUnimplemented):
            #print(f"{param.attrib['name']} is unimplemented!")
            param_fields_obsolete.append(param.attrib)
            continue

        param_fields.append(param.attrib)

    # Add all the fields to the gdkeys list...
    for param in param_fields:
        g_class.gdkeys.append(param["name"].strip())

     # Add all the fields to the gdkeys_obsolete list...
    for param in param_fields_obsolete:
        g_class.gdkeys_Obsolete.append(param["name"].strip())

# Grab custom properties from the object
def ProcessGamedata(obj, outObj):
    try:
        cmds = obj["ma"].split('\n')
        lc = [x.lower() for x in g_class.gdkeys]
        lc_obsolete = [x.lower() for x in g_class.gdkeys_Obsolete]
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

            if index[:i + 1].lower() in lc_obsolete:
                g_class.logError(f"GAMEDATA ERROR: The gamedata key {index[:i + 1]} found in {obj.name} is obsolete! Remove it from this entity and export again.")
                continue
                
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
