# Module for exporting a .ape file and adding UI to execute

# FANG TOOLKIT
from . import g_class       # Get our global variables like header data & I/O file
# Grab all our defs for exporting Blender data to PASM formatted data
from . import file_def_ape # . is the add-on folder directory
from .process_object_geo   import ExportObjGeo
from .process_object_light import ExportObjLight
from .process_object_bone  import ExportObjBone

# BLENDER
import bpy              # For working with Blender data
import os               # We need this for accessing filepath functions
from bpy.props import ( # We need these properties for the export settings config
        BoolProperty,
        #BoolVectorProperty,
        #CollectionProperty,
        #EnumProperty,
        #FloatProperty,
        #FloatVectorProperty,
        #IntProperty,
        #IntVectorProperty,
        #PointerProperty,
        #StringProperty
        )

# Operator allows a class to interface with the rest of Blender essentially
# Exposes the use of the execute() function and directing bl_ data
from bpy.types import Operator
        
# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper

class ExportAPE(Operator, ExportHelper):
        """Export scene to a Pasm compatible .ape file"""
        # Should this stuff be in the menu_func func? something to consider
        bl_idname    = 'export_scene.ape'
        bl_label     = 'Export APE'
        filename_ext = '.ape'
        
        # UI Variables
        m_bUseSelection:          BoolProperty( name="Selection Only",          description="Export selected objects only",                                                                     default=False )
        m_bExportLights:          BoolProperty( name="Export Light Data",       description="Export all lights from the scene",                                                                 default=False ) 
        m_bExportGeo:             BoolProperty( name="Export Geometry Data",    description="Export all geometry from the scene",                                                               default=True  )
        m_bExportHierarchy:       BoolProperty( name="Export Hierarchy",        description="Export the armature from the scene",                                                               default=True  )
        m_bExportBinarySkinning:  BoolProperty( name="Export Binary Skinning",  description="Enforce binary skinning (Polygons can only be weighted to a single bone) Recommended to leave on", default=True  )

        # Draw the export properties which are then stored in self for access
        def draw(self, context):
            layout = self.layout
            
            boxHeader = layout.box()
            boxHeader.label(text="Ape File Exporter")
        
            layout.prop(self, "m_bUseSelection")
            
            boxSettings = layout.box()
            
            boxSettings.prop(self, "m_bExportLights")
            boxSettings.prop(self, "m_bExportGeo")
            boxSettings.prop(self, "m_bExportHierarchy")
            boxSettings.prop(self, "m_bExportBinarySkinning")
            
            g_class.writeFooterInfo(layout)
                    
        # The Blender Python API's equivalent of C/C++ main()
        def execute(self, context):
            
            # Init and dress a fresh header
            g_class.gApeHeader = file_def_ape.PASMHeader() 
            
            filename = os.path.basename(self.filepath)
            filename = filename[:len(filename)-4]
            g_class.gApeHeader.sceneName = filename
            
            g_class.gApeHeader.bWld = 0
            
            # Init our out file and error log in the global g_class for other modules to access
            with open(self.filepath, 'wb')     as g_class.file, \
                 open(g_class.fpErrorLog, 'a') as g_class.errorLogFile:
                             
                g_class.file.write(g_class.gApeHeader.packBytes()) # This will be overwritten at the very end with the correct data
                g_class.bShowErrorLog = False # Init our error log file
                
                # The data we want from the scene are the "objects"
                # Objects are generic containers that contain "data"
                # Data for an Object can be a mesh, light, empty etc
                
                if (self.m_bUseSelection): objects = [obj for obj in context.selected_objects]
                else:                      objects = [obj for obj in context.scene.objects]
                    
                # Before we work on any objects we trim the selection set
                    
                # REMOVE ALL _off OBJECTS
                for obj in objects:
                    if obj.name[:4].lower() == "off_":
                        #print("REMOVE OFF_ OBJECT " + obj.name)
                        try:    objects.remove(obj)
                        except: pass
                
                # REMOVE ALL CHILDREN OF obj_ OBJECTS
                for obj in objects:
                    if obj.name[:4].lower() == "obj_":
                        #print("REMOVE OBJ_ CHILDREN " + obj.name)
                        for objA in obj.children_recursive:
                            for objB in objects:
                                if objA.name == objB.name:
                                    #print("  REMOVE " + objA.name)
                                    try:    objects.remove(objA)
                                    except: pass
                
                # REMOVE CHILDREN IN off_ COLLECTIONS   
                for collection in bpy.data.collections:
                    if collection.name[:4].lower() == "off_":
                        #print("REMOVE COLLECTION " + collection.name)
                        for obj in collection.all_objects:
                            #print("  REMOVE " + obj.name)
                            try:    objects.remove(obj)
                            except: pass
    
                # To mimic the original exporter as closely as possible
                # We itterate over the entire scene for each section of the PASM file
                # One loop for lights, one for geo, one for cells, and so on
            
                if(self.m_bExportHierarchy):
                    for obj in objects:
                        ExportObjBone(obj)
                        
                if(self.m_bExportLights):
                    for obj in objects:
                        ExportObjLight(obj)
                
                # TODO: Add LOD Support
                if(self.m_bExportGeo):
                    for obj in objects:
                        ExportObjGeo(obj, self.m_bExportHierarchy, self.m_bExportBinarySkinning)
                
                # Go back to the start and rewrite the header with correct data
                g_class.file.seek(0)
                g_class.file.write(g_class.gApeHeader.packBytes())
                
                # Do a check for .apes that somehow got this far and didn't export any geometry / segments
                # PASM will complain about this not being a valid .ape
                if(g_class.gApeHeader.nNumSegments == 0):
                    g_class.logError("APE ERROR: The exported file has no geometry.\n" +
                    "POSSIBLE FIX 1: Ensure geometry you want exported does not have obj_ prefix.\n" +
                    "POSSIBLE FIX 2: Ensure geometry has FANG Materials or FANG Composite Materials applied, regular materials will NOT be exported.")
    
            # Did we encounter any errors?
            if(g_class.bShowErrorLog): os.startfile(g_class.fpErrorLog)
            
            print("APE Export Finished!")
            self.report({'INFO'}, "APE Export Finished!")
        
            return {'FINISHED'}
                
def exportAPE_MenuFunc(self, context):
    self.layout.operator(
        ExportAPE.bl_idname, text="Metal Arms Pasm Ape (.ape)")