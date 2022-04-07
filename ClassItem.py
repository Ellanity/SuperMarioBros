from ClassEntity import Entity
import pygame


class Item(Entity):
    def __init__(self, level, image_name=None, type_name=None):
        super().__init__(level=level, image_name=image_name, type_name=type_name)
        self.speed = 3
        self.load_sets_of_images()
        # jump
        self.jump_speed = 15
        self.max_jump_height = 120
        self.start_jump_height = 0
        self.jumped_up = False
        self.moved_up = False
        # anim
        self.animation_speed = 0.2
        self.turned_right = False
        #
        # additional params
        """if self.type_name == "MushroomBig" or \
                self.type_name == "MushroomLive":
            self.speed = 3
            self.max_jump_height = 0
            self.jump_speed = 10
            self.have_physics = True

        if self.type_name == "FlowerFire":
            self.max_jump_height = 0
            self.jump_speed = 10"""

    def update_sprite(self):
        path_to_sprite = "img/Item"
        if self.type_name == "Coin":
            path_to_sprite += "/Coin"
            if self.moved_up:
                self.set_of_images = self.level.sets_of_images[f"{path_to_sprite}/Static"]
            else:
                self.set_of_images = self.level.sets_of_images[f"{path_to_sprite}/Animation"]
        if self.type_name == "MushroomBig":
            path_to_sprite += "/MushroomBig"
            self.set_of_images = self.level.sets_of_images[f"{path_to_sprite}"]
        if self.type_name == "MushroomLive":
            path_to_sprite += "/MushroomLive"
            self.set_of_images = self.level.sets_of_images[f"{path_to_sprite}"]
        if self.type_name == "FlowerFire":
            path_to_sprite += "/FlowerFire"
            self.set_of_images = self.level.sets_of_images[f"{path_to_sprite}"]

        if self.image is not None:
            self.recalculate_the_mask()
            self.recalculate_the_rect()

    def action(self):
        if self.moved_up:
            self.movement_up()
        if self.have_physics:
            if self.type_name == "MushroomBig" and not self.moved_up:
                self.physics()
        if self.state["move"] is True:
            if self.turned_right is True:
                self.movement_right()
                if self.state["move"] is False:
                    self.turned_right = False
                    self.state["move"] = True
            elif self.turned_right is False:
                self.movement_left()
                if self.state["move"] is False:
                    self.turned_right = True
                    self.state["move"] = True
