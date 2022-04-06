import pygame


# A class from which all types of entities on the level are inherited,
# common characteristics inherent in all types of objects
class Entity(pygame.sprite.Sprite):
    type_name = ""

    def __init__(self, level=None, image_name=None, type_name=None):
        super().__init__()
        self.data_to_jump = dict()
        self.level = level
        # pos
        self.position_x = 0
        self.position_y = 0
        # content
        self.content = list()
        self.quantity_of_content = 0
        # sprite
        self.current_image = 0
        self.set_of_images = list()
        self.sets_of_images = {}
        self.animation_speed = 0.2
        self.mask = pygame.mask.Mask((0, 0), False)
        # jump
        self.jump_speed = 0
        self.max_jump_height = 0
        self.start_jump_height = 0
        self.jumped_up = False
        self.moved_up = False

        if image_name is not None and type_name is not None:
            self.set_image(image_name)
            self.type_name = type_name

    def set_image(self, image_name):
        self.image = pygame.image.load(f"{image_name}.png").convert_alpha()
        self.set_of_images.append(self.image)
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

    def animate(self, animation_speed=None):
        # animation speed recommended range (0, 1)
        if animation_speed is not None:
            self.current_image += animation_speed
        else:
            self.current_image += self.animation_speed

        if self.current_image >= len(self.set_of_images):
            self.current_image = 0
        self.image = self.set_of_images[int(self.current_image)]
        self.update_sprite()

    def action(self):
        pass

    def movement_up(self):
        if len(self.data_to_jump) <= 0:
            if not self.jumped_up:
                if self.start_jump_height == 0:
                    self.start_jump_height = self.position_y
                    self.moved_up = True
                elif self.start_jump_height - self.position_y <= self.max_jump_height and self.moved_up:
                    self.position_y -= self.jump_speed / 2
                else:
                    self.jumped_up = True
            else:
                if self.position_y <= self.start_jump_height:
                    self.position_y += self.jump_speed / 2
                if self.position_y > self.start_jump_height:
                    self.position_y = self.start_jump_height
                    self.start_jump_height = 0
                    self.moved_up = False
                    self.jumped_up = False
            # self.update_sprite()
        else:
            if not self.jumped_up:
                if self.start_jump_height == 0:
                    self.start_jump_height = self.position_y
                    self.moved_up = True
                elif self.start_jump_height - self.position_y <= self.data_to_jump["max_jump_height"] and self.moved_up:
                    self.position_y -= self.data_to_jump["jump_speed"] / 2
                else:
                    self.jumped_up = True
            else:
                if self.position_y <= self.start_jump_height:
                    self.position_y += self.data_to_jump["jump_speed"] / 2
                if self.position_y > self.start_jump_height:
                    self.position_y = self.start_jump_height
                    self.start_jump_height = 0
                    self.moved_up = False
                    self.jumped_up = False
                    self.data_to_jump.clear()
        # just need to be everywhere
        self.update_sprite()

