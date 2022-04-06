from ClassEntity import Entity
import pygame


class Item(Entity):
    def __init__(self, level, image_name=None, type_name=None):
        super().__init__(level=level, image_name=image_name, type_name=type_name)
        self.speed = 0
        self.load_sets_of_images()
        # jump
        self.jump_speed = 15
        self.max_jump_height = 120
        self.start_jump_height = 0
        self.jumped_up = False
        self.moved_up = False
        # anim
        self.animation_speed = 0.2

    def update_sprite(self):
        path_to_sprite = "img/Item"
        if self.type_name == "Coin":
            path_to_sprite += "/Coin"
            if self.moved_up:
                self.set_of_images = self.sets_of_images[f"{path_to_sprite}/Static"]
            else:
                self.set_of_images = self.sets_of_images[f"{path_to_sprite}/Animation"]

        self.recalculate_the_mask()
        self.recalculate_the_rect()

    def load_sets_of_images(self):
        try:
            path_to_sprite = "img/Item"
            self.sets_of_images[f"{path_to_sprite}/Coin/Static"] = \
                [pygame.image.load(f"{path_to_sprite}/Coin/{i}.png") for i in range(1, 5)]
            self.sets_of_images[f"{path_to_sprite}/Coin/Animation"] = \
                [pygame.image.load(f"{path_to_sprite}/Coin/3.png")]
        except Exception as ex:
            print(ex)

    def action(self):
        if self.moved_up:
            self.movement_up()
