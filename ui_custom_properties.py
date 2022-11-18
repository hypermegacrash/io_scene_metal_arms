# Module that adds a text input window under the 

# Native Blender
import bpy
from bpy.types import VIEW3D_MT_object_context_menu # We need access to the context menu struct
from bpy.types import Operator

# Imgui
from .thirdparty import blender_imgui
import imgui

class MAImgui(Operator,blender_imgui.ImguiBasedOperator):
    """(Part of Metal Arms PASM Toolkit Add-on)
Multi line text field for inputting gamedata (Entity parameters) associated with the selected object.
Recreation of the Object Properties window from 3DS MAX 5 using Dear Imgui"""
    bl_idname = "object.ma_imgui_example"
    bl_label = "MA Gamedata"
 
    def draw(self, context):
        # This is where you can use any code from pyimgui's doc
        # see https://pyimgui.readthedocs.io/en/latest/
        imgui.set_next_window_size(300, 400, imgui.APPEARING)
        imgui.set_next_window_position((context.window.width/2) - 100, (context.window.height/2) - 200, imgui.APPEARING )
        self.window = imgui.begin("MA Gamedata", True)
        imgui.text("Editing: " + self.obj.name)
        #imgui.text("User Defined Properties:")
        changed, bpy.data.objects[self.obj.name]["ma"] = imgui.input_text_multiline(
            '',
            bpy.data.objects[self.obj.name]["ma"],
            2056,
            imgui.get_window_width() - 15,
            imgui.get_window_height() - 70
        )
        imgui.end()
        
    def invoke(self, context, event):
        #print("invoke is a go")
        # @Bug If there are no objs in the scene this will crash
        self.obj = bpy.context.active_object
        # Call init_imgui() at the beginning
        self.init_imgui(context)
        context.window_manager.modal_handler_add(self)
        
        # Get current object for custom property
        self.obj = bpy.context.active_object
        #print(self.obj.name)
        try:
            print(bpy.data.objects[self.obj.name]["ma"])
        except:
            #print("no ma custom properties for this object")
            bpy.data.objects[self.obj.name]["ma"] = ""
        return {'RUNNING_MODAL'}
        
    def modal(self, context, event):
        context.area.tag_redraw()
          
        # Wrapping in a try except prevents annoying error message
        try:
            if self.window[1] == False:
                # Call shutdown_imgui() any time you'll return {'CANCELLED'} or {'FINISHED'}
                self.shutdown_imgui()
                return {'CANCELLED'}
        except:
            None

        # Don't forget to call parent's modal:
        self.modal_imgui(context, event)
        return {'RUNNING_MODAL'}

def MAGUI_MenuFunc(self, context):
     col = self.layout.column()
     self.layout.operator_context  = 'INVOKE_DEFAULT'
     col.operator(MAImgui.bl_idname)