# Module for exporting a .wld file and adding UI to execute

# FANG TOOLKIT
from . import g_class       # Get our global variables like header data & I/O file
# Grab all our defs for exporting Blender data to PASM formatted data
from . import file_def_ape # . is the add-on folder directory
from .process_object_geo     import ExportObjGeo
from .process_object_light   import ExportObjLight
from .process_object_object  import ExportObjObject
from .process_object_shape   import ExportObjShape
from .process_object_volume  import ExportObjVolume
from .process_object_portal  import ExportObjPortal
from .process_object_fog     import ExportObjFog

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

# The MEAT, when this class is executed it returns a PASM compatible .wld file
class ExportWLD(Operator, ExportHelper):
        """Export scene to a Pasm compatible .wld file"""
        # Should this stuff be in the menu_func func? something to consider
        bl_idname    = 'export_scene.wld'
        bl_label     = 'Export WLD'
        filename_ext = '.wld'
        
        # UI Variables
        m_bUseSelection:  BoolProperty( name="Selection Only",       description="Export selected objects only",       default=False )
        m_bExportLights:  BoolProperty( name="Export Light Data",    description="Export all lights from the scene",   default=True  ) 
        m_bExportGeo:     BoolProperty( name="Export Geometry Data", description="Export all geometry from the scene", default=True  )
        m_bExportObjects: BoolProperty( name="Export Object Data",   description="Export all objects from the scene",  default=True  )

        # Draw the export properties which are then stored in self to be accessed later
        def draw(self, context):
            layout = self.layout
            
            boxHeader = layout.box()
            boxHeader.label(text="Wld File Exporter")
        
            layout.prop(self, "m_bUseSelection")
            
            boxSettings = layout.box()
            
            boxSettings.prop(self, "m_bExportLights")
            boxSettings.prop(self, "m_bExportGeo")
            boxSettings.prop(self, "m_bExportObjects")
            
            g_class.writeFooterInfo(layout)
                    
        # The Blender Python API's equivalent of C/C++ main()
        def execute(self, context):
              
            # Init and dress a fresh header
            g_class.gApeHeader = file_def_ape.PASMHeader() 
            
            filename = os.path.basename(self.filepath)
            filename = filename[:len(filename)-4]
            g_class.gApeHeader.sceneName = filename
            
            g_class.gApeHeader.bWld = 1
                       
            # Init our out file and error log in the global g_class for other modules to access
            with open(self.filepath, 'wb')     as g_class.file, \
                 open(g_class.fpErrorLog, 'a') as g_class.errorLogFile:
                             
                g_class.file.write(g_class.gApeHeader.packBytes()) # This will be overwritten at the very end with the correct data
                g_class.bShowErrorLog = False # Init our error log file
                
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
                        # NOTE: Could have a pattern like
                        # obj_thingyA -> whatever -> obj_thingyB
                        # This would cause issues as the parent of obj_thingyB wouldn't be exported
                        for objA in obj.children_recursive:
                            for objB in objects:
                                # We don't export shapes parented under objects because said shape could exist in the .ape
                                # the obj_ is referencing and we might have merged the mesh into the scene under a obj_ dummy for reference
                                # EX: No reason to export a obj_ with a tack_ child when the tack_ exists in the .ape
                                # obj_ is allowed to have obj_ children, EX: Victory screen with obj glitch parent with obj spew child
                                if objA.name == objB.name and objA.name[:4].lower() != "obj_":
                                    #print("  REMOVE " + objA.name)
                                    try:    objects.remove(objA)
                                    except: pass
                
               # REMOVE CHILDREN IN off_ COLLECTIONS   
                for collection in bpy.data.collections:
                    if collection.name[:4].lower() == "off_":
                        #print("  REMOVE COLLECTION " + collection.name)
                        for obj in collection.all_objects:
                            #print("    REMOVE " + obj.name)
                            try:    objects.remove(obj)
                            except: pass
                            
                VolumeColls = []
                
                # ORGANIZE cell_ COLLECTIONS INTO SEPERATE LISTS
                #print("\nREMOVE CHILDREN IN cell_ COLLECTIONS\n")         
                for collection in bpy.data.collections:
                    #print(collection.name)
                    if collection.name[:5].lower() == "cell_":
                        thisVolume = []
                        #print("  REMOVE COLLECTION " + collection.name)
                        for obj in collection.all_objects:
                            #print("    ADD TO COLL AND REMOVE FROM SELECTED OBJECTS " + obj.name)
                            thisVolume.append(obj)
                            try:    objects.remove(obj)
                            except: pass
                        VolumeColls.append(thisVolume)

                # To mimic the original exporter as closely as possible
                # We itterate over the entire scene for each section of the PASM file
                # One loop for lights, one for geo, one for cells, and so on
	       
                if(self.m_bExportLights):
                    for obj in objects:
                        ExportObjLight(obj)
                
                if(self.m_bExportObjects):
                    for obj in objects:
                        ExportObjObject(obj)
	
                # Fog got deprecated and moved to level .csv
                #for obj in objects:
                #    ExportObjFog(obj)
	
                for obj in objects:
                    ExportObjShape(obj)

                for obj in objects:
                    ExportObjVolume(obj)
                for Volume in VolumeColls:
                    ExportObjVolume(Volume)
                    
                for obj in objects:
                    ExportObjPortal(obj)
                
                if(self.m_bExportGeo):                
                    for obj in objects:
                        ExportObjGeo(obj, False)
                
                # Go back to the start and rewrite the header with correct data
                g_class.file.seek(0)
                g_class.file.write(g_class.gApeHeader.packBytes())
              
            # Did we encounter any errors?
            if(g_class.bShowErrorLog): os.startfile(g_class.fpErrorLog)
            
            print("WLD Export Finished!")
            self.report({'INFO'}, "WLD Export Finished!")
        
            return {'FINISHED'}
                
def exportWLD_MenuFunc(self, context):
    self.layout.operator(
        ExportWLD.bl_idname, text="Metal Arms Pasm Wld (.wld)")