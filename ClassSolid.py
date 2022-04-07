from ClassEntity import Entity
import pygame


class Solid(Entity):
    def __init__(self, level, image_name=None, type_name=None):
        super().__init__(image_name=image_name, type_name=type_name)
        self.level = level
        self.load_sets_of_images()

        # jump starter pack
        self.jump_speed = 10
        self.max_jump_height = 15
        self.start_jump_height = 0
        self.jumped_up = False
        self.moved_up = False
        # animate
        self.animation_speed = 0.1

    def update_sprite(self):
        path_to_sprite = "img/Solid"
        if self.type_name == "Block" and self.content is not None:
            path_to_sprite += "/Block"
            if self.quantity_of_content != 0:
                self.set_of_images = self.level.sets_of_images[f"{path_to_sprite}/Content"]
            else:
                self.set_of_images = self.level.sets_of_images[f"{path_to_sprite}/NoContent"]
        if self.type_name == "Brick" and self.content is not None:
            path_to_sprite += "/Brick"
            if (self.quantity_of_content > 0 and len(self.content) > 0) or len(self.content) <= 0:
                self.set_of_images = self.level.sets_of_images[f"{path_to_sprite}/Content"]
            else:
                self.set_of_images = self.level.sets_of_images[f"{path_to_sprite}/NoContent"]

        self.recalculate_the_mask()
        self.recalculate_the_rect()

    def action(self):
        if self.moved_up:
            self.movement_up()
