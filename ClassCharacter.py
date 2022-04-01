import pygame
from ClassEntity import Entity
# 10128 - конец уровн

class Character(Entity):
    def __init__(self, level, image_name=None, type_name=None):
        super().__init__(level=level, image_name=image_name, type_name=type_name)
        self.speed = 0
        self.jump_speed = 30
        self.max_jump_height = 150
        self.start_jump_height = 0
        self.jumped_up = False
        self.turned_right = True

    def movement_right(self, cant_go_beyond_screen=False):
        # sprite
        if not self.turned_right:
            self.turned_right = True
            self.image = pygame.transform.flip(self.image, True, False)
        self.update_sprite()
        # movement
        obstacle = None
        intersections = self.get_intersections(self.level.solids)
        for intersection in intersections:
            if intersection["type_x"] == "right":
                obstacle = intersection
        if obstacle is None:
            self.position_x += self.speed  # + speed
            self.update_sprite()
            # check new after movement obstacle
            new_obstacle = None
            intersections = self.get_intersections(self.level.solids)
            for intersection in intersections:
                if intersection["type_x"] == "right":
                    new_obstacle = intersection
            if new_obstacle is not None:
                self.position_x = new_obstacle["sprite"].position_x - self.image.get_width()
        else:
            self.position_x = obstacle["sprite"].position_x - self.image.get_width()
        """        obstacle = None
        intersections = self.get_intersections(self.level.solids)
        for intersection in intersections:
            if intersection["type_x"] == "right":
                obstacle = intersection
        if obstacle is None:
            self.position_x += self.speed  # + speed
        else:
            self.position_x = obstacle["sprite"].position_x - self.image.get_width()"""
        # additional condition
        if cant_go_beyond_screen:
            if self.position_x + self.image.get_width() > self.level.window.get_width() + self.level.coordinate_level_left_border:
                self.position_x = self.level.coordinate_level_left_border + self.level.window.get_width() - self.image.get_width()
        self.update_sprite()

    def movement_left(self, cant_go_beyond_screen=False):
        # sprite change
        if self.turned_right:
            self.turned_right = False
            self.image = pygame.transform.flip(self.image, True, False)
        # movement
        obstacle = None
        intersections = self.get_intersections(self.level.solids)
        for intersection in intersections:
            if intersection["type_x"] == "left":
                obstacle = intersection
        if obstacle is None:
            self.position_x -= self.speed  # - speed
            self.update_sprite()
            # check new after movement obstacle
            new_obstacle = None
            intersections = self.get_intersections(self.level.solids)
            for intersection in intersections:
                if intersection["type_x"] == "left":
                    new_obstacle = intersection
            if new_obstacle is not None:
                self.position_x = new_obstacle["sprite"].position_x + new_obstacle["sprite"].image.get_width()
        else:
            self.position_x = obstacle["sprite"].position_x + obstacle["sprite"].image.get_width()
        # additional condition
        if cant_go_beyond_screen:
            if self.position_x < self.level.coordinate_level_left_border:
                self.position_x = self.level.coordinate_level_left_border
        self.update_sprite()

    def movement_up(self):
        roof = False
        intersections = self.get_intersections(self.level.solids)
        for intersection in intersections:
            if intersection["type_y"] == "top":
                roof = True
            # for the first time in my life I'm doing a bug on purpose
            if intersection["type_y"] == "top" and \
                    self.position_x + self.image.get_width() < intersection["sprite"].position_x + 8:
                self.position_x -= (self.position_x + self.image.get_width() - intersection["sprite"].position_x)
                self.update_sprite()
                roof = False
            if intersection["type_y"] == "top" and \
                    self.position_x > intersection["sprite"].position_x + intersection["sprite"].image.get_width() - 8:
                self.position_x += (intersection["sprite"].position_x + intersection["sprite"].image.get_width() - self.position_x)
                self.update_sprite()
                roof = False
            # now its ok
            """if intersection["type_x"] == "left":
                self.position_x = intersection["sprite"].position_x + intersection["sprite"].image.get_width()
            if intersection["type_x"] == "right":
                self.position_x = intersection["sprite"].position_x - self.image.get_width()"""

        if not self.jumped_up:
            if self.start_jump_height == 0:
                self.start_jump_height = self.position_y
            if self.start_jump_height - self.position_y <= self.max_jump_height and not roof:
                self.position_y -= self.jump_speed
            else:
                self.jumped_up = True
        else:
            self.start_jump_height = 0
        self.update_sprite()

        intersections = self.get_intersections(self.level.solids)
        for intersection in intersections:
            if intersection["type_y"] == "bottom":
                self.position_y = intersection["sprite"].position_y - self.image.get_height() + 1
                self.jumped_up = False
                break
        self.update_sprite()

    def movement_fall_after_jump(self):
        self.jumped_up = True

    def physics(self):
        intersections = self.get_intersections(self.level.solids)
        have_fulcrum = False

        for intersection in intersections:
            if intersection["type_y"] == "bottom":
                self.position_y = intersection["sprite"].position_y - self.image.get_height() + 1
                self.update_sprite()
                have_fulcrum = True
                break

        if not have_fulcrum:
            self.position_y += self.jump_speed / 2
            self.update_sprite()
            intersections = self.get_intersections(self.level.solids)
            for intersection in intersections:
                if intersection["type_y"] == "bottom":
                    self.position_y = intersection["sprite"].position_y - self.image.get_height() + 1
                    break

        self.update_sprite()

    def movement_down(self):
        pass  # entrance to the underworld through a pipe

    def get_intersections(self, sprites_group):
        intersections = list()
        for sprite in sprites_group:
            if pygame.sprite.collide_rect(self, sprite):
                ##########################################################################
                ###########          !!!    Congratulations     !!!          #############
                ###########          !!!    It does not work    !!!          #############
                ##########################################################################
                type_of_intersection_y = str()
                type_of_intersection_x = str()
                # vertical intersections
                if self.position_y >= sprite.position_y >= self.position_y - self.image.get_height() and \
                        self.position_x + self.image.get_width() >= sprite.position_x and \
                        self.position_x <= sprite.position_x + sprite.image.get_width():
                        # abs(sprite.position_x - self.position_x) < self.image.get_width():
                    type_of_intersection_y = "top"
                # if sprite.position_y - sprite.image.get_height() + 10 >= self.position_y >= sprite.position_y -
                # sprite.image.get_height() - 2 and \
                if sprite.position_y >= self.position_y >= sprite.position_y - sprite.image.get_height() - 2 and \
                        self.position_x + self.image.get_width() >= sprite.position_x and \
                        self.position_x <= sprite.position_x + sprite.image.get_width():
                        # abs(sprite.position_x - self.position_x) < self.image.get_width():
                    type_of_intersection_y = "bottom"
                # horizontal
                if sprite.position_y >= self.position_y >= sprite.position_y - sprite.image.get_height() and \
                        sprite.position_x < self.position_x:
                    type_of_intersection_x = "left"
                if sprite.position_y >= self.position_y >= sprite.position_y - sprite.image.get_height() and \
                        sprite.position_x > self.position_x:
                    type_of_intersection_x = "right"

                intersections.append({"sprite": sprite,
                                      "type_y": type_of_intersection_y,
                                      "type_x": type_of_intersection_x})
        return intersections

