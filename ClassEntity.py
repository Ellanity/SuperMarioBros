import pygame


# A class from which all types of entities on the level are inherited,
# common characteristics inherent in all types of objects
class Entity(pygame.sprite.Sprite):
    type_name = ""

    def __init__(self, level=None, image_name=None, type_name=None):
        super().__init__()
        self.level = level
        self.position_x = 0
        self.position_y = 0
        self.mask = pygame.mask.Mask((0, 0), False)
        if image_name is not None and type_name is not None:
            self.set_image(image_name)
            self.type_name = type_name

    def set_image(self, image_name):
        self.image = pygame.image.load(f"{image_name}.png").convert_alpha()
        self.recalculate_the_mask()
        self.recalculate_the_rect()

    def set_type_name(self, type_name):
        self.type_name = type_name

    def set_position_x(self, pos):
        self.position_x = pos

    def set_position_y(self, pos):
        self.position_y = pos

    def recalculate_the_mask(self):
        self.mask = pygame.mask.from_surface(self.image)

    def recalculate_the_rect(self):
        self.rect = pygame.Rect(self.position_x, self.position_y, self.image.get_width(), self.image.get_height())

    def update_sprite(self):
        self.recalculate_the_mask()
        self.recalculate_the_rect()
