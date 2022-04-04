from ClassEntity import Entity
import pygame


class Solid(Entity):
    def __init__(self, level, image_name=None, type_name=None):
        super().__init__(image_name=image_name, type_name=type_name)
        self.level = level
        self.load_sets_of_images()

        # jump starter pack
        self.jump_speed = 30
        self.max_jump_height = 150
        self.start_jump_height = 0
        self.jumped_up = False

    def update_sprite(self):
        path_to_sprite = "img/Solid"
        if self.type_name == "Block" and self.content is not None:
            path_to_sprite += "/Block"
            if self.quantity_of_content != 0:
                self.set_of_images = self.sets_of_images[f"{path_to_sprite}/Content"]
            else:
                self.set_of_images = self.sets_of_images[f"{path_to_sprite}/NoContent"]

        self.recalculate_the_mask()
        self.recalculate_the_rect()

    def load_sets_of_images(self):
        try:
            path_to_sprite = "img/Solid"
            self.sets_of_images[f"{path_to_sprite}/Block/Content"] = \
                [pygame.image.load(f"{path_to_sprite}/Block/{i}.png") for i in range(1, 5)]
            self.sets_of_images[f"{path_to_sprite}/Block/NoContent"] = \
                [pygame.image.load(f"{path_to_sprite}/Block/5.png")]
        except Exception as ex:
            print(ex)

    # it does not work
    def movement_up(self):
        if not self.jumped_up:
            if self.start_jump_height == 0:
                self.start_jump_height = self.position_y
            elif self.start_jump_height - self.position_y <= self.max_jump_height:
                self.position_y -= self.jump_speed
            else:
                self.jumped_up = True
        else:
            if self.position_y <= self.start_jump_height:
                self.position_y += self.jump_speed
            else:
                self.position_y = self.start_jump_height
                self.start_jump_height = 0
        self.update_sprite()
