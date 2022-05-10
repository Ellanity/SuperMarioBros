from ClassEntity import Entity
import pygame


class Item(Entity):
    def __init__(self, level, image_name=None, type_name=None):
        super().__init__(level=level, image_name=image_name, type_name=type_name)
        self.speed = 3
        self.load_sets_of_images()
        # JUMP
        self.jump_speed = 12
        self.max_jump_height = 120
        self.start_jump_height = 0
        self.jumped_up = False
        self.moved_up = False
        # SPRITE
        self.animation_speed = 0.2
        self.turned_right = False
        self.appearance = True
        # OTHER
        self.additional_input_data()

    def additional_input_data(self):
        pass
        # if self.type_name == "MushroomBig":
        #     self.jump_speed = 6

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

        if not self.turned_right:
            self.set_of_images = [pygame.transform.flip(image, True, False) for image in self.set_of_images]

        if self.image is not None:
            self.recalculate_the_mask()
            self.recalculate_the_rect()

    def action(self):
        if self.moved_up:
            self.movement_up()
        if self.type_name == "MushroomBig":
            if self.moved_up:
                if self.jumped_up:
                    self.appearance = False  # after first jump it always false
                    self.max_jump_height = 48
            if self.have_physics:
                if not self.appearance:
                    self.physics()
                    self.state["Move"] = True

        if self.state["Move"] is True:
            if self.turned_right is True:
                self.movement_right()
                if self.state["Move"] is False:
                    self.turned_right = False
                    self.state["Move"] = True
            elif self.turned_right is False:
                self.movement_left()
                if self.state["Move"] is False:
                    self.turned_right = True
                    self.state["Move"] = True

    def jump_from_block(self, block):
        if self.type_name == "MushroomBig":
            self.moved_up = True
            self.turned_right = True
            self.have_physics = True
            self.start_jump_height = block.position_y - block.image.get_height()
            self.data_to_jump = {"max_jump_height": 0, "jump_speed": 2}
        if self.type_name == "Coin":
            self.moved_up = True
