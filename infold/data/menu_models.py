from PIL import Image, ImageDraw, ImageOps, ImageFont


main_buttons_font = ("levels/images/menu/pixelart.TTF", 175)
settings_buttons_font = ("levels/images/menu/pixelart.TTF", 100)

main_button_img_idle_base = Image.open("levels/images/menu/button_main_idle.png").resize((1000, 400))
main_button_img_hover_base = Image.open("levels/images/menu/button_main_hover.png").resize((1000, 400))

settings_button_img_idle_base = Image.open("levels/images/menu/button_main_idle.png").resize((1000, 200))
settings_button_img_hover_base = Image.open("levels/images/menu/button_main_hover.png").resize((1000, 200))

menu_models = { # preloads all the models
    "background": {"images": {"main": Image.open("levels/images/menu/background.png")}, "sequences": {}},
    "banner": {"images": {"main": Image.open("levels/images/menu/banner.png")}, "sequences": {}},
    "cross": {"images": {"main": Image.open("levels/images/menu/croix.png")}, "sequences": {}},
    "gear": {"images": {"main": Image.open("levels/images/menu/engrenage.png")}, "sequences": {}},

    "flags": {
        "EN": {"images": {"main": Image.open("levels/images/menu/flags/EN.png")}, "sequences": {}},
        "FR": {"images": {"main": Image.open("levels/images/menu/flags/FR.png")}, "sequences": {}},
    }
}

def generate_filled_image(width: int, height: int, fill: tuple):
    """
    Generates an image filled with the given fill color (has to have an alpha integer).
    """

    return Image.new("RGBA", (width, height), fill)


def generate_text_image(image: object, text: str, x: int, y: int, font: tuple, color: tuple):
    """
    Generates a text on the given image.

    inputs:
    image: Image, pil image object
    text: str, the text that will be added to the image
    x/y: ints, coordinates of the text
    font: tuple, containing a path to the ttf file and its size
    color: tuple of 3 ints, color of the text
    """

    im_w, im_h = image.size
    im_w, im_h = im_w * 1.1, im_h * 1.2 # gives us some wiggle room for texts sizes 
    image_draw = ImageDraw.Draw(image)

    size = font[1]
    if size * len(text) > im_w:
        size = im_w // len(text)
    if size > im_h:
        size = im_h * 0.8

    font = ImageFont.truetype(font[0], int(size))
    _, _, w, h = image_draw.textbbox((0, 0), text, font = font)
    image_draw.text((x - w/2, y - h/2), text, font = font, fill = color)

def generate_menu_models(texts: dict):
    """
    Updates the menu_models dict buttons by replacing their texts with the corresponding game language.
    """
    global menu_models
    global main_buttons_font, main_button_img_idle_base, main_button_img_hover_base
    global settings_buttons_font, settings_button_img_idle_base, settings_button_img_hover_base

    # ----- main menu buttons -----
    main_button_play_idle = main_button_img_idle_base.copy()
    generate_text_image(main_button_play_idle, texts["play"], 500, 180, main_buttons_font, (220, 220, 220))
    main_button_play_hover = main_button_img_hover_base.copy()
    generate_text_image(main_button_play_hover, texts["play"], 500, 180, main_buttons_font, (220, 220, 220))

    main_button_levels_idle = main_button_img_idle_base.copy()
    generate_text_image(main_button_levels_idle, texts["levels"], 500, 180, main_buttons_font, (220, 220, 220))
    main_button_levels_hover = main_button_img_hover_base.copy()
    generate_text_image(main_button_levels_hover, texts["levels"], 500, 180, main_buttons_font, (220, 220, 220))

    # ----- settings button -----
    settings_button_username_idle = settings_button_img_idle_base.copy()
    generate_text_image(settings_button_username_idle, texts["username"], 500, 90, settings_buttons_font, (220, 220, 220))
    settings_button_username_hover = settings_button_img_hover_base.copy()
    generate_text_image(settings_button_username_hover, texts["username"], 500, 90, settings_buttons_font, (220, 220, 220))

    settings_button_reset_progression_idle = settings_button_img_idle_base.copy()
    generate_text_image(settings_button_reset_progression_idle, texts["reset_progression"], 500, 90, settings_buttons_font, (220, 220, 220))
    settings_button_reset_progression_hover = settings_button_img_hover_base.copy()
    generate_text_image(settings_button_reset_progression_hover, texts["reset_progression"], 500, 90, settings_buttons_font, (220, 220, 220))

    settings_button_all_access_idle = settings_button_img_idle_base.copy()
    generate_text_image(settings_button_all_access_idle, texts["all_access"], 500, 90, settings_buttons_font, (220, 220, 220))
    settings_button_all_access_hover = settings_button_img_hover_base.copy()
    generate_text_image(settings_button_all_access_hover, texts["all_access"], 500, 90, settings_buttons_font, (220, 220, 220))


    menu_models["play"] = {
        "images": {
            "idle": main_button_play_idle,
            "hover": main_button_play_hover
        },
        "sequences": {}
    }
    menu_models["levels"] = {
        "images": {
            "idle": main_button_levels_idle,
            "hover": main_button_levels_hover
        },
        "sequences": {}
    }
    menu_models["pseudonyme"] = {
        "images": {
            "idle": settings_button_username_idle,
            "hover": settings_button_username_hover
        },
        "sequences": {}
    }
    menu_models["reset_progression"] = {
        "images": {
            "idle": settings_button_reset_progression_idle,
            "hover": settings_button_reset_progression_hover
        },
        "sequences": {}
    }
    menu_models["all_access"] = {
        "images": {
            "idle": settings_button_all_access_idle,
            "hover": settings_button_all_access_hover
        },
        "sequences": {}
    }