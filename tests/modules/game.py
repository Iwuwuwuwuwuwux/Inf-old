import threading

class Game:
    def __init__(self):
        self.cs_start_func = None
        
        self.cs_show_menu_func = None
        self.cs_exit_menu_func = None
        self.menu_objects = {}

        self.cs_change_level_func = None

        self.global_objects = {}
        self.global_data = {}

        self.binds = {}
        self.levels = {}
        self.sounds = {}

        self.frame = None
        self.tkinter_thread_id = threading.get_ident()

        self.current_level = None
        self.is_running = False
        self.is_ingame = False


    def initialize(self):
        pass


    def draw_menu(self):
        pass


    def exit_menu(self):
        pass


    def set_binds(self):
        pass

    def modify_bind(self):
        pass


    def change_level(self):
        pass


    