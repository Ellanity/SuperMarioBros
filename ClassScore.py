from ClassEntity import Entity
import pygame


class Score(Entity):
    def __init__(self, count, level, image_name=None, type_name=None):
        super().__init__(level=level, image_name=image_name, type_name=type_name)
        self.type_name = "Score"
        font = pygame.font.Font("font/ARCADECLASSIC.TTF", 26)
        self.image = font.render(str(count), True, (255, 255, 255))
        self.set_of_images = [self.image]
        self.moved_up = True
        self.jump_speed = 5
        self.max_jump_height = 100

    def action(self):
        if not self.jumped_up:
            self.movement_up()
        else:
            self.level.destroy_entity(self)
