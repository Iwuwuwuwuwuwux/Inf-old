import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from PIL import Image
from time import sleep

from modules import entity, level, sprite as entity, level, sprite

from levels.translations import TNiveau1 as texts

class CLevel (level.Level):
    def __init__(self, game_instance: object):
        level_size = (50,50)
        self.initialize(game_instance, level_size)
        
        if not game_instance.settings["language"] in texts.languages:
            self.texts_ref = texts.languages["FR"]
        else:
            self.texts_ref = texts.languages[game_instance.settings["language"]]

        self.name = "Niveau 1"
        self.description = "No description."
    
    def create(self):
        self.create_render_frame()
        
        self.val = sprite.Sprite(
            self.frame,
            {
                "images": {
                    "main": Image.open("levels/images/samples/clash.png"),
                    "hidden": Image.new("RGBA", (1, 1), (0, 0, 0, 0))
                },
                "sequences": {
                    "loop": [True, ("main", (0, 0)), 1000, ("hidden", (0, 0)), 1000]
                }
            },
            "main",
            (0, 0),
            (500, 500)
        )

        print("aaw")
        self.val.start_sequence("loop")
"""
model = {
    "images": {
        "img1": Image.open("levels/images/image JL/Fond/N1.png")
    },
    "sequences": {
        "seq1": []
    }
}"""