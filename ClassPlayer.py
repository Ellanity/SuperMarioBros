import time
from operator import itemgetter

import pygame
from ClassCharacter import Character


class Player(Character):

    def __init__(self, level, image_name=None, type_name=None):
        super().__init__(level=level, image_name=image_name, type_name=type_name)
        # GAME
        self.type_name = "Player"
        self.score = 0
        self.coins = 0
        self.lives = 3
        # MOVEMENT
        self.speed = 7
        # JUMP
        self.jump_speed = 20
        self.max_jump_height = 195
        self.jumped_up = True
        self.jump_after_kill = False
        self.jump_after_death = False
        # POSITION
        self.rect_width = 48
        self.rect_height = 48
        # SPRITE
        self.set_image("img/MarioSmall/1")
        self.state = {"Large": False,
                      "Fire": False,
                      "Star": False,
                      "Move": False,
                      "Up": False,
                      "Death": False,
                      "Immortal": False}
        self.load_sets_of_images()
        # TIME
        self.was_killed = False
        # death time
        # self.time_of_death = 0
        # self.time_range_to_disappear = 1
        # time of immortality [if had bonus and was killed]
        self.time_immortality_start = 0
        self.time_range_of_immortality = 3
        # star time
        self.time_star_start = 0
        self.time_range_of_star = 10

    def update_sprite(self):

        path_before = self.path_to_sprite

        self.path_to_sprite = "img/Mario"
        # size
        if self.state["Large"] is True:
            self.path_to_sprite += "/Large"
        else:
            self.path_to_sprite += "/Small"
        # fire
        if self.state["Fire"] is True:
            self.path_to_sprite += "/Fire"
        # immortality
        if self.state["Immortal"] is True:
            self.path_to_sprite += "/Immortal"
        # move
        if self.state["Death"] is True:
            self.set_of_images = self.level.sets_of_images[f"{self.path_to_sprite}/Death"]
            self.path_to_sprite += "/Death"
        elif self.state["Up"] is True:
            self.set_of_images = self.level.sets_of_images[f"{self.path_to_sprite}/Up"]
            self.path_to_sprite += "/Up"
        elif self.state["Move"] is True:
            self.set_of_images = self.level.sets_of_images[f"{self.path_to_sprite}/Move"]
            self.path_to_sprite += "/Move"
        else:
            self.set_of_images = self.level.sets_of_images[f"{self.path_to_sprite}/Stay"]
            self.path_to_sprite += "/Stay"
        # i don't know why it works right
        if not self.turned_right:
            self.set_of_images = [pygame.transform.flip(image, True, False) for image in self.set_of_images]

        # Small => Large (change pos)
        try:
            if path_before.find("Small") != -1 and self.path_to_sprite.find("Large") != -1:
                self.position_y -= (self.level.sets_of_images[self.path_to_sprite][0].get_height() -
                                    self.level.sets_of_images[path_before][0].get_height())
                self.update_sprite()
        except Exception as ex:
            print(ex)

        self.recalculate_the_mask()
        self.recalculate_the_rect()

    def movement_up(self):
        # define entity for action
        top_intersections = list()
        intersections = self.get_intersections(self.level.solids)
        entity_for_action = None
        for intersection in intersections:
            if intersection["type_y"] == "top":
                # right
                # if self.position_x + self.image.get_width() < intersection["sprite"].position_x + \
                # intersection["sprite"].image.get_width():
                if self.position_x < intersection["sprite"].position_x:
                    top_intersections.append((intersection, self.position_x + self.image.get_width() -
                                              intersection["sprite"].position_x))
                # left
                if self.position_x > intersection["sprite"].position_x:
                    top_intersections.append((intersection, intersection["sprite"].position_x +
                                              intersection["sprite"].image.get_width() - self.position_x))
        if len(top_intersections) != 0:
            entity_for_action = max(top_intersections, key=itemgetter(1))[0]

        # define roof
        roof = False
        for intersection in intersections:
            action_performed = False
            if intersection["type_y"] == "top":
                roof = True
                position_x_before = self.position_x
                # Sliding on the block when jumping
                # right
                if self.position_x + self.image.get_width() < intersection["sprite"].position_x + 10:
                    self.position_x -= (self.position_x + self.image.get_width() -
                                        intersection["sprite"].position_x)
                    roof = False
                    action_performed = True
                # left
                if self.position_x > intersection["sprite"].position_x + intersection["sprite"].image.get_width() - 10:
                    self.position_x += (intersection["sprite"].position_x + intersection[
                        "sprite"].image.get_width() - self.position_x)
                    roof = False
                    action_performed = True
                self.update_sprite()

                # if two blocks near
                new_intersections = self.get_intersections(self.level.solids)
                for new_intersection in new_intersections:
                    if new_intersection["type_y"] == "top":
                        self.position_x = position_x_before
                        self.update_sprite()
                        roof = True
                        break
                # need check intersection to destroy or animate block / or smth else
                if (not self.jumped_up) and (intersection is entity_for_action) and (not action_performed):
                    self.interaction_with_entity(entity=intersection["sprite"],
                                                 intersection_x=intersection["type_x"],
                                                 intersection_y=intersection["type_y"])
                    roof = True

            # when the character has a fulcrum after jumping, he can jump again
            if intersection["type_y"] == "bottom":
                self.position_y = intersection["sprite"].position_y - self.image.get_height()
                self.jumped_up = False
                if intersection["type_x"] == "left":
                    self.position_x = intersection["sprite"].position_x + intersection["sprite"].image.get_width()
                if intersection["type_x"] == "right":
                    self.position_x = intersection["sprite"].position_x - self.image.get_width()
        self.update_sprite()

        # jump
        max_jump_height = self.max_jump_height
        jump_speed = self.jump_speed
        if len(self.data_to_jump) > 0:
            max_jump_height = self.data_to_jump["max_jump_height"]
            jump_speed = self.data_to_jump["jump_speed"]

        if not self.jumped_up:
            if self.start_jump_height == 0:
                self.start_jump_height = self.position_y
                self.state["Up"] = True
            elif self.start_jump_height - self.position_y <= max_jump_height and not roof:
                self.position_y -= jump_speed
                self.state["Up"] = True
            else:
                self.jumped_up = True
                self.jump_after_kill = False
                self.jump_after_death = False
                self.was_killed = False
                self.data_to_jump.clear()
        else:
            self.start_jump_height = 0

        self.update_sprite()

        # should not pay attention to objects at death
        # if self.jump_after_death:
        #    return

        # define fulcrum
        self.position_y += 1  # this is so that there is an intersection and it is possible to determine the fulcrum
        self.update_sprite()
        intersections = self.get_intersections(self.level.solids)
        for intersection in intersections:
            if intersection["type_y"] == "bottom":
                self.position_y = intersection["sprite"].position_y - self.image.get_height()
                self.jumped_up = False
                break
        self.update_sprite()

    def movement_right(self, cant_go_beyond_screen=False):
        # sprite
        self.state["Move"] = True
        if not self.turned_right:
            self.turned_right = True
        # movement
        obstacle = None
        self.update_sprite()
        intersections = self.get_intersections(self.level.solids)
        for intersection in intersections:
            if (intersection["type_x"] == "right" and intersection["type_y"] == "") or \
                    (intersection["type_x"] == "right" and self.jumped_up is True):
                obstacle = intersection
        if obstacle is None:
            self.position_x += self.speed  # go right (+)
            self.update_sprite()
            # check new obstacle after movement
            new_obstacle = None
            intersections = self.get_intersections(self.level.solids)
            for intersection in intersections:
                if (intersection["type_x"] == "right" and intersection["type_y"] == "") or \
                        (intersection["type_x"] == "right" and self.jumped_up is True):
                    new_obstacle = intersection
            if new_obstacle is not None:
                self.state["Move"] = False
                self.update_sprite()
                self.position_x = new_obstacle["sprite"].position_x - self.image.get_width()
        else:
            self.state["Move"] = False
            self.update_sprite()
            self.position_x = obstacle["sprite"].position_x - self.image.get_width()
        # additional condition
        if cant_go_beyond_screen:
            if self.position_x + self.image.get_width() > \
                    self.level.window.get_width() + self.level.coordinate_level_left_border:
                self.position_x = self.level.coordinate_level_left_border + \
                                  self.level.window.get_width() - self.image.get_width()
        self.update_sprite()

    def movement_left(self, cant_go_beyond_screen=False):
        # sprite change
        self.state["Move"] = True
        if self.turned_right:
            self.turned_right = False
        # movement
        obstacle = None
        intersections = self.get_intersections(self.level.solids)
        for intersection in intersections:
            if (intersection["type_x"] == "left" and intersection["type_y"] == "") or \
                    (intersection["type_x"] == "left" and self.jumped_up is True):
                obstacle = intersection
        if obstacle is None:
            self.position_x -= self.speed  # go left (-)
            self.update_sprite()
            # check new after movement obstacle
            new_obstacle = None
            intersections = self.get_intersections(self.level.solids)
            for intersection in intersections:
                if (intersection["type_x"] == "left" and intersection["type_y"] == "") or \
                        (intersection["type_x"] == "left" and self.jumped_up is True):
                    new_obstacle = intersection
            if new_obstacle is not None:
                self.state["Move"] = False
                self.position_x = new_obstacle["sprite"].position_x + new_obstacle["sprite"].image.get_width()
        else:
            self.position_x = obstacle["sprite"].position_x + obstacle["sprite"].image.get_width()
        # additional condition
        if cant_go_beyond_screen:
            if self.position_x < self.level.coordinate_level_left_border:
                self.position_x = self.level.coordinate_level_left_border
        self.update_sprite()

    def interaction_with_entity(self, entity, intersection_x, intersection_y):

        # Solid
        if entity.type_name == "Brick":
            if entity.quantity_of_content > 0:
                self.get_item_from_block(entity)
            if not self.state["Large"] and not entity.moved_up and len(entity.content) <= 0:
                entity.moved_up = True
            elif self.state["Large"] and len(entity.content) <= 0:
                self.level.destroy_entity(entity)

        if entity.type_name == "Block":
            if entity.quantity_of_content > 0:
                self.get_item_from_block(entity)

        # MushroomBig
        if entity.type_name == "MushroomBig":
            self.state["Large"] = True
            self.score += 1000
            self.level.show_score(coords=(entity.position_x + entity.image.get_width(),
                                          entity.position_y), score=1000)
            self.update_sprite()
            self.level.destroy_entity(entity)
            self.state["Immortal"] = True
            self.time_immortality_start = time.time()

        # Characters
        if (not entity.state["Death"]) and (not self.state["Death"]) and (not self.state["Immortal"]):
            # Goomba
            if entity.type_name == "Goomba":
                if intersection_y == "bottom":
                    entity.death()
                    self.score += 200
                    self.level.show_score(coords=(entity.position_x + entity.image.get_width(),
                                                  entity.position_y), score=200)
                    self.jump_after_kill = True
                    self.jumped_up = False
                    self.start_jump_height = self.position_y
                    self.data_to_jump = {"max_jump_height": 48, "jump_speed": self.jump_speed}
                elif intersection_x == "left" or intersection_x == "right":
                    self.death()
                    self.was_killed = True

    def get_item_from_block(self, entity):
        if not entity.moved_up:
            entity.moved_up = True
            entity.quantity_of_content -= 1
            # Coin
            if entity.content[entity.quantity_of_content].type_name == "Coin":
                entity.content[entity.quantity_of_content].jump_from_block(entity)
                self.coins += 1
                self.score += 200
            # MushroomBig
            if entity.content[entity.quantity_of_content].type_name == "MushroomBig":
                entity.content[entity.quantity_of_content].jump_from_block(entity)

    def check_intersection_with_items(self):
        # the items are arranged so that their lower part coincides
        # with the lower part of the block, so that when the player jumps,
        # he can cross both objects
        intersections_to_return = list()
        intersections_items = self.get_intersections(self.level.items)
        intersections_solids = self.get_intersections(self.level.solids)
        for intersection_item in intersections_items:
            if intersection_item["sprite"].type_name == "MushroomBig":
                touching_an_invisible_object = False
                for intersection_solid in intersections_solids:
                    if intersection_item["sprite"] in intersection_solid["sprite"].content:
                        touching_an_invisible_object = True
                        break
                if not touching_an_invisible_object:
                    intersections_to_return.append(intersection_item)
        return intersections_to_return

    def action(self):
        # movement up
        if self.jump_after_kill or self.jump_after_death:
            self.movement_up()

        # physics
        if self.state["Death"]:
            self.physics(ignore_solid=True)
        else:
            self.physics()

        # intersections with items
        for intersection in self.check_intersection_with_items():
            self.interaction_with_entity(entity=intersection["sprite"],
                                         intersection_x=intersection["type_x"],
                                         intersection_y=intersection["type_y"])
        # death
        self.check_death()

        # bonuses will end after the death check
        self.check_bonus_time()

    def check_bonus_time(self):
        now_time = time.time()
        # immortal
        if self.state["Immortal"] and (not self.time_immortality_start == 0):
            self.state["Death"] = False
            self.animation_speed = 0.4
            left_time_of_bonus = self.time_range_of_immortality - \
                                 (now_time - self.time_immortality_start) + self.level.time_pause_range
            if left_time_of_bonus < 0:
                self.state["Immortal"] = False
        else:
            self.animation_speed = 0.2  # return anim speed

        # star
        if self.state["Star"] and (not self.time_immortality_start == 0):
            self.state["Death"] = False
            self.animation_speed = 0.4
            left_time_of_bonus = self.time_range_of_star - \
                                 (now_time - self.time_star_start) + self.level.time_pause_range
            if left_time_of_bonus < 0:
                self.state["Star"] = False
        else:
            self.animation_speed = 0.2

    def check_death(self):
        # intersection with character
        intersections = self.get_intersections(self.level.characters)
        for intersection in intersections:
            self.interaction_with_entity(entity=intersection["sprite"],
                                         intersection_x=intersection["type_x"],
                                         intersection_y=intersection["type_y"])
        # out of window
        if self.position_y > self.level.window.get_height():
            self.jumped_up = False
            self.was_killed = False
            self.death()

        # when die, always do
        if self.state["Death"]:
            self.death()

    def death(self):
        # cases when it can survive
        if self.state["Large"] or self.state["Fire"] and self.was_killed:
            self.state["Large"] = self.state["Fire"] = False
            self.state["Immortal"] = True
            self.time_immortality_start = time.time()
            self.was_killed = False
        # no chance to survive
        else:
            # character kills player
            if self.was_killed:
                # jump data
                self.jump_after_death = True
                self.jumped_up = False
                self.data_to_jump = {"max_jump_height": 96, "jump_speed": self.jump_speed}
                if not self.state["Death"]:
                    self.start_jump_height = self.position_y
                #
                self.state["Death"] = True
                self.update_sprite()
            # the player fell into the abyss
            elif not self.jumped_up:
                if self.lives > 0:
                    # reset params
                    self.state["Death"] = False
                    self.lives -= 1
                    self.coins = 0
                    self.score = 0
                    self.jumped_up = False
                    # time
                    self.time_immortality_start = 0
                    self.time_star_start = 0
                    #
                    self.level.restart()
                else:
                    self.level.loose()
