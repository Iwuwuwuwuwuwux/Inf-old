import tkinter as tk
from time import sleep


"""
A grid map is a 2D list containing the tiles' entities and sprites in a list.

IT SHOULD ONLY HAVE ENTITIES.
"""

# below is a dict made to identificate functions that need to be executed in their main thread
# when a thread need a func to be executed in its origin thread, an entry of that dict with the origin's
# thread id is made and its value is a list that acts like a queue of funcs
funcs_exec_queue = {}
funcs_exec_queue_availible = {}

class Level:
    """
    Parent class of other levels, allows these to have a predefined template and possibility to override/add
    functions if necessary.

    funcs override particularities:
    __init__(self, game_instance) - has to have "game_instance" as parameter, and call the function self.initialize(game_instance)
    create(self) - has to call the self.create_render_frame() func
    """
    
    def initialize(self, game_instance: object, grid_dimensions: tuple) -> None:
        """
        Mandatory function to be executed in the init of any level, makes sure all attributes of the class
        are at least created so that there is no error.

        grid_dimensions: tuple of 2 ints, number of tiles of the game grid, x and y

        Note: the grid system is used to prevent unecessary for loops when lookings for objects using their coordinates.
        """

        self.game_instance = game_instance

        self.name = "Untitled"
        self.description = "No description."
        self.thumbnail = None # PIL Image
        
        self.type = "level"
        self.frame = None

        game_scale = self.game_instance.frame_size
        tile_scale = (int(game_scale[0] / grid_dimensions[0]), int(game_scale[0] / grid_dimensions[1]))
 
        self.tile_scale = tile_scale
        self.grid_dimensions = grid_dimensions

        self.init_data()
        self.walls_map = [[False for _ in range(self.grid_dimensions[0])] for _ in range(self.grid_dimensions[1])]

    def init_data(self) -> None:
        """Creates/clears the sounds/binds/objects/grid_map dict."""

        self.sounds = {}

        self.objects = [] # stores the entities/UI/sprites
        self.grid_map = [[[] for _ in range(self.grid_dimensions[0])] for _ in range(self.grid_dimensions[1])]        

    def __init__(self, game_instance: object) -> None:
        """
        Can only have game_instance as parameter.

        Has to call self.initialize(game_instance)
        """
        self.initialize(game_instance, (50, 50))


    def move_grid_object(self, obj_ref: object, old_coords: tuple, new_coords: tuple) -> None:
        """
        Moves the given object on the grid, doesn't change the object's internal coordinates.

        obj_ref: object, reference of the object
        old_coords: x and y (ints), past coordinates of the object
        new_coords: x and y (ints), new coordinates of the object
        """

        oc_x, oc_y = old_coords
        nc_x, nc_y = new_coords
    
        old_coords_tile_ref = self.grid_map[oc_y][oc_x] # for optimization, ref of the tile at the old coordinates
        obj_index = None
        for i in range(len(old_coords_tile_ref)):
            if old_coords_tile_ref[i] == obj_ref:
                obj_index = i
        if obj_index is None: return # if the object isn't on the tile at the old coordinates

        self.grid_map[nc_y][nc_x] += [obj_ref] # adds the object's ref to the new tile
        del self.grid_map[oc_y][oc_x][obj_index] # deletes the reference of the object at the old coordinates

    def check_tile_availible(self, coords: tuple) -> bool:
        """
        Returns wether the tile contains an object with collisions enabled (if it's an entity), or a wall.

        coords: tuple of 2 ints, x and y
        """

        x, y = coords
        tile_data = self.grid_map[y][x]

        for obj in tile_data.values(): # checks if an object with collisions enabled is on the tile
            if obj.type == "entity":
                if obj.collisions: return False

        return self.walls_map[y][x]
    

    def add_bind(self, command: str, callback) -> None:
        """
        Adds a bind.

        list of given commands -> https://www.tcl.tk/man/tcl8.4/TkCmd/bind.html

        command: str, the bind's tkinter command
        callback: function, the function to be executed
        """

        if self.frame in self.game_instance.binds: # global binds cannot be overriden
            if command in self.game_instance.binds[self.frame]:
                return

        self.frame.bind(command, callback, self)
    
    def remove_bind(self, command: str) -> None:
        """
        Removes a bind.

        command: str, the bind's tkinter command
        """

        self.frame.unbind(command, self)


    def create_render_frame(self) -> None:
        """
        Function that creates the background frame of a level when called.
        Mandatory.

        Modifies the value of self.frame
        """
        global funcs_exec_queue, funcs_exec_queue_availible

        self.game_instance.is_ingame = True

        tk_thrd_id = self.game_instance.tkinter_thread_id        
        game_inst = self.game_instance # for simplification purposes
        w, h = game_inst.frame_size

        def f(): # ghost func
            self.frame = LevelCanvas(game_inst.frame, w = w, h = h)
            self.frame.place(x = 0, y = 0, anchor = "nw")

            self.frame.tkinter_thread_id = tk_thrd_id

        while not funcs_exec_queue_availible[tk_thrd_id]: sleep(0.001)
        funcs_exec_queue[tk_thrd_id] += [f] # pushes the function into the exec queue

        while self.frame is None: sleep(0.01) # made to ensure that next calls will be able to use the canvas

    def create(self) -> None:
        """
        Creates the level and its render context.
        The level has to be already initalized first for this function to work properly.
        
        Override this function to create all of the entities/binds/... of your level.
        Has to call self.create_render_frame()
        """

        self.create_render_frame()

    def destroy(self) -> None:
        """
        Removes every objects from the level and destroys its frame.
        """

        for sound in self.sounds.values():
            sound.stop()
        for obj in self.objects:
            obj.destroy()

        self.init_data()

        self.frame.destroy()

        self.game_instance.is_ingame = False



