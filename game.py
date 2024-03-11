import threading
import tkinter as tk
import os
from time import sleep
import sys

import modules.level as level
import modules.sprite as sprite
import modules.entity as entity

tkinter_thread_id_counter = 1 # only modified internally, do not change

class Game:
    """
    Parent class of the game instance.
    Override functions inside of a child object to implement functionalities.

    Overridable functions particularities:
    __init__(self, game_instance) - has to have "game_instance" as parameter, and call the function self.initialize(game_instance)
    """

    def initialize(self, game_name: str = "Untitled game", frame_size: tuple = (500, 500), debug: bool = False) -> None:
        """
        Initializes the parameters of the game instance.
        Has to be called in the init function of the class.
        Mandatory function.

        Also creates the game's window.

        game_name: (str), name of the game
        frame_size: (tuple), scale of the window
        """
        global tkinter_thread_id_counter

        self.game_name = game_name
        self.type = "game_engine"
        self.debug = debug

        self.menu_objects = {}
        self.global_objects = {}

        self.binds = {}
        self.sounds = {}

        self.frame = None
        self.frame_size = frame_size

        self.current_level = None
        self.is_running = True
        self.is_ingame = False

        self.internal_tk_exec_queue = []
        self.internal_tk_exec_queue_availible = False

        self.internal_tk_exec_queue_postprocess = []
        self.internal_tk_exec_queue_postprocess_availible = False

        self.tkinter_thread_id = tkinter_thread_id_counter
        self.tkinter_render_thread = threading.Thread(name = "game_instance_{}_tkinter_thread".format(tkinter_thread_id_counter), target = self.update_frame)
        tkinter_thread_id_counter += 1

        self.temp_stop = True
        self.tkinter_render_thread.start()

        while self.temp_stop: sleep(0.001) # waits for the tkinter thread to initialize before proceiding

        # imports the levels
        self.levels = {}

        sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/levels") # allows import from the levels folder
        for file_data in os.listdir("levels/"):
            file_data = file_data.split(".")
            if len(file_data) == 1: continue # if the object is a directory, pass
            
            file_name = file_data[0]
            file_extension = file_data[1]
            if file_extension != "py": continue # if the file isn't a python file
            if file_name[0] != "L": continue # levels that will be loaded start with the caracter L

            # levels are identified in the dict by their file's name, because two files
            # can't have the same name (= uniqueness constraint)
            level_imported = __import__(file_name)
            level_object = level_imported.CLevel(self)
            self.levels[file_name] = level_object 

    def __init__(self) -> None:
        """
        Has to call self.initialize()
        """     
        self.initialize("Untitled Game")

        self.draw_menu()


    def queue_function(self, function: object) -> None:
        """Executes a function inside of the tkinter thread (internal queue)."""

        while not self.internal_tk_exec_queue_availible: sleep(0.001)
        self.internal_tk_exec_queue += [function]

    def queue_function_postprocess(self, function: object) -> None:
        """Executes a function inside of the tkinter thread (internal postprocess queue)."""

        while not self.internal_tk_exec_queue_postprocess_availible: sleep(0.001)
        self.internal_tk_exec_queue_postprocess += [function]


    def create_menu_canvas(self, name: str, x: int, y: int, width: int, height: int) -> object:
        """
        Used for simplification of the process of creating the background of the menu.
        Assigns the "canvas" entry of the menu_objects dict to the created object.
        Waits until it is created before returning.

        name: str, name under which the LevelCanvas object stored will be in the self.menu_objects dict
        x/y/width/height: ints

        Returns: the LevelCanvas object.
        """

        def f(): # ghost func
            canvas = level.LevelCanvas(self.frame, width, height)
            canvas.place(x = x, y = y, anchor = "nw")

            return canvas
        
        if not threading.get_ident() == self.tkinter_render_thread.ident: # if this func is not executed inside of the tkinter thread
            self.assign_menu_object_queued(name, f)
            self.wait_menu_object_creation(name)
        else:
            self.menu_objects[name] = f()

        return self.menu_objects[name]

    def delete_menu_widget_queued(self, name: str) -> None:
        """Deletes a widget from the menu_objects dict."""

        if name in self.menu_objects:
            widget = self.menu_objects[name]
            del self.menu_objects[name]

            if widget.winfo_exists() == 1: # if the widget hasn't been destroyed yet
                if threading.get_ident() == self.tkinter_render_thread.ident: # if this func is executed inside of the tkinter thread
                    widget.destroy()
                else:
                    self.queue_function_postprocess(widget.destroy)

    def assign_menu_object_queued(self, name: str, function: object) -> None:
        """
        Executed in the tkinter main thread. Assigns self.menu_objects[name] to what's returned by the given function.
        Makes sure the given function is executed at the very start of the frame's computation
        """

        def f(): # ghost func
            self.menu_objects[name] = function()

        self.queue_function(f)

    def assign_menu_object_queued_postprocess(self, name: str, function: object) -> None:
        """
        Executed in the tkinter main thread. Assigns self.menu_objects[name] to what's returned by the given function.
        Makes sure the given function is executed at the very end of the frame's computation.
        """

        def f(): # ghost func
            self.menu_objects[name] = function()

        self.queue_function_postprocess(f)

    def wait_menu_object_creation(self, name: str) -> None:
        """
        Forces the program to wait until an entry with the given name is created in the menu_objects dict.
        DO NOT CALL INSIDE OF A BIND RELATED CALLBACK OF ANY TKINTER OBJECT (infinite loop)
        
        name: str, name of the entry to wait for
        """

        while not name in self.menu_objects: sleep(0.01)


    def draw_menu(self) -> None:
        """
        Overridable function.
        """

        pass

    def exit_menu(self) -> None:
        """
        Overridable function.
        """

        pass


    def add_bind(self, command: str, callback) -> bool:
        """
        Adds a bind in the main window.
        Clicks binds aren't useful/recommended inside of this context.
        For binds only used in the menu, prefer declaring these inside the self.draw_menu() function.

        list of given commands -> https://www.tcl.tk/man/tcl8.4/TkCmd/bind.html

        command: str, the bind's tkinter command
        callback: function, the function to be executed

        returns:
        bool: whether the binds was created or not
        """

        if command in self.binds: return False
        
        self.binds[command] = callback
        self.frame.bind(command, callback)

        return True

    def remove_bind(self, command: str) -> bool:
        """
        Removes a bind from the main window.

        command: str, the bind's tkinter command

        returns:
        bool: whether the binds was deleted or not
        """
        
        if not command in self.binds: return False

        self.frame.unbind(command)

        return True


    def exec_queue(self, queue: list) -> None:
        """Internal function that execute each function of the given queue."""

        try:
            for function in queue:
                if self.debug: print(function)

                function()

        except:
            print("////////// Error during last frame ({}), queue exited prematurely.".format(self.frames_counter))

    def update_frame(self) -> None:
        """
        Function that refreshes the content of the tkinter frame.
        Also creates the TKinter window.
        Made to get a frame rate of around 20 frame/sec.

        Internal function, used by the TKinter thread.
        """

        tkinter_thread_id = self.tkinter_thread_id # used to avoid constant repetitions

        self.internal_tk_exec_queue_availible = True
        level.funcs_exec_queue[tkinter_thread_id] = []
        level.funcs_exec_queue_availible[tkinter_thread_id] = True
        sprite.funcs_exec_queue[self.tkinter_thread_id] = []
        sprite.funcs_exec_queue_availible[self.tkinter_thread_id] = True
        self.internal_tk_exec_queue_postprocess_availible = True


        self.frame = tk.Tk()
        self.frame.tkinter_thread_id = tkinter_thread_id
        self.frame.title(self.game_name)

        x, y = self.frame_size
        self.frame.geometry("{}x{}".format(x, y))
        self.frame.resizable(width = False, height = False)

        self.temp_stop = False
        
        self.frames_counter = 0
        while self.is_running:
            self.frames_counter += 1
            if self.debug: has_executed = False
            
            # Repetitions in this section are necessary to improve the repartition of requests.
            # DO NOT TRY TO "OPTIMIZE" THIS SECTION, IT WAS INTENTIONNALY MADE REDUNDANT TO FIX ISSUES AND SAVE FRAME TIME

            # ----- internal queue execution -----
            self.internal_tk_exec_queue_availible = False

            requests = self.internal_tk_exec_queue
            self.internal_tk_exec_queue = []

            self.internal_tk_exec_queue_availible = True

            if self.debug:
                if len(requests) != 0:
                    print("Executing internal requests ({} calls)...".format(len(requests)))
                    has_executed = True

            self.exec_queue(requests)


            # ----- level queue execution -----
            level.funcs_exec_queue_availible[tkinter_thread_id] = False

            requests = level.funcs_exec_queue[tkinter_thread_id]
            level.funcs_exec_queue[tkinter_thread_id] = []

            level.funcs_exec_queue_availible[tkinter_thread_id] = True

            if self.debug:
                if len(requests) != 0:
                    print("Executing level's requests ({} calls)...".format(len(requests)))
                    has_executed = True

            self.exec_queue(requests)


            # ----- sprite queue execution -----
            sprite.funcs_exec_queue_availible[tkinter_thread_id] = False

            requests = sprite.funcs_exec_queue[tkinter_thread_id]
            sprite.funcs_exec_queue[tkinter_thread_id] = []

            sprite.funcs_exec_queue_availible[tkinter_thread_id] = True

            if self.debug:
                if len(requests) != 0:
                    print("Executing sprite's requests ({} calls)...".format(len(requests)))
                    has_executed = True

            self.exec_queue(requests)


            # ----- internal postprocess queue execution ------
            self.internal_tk_exec_queue_postprocess_availible = False

            requests = self.internal_tk_exec_queue_postprocess
            self.internal_tk_exec_queue_postprocess = []

            self.internal_tk_exec_queue_postprocess_availible = True

            if self.debug:
                if len(requests) != 0:
                    print("Executing internal postprocess requests ({} calls)...".format(len(requests)))
                    has_executed = True

            self.exec_queue(requests)


            # -----------------------------------------------------

            if self.debug and has_executed: print("End of requests for frame {}. Updating GUI.\n".format(self.frames_counter))
            self.frame.update()
            sleep(0.05)

        if not self.current_level is None: self.current_level.destroy()

        self.frame.destroy()


    def change_level(self, new_level_filename: str):
        """
        Changes the current level.
        If a level is ongoing, destroys it, otherwise hides the main menu.

        new_level_filename: str, name of the new level's file
        """
        if not new_level_filename in self.levels: return

        if self.is_ingame: self.exit_level()
        else: self.exit_menu()

        self.is_ingame = True

        self.current_level = self.levels[new_level_filename]
        self.current_level.create()

    def exit_level(self):
        """
        Exits the current level, if one.
        
        returns:
        bool: whether a level was exited or not
        """
        if self.current_level is None: return

        self.current_level.destroy()
        self.current_level = None

        self.is_ingame = False


    