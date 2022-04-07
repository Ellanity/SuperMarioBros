import json
import pygame
from ClassPlayer import Player
from ClassSolid import Solid
from ClassItem import Item
from ClassCharacter import Character
from ClassScenery import Scenery


class Level:
    def __init__(self, window):
        # Main window, to draw everything there is
        self.window = window
        self.data = None
        self.time = 0
        self.time_left = 0
        # Two coordinate systems
        #
        # the first system is the coordinates of the main window (to draw)
        # it is in the self.window object
        #
        # the second system is the coordinates inside the level
        self.coordinate_level_left_border = 0  # used to move the screen + a reference point for rendering
        self.coordinate_level_max_right_point = self.window.get_width()
        self.length = 0

        # All in-game entities
        self.sceneries = list()
        self.solids = list()
        self.items = list()
        self.characters = list()
        self.player = Player(self)

        # Different entities have different names.
        # Lists are required to separate entities into groups by name
        self.sceneries_type_names = ["BrickPlain", "Bush1", "Bush2", "Bush3",
                                     "Cloud1", "Cloud2", "Cloud3", "HillSmall", "HillLarge"]
        self.solids_type_names = ["Floor", "Stone", "Brick", "PipeHorizontal",
                                  "PipeVertical", "PipeCapHorizontal", "PipeCapVertical", "PipeCrossroad", "Block"]
        self.items_type_names = ["Coin", "MushroomBig", "MushroomLive", "FlowerFire"]
        self.characters_type_names = list()
        #
        self.sets_of_images = {}
        self.load_sets_of_images()

    def draw_background(self):
        self.window.fill((153, 204, 255))

    def draw_player(self):
        self.player.state["move"] = False
        self.player.animate(animation_speed=0.2)
        pos_x_to_draw = self.player.position_x - self.coordinate_level_left_border
        pos_y_to_draw = self.player.position_y
        self.window.blit(self.player.image, (pos_x_to_draw, pos_y_to_draw))

    # Use for drawing any list of images
    def draw_group_of_entities(self, entities):
        for entity in entities:
            left_border = self.coordinate_level_left_border - self.window.get_width()
            right_border = self.coordinate_level_left_border + self.window.get_width()
            if left_border < entity.position_x < right_border:
                pos_x_to_draw = entity.position_x - self.coordinate_level_left_border
                pos_y_to_draw = entity.position_y
                entity.animate()
                self.window.blit(entity.image, (pos_x_to_draw, pos_y_to_draw))

    def display_stats(self, score, time, world, coins, lives):
        self.display_stat("SCORE", str(score), 1, 5)
        self.display_stat("TIME",  str(time),  2, 5)
        self.display_stat("WORLD", str(world), 3, 5)
        self.display_stat("COINS", str(coins), 4, 5)
        self.display_stat("LIVES", str(lives), 5, 5)

    def display_stat(self, stat_name, stat, serial_number, quantity_stats):
        font = pygame.font.Font("font/ARCADECLASSIC.TTF", 36)
        white = (255, 255, 255)
        block_width = self.window.get_width() / quantity_stats
        text_stat_name = font.render(stat_name, True, white)
        text_stat_count = font.render(stat, True, white)

        pos_x_for_text_stat_name = block_width * (serial_number - 1) + ((block_width - text_stat_name.get_width()) / 2)
        pos_x_for_text_stat_count = block_width * (serial_number - 1) + ((block_width - text_stat_count.get_width()) / 2)

        self.window.blit(text_stat_name, (pos_x_for_text_stat_name, 10))
        self.window.blit(text_stat_count, (pos_x_for_text_stat_count, 36))

    def frame_rendering(self):
        self.draw_background()
        self.draw_group_of_entities(self.sceneries)
        self.draw_group_of_entities(self.items)
        self.draw_group_of_entities(self.solids)
        self.draw_group_of_entities(self.characters)
        self.draw_player()
        self.display_stats(self.player.score, self.time_left, self.data["name"], self.player.coins, self.player.lives)

    def physics(self):
        self.player.physics()

    def updating_independent_world_parameters(self):

        self.player.action()
        self.player.update_sprite()

        for solid in self.solids:
            solid.action()
            solid.update_sprite()
        for character in self.characters:
            character.action()
            character.update_sprite()
        for scenery in self.sceneries:
            scenery.action()
            scenery.update_sprite()
        for item in self.items:
            item.action()
            item.update_sprite()

        self.physics()

    def move_screen(self):
        # self.player.image.get_width() +
        if self.player.position_x + self.player.image.get_width() + int(self.window.get_width() / 10 * 4) < self.length:
            line_of_screen_movement = int(self.window.get_width() / 10 * 6)  # 60% of screen size
            if self.player.position_x - self.coordinate_level_left_border > line_of_screen_movement:
                self.coordinate_level_left_border += self.player.speed

    def load_level_from_file(self, file_name):
        # reading json from file
        try:
            with open(file_name, 'r') as file:
                self.data = json.load(file)
        except Exception as ex:
            print(ex)

        # Convert data to level objects
        if self.data is not None:
            self.length = self.data["length"]
            if self.data["time"] != "Infinity":
                self.time = int(self.data["time"])
            # Can consist of several zones(areas)
            for area in self.data["areas"]:
                # Depending on the zone, the colors of the images change, so we define the suffix
                image_suffix = ""
                if area["setting"] == "Overworld":
                    image_suffix = ""
                elif area["setting"] == "Underworld":
                    image_suffix = "Underworld"
                # Defining the entity group
                for entity in area["creation"]:
                    if "type" in entity:
                        # image_name = self.get_entity_image_by_type_and_suffix(entity["type"], image_suffix)
                        new_entity = self.get_entity_from_file(json_data=entity, image_suffix=image_suffix)
                        self.add_entity(new_entity)
                    if "macro" in entity:
                        image_name = self.get_entity_image_by_type_and_suffix(entity["macro"], image_suffix)
                        # for row in range(0, -int(entity["quantity_vertical"]), -1):
                        for row in range(int(entity["quantity_vertical"])):
                            for column in range(int(entity["quantity_horizontal"])):
                                #
                                # (0,0) .---------->        x_width = image.get_width()    #     ^ quantity_vertical
                                #       |          x        y_height = image.get_height()  #     |---,---,---,
                                #       |                                                  #     |---|---|---|
                                #       |y                                                 #     |---'---'---'----->
                                #                                                                    quantity_horizontal
                                image = pygame.image.load(f"{image_name}.png")
                                block_width = image.get_width()
                                block_height = image.get_height()
                                x = column * block_width + entity["x"]
                                y = row * block_height + entity["y"]
                                new_entity = self.get_entity_from_file(json_data=entity, image_suffix=image_suffix,
                                                                       coords=(x, y))
                                self.add_entity(new_entity)

    def get_entity_image_by_type_and_suffix(self, type_name, image_suffix):
        image_pre_designation = type_name + image_suffix
        image_name = str()
        if type_name in self.solids_type_names:
            image_name = f"img/Solid/{image_pre_designation}"
        if type_name in self.characters_type_names:
            image_name = f"img/Character/{image_pre_designation}"
        if type_name in self.sceneries_type_names:
            image_name = f"img/Scenery/{image_pre_designation}"
        if type_name in self.items_type_names:
            image_name = f"img/Item/{image_pre_designation}"
        return image_name

    def get_entity_from_file(self, json_data, image_suffix, coords=None):
        new_entity = None
        image_name = ""
        type_name = ""
        if "type" in json_data:
            image_name = self.get_entity_image_by_type_and_suffix(json_data["type"], image_suffix)
            type_name = json_data["type"]
        if "macro" in json_data:
            image_name = self.get_entity_image_by_type_and_suffix(json_data["macro"], image_suffix)
            type_name = json_data["macro"]

        if type_name in self.solids_type_names:
            new_entity = Solid(self, image_name, type_name)
        elif type_name in self.characters_type_names:
            new_entity = Character(self, image_name, type_name)
        elif type_name in self.sceneries_type_names:
            new_entity = Scenery(self, image_name, type_name)
        elif type_name in self.items_type_names:
            new_entity = Item(self, image_name, type_name)

        # for convenience, the entity file is stored with a coordinate system,
        # where the axes start in the lower left corner
        # Therefore, the Y axis turns over
        if coords is None:
            coords = (int(json_data["x"]), int(json_data["y"]))
        new_entity.position_x = coords[0]
        new_entity.position_y = int(self.window.get_height() - coords[1] - new_entity.image.get_height())

        if "quantity_of_content" in json_data:
            new_entity.quantity_of_content = int(json_data["quantity_of_content"])
        for i in range(0, new_entity.quantity_of_content):
            if "content" in json_data:
                new_entity.content.append(self.get_entity_from_file(json_data["content"], image_suffix))
                self.add_entity(new_entity.content[-1])

        return new_entity

    def add_entity(self, entity):
        if entity.type_name in self.solids_type_names:
            self.solids.append(entity)
        if entity.type_name in self.characters_type_names:
            self.characters.append(entity)
        if entity.type_name in self.sceneries_type_names:
            self.sceneries.append(entity)
        if entity.type_name in self.items_type_names:
            self.items.append(entity)

    def destroy_entity(self, entity):
        pass

    def load_sets_of_images(self):
        try:
            # Solids
            path_to_sprite = "img/Solid"
            # Block
            self.sets_of_images[f"{path_to_sprite}/Block/Content"] = \
                [pygame.image.load(f"{path_to_sprite}/Block/{i}.png") for i in range(1, 5)]
            self.sets_of_images[f"{path_to_sprite}/Block/NoContent"] = \
                [pygame.image.load(f"{path_to_sprite}/Block/5.png")]

            # Brick
            self.sets_of_images[f"{path_to_sprite}/Brick/Content"] = \
                [pygame.image.load(f"{path_to_sprite}/Brick/1.png")]
            self.sets_of_images[f"{path_to_sprite}/Brick/NoContent"] = \
                [pygame.image.load(f"{path_to_sprite}/Brick/2.png")]

            # Mario
            path_to_sprite = "img/Mario"
            self.sets_of_images[f"{path_to_sprite}/Small/Up"] = [pygame.image.load(f"{path_to_sprite}/Small/5.png")]
            self.sets_of_images[f"{path_to_sprite}/Small/Move"] = \
                [pygame.image.load(f"{path_to_sprite}/Small/{i}.png") for i in range(1, 5)]
            self.sets_of_images[f"{path_to_sprite}/Small/Stay"] = [pygame.image.load(f"{path_to_sprite}/Small/1.png")]
            self.sets_of_images[f"{path_to_sprite}/Small/Death"] = [pygame.image.load(f"{path_to_sprite}/Small/0.png")]

            self.sets_of_images[f"{path_to_sprite}/Large/Up"] = [pygame.image.load(f"{path_to_sprite}/Large/5.png")]
            self.sets_of_images[f"{path_to_sprite}/Large/Move"] = \
                [pygame.image.load(f"{path_to_sprite}/Large/{i}.png") for i in range(1, 5)]
            self.sets_of_images[f"{path_to_sprite}/Large/Stay"] = [pygame.image.load(f"{path_to_sprite}/Large/1.png")]
            self.sets_of_images[f"{path_to_sprite}/Large/Death"] = [pygame.image.load(f"{path_to_sprite}/Small/0.png")]

            # Items
            path_to_sprite = "img/Item"
            self.sets_of_images[f"{path_to_sprite}/Coin/Static"] = \
                [pygame.image.load(f"{path_to_sprite}/Coin/{i}.png") for i in range(1, 5)]
            self.sets_of_images[f"{path_to_sprite}/Coin/Animation"] = \
                [pygame.image.load(f"{path_to_sprite}/Coin/3.png")]

            self.sets_of_images[f"{path_to_sprite}/MushroomLive"] = \
                [pygame.image.load(f"{path_to_sprite}/Mushroom/1.png")]
            self.sets_of_images[f"{path_to_sprite}/MushroomBig"] = \
                [pygame.image.load(f"{path_to_sprite}/Mushroom/2.png")]
            self.sets_of_images[f"{path_to_sprite}/FlowerFire"] = \
                [pygame.image.load(f"{path_to_sprite}/Flower/{i}.png") for i in range(1, 5)]
        except Exception as ex:
            print(ex)
