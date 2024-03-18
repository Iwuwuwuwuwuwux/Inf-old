from PIL import Image, ImageTk
from json import dumps, loads
from time import sleep
import tkinter
import threading

import game
import modules.level as level
import modules.sprite as sprite
import modules.entity as entity

from infold.data.menu_models import menu_models, generate_filled_image, generate_menu_models
import infold.data.translations as translations
import infold.settings as settings


class Infold(game.Game):
    """Class containing all of the project's related code."""

    def __init__(self) -> None:
        global menu_models

        self.settings = settings.current_settings # ref, used to allow access to the settings by the levels

        self.texts = translations.translations
        self.text_font = ("Cascadia Code", 15)
        self.sub_text_font = ("Cascadia Code", 12)

        if self.settings["language"] in self.texts:
            generate_menu_models(self.texts[self.settings["language"]])
        else:
            generate_menu_models(self.texts["EN"])
        self.menu_models = menu_models

        self.initialize("Inf'Old: A new start", debug = True) # also initializes the levels
        self.levels_roadmap = ["Niveau 1", "Niveau 2", "Niveau 3", "Niveau 4", "Niveau 5", "EasterEgg"]

        self.draw_menu()


    # -------------------- LANGUAGE FUNCTIONS --------------------

    def get_text(self, name: str) -> str:
        """
        Returns the translation of the given text if found.

        name: str, the entry of the text

        returns: the translated text or a default one
        """

        lang = self.settings["language"]

        if lang in self.texts:
            return self.texts[lang][name]
        else:
            if self.debug: print("Language {} not found, returning default EN text.".format(lang))
            return self.texts["EN"][name]
        
    def select_language(self, new_lang: str) -> bool:
        """
        Changes the language of the game and saves it into the settings.
        
        Returns: if the language has been changed
        """

        if new_lang == self.settings["language"]: return False

        self.settings["language"] = new_lang # also changes the settings.current_settings dict
        settings.save_settings()

        if new_lang in self.texts:
            generate_menu_models(self.texts[new_lang])
        else:
            generate_menu_models(self.texts["EN"])
        if "main_canvas" in self.menu_objects:
            self.exit_menu()
            self.draw_menu()
        self.queue_function(self.open_settings)

        return True

    
    # -------------------- MAIN MENU --------------------

    def draw_menu(self) -> None: 
        # creates the canvas for the buttons/background, made a bit larger than the window to ensure no border
        main_canvas = self.create_menu_canvas("main_canvas", -2, -2, self.frame_size[0]+4, self.frame_size[1]+4)

        # creates the background image of the menu
        self.menu_objects["background_image"] = sprite.Sprite(
            main_canvas,
            self.menu_models["background"],
            "main",
            (0, 0),
            (504, 504)
        )

        self.menu_objects["banner"] = sprite.Sprite(
            main_canvas,
            self.menu_models["banner"],
            "main",
            (0, 50),
            (500, 150)
        )

        self.menu_objects["quit_button"] = sprite.Sprite(
            main_canvas,
            self.menu_models["cross"],
            "main",
            (10, 10),
            (35, 35)
        )
        def quit_game():
            self.is_running = False
        self.menu_objects["quit_button"].set_click_callback(quit_game)

        self.menu_objects["settings_button"] = sprite.Sprite(
            main_canvas,
            self.menu_models["gear"],
            "main",
            (450, 450),
            (40, 40)
        )
        self.menu_objects["settings_button"].set_click_callback(self.open_settings)


        self.menu_objects["play_button"] = sprite.Sprite(
            main_canvas,
            self.menu_models["play"],
            "idle",
            (200, 300),
            (100, 50)
        )
        self.menu_objects["play_button"].set_hover_callback(
            lambda: self.menu_objects["play_button"].set_current_image("hover"),
            lambda: self.menu_objects["play_button"].set_current_image("idle")
        )
        self.menu_objects["play_button"].set_click_callback(lambda: self.change_level(self.settings["progression"]))

        self.menu_objects["levels_button"] = sprite.Sprite(
            main_canvas,
            self.menu_models["levels"],
            "idle",
            (200, 375),
            (100, 50)
        )
        self.menu_objects["levels_button"].set_hover_callback(
            lambda: self.menu_objects["levels_button"].set_current_image("hover"),
            lambda: self.menu_objects["levels_button"].set_current_image("idle")
        )


    # -------------------- SETTINGS MENU --------------------

    def open_settings(self):
        """Functions used by the settings button in the main menu."""

        if "settings_canvas" in self.menu_objects: return # if the settings are already open
        if "main_canvas" in self.menu_objects:
            self.queue_function(self.menu_objects["quit_button"].hide)
            self.queue_function(self.menu_objects["settings_button"].hide)

        settings_canvas = self.create_menu_canvas("settings_canvas", 30, 30, 440, 440)

        self.menu_objects["settings_background"] = sprite.Sprite(
            settings_canvas,
            self.menu_models["background"],
            "main",
            (-32, -32),
            (504, 504)
        )

        def draw_decorations(): # ghost func to be executed in postprocess
            ids = []

            ids += [settings_canvas.create_text(30, 3, text = self.get_text("settings"), fill = "white", font = self.text_font, anchor = "nw")]
            ids += [settings_canvas.create_rectangle(407, 0, 450, 35, outline = "white")]
            ids += [settings_canvas.create_rectangle(0, 0, 450, 35, outline = "white")]

            return ids
        self.assign_menu_widget_queued_postprocess("settings_decorations", draw_decorations) # used to make sure the background isn't hiding it

        self.menu_objects["settings_quit_button"] = sprite.Sprite(
            settings_canvas,
            self.menu_models["cross"],
            "main",
            (415, 10),
            (20, 20)
        )
        self.menu_objects["settings_quit_button"].set_click_callback(self.close_settings)


        self.menu_objects["settings_username_button"] = sprite.Sprite(
            settings_canvas,
            self.menu_models["pseudonyme"],
            "idle",
            (30, 100),
            (150, 30)
        )
        self.menu_objects["settings_username_button"].set_click_callback(self.open_username_menu)
        self.menu_objects["settings_username_button"].set_hover_callback(
            lambda: self.menu_objects["settings_username_button"].set_current_image("hover"),
            lambda: self.menu_objects["settings_username_button"].set_current_image("idle")
        )

        self.menu_objects["settings_reset_progression_button"] = sprite.Sprite(
            settings_canvas,
            self.menu_models["reset_progression"],
            "idle",
            (30, 170),
            (150, 30)
        )
        def reset_progression():
            self.settings["progression"] = "LNiveau1"
        self.menu_objects["settings_reset_progression_button"].set_click_callback(reset_progression)
        self.menu_objects["settings_reset_progression_button"].set_hover_callback(
            lambda: self.menu_objects["settings_reset_progression_button"].set_current_image("hover"),
            lambda: self.menu_objects["settings_reset_progression_button"].set_current_image("idle")
        )

        self.menu_objects["settings_all_access_button"] = sprite.Sprite(
            settings_canvas,
            self.menu_models["all_access"],
            "idle",
            (30, 240),
            (150, 30)
        )
        def set_all_access():
            self.settings["all_access"] = not self.settings["all_access"]
        self.menu_objects["settings_all_access_button"].set_click_callback(set_all_access)
        self.menu_objects["settings_all_access_button"].set_hover_callback(
            lambda: self.menu_objects["settings_all_access_button"].set_current_image("hover"),
            lambda: self.menu_objects["settings_all_access_button"].set_current_image("idle")
        )

        self.menu_objects["settings_FR_flag"] = sprite.Sprite(
            settings_canvas,
            self.menu_models["flags"]["FR"],
            "main",
            (400, 410),
            (30, 20)
        )
        self.menu_objects["settings_FR_flag"].set_click_callback(lambda: self.select_language("FR"))

        self.menu_objects["settings_EN_flag"] = sprite.Sprite(
            settings_canvas,
            self.menu_models["flags"]["EN"],
            "main",
            (360, 410),
            (30, 20)
        )
        self.menu_objects["settings_EN_flag"].set_click_callback(lambda: self.select_language("EN"))

    def close_settings(self) -> None:
        """Close the settings menu."""

        if "main_canvas" in self.menu_objects:
            self.menu_objects["quit_button"].show()
            self.menu_objects["settings_button"].show()

        self.delete_menu_widget_queued("settings_canvas")


    # -------------------- USERNAME MENU --------------------

    def open_username_menu(self) -> None:
        """Opens the username menu."""

        if "username_canvas" in self.menu_objects: return # if the menu is already open

        username_canvas = self.create_menu_canvas("username_canvas", 150, 175, 200, 150)

        self.menu_objects["username_background"] = sprite.Sprite(
            username_canvas,
            self.menu_models["background"],
            "main",
            (-152, -180),
            (504, 504)
        )

        def create_tkinter_objects(): # ghost function, creating tkinter elements inside of the canvas
            self.menu_objects["username_textinput"] = tkinter.Entry(
                username_canvas,
                width = 21,
                font = self.sub_text_font,
                bg = "white"
            )
            self.menu_objects["username_textinput"].place(x = 5, y = 95, anchor = "nw")


            # ----- decorations -----
            ids = []
            background_transparent = ImageTk.PhotoImage(image = generate_filled_image(200, 200, (200, 200, 200, 255)))
            ids += [username_canvas.create_image(0, 0, image = background_transparent, anchor = "nw")]

            ids += [username_canvas.create_text(30, 3, text = self.get_text("username"), fill = "white", font = self.text_font, anchor = "nw")]
            ids += [username_canvas.create_rectangle(0, 0, 200, 35, outline = "white")]

            ids += [username_canvas.create_text(
                10,
                38,
                text = self.settings["username"],
                fill = "white",
                font = self.sub_text_font,
                anchor = "nw"
            )]
            ids += [username_canvas.create_text(
                10,
                65,
                text = self.get_text("new_username"),
                fill = "white",
                font = self.sub_text_font,
                anchor = "nw"
            )]

            self.menu_objects["username_decorations"] = ids

        self.queue_function_postprocess(create_tkinter_objects)


    def exit_menu(self) -> None:
        self.delete_menu_widget_queued("main_canvas")
        self.delete_menu_widget_queued("settings_canvas")
        self.delete_menu_widget_queued("username_canvas")

    # ----------  BIND FUNCTIONS ----------
        
game_instance = Infold()