from PIL import Image, ImageDraw, ImageOps, ImageFont


buttons_font = ("levels/images/menu/pixelart.TTF", 175)

main_button_img_idle_base = Image.open("levels/images/menu/button_main_idle.png").resize((1000, 400))
main_button_img_hover_base = Image.open("levels/images/menu/button_main_hover.png").resize((1000, 400))

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

    im_w, im_h, _ = image.size()
    im_w, im_h = im_w * 1.2, im_h * 1.2 # gives us some wiggle room for texts sizes 
    image_draw = ImageDraw.Draw(image)

    size = font[1]
    mul_size = size * len(text)
    if mul_size > im_w or mul_size > im_h:
        pass

    font = ImageFont.truetype(font[0], size)

    _, _, w, h = image_draw.textbbox((0, 0), text, font = font)
    image_draw.text((x - w/2, y - h/2), text, font = font, fill = color)

def generate_menu_models(texts: dict):
    """
    Updates the menu_models dict buttons by replacing their texts with the corresponding game language.
    """

    global buttons_font, main_button_img_idle_base, main_button_img_hover_base, menu_models

    # ----- main menu buttons -----
    main_button_play_idle = main_button_img_idle_base.copy()
    generate_text_image(main_button_play_idle, texts["play"], 500, 180, buttons_font, (220, 220, 220))
    main_button_play_hover = main_button_img_hover_base.copy()
    generate_text_image(main_button_play_hover, texts["play"], 500, 180, buttons_font, (220, 220, 220))

    main_button_levels_idle = main_button_img_idle_base.copy()
    generate_text_image(main_button_levels_idle, texts["levels"], 500, 180, buttons_font, (220, 220, 220))
    main_button_levels_hover = main_button_img_hover_base.copy()
    generate_text_image(main_button_levels_hover, texts["levels"], 500, 180, buttons_font, (220, 220, 220))

    # ----- settings button -----
    settings_button_username_idle = main_button_img_idle_base.copy()
    generate_text_image(settings_button_username_idle, texts["username"], 500, 180, buttons_font, (220, 220, 220))
    settings_button_username_hover = main_button_img_hover_base.copy()
    generate_text_image(settings_button_username_hover, texts["username"], 500, 180, buttons_font, (220, 220, 220))


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