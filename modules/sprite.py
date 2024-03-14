import tkinter
import threading
from time import sleep
from PIL import Image, ImageTk, ImageOps


"""A "model" is a dict containing 2 main keys:
- "images": dict of tuples with keys being the name of the image and containing :
    1 : image path
    2 : PIL image object
- "sequences": dict of lists with keys being the sequence's name and containing a sequence data :
    -> THE FIRST VALUE HAS TO BE A BOOL, if True, the animation is a loop and repeats until it is manually stopped
    if a value is a tuple, it switches the image of the sprite (str image name, 1st elt) and set its position (tuple pos, 2nd elt)
    if a value is an int, it represents a delay in milliseconds
"""

# below is a dict made to identificate functions that need to be executed in their main thread
# when a thread need a func to be executed in its origin thread, an entry of that dict with the origin's
# thread id is made and its value is a list that acts like a queue of funcs
funcs_exec_queue = {}
funcs_exec_queue_availible = {}

# var used to make sure two sprites don't have the same idea
id_increment = 1

class Sprite:
    """Visual object, contains all data of the TKinter widget and useful methods for it to be used with."""

    def __init__(self, parent_canvas: object, model: dict, current_image_name: str, pos: tuple, scale: tuple, displacement: tuple = (0, 0)) -> object:
        """
        parent_canvas: TKinter frame, basically anything that withstand the creation of labels
        model: dict, made as described above
        current_image_name: str
        pos/scale/displacement: tuples of 2 positive ints
        """
        global id_increment

        self.main_thread_id = parent_canvas.tkinter_thread_id
        self.type = "sprite"

        self.id = id_increment
        id_increment += 1

        self.parent_canvas = parent_canvas
        self.model = model
        self.current_image = None
        self.current_tk_image = None
        
        self.current_image_name = current_image_name

        self.mirrored = False
        self.flipped = False

        self.displacement = displacement # relative pos, kind of displacement
        self.scale = scale

        self.global_pos = pos
        self.composed_coordinates = (0, 0)

        self.is_shown = True
        self.click_callback = None
        self.hover_callback = None
        self.is_hovered = False

        self.sequence_thread = None
        self.stop_current_sequence = False # flag used to stop the currently playing sequence
        self.current_sequence = None # name of the sequence playing (str), None otherwise
        self.sequence_time_factor = 1

        self.canvas_id = None

        self.move(pos)


    def set_model(self, model: dict, current_image_name: str) -> None:
        """
        model: dict, made as described above
        -> {"images": {"img1": IMG_object, ...}, "sequences": {"seq1": [1,2,3,4], ...}}
        current_image_name: str, name of the current image, has to be in the "images" dict
        """

        self.model = model

        self.set_current_image(current_image_name)

    def change_image(self) -> None:
        """Internal func that deletes the sprite's widget to recreate it with a different appearance."""

        if self.parent_canvas.destroyed: return

        if not self.canvas_id is None: self.parent_canvas.delete(self.canvas_id)
        if not self.is_shown: return

        self.current_tk_image = ImageTk.PhotoImage(image = self.current_image)

        self.canvas_id = self.parent_canvas.create_image(
            self.composed_coordinates[0],
            self.composed_coordinates[1],
            anchor = "nw",
            image = self.current_tk_image
        )

    def mirror_image(self, mirror: bool) -> None:
        """Mirrors the sprite."""
        self.mirrored = mirror

        self.set_current_image(self.current_image_name)

    def flip_immage(self, flip: bool) -> None:
        """Flips the sprite."""
        self.flipped = flip

        self.set_current_image(self.current_image_name)
        
    def set_current_image(self, new_image_name: str) -> None:
        """
        Calls the change_image func and makes it execute in the tkinter thread of the game.
        
        new_image_name: str, key of the "images" dict contained in a model dict
        """
        global funcs_exec_queue, funcs_exec_queue_availible

        self.current_image_name = new_image_name

        new_image = self.model["images"][new_image_name].resize(self.scale) # creates a resized copy of the original image
        if self.mirrored: new_image = ImageOps.mirror(new_image)
        if self.flipped: new_image = ImageOps.flip(new_image)

        self.current_image = new_image

        if not self.is_shown: return

        # puts in the funcs queue a function that changes the sprite model
        while not funcs_exec_queue_availible[self.main_thread_id]: sleep(0.001)
        funcs_exec_queue[self.main_thread_id] += [self.change_image]


    def set_scale(self, new_scale: tuple) -> None:
        """new_scale: tuple of 2 positive ints"""

        self.scale = new_scale

        self.set_current_image(self.current_image_name)

    def set_displacement(self, new_displacement: tuple) -> None:
        """
        Sets the widget's relative pos, kind of displacement from its global position.

        new_scale: tuple of 2 positive ints
        """

        self.displacement = new_displacement

        self.move(self.global_pos)

    def move(self, new_global_pos: tuple):
        """
        Moves the widget on its parent in the tkinter window.

        new_global_pos: tuple of 2 positive ints
        """
        
        self.global_pos = new_global_pos

        ng_x = new_global_pos[0] + self.displacement[0] # new global x with displacement
        ng_y = new_global_pos[1] + self.displacement[1] # new global y with displacement

        self.composed_coordinates = (ng_x, ng_y)

        self.set_current_image(self.current_image_name)

    def is_in_boundaries(self, pos: tuple) -> bool:
        """
        Returns whether the given coordinates are pointing on the area covered by the sprite on screen.
        
        pos: tuple of 2 positive ints
        """

        x, y = pos # checked x and y coordinates
        s_x, s_y = self.composed_coordinates # sprite's x and y coordinates
        ss_x, ss_y = self.scale # sprite's x and y scale

        return (x >= s_x and x <= s_x + ss_x) and (y >= s_y and y <= s_y + ss_y)


    def set_click_callback(self, new_callback) -> None:
        """
        Defines/changes the callback of the sprite when it's clicked.

        new_callback: function, called when the sprite receives a tkinter "clicked" event
        """

        self.click_callback = new_callback

        def f(event): # ghost function
            if self.is_shown and self.is_in_boundaries((event.x, event.y)): # if the sprite is shown and the mouse is in boundaries
                self.click_callback()

        self.parent_canvas.bind("<Button-1>", f, self)

    def remove_click_callback(self):
        """
        Unbinds the click callback from the sprite.
        """

        self.click_callback = None
        
        self.parent_canvas.unbind("<Button-1>", self)

    def set_hover_callback(self, new_callback_hovered, new_callback_released, need_event_coordinates = False) -> None:
        """
        Defines/changes the callback of the sprite when it's hovered with the mouse.
        If need_event_coordinates is set to True, the callbacks will be called with 2 ints passed as parameters, being the
        coordinates of the mouse at the given moment (quit slow so don't try to use that for high speed applications, coordinates
        are relative to the canvas on which the sprite was created).

        new_callback_hovered: function, called when the mouse is over the sprite
        new_callback_released: function, called when the mouse isn't over the sprite anymore
        """

        self.hover_callback = (new_callback_hovered, new_callback_released)

        def f(event): # ghost function
            if self.is_in_boundaries((event.x, event.y)) == self.is_hovered: return
            
            self.is_hovered = not self.is_hovered

            if self.is_shown: # if the sprite is shown
                if need_event_coordinates:
                    if self.is_hovered: self.hover_callback[0](event.x, event.y)
                    else: self.hover_callback[1](event.x, event.y)
                else:
                    if self.is_hovered: self.hover_callback[0]()
                    else: self.hover_callback[1]()

        self.parent_canvas.bind("<Motion>", f, self)

    def remove_hover_callback(self):
        """
        Unbinds the hover callback from the sprite.
        """

        self.hover_callback = None

        self.parent_canvas.unbind("<Motion>", self)


    def show(self) -> None:
        """Makes the widget reappear on the TK window"""

        self.is_shown = True

        self.set_current_image(self.current_image_name)

    def hide(self) -> None:
        """Makes the widget disappear from the TK window. (Destroys it)"""
        global funcs_exec_queue, funcs_exec_queue_availible

        if not self.hover_callback is None: self.hover_callback[1]() # calls the hover released func if defined

        if self.canvas_id is None: return

        self.is_shown = False
        self.stop_sequence()

        id_ref = self.canvas_id
        self.canvas_id = None

        while not funcs_exec_queue_availible[self.main_thread_id]: sleep(0.001)
        funcs_exec_queue[self.main_thread_id] += [lambda: self.parent_canvas.delete(id_ref)]


    def play_sequence(self, sequence_name: str) -> None:
        """
        Executes the sequence, as described in the model dict description.

        sequence_name: str, name of the sequece in the "sequences" dict of the model dict
        """

        index = 0
        sequence_ref = self.model["sequences"][sequence_name]
        sequence_len = len(sequence_ref)

        # repeats if the sequence is a loop or until its end, also checks if the sequence should keep executing
        while (sequence_ref[0] or index < sequence_len) and (not self.stop_current_sequence):
            if index >= sequence_len: index = 0
            
            instr = sequence_ref[index]
            if isinstance(instr, int): # if the instruction is a delay
                sleep(instr/1000 / self.sequence_time_factor)
            elif isinstance(instr, tuple): # if the instruction is a model swap
                self.set_displacement(instr[1])
                self.set_current_image(instr[0])

            index += 1

        self.stop_current_sequence = False # resets the flag
        self.current_sequence = None

    def start_sequence(self, sequence_name: str) -> None:
        """
        Triggers the start of the execution of a sequence in a new thread.

        sequence_name: str, name of the sequence to be started from the "sequences" dict in the model dict
        """

        if not self.current_sequence is None: return # if a sequence is already running

        self.current_sequence = sequence_name
        self.stop_current_sequence = False # make sure the flag is reset before the start of the sequence

        self.sequence_thread = threading.Thread(name = str(self.id)+"_"+self.current_sequence, target = lambda: self.play_sequence(sequence_name))
        self.sequence_thread.start() # no need for internal queue since all of the sprite's render func are called in the main thread

    def stop_sequence(self) -> None:
        """Triggers the stop sequence flag if one is running."""

        if not self.current_sequence is None: # if a sequence is running
            self.stop_current_sequence = True # triggers the stop sequence flag


    def destroy(self) -> None:
        """Pretty much self explanatory."""

        self.hide()