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
    if a value is a string, it switches the model of the sprite
    if a value is an int, it represents a delay in milliseconds
"""

# below is a dict made to identificate functions that need to be executed in their main thread
# when a thread need a func to be executed in its origin thread, an entry of that dict with the origin's
# thread id is made and its value is a list that acts like a queue of funcs
funcs_exec_queue = {}

# var used to make sure two sprites don't have the same idea
id_increment = 1

class Sprite:
    """Visual object, contains all of its data and its TKinter widget."""

    def __init__(self, game_instance: object, parent_frame: object, model: dict, current_image_name: str, pos: tuple, scale: tuple):
        """
        game_instance: The instance of the game currently running
        parent_frame: TKinter frame, basically anything that withstand the creation of labels
        model: dict, made as described above
        pos/scale: tuples of 2 positive ints
        """
        global id_increment

        self.game_instance = game_instance
        self.main_thread_id = game_instance.tkinter_thread_id

        self.id = id_increment
        id_increment += 1

        self.parent_frame = parent_frame
        self.model = model
        self.current_image_name = current_image_name

        self.mirrored = False
        self.flipped = False

        self.pos = pos
        self.scale = scale

        self.is_shown = True

        self.sequence_thread = None
        self.stop_current_sequence = False # flag used to stop the currently playing sequence
        self.current_sequence = None # name of the sequence playing (str), None otherwise
        self.sequence_time_factor = 1

        self.widget = None
        self.set_current_image(current_image_name)


    def set_model(self, model: dict, current_image_name: str):
        """
        model: dict, made as described above
        -> {"images": {"img1": IMG_object, ...}, "sequences": {"seq1": [1,2,3,4], ...}}
        current_image_name: str, name of the current image, has to be in the "images" dict
        """

        self.model = model
        self.current_image_name = current_image_name

        self.set_current_image(current_image_name)

    def change_image(self, new_image_name: str):
        """
        Internal func that deletes the sprite's widget to recreate it with a different appearance.

        new_image_name: str, key of the "images" dict contained in a model dict
        """

        if not self.widget is None: self.widget.destroy()

        new_image = self.model["images"][new_image_name].resize(self.scale) # creates a resized copy of the original image

        if self.mirrored: new_image = ImageOps.mirror(new_image)
        if self.flipped: new_image = ImageOps.flip(new_image)

        new_image_tk = ImageTk.PhotoImage(image = new_image)

        self.widget = tkinter.Label(self.parent_frame, image = new_image_tk)
        self.widget.image = new_image_tk
        x, y = self.pos 
        self.widget.place(anchor = "center", x=x, y=y) # places the widget at the given coordinates
        
    def set_current_image(self, new_image_name: str):
        """
        Calls the change_image func and makes it execute in the tkinter thread of the game.
        
        new_image_name: str, key of the "images" dict contained in a model dict
        """

        self.current_image_name = new_image_name
        if not self.is_shown: return

        if not self.main_thread_id in funcs_exec_queue: funcs_exec_queue[self.main_thread_id] = []

        # puts in the funcs queue a function that changes the sprite model
        funcs_exec_queue[self.main_thread_id] += [lambda: self.change_image(new_image_name)]


    def set_scale(self, new_scale: tuple):
        """new_scale: tuple of 2 positive ints"""

        self.scale = new_scale
        if self.widget is None: return

        self.set_current_image(self.current_image_name)

    def set_pos(self, new_pos: tuple):
        """new_scale: tuple of 2 positive ints"""

        self.pos = new_pos
        if self.widget is None: return

        x, y = new_pos
        self.widget.place(anchor = "nw", x=x, y=y)


    def show(self):
        """Makes the widget reappear on the TK window"""

        self.is_shown = True

        self.set_current_image(self.current_image_name)

    def hide(self):
        """Makes the widget disappear from the TK window."""

        self.is_shown = False

        self.destroy()


    def play_sequence(self, sequence_name: str):
        """
        Starts the execution of a sequence, as described in the model dict description.

        sequence_name: str, name of the sequece in the "sequences" dict of the model dict
        """
        global funcs_exec_queue

        index = 0
        sequence_ref = self.model["sequences"][sequence_name]
        sequence_len = len(sequence_ref)

        # repeats if the sequence is a loop or until its end, also checks if the sequence should keep executing
        while (self.model["sequences"][sequence_name][0] or index < sequence_len) and (not self.stop_current_sequence) and self.is_shown:
            if index >= sequence_len: index = 0
            
            instr = sequence_ref[index]
            if isinstance(instr, int): # if the instruction is a delay
                sleep(instr/1000 / self.sequence_time_factor)
            elif isinstance(instr, str): # if the instruction is a model swap
                self.set_current_image(instr)

            index += 1

        self.stop_current_sequence = False # resets the flag
        self.current_sequence = None

    def start_sequence(self, sequence_name: str):
        """
        Triggers the start of the execution of a sequence in a new thread.

        sequence_name: str, name of the sequence to be started from the "sequences" dict in the model dict
        """
        if not self.current_sequence is None: return

        self.current_sequence = sequence_name
        self.stop_current_sequence = False # make sure the flag is reset before the start of the sequence

        self.sequence_thread = threading.Thread(name = str(self.id)+"_"+self.current_sequence, target = lambda: self.play_sequence(sequence_name))
        self.sequence_thread.start() # no need for internal queue since all of the sprite's render func are called in the main thread

    def stop_sequence(self):
        """Triggers the stop sequence flag if one is running."""

        if not self.current_sequence is None: # if a sequence is running
            self.stop_current_sequence = True # triggers the stop sequence flag


    def destroy(self):
        """Pretty much self explanatory."""

        self.widget.destroy()