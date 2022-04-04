import pygame
from ClassCharacter import Character


class Player(Character):

    def __init__(self, level, image_name=None, type_name=None):
        super().__init__(level=level, image_name=image_name, type_name=type_name)

        self.type_name = "Player"
        self.rect_width = 48
        self.rect_height = 48

        self.speed = 5  # 5
        self.set_image("img/MarioSmall/1")

        self.jump_speed = 20  # 25
        self.max_jump_height = 195
        self.jumped_up = False

        self.position_x = 0
        self.position_y = 300

        self.state = {"large": False, "fire": False, "move": False, "up": False, "death": False}
        self.load_sets_of_images()

    def update_sprite(self):
        path_to_sprite = "img/Mario"
        # size
        if self.state["large"] is True:
            path_to_sprite += "/Large"
        else:
            path_to_sprite += "/Small"
        # fire
        if self.state["fire"] is True:
            path_to_sprite += "/Fire"
        # move
        if self.state["up"] is True:
            self.set_of_images = self.sets_of_images[f"{path_to_sprite}/Up"]
        elif self.state["move"] is True:
            self.set_of_images = self.sets_of_images[f"{path_to_sprite}/Move"]
        else:
            self.set_of_images = self.sets_of_images[f"{path_to_sprite}/Stay"]
        if not self.turned_right:
            self.set_of_images = [pygame.transform.flip(image, True, False) for image in self.set_of_images]

        self.recalculate_the_mask()
        self.recalculate_the_rect()

    def load_sets_of_images(self):
        path_to_sprite = "img/Mario"
        self.sets_of_images[f"{path_to_sprite}/Small/Up"] = [pygame.image.load(f"{path_to_sprite}/Small/5.png")]
        self.sets_of_images[f"{path_to_sprite}/Small/Move"] = [pygame.image.load(f"{path_to_sprite}/Small/{i}.png") for
                                                               i in range(1, 5)]
        self.sets_of_images[f"{path_to_sprite}/Small/Stay"] = [pygame.image.load(f"{path_to_sprite}/Small/1.png")]
