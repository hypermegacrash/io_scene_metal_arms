# Module that processes a light object and returns byte data

# FANG TOOLKIT
from . import file_def_ape  # Get our PASM file classes
from . import g_class       # Get our global variables for the header data
from . import pasm_math     # PASM helper defs
from .process_star_command import CLightStringParser # Import just the Light Star Command Parser
from .process_gamedata import parse_ma_string
APE_LIGHT_FLAG_LIGHTMAP_ONLY_LIGHT       = 0x00000010    # This light will only be used in the lightmap portion of PASM and will not be exported to the engine.
APE_LIGHT_FLAG_LIGHTMAP_LIGHT            = 0x00000020    # This light is to be used for generating lightmaps (If it is not dynamic, it can be discarded prior to the engine)
APE_LIGHT_FLAG_UNIQUE_LIGHTMAP           = 0x00000040    # This light will generate its own unique lightmap in the lightmapping phase (it must also have a unique m_nLightID)

def ExportObjLight(obj):
    bExitEarly = False
    
    if obj.name[:4].lower() == "off_": return # Doesn't matter it's off bail early
    if obj.type             != "LIGHT":                           bExitEarly = True  # Not a light then we don't export
    if obj.name[:7].lower() == "ambient" and obj.type == "EMPTY": bExitEarly = False # Ambient lights are empty cube objects
    
    if(bExitEarly): return
        
    # print(obj.name, "is a light object")

    outLight = file_def_ape.PASMLight()
    
    if obj.type == "LIGHT":
        if   obj.data.type == "SUN":   outLight.nApeLightType = file_def_ape.PASMLightType_e.APE_LIGHT_TYPE_DIR
        elif obj.data.type == "POINT": outLight.nApeLightType = file_def_ape.PASMLightType_e.APE_LIGHT_TYPE_OMNI
        elif obj.data.type == "SPOT":  outLight.nApeLightType = file_def_ape.PASMLightType_e.APE_LIGHT_TYPE_SPOT
        
    if obj.name[:7].lower() == "ambient" and obj.type == "EMPTY": outLight.nApeLightType = file_def_ape.PASMLightType_e.APE_LIGHT_TYPE_AMBIENT
        
    if outLight.nApeLightType == -1:
        g_class.logError(f"LIGHT ERROR: Unable to assign nApeLightType for {obj.name}, skipping.")
        return
        
    outLight.szLightName = obj.name
    
    if obj.type == "LIGHT":
        outLight.Color[0] = pasm_math.color_scene_linear_to_srgb(obj.data.color[0])
        outLight.Color[1] = pasm_math.color_scene_linear_to_srgb(obj.data.color[1])
        outLight.Color[2] = pasm_math.color_scene_linear_to_srgb(obj.data.color[2])
    elif obj.name[:7].lower() == "ambient" and obj.type == "EMPTY":
        # Pull the 'red' 'green' 'blue' gamedata fields for the ambient color

        if "ma" not in obj:
            g_class.logError(f"LIGHT ERROR: No gamedata for ambient entity {obj.name}, skipping.")
            return

        try:
            parsed = parse_ma_string(obj["ma"])
            parsed = {k.lower(): v for k, v in parsed.items()}
        except Exception as e:
            g_class.logError(f"LIGHT ERROR: Failed to parse gamedata on ambient entity {obj.name}, skipping. {e}")
            return
        
        if "red" not in parsed or "green" not in parsed or "blue" not in parsed:
            g_class.logError(f"LIGHT ERROR: Unable to find integer gamedata values red green blue for {obj.name}, skipping.")
            return
        
        try:
            nRed, nGreen, nBlue = (
                int(parsed["red"]),
                int(parsed["green"]),
                int(parsed["blue"]),
            )
        except (ValueError, TypeError):
            g_class.logError(f"LIGHT ERROR: Non-integer RGB gamedata on {obj.name}, skipping.")
            return
        
        # Floor it
        nRed   = max(0, min(nRed,   255))
        nGreen = max(0, min(nGreen, 255))
        nBlue  = max(0, min(nBlue,  255))
        # Convert to float
        nRed   = nRed   * float((1/255))
        nGreen = nGreen * float((1/255))
        nBlue  = nBlue  * float((1/255))    
        # Assign it
        outLight.Color[0] = nRed
        outLight.Color[1] = nGreen
        outLight.Color[2] = nBlue
    else:
        g_class.logError(f"LIGHT ERROR: Unable to assign Light color for {obj.name}, skipping.")
        return
        
    # Parse light name for star commands
    lightStrParser = CLightStringParser()
    lightStrParser.Parse(obj.name.lower())
    outLight.nFlags = lightStrParser.m_ApeLightFlag
    outLight.fCoronaScale = lightStrParser.m_fCoronaScale
    outLight.szCoronaTexture = lightStrParser.m_szCoronaTexture
    outLight.szPerPixelTexture = lightStrParser.m_szPerPixelTexture
    outLight.nLightID = lightStrParser.m_nLightID
  
    if obj.type == "LIGHT":
        outLight.Intensity = obj.data.ma_light_props.fIntensity
    elif obj.name[:7].lower() == "ambient" and obj.type == "EMPTY":
        outLight.Intensity = 1.0
    else:
        g_class.logError(f"LIGHT ERROR: Unable to assign Light intensity for {obj.name}, skipping.")
        return
      
    # Lights calculate their rotation matrix in a different way to everything else
    outLight.mtxOrientation = pasm_math.BObj2F43MtxLIGHT(obj)
    
    if outLight.nApeLightType == file_def_ape.PASMLightType_e.APE_LIGHT_TYPE_DIR or outLight.nApeLightType == file_def_ape.PASMLightType_e.APE_LIGHT_TYPE_SPOT:
        # This is the 3rd row of the rotation matrix
        outLight.Direction[0] =  outLight.mtxOrientation[6]
        outLight.Direction[1] =  outLight.mtxOrientation[7]
        outLight.Direction[2] =  outLight.mtxOrientation[8]
    
    if outLight.nApeLightType == file_def_ape.PASMLightType_e.APE_LIGHT_TYPE_OMNI or outLight.nApeLightType == file_def_ape.PASMLightType_e.APE_LIGHT_TYPE_SPOT:
        outLight.Sphere[0] = obj.data.ma_light_props.fRadius
        outLight.Sphere[1] = outLight.mtxOrientation[9]
        outLight.Sphere[2] = outLight.mtxOrientation[10]
        outLight.Sphere[3] = outLight.mtxOrientation[11]
        
    if outLight.nApeLightType == file_def_ape.PASMLightType_e.APE_LIGHT_TYPE_SPOT:
        if obj.data.spot_blend == 1.0: # This is a super soft light
            outLight.fSpotInnerAngle = 0.0
        else: # Regular light
            outLight.fSpotInnerAngle = (1 - obj.data.spot_blend) * obj.data.spot_size

        # If fSpotInnerAngle > fSpotOuterAngle the light will become inverted
        if outLight.fSpotInnerAngle >= obj.data.spot_size:
            outLight.fSpotInnerAngle = obj.data.spot_size - 2
        if outLight.fSpotInnerAngle <= 0.5:
            outLight.fSpotInnerAngle = 0.5

        if obj.data.spot_size <= 1.0:
            outLight.fSpotOuterAngle = 1.0
        else:
            outLight.fSpotOuterAngle = obj.data.spot_size
        
    # Check to see if this light is attached to an armature
    if (obj.parent_bone):
        hArmature = obj.parent.data
        outLight.szParentBoneName = hArmature.bones[obj.parent_bone].parent.name
    
    # Finally, write data to the file, and our header
    g_class.file.write(outLight.packBytes())
    g_class.gApeHeader.fileSize += len(outLight.packBytes())
    g_class.gApeHeader.nNumLights += 1
    



