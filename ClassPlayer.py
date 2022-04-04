import pygame
from ClassCharacter import Character


class Player(Character):

    def __init__(self, level, image_name=None, type_name=None):
        super().__init__(level=level, image_name=image_name, type_name=type_name)

        self.rect_width = 48
        self.rect_height = 48

        self.speed = 5  # 5
        self.set_image("img/MarioSmall/1")

        self.jump_speed = 20 # 25
        self.max_jump_height = 195
        self.jumped_up = False

        self.position_x = 0
        self.position_y = 300



        self.state = {"large": False, "fire": False, "move": False, "up": False, "death": False}

    def update_sprite(self):
        path_to_sprite = "img/Mario"
        # size
        if self.state["large"] is True:
            path_to_sprite += "Large"
        else:
            path_to_sprite += "Small"
        # fire
        if self.state["fire"] is True:
            path_to_sprite += "Fire"
        # move
        if self.state["up"] is True:
            self.set_of_images = [pygame.image.load(f"{path_to_sprite}/5.png")]
        elif self.state["move"] is True:
            self.set_of_images = [pygame.image.load(f"{path_to_sprite}/{i}.png") for i in range(1, 5)]
        else:
            self.set_of_images = [pygame.image.load(f"{path_to_sprite}/1.png")]
            # self.set_image(f"{path_to_sprite}/1")

        if not self.turned_right:
            # self.image = pygame.transform.flip(self.image, True, False)
            self.set_of_images = [pygame.transform.flip(image, True, False) for image in self.set_of_images]

        # intersections
        """for intersection in self.get_intersections(self.level.solids):
            if intersection["type_x"] == "left":
                self.position_x = intersection["sprite"].position_x + intersection["sprite"].image.get_width()
            if intersection["type_x"] == "right":
                self.position_x = intersection["sprite"].position_x - self.image.get_width()"""

        self.recalculate_the_mask()
        self.recalculate_the_rect()

    # def recalculate_the_rect(self):
        # self.rect = pygame.Rect(self.position_x, self.position_y, self.rect_width, self.rect_height)