class LevelCanvas (tk.Canvas):
    """Adds functionnalities to the tkinter canvas class (makes possible the handling of several funcs for the same bind)."""

    def __init__(self, parent_frame, w, h):
        self.tkinter_thread_id = parent_frame.tkinter_thread_id
        self.binds = {}

        super().__init__(parent_frame, width = w, height = h, border = False) # calls constructor of parent class
        self.configure(border = False)

        self.destroyed = False


    def event_handler(self, event, command: str) -> None:
        """Handles the execution of several functions for the same bind."""

        defined_callbacks = dict(self.binds[command])

        for ref in defined_callbacks:
            defined_callbacks[ref](event)


    def bind_tk_func(self, command):
        """Internal function called inside of the tkinter main thread."""

        if self.destroyed: return

        super().bind(command, lambda event: self.event_handler(event, command)) # calls the base class bind function

    def bind(self, command: str, callback: object, ref: object) -> None:
        """Overrides default TKinter Canvas' bind function."""

        if not command in self.binds: # if there is no assigned bind to the specified tkinter event
            self.binds[command] = {}

            while not funcs_exec_queue_availible[self.tkinter_thread_id]: sleep(0.001)
            funcs_exec_queue[self.tkinter_thread_id] += [lambda: self.bind_tk_func(command)] # calls the base class bind function

        self.binds[command][ref] = callback # adds the callback in the list of function assigned to the given event

    def unbind(self, command, ref) -> None:
        """Overrides default TKinter Canvas' unbind function."""

        if ref in self.binds[command]:
            del self.binds[command][ref]

    
    def destroy_tk_func(self) -> None:
        """Called inside of the tkinter main thread."""

        for command in self.binds:
            self.binds[command] = {}

            super().unbind(command)
        self.binds = {}
        
        super().destroy()

    def destroy(self) -> None:
        """Destroys the widget in the right way."""

        self.destroyed = True

        while not funcs_exec_queue_availible[self.tkinter_thread_id]: sleep(0.001)
        funcs_exec_queue[self.tkinter_thread_id] += [self.destroy_tk_func]