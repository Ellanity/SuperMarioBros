import time

from ClassEntity import Entity
import pygame


class Character(Entity):
    def __init__(self, level, image_name=None, type_name=None):
        super().__init__(level=level, image_name=image_name, type_name=type_name)
        # MOVEMENT
        self.speed = 0
        # TIME of death
        self.time_of_death = 0
        self.time_range_to_disappear = 1
        # JUMP
        self.jump_speed = 30
        self.max_jump_height = 150
        self.start_jump_height = 0
        self.jumped_up = False
        self.have_physics = True
        # SPRITE
        self.turned_right = True
        self.current_image = 0
        self.state = {"Move": True, "Up": False, "Death": False}
        # OTHER
        self.additional_input_data()

    def additional_input_data(self):
        if self.type_name == "Goomba":
            self.jump_speed = 5
            self.speed = 2
            self.turned_right = False
            self.animation_speed = 0.05

    def update_sprite(self):
        path_to_sprite = "img/Character"
        if self.type_name == "Goomba":
            path_to_sprite += "/Goomba"
            if self.state["Death"]:
                self.set_of_images = self.level.sets_of_images[f"{path_to_sprite}/Death"]
            else:
                self.set_of_images = self.level.sets_of_images[f"{path_to_sprite}/Move"]

        if not self.turned_right:
            self.set_of_images = [pygame.transform.flip(image, True, False) for image in self.set_of_images]

        if self.image is not None:
            self.recalculate_the_mask()
            self.recalculate_the_rect()

    def movement_up(self):
        # I think the roof variable can be removed and the code rewritten
        # so that only the self.jumped_up variable is used
        roof = False
        intersections = self.get_intersections(self.level.solids)
        for intersection in intersections:
            if intersection["type_y"] == "top":
                roof = True
            # when the character has a fulcrum after jumping, he can jump again
            if intersection["type_y"] == "bottom":
                self.position_y = intersection["sprite"].position_y - self.image.get_height()
                self.jumped_up = False
                if intersection["type_x"] == "left":
                    self.position_x = intersection["sprite"].position_x + intersection["sprite"].get_width()
                if intersection["type_x"] == "right":
                    self.position_x = intersection["sprite"].position_x - self.image.get_width()
        self.update_sprite()

        if not self.jumped_up:
            if self.start_jump_height == 0:
                self.start_jump_height = self.position_y
                self.state["Up"] = True
            elif self.start_jump_height - self.position_y <= self.max_jump_height and not roof:
                self.position_y -= self.jump_speed
                self.state["Up"] = True
            else:
                self.jumped_up = True
        else:
            self.start_jump_height = 0
        self.update_sprite()

        self.position_y += 1  # this is so that there is an intersection and it is possible to determine the fulcrum
        self.update_sprite()
        intersections = self.get_intersections(self.level.solids)
        for intersection in intersections:
            if intersection["type_y"] == "bottom":
                self.position_y = intersection["sprite"].position_y - self.image.get_height()
                self.jumped_up = False
                break
        self.update_sprite()

    def movement_fall_after_jump(self):
        self.jumped_up = True

    def action(self):
        # print(self.set_of_images, self.position_x)
        # move down
        if self.have_physics:
            self.physics()

        # move right/left
        if (self.state["Move"] is True) and (self.level.player.position_x > self.move_when_player_x):
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

        # death, out of window
        if self.position_y > self.level.window.get_height() + 48:
            self.death()

        if self.state["Death"]:
            self.death()

    def death(self):
        if self.time_of_death == 0:
            self.time_of_death = time.time()
            self.state["Move"] = False
            self.state["Death"] = True
            self.animation_speed = 0.7
        self.update_sprite()
        time_left = self.time_range_to_disappear - ((time.time() - self.time_of_death) + self.level.time_pause_range)
        if time_left < 0:
            self.level.destroy_entity(self)
