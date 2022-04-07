from operator import itemgetter

import pygame
from ClassCharacter import Character


class Player(Character):

    def __init__(self, level, image_name=None, type_name=None):
        super().__init__(level=level, image_name=image_name, type_name=type_name)

        self.score = 0
        self.coins = 0
        self.lives = 3

        self.type_name = "Player"
        self.rect_width = 48
        self.rect_height = 48

        self.speed = 7  # 5
        self.set_image("img/MarioSmall/1")

        self.jump_speed = 20  # 25
        self.max_jump_height = 195
        self.jumped_up = False

        self.position_x = 0
        self.position_y = self.level.window.get_height() - 145

        self.state = {"large": False,
                      "fire": False,
                      "move": False,
                      "up": False,
                      "death": False}
        self.load_sets_of_images()

    def movement_up(self):
        # I think the roof variable can be removed and the code rewritten
        # so that only the self.jumped_up variable is used
        intersections = self.get_intersections(self.level.solids)
        # define entity for action
        top_intersections = list()
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
            # for the first time in my life I'm doing a bug on purpose
            #
            # There's another bug that I didn't want to do
            # if there are two blocks above the hero, he will jump, the first one will say that he crashed,
            # and there is no roof anymore, and the character will pass through the second block
            action_performed = False
            if intersection["type_y"] == "top":
                roof = True
                position_x_before = self.position_x
                # right
                if self.position_x + self.image.get_width() < intersection["sprite"].position_x + 10:
                        # (self.image.get_width() / 2 - 10):
                    self.position_x -= (self.position_x + self.image.get_width() -
                                        intersection["sprite"].position_x)
                    roof = False
                    action_performed = True
                # left
                if self.position_x > intersection["sprite"].position_x + intersection["sprite"].image.get_width() - 10:
                        # (self.image.get_width() / 2 - 10):
                    self.position_x += (intersection["sprite"].position_x + intersection[
                        "sprite"].image.get_width() - self.position_x)
                    roof = False
                    action_performed = True
                # this should fix the error described above \/
                self.update_sprite()
                new_intersections = self.get_intersections(self.level.solids)
                for new_intersection in new_intersections:
                    if new_intersection["type_y"] == "top":
                        self.position_x = position_x_before
                        self.update_sprite()
                        roof = True
                        break
                # need check intersection to destroy or animate block / or smth else
                if not self.jumped_up and intersection is entity_for_action and not action_performed:
                    self.interaction_with_entity(entity=intersection["sprite"],
                                                 intersection_x=intersection["type_x"],
                                                 intersection_y=intersection["type_y"])
                    # self.position_x = position_x_before

            # when the character has a fulcrum after jumping, he can jump again
            if intersection["type_y"] == "bottom":
                self.position_y = intersection["sprite"].position_y - self.image.get_height()
                self.jumped_up = False
                if intersection["type_x"] == "left":
                    self.position_x = intersection["sprite"].position_x + intersection["sprite"].image.get_width()
                if intersection["type_x"] == "right":
                    self.position_x = intersection["sprite"].position_x - self.image.get_width()
        self.update_sprite()

        if not self.jumped_up:
            if self.start_jump_height == 0:
                self.start_jump_height = self.position_y
                self.state["up"] = True
            elif self.start_jump_height - self.position_y <= self.max_jump_height and not roof:
                self.position_y -= self.jump_speed
                self.state["up"] = True
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

    def update_sprite(self):

        path_before = ""
        for set_ in self.level.sets_of_images:
            if self.level.sets_of_images[set_] == self.set_of_images:
                path_before = set_
                break

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
            self.set_of_images = self.level.sets_of_images[f"{path_to_sprite}/Up"]
        elif self.state["move"] is True:
            self.set_of_images = self.level.sets_of_images[f"{path_to_sprite}/Move"]
        else:
            self.set_of_images = self.level.sets_of_images[f"{path_to_sprite}/Stay"]
        if not self.turned_right:
            self.set_of_images = [pygame.transform.flip(image, True, False) for image in self.set_of_images]

        try:
            if path_before.find("Small") != -1 and path_to_sprite.find("Large") != -1:
                for intersection in self.get_intersections(self.level.solids):
                    if intersection["type_y"] == "bottom":
                        self.position_y -= self.level.sets_of_images[path_to_sprite][0].get_height() - \
                                           self.level.sets_of_images[path_before][0].get_height()
        except Exception as ex:
            pass
            # print(ex)
        # if path_to_sprite.find("Large")

        self.recalculate_the_mask()
        self.recalculate_the_rect()

    def interaction_with_entity(self, entity, intersection_x, intersection_y):

        if entity.type_name == "Brick":
            if entity.quantity_of_content > 0:
                self.get_item(entity)
            if not self.state["large"] and not entity.moved_up and len(entity.content) <= 0:
                entity.moved_up = True
            if self.state["large"] and entity.content is None:
                self.level.destroy_entity(entity)

        if entity.type_name == "Block":
            if entity.quantity_of_content > 0:
                self.get_item(entity)

    def get_item(self, entity):
        if not entity.moved_up:
            entity.moved_up = True
            entity.quantity_of_content -= 1
            # coin
            if entity.content[entity.quantity_of_content].type_name == "Coin":
                entity.content[entity.quantity_of_content].moved_up = True
                self.coins += 1
                self.score += 200
                for content_entity in entity.content:
                    try:
                        if content_entity != entity.content[entity.quantity_of_content] and not content_entity.moved_up:
                            content_entity.moved_up = True
                            content_entity.data_to_jump = \
                                {"max_jump_height": entity.max_jump_height, "jump_speed": entity.jump_speed}
                    except Exception as ex:
                        print(ex)
            # other items
            if entity.content[entity.quantity_of_content].type_name == "MushroomBig":
                item = entity.content[entity.quantity_of_content]
                item.moved_up = True
                item.state["move"] = True
                item.start_jump_height = entity.position_y - 48
                #
                item.turned_right = False
                item.max_jump_height = 0
                item.jump_speed = 10
                item.have_physics = True

    def action(self):
        # intersections
        intersections_items = self.get_intersections(self.level.items)
        intersections_solids = self.get_intersections(self.level.solids)
        # print([item for item in intersections_items])
        for intersection_item in intersections_items:
            if intersection_item["sprite"].type_name == "MushroomBig":
                touching_an_invisible_object = False
                for intersection_solid in intersections_solids:
                    if intersection_item["sprite"] in intersection_solid["sprite"].content:
                        touching_an_invisible_object = True

                if not touching_an_invisible_object:
                    self.state["large"] = True
                    self.update_sprite()
