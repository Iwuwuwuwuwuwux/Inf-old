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

        Overridable function.
        """     
        self.initialize("Untitled Game")

        self.draw_menu()


    def queue_function(self, function: object) -> None:
        """Executes a function inside of the tkinter thread (internal queue)."""

        self.internal_tk_exec_queue += [function]

    def queue_function_postprocess(self, function: object) -> None:
        """Executes a function inside of the tkinter thread (internal postprocess queue)."""

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

        def create_level_canvas(): # ghost func
            canvas = level.LevelCanvas(self.frame, width, height)
            canvas.place(x = x, y = y, anchor = "nw")

            return canvas
        
        if not threading.get_ident() == self.tkinter_render_thread.ident: # if this func is not executed inside of the tkinter thread
            self.assign_menu_widget_queued(name, create_level_canvas)
            while not name in self.menu_objects: sleep(0.01)
        else:
            if self.debug: print("----- Internal priority request: canvas creation (menu)")
            self.menu_objects[name] = create_level_canvas()

        return self.menu_objects[name]

    def delete_menu_widget_queued(self, name: str) -> bool:
        """
        Deletes a widget from the menu_objects dict.
        
        returns: if the object has been or was already deleted
        """

        if name in self.menu_objects:
            widget = self.menu_objects[name]
            del self.menu_objects[name]

            if widget.winfo_exists() == 1: # if the widget hasn't been destroyed yet
                self.queue_function_postprocess(widget.destroy)

            return True

        else:
            return False

    def assign_menu_widget_queued(self, name: str, function: object) -> None:
        """
        Executed in the tkinter main thread. Assigns self.menu_objects[name] to what's returned by the given function.
        Makes sure the given function is executed at the very start of the frame's computation.

        inputs:
        name: str, name of the object that will be stored is the self.menu_objects dict
        function: func, doesn't take any parameter and returns a TKinter/LevelCanvas object.
        """

        def assign_menu(): # ghost func
            self.menu_objects[name] = function()

        self.queue_function(assign_menu)

    def assign_menu_widget_queued_postprocess(self, name: str, function: object) -> None:
        """
        Executed in the tkinter main thread. Assigns self.menu_objects[name] to what's returned by the given function.
        Makes sure the given function is executed at the very end of the frame's computation.
        """

        def assign_menu(): # ghost func
            self.menu_objects[name] = function()

        self.queue_function_postprocess(assign_menu)


    def draw_menu(self) -> None:
        """
        Overridable function.
        """

        pass

    def exit_menu(self) -> None:
        """
        Overridable function.

        Executed when changing level.
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

        returns: if the bind has been created
        """

        if command in self.binds: return False
        
        self.binds[command] = callback
        self.frame.bind(command, callback)

        return True

    def remove_bind(self, command: str) -> bool:
        """
        Removes a bind from the main window.

        command: str, the bind's tkinter command

        returns: if a bind has been deleted
        """
        
        if not command in self.binds: return False

        del self.binds[command]
        self.frame.unbind(command)

        return True


    def update_frame(self) -> None:
        """
        Function that refreshes the content of the tkinter frame.
        Also creates the TKinter window.
        Made to get a frame rate of around 20 frame/sec.

        Internal function, used by the TKinter thread.
        """

        tkinter_thread_id = self.tkinter_thread_id # used to avoid constant repetitions

        level.funcs_exec_queue[tkinter_thread_id] = []
        sprite.funcs_exec_queue[self.tkinter_thread_id] = []


        self.frame = tk.Tk()
        self.frame.tkinter_thread_id = tkinter_thread_id
        self.frame.title(self.game_name)

        x, y = self.frame_size
        self.frame.geometry("{}x{}".format(x, y))
        self.frame.resizable(width = False, height = False)

        self.temp_stop = False
        
        def exec_queue(queues_original: list, debug_names: list):
            """Executes each function of the given queue."""
            queues = []
            for element in queues_original:
                queues += [element.copy()]

            tot_count = 0
            for queue_index in range(len(queues)):
                queue = queues[queue_index]

                func_index = -1 # ensures that even if the queue is empty the var will still be initialized
                #try:
                for func_index in range(len(queue)):
                    if self.debug: print(queue[func_index])

                    queue[func_index]()

                #except:
                #    print("////////// Error during last frame ({}), queue exited prematurely.".format(self.frames_counter))

                if func_index != -1:
                    # ensures that unexecuted functions will be pushed back in the queue may triggers errors but it at least
                    # ensures that the program won't instantly crash at the first encountered error tho it isn't a reason to
                    # intentionnaly make some
                    for _ in range(func_index + 1):
                        queues_original[queue_index].pop(0)

                    tot_count += func_index + 1

                    if self.debug: print("End of {} queue ({} requests executed).".format(debug_names[queue_index], func_index + 1))

            if self.debug and tot_count != 0:
                print("Finished executing frame {}, {} requests executed.\n".format(self.frames_counter, tot_count))


        if self.debug: print("TKinter thread {} initialized, starting requests execution.\n".format(self.tkinter_render_thread.ident))

        self.frames_counter = 0
        while self.is_running and bool(self.frame.winfo_exists()):
            self.frames_counter += 1
            if self.debug: has_executed = False

            # ---------- queues executions ----------

            requests = [
                self.internal_tk_exec_queue,
                level.funcs_exec_queue[self.tkinter_thread_id],
                sprite.funcs_exec_queue[self.tkinter_thread_id],
                self.internal_tk_exec_queue_postprocess
            ]

            exec_queue(requests, ["internal execution", "sprites", "levels", "internal postprocess"])

            self.frame.update()
            sleep(0.05)

        if not self.current_level is None: self.current_level.destroy()

        self.frame.destroy()


    def change_level(self, new_level_filename: str) -> bool:
        """
        Changes the current level.
        If a level is ongoing, destroys it, otherwise destroys the main menu.

        new_level_filename: str, name of the new level's file

        returns: if the level was created
        """
        if not new_level_filename in self.levels:
            if self.debug: print("Level \"{}\" not found.".format(new_level_filename))
            return False

        if self.is_ingame: self.exit_level()
        else: self.exit_menu()

        self.is_ingame = True

        if self.debug: print("Changing level to {}....".format(new_level_filename))

        self.current_level = self.levels[new_level_filename]
        self.current_level.create()

        if self.debug: print("Level created succesfully.")
        return True

    def exit_level(self)-> bool:
        """
        Exits the current level, if one.
        
        returns: if a level was exited
        """
        if self.current_level is None: return False

        self.current_level.destroy()
        self.current_level = None

        self.is_ingame = False

        return True


    