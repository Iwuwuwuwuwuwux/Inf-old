import sys
sys.path.append("../code")

from modules import entity as entity
from modules import sprite as sprite

# variable s'assurant que deux entités n'ont pas le même ID
id_increment = 1

class UI (entity.Entity):
    """"""

    def initialize(self, level_instance: object):
        """Fonction interne obligatoire."""
        global id_increment

        self.level_instance = level_instance
        self.type = "entity"

        self.id = id_increment
        id_increment += 1

        self.sprite = None
        self.model = {}
        self.sounds = {}

        self.pos = (0, 0)
        self.scale = (1.0, 1.0)

        self.is_shown = False
        self.collision = False

    def __init__(self, level_instance: object, pos: tuple):
        """Doit absolument appeler self.initialize(level_instance, pos)."""

        self.initialize(level_instance)

    
    def update_scale(self, new_scale: tuple):
        """
        Modifie la taille de l'entité.
        
        new_scale: tuple de 2 floats, facteur multiplicatif de la taille en x et y
        """

        self.scale = new_scale

        sprite_scale = self.sprite.scale # optimisation
        self.sprite.set_scale(sprite_scale[0] * new_scale[0], sprite_scale[1] * new_scale[1])

    def set_pos(self, new_pos: tuple):
        """modifie la position et déplace l'entité sur la grille du niveau."""

        self.pos = new_pos 

        if self.collision:
            if not self.level_instance.check_tile_availible(new_pos): return
        self.level_instance.move_grid_object(self, self.pos, new_pos)

        tile_scale_ref = self.level_instance.tile_scale # optimisation
        x_coords = tile_scale_ref[0]/2 + tile_scale_ref[0] * self.pos[0]
        y_coords = tile_scale_ref[1]/2 + tile_scale_ref[1] * self.pos[1]

        self.sprite.move((x_coords, y_coords))
    

    def set_sprite(self, new_model: dict, start_image: str, sprite_scale: tuple, sprite_displacement: tuple = (0, 0)):
        """modifie le visuel de l'entité"""

        self.model = new_model

        if not self.sprite is None: self.sprite.destroy()
        self.sprite = sprite.Sprite(
            self.level_instance.frame,
            self.model,
            start_image,
            (0, 0),
            (self.scale[i] * sprite_scale[i] for i in range(2)),
            sprite_displacement
        )

        if self.is_shown: self.sprite.show()
        else: self.sprite.hide()
    
    
    def show(self):
        """affiche l'entité à l'écran"""

        self.is_shown = True
        self.sprite.show()     

    def hide(self):
        """cache l'entité de l'écran"""

        self.is_shown = False
        self.sprite.hide()
    
    def set_collision(self,collision):
        """définis si l'objet a des collisions ou non"""

        self.collision = collision
    
    def destroy(self):
        self.hide()