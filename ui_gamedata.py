# Module that adds a text input window under the 

# BLENDER UI
import bpy # Blender Internal
import gpu # Low Level Graphics Drawing
import blf # Font drawing

from gpu_extras.batch import batch_for_shader
        
class MAGD_Operator(bpy.types.Operator):
    """(Part of Metal Arms PASM Toolkit Add-on)
Multi line text field for inputting gamedata (Entity parameters) associated with the selected object.
Recreation of the Object Properties window from 3DS MAX 5 using Dear Imgui"""
    bl_idname = "object.ma_ui_gamedata"
    bl_label = "MA Gamedata"
    bl_description = "Input Panel for Metal Arms Entity Parameters"
    
    _caret_pos = 0
    currentObj = None
    
    # Drawing a 2D rectangle
    # https://docs.blender.org/api/current/gpu.html#d-rectangle
    
    pos    = [100, 100] # The X Y position on the screen starting from bottom left
    width  = 300 # How many pixels wide the panel is
    height = 400 # How many pixels tall the panel is
    
    vertices = (
        (pos[0], pos[1]),          (pos[0] + width, pos[1]),
        (pos[0], pos[1] + height), (pos[0] + width, pos[1] + height))
    
    indices = (
        (0, 1, 2), (2, 1, 3))
    
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
    
    import blf
    
    handler = None
    
    def draw_callback_px(self, context, extra):
        """Draw on the viewports"""
        self.currentObj = bpy.context.active_object
        
        # Draw the BG Panel first
        self.shader.uniform_float("color", (0.05, 0.05, 0.05, 1.0))
        self.batch.draw(self.shader)
        
        # Then draw the Panel Header Text
        font_id = 0 # Default font
        blf.position(font_id, 200, 475, 0)
        blf.size(font_id, 16.0)
        blf.color(font_id, 1.0, 1.0, 1.0, 1.0)
        blf.draw(font_id, "MA Gamedata")
        
        # Draw the controls for the gamedata panel
        blf.position(font_id, 200, 700, 0)
        blf.size(font_id, 16.0)
        blf.color(font_id, 1.0, 1.0, 1.0, 1.0)
        # Give a little drop shadow in case we draw white on white
        blf.enable(font_id, 4)
        blf.shadow_offset(font_id, 1, -1)
        
        controlLines = [
        "Left Arrow - Previous Character", 
        "Right Arrow - Next Character", 
        "CTRL + Left Arrow - Previous Line", 
        "CTRL + Right Arrow - Next Line", 
        "CTRL + C - Save to clipboard", 
        "CTRL + V - Paste from clipboard",
        "Left / Right Click or ESC - Close",
        ]
        
        lineOffset = [110, 500 + (len(controlLines) * 16)]
        for line in controlLines:
            blf.position(font_id, lineOffset[0], lineOffset[1], 0)
            blf.draw(font_id, line)
            lineOffset[1] -= 18
            
        blf.disable(font_id, 4)
        
        # After draw the name of the object we are editing
        blf.position(font_id, 110, 435, 0)
        blf.size(font_id, 16.0)
        blf.color(font_id, 1.0, 1.0, 1.0, 1.0)
        blf.draw(font_id, "Editing: " + self.currentObj.name)
        
        # Next draw the gamedata parameters
        blf.position(font_id, 110, 400, 0)
        blf.size(font_id, 16.0)
        blf.color(font_id, 1.0, 1.0, 1.0, 1.0)
        
        if self.currentObj == None:
            blf.draw(font_id, "No Object Selected")
            return
            
        lines = bpy.data.objects[self.currentObj.name]["ma"].split("\n")
        
        lineOffset = [110, 400]
        for line in lines:
            blf.position(font_id, lineOffset[0], lineOffset[1], 0)
            blf.draw(font_id, line)
            lineOffset[1] -= 18
            
        # We add a newline to every character so we can hover over the last character
        for line in range(len(lines)):
            lines[line] += '\n'

        # Draw the caret
        caretRow = self._caret_pos
        subCaretPos = 0
        for idx, line in enumerate(lines):
            if caretRow > len(line): # We aren't on this row, advance forward
                caretRow -= len(line)
            elif caretRow == len(line): # We are assuming here we are on the last line
                subCaretPos = 0
                caretRow = len(lines)-1
                break
            else: # If the count isn't bigger than the line we are on this row
                subCaretPos = caretRow
                caretRow = idx
                break
                
        #print(lines)
        #print(caretRow, subCaretPos, self._caret_pos)
        width, height = blf.dimensions(0, lines[caretRow][:subCaretPos])
        lineOffset[1] = 400 - (18 * caretRow)
        lineOffset[0] = 110 + width
        blf.position(font_id, lineOffset[0], lineOffset[1], 0)
        blf.draw(font_id, "|")
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None 
    
    def modal(self, context, event):
        context.area.tag_redraw()
        
        self.currentObj = bpy.context.active_object
        
        # If this is ascii key presses, add the keys to the string
        if event.ascii:
            bpy.data.objects[self.currentObj.name]["ma"] = bpy.data.objects[self.currentObj.name]["ma"][:self._caret_pos] + event.ascii + bpy.data.objects[self.currentObj.name]["ma"][self._caret_pos:]
            self._caret_pos += 1
           
        # If we are backspacing we are deleting a single character from the string
        if event.type == 'BACK_SPACE' and event.value == 'PRESS':
            if len(bpy.data.objects[self.currentObj.name]["ma"]) != 0 and self._caret_pos != 0:
                bpy.data.objects[self.currentObj.name]["ma"] = bpy.data.objects[self.currentObj.name]["ma"][:self._caret_pos-1] + bpy.data.objects[self.currentObj.name]["ma"][self._caret_pos:]
                self._caret_pos -= 1
            
        # If we press Enter / Return we are adding a newline to the input
        if event.type == 'RET' and event.value == 'PRESS':
            bpy.data.objects[self.currentObj.name]["ma"] = bpy.data.objects[self.currentObj.name]["ma"][:self._caret_pos] + '\n' + bpy.data.objects[self.currentObj.name]["ma"][self._caret_pos:]
            self._caret_pos += 1
        
        # If we press CTRL + C, we want to copy the gamedata to our clipboard
        if event.ctrl and event.type == 'C' and event.value == 'PRESS':
            bpy.context.window_manager.clipboard = bpy.data.objects[self.currentObj.name]["ma"]
        
        # If we press CTRL + V, we want to add the contents of our clipboard
        if event.ctrl and event.type == 'V' and event.value == 'PRESS':
            bpy.data.objects[self.currentObj.name]["ma"] += bpy.context.window_manager.clipboard
            self._caret_pos += len(bpy.context.window_manager.clipboard)
            
        # Move the cursor right
        if event.type == 'RIGHT_ARROW' and event.value == 'PRESS':
            self._caret_pos += 1
            if self._caret_pos > len(bpy.data.objects[self.currentObj.name]["ma"]):
                self._caret_pos = len(bpy.data.objects[self.currentObj.name]["ma"])
            
        # Move the cursor left
        if event.type == 'LEFT_ARROW' and event.value == 'PRESS':
            self._caret_pos -= 1
            if self._caret_pos <= 0:
                self._caret_pos = 0
                
        # Move the cursor left to the previous line
        if event.ctrl and event.type == 'LEFT_ARROW' and event.value == 'PRESS':
            newLineIdx = bpy.data.objects[self.currentObj.name]["ma"].rfind('\n', 0, self._caret_pos)   
            if self._caret_pos != -1 and newLineIdx < self._caret_pos:
                self._caret_pos = newLineIdx
            if self._caret_pos <= 0:
                self._caret_pos = 0
         
        # Move the cursor right to the previous line
        if event.ctrl and event.type == 'RIGHT_ARROW' and event.value == 'PRESS':
            newLineIdx = bpy.data.objects[self.currentObj.name]["ma"].find('\n', self._caret_pos)   
            if newLineIdx == -1:
                self._caret_pos = len(bpy.data.objects[self.currentObj.name]["ma"])
            elif newLineIdx > self._caret_pos:
                self._caret_pos = newLineIdx        
            if self._caret_pos > len(bpy.data.objects[self.currentObj.name]["ma"]):
                self._caret_pos = len(bpy.data.objects[self.currentObj.name]["ma"])

        # If we press any of these buttons kill the modal to exit this state
        if event.type in {'LEFTMOUSE', 'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            # the arguments we pass the the callback
            args = (self, context)
            # Add the region drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

            self.currentObj = bpy.context.active_object
            
            if "ma" not in bpy.data.objects[self.currentObj.name]:    
                bpy.data.objects[self.currentObj.name]["ma"] = ""
            
            self._caret_pos = len(bpy.data.objects[self.currentObj.name]["ma"])
            
            # Perhaps this could be a context.window_manager.popup_menu
            # So it can remain in the corner of the screen?
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
    

def MAGD_MenuFunc(self, context):
    self.layout.separator()
    col = self.layout.column()
    self.layout.operator_context = 'INVOKE_DEFAULT'
    col.operator(MAGD_Operator.bl_idname, icon="TEXT")