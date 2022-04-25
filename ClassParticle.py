from ClassEntity import Entity
import pygame


class Particle(Entity):
    def __init__(self, level, image_name=None, type_name=None):
        super().__init__(level=level, image_name=image_name, type_name=type_name)
        self.speed = 3
        self.load_sets_of_images()
        # JUMP
        self.jump_speed = 15
        self.max_jump_height = 120
        self.start_jump_height = 0
        self.jumped_up = False
        self.moved_up = False
        # SPRITE
        self.animation_speed = 0.2
        self.turned_right = True
        if self.type_name == "BrickPart":
            self.have_physics = True

    def update_sprite(self):
        path_to_sprite = "img/Particle"
        if self.type_name == "BrickPart":
            path_to_sprite += "/BrickPart"
            self.set_of_images = self.level.sets_of_images[f"{path_to_sprite}"]
        if not self.turned_right:
            self.set_of_images = [pygame.transform.flip(image, True, False) for image in self.set_of_images]

        if self.image is not None:
            self.recalculate_the_mask()
            self.recalculate_the_rect()

    def movement_left(self, **kwargs):
        self.position_x -= self.speed  # go left (-)
        self.update_sprite()

    def movement_right(self, **kwargs):
        self.position_x += self.speed  # go right (+)
        self.update_sprite()

    def physics(self, **kwargs):
        self.position_y += self.jump_speed / 2
        self.update_sprite()

    def action(self):
        if self.moved_up:
            self.movement_up()
        if self.have_physics:
            if not self.moved_up:
                self.jump_speed += 2  # acceleration of the free fall of particles
            self.physics()
        if self.state["Move"] is True:
            if self.turned_right is True:
                self.movement_right()
            else:
                self.movement_left()

        # out of window
        if self.position_y > self.level.window.get_height() + 48:
            self.level.destroy_entity(self)
