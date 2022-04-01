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
                                  "PipeVertical", "PipeCapHorizontal", "PipeCapVertical", "PipeCrossroad"]
        self.items_type_names = list()
        self.characters_type_names = list()

    def draw_background(self):
        self.window.fill((153, 204, 255))

    def draw_player(self):
        pos_x_to_draw = self.player.position_x - self.coordinate_level_left_border
        pos_y_to_draw = self.player.position_y
        self.window.blit(self.player.image, (pos_x_to_draw, pos_y_to_draw))
        # screen.blit(self.player.image, (self.player.position_x, self.player.position_y))

    # Use for drawing any list of images
    def draw_group_of_entities(self, entities):
        for entity in entities:
            left_border = self.coordinate_level_left_border - self.window.get_width()
            right_border = self.coordinate_level_left_border + self.window.get_width()
            if left_border < entity.position_x < right_border:
                pos_x_to_draw = entity.position_x - self.coordinate_level_left_border
                pos_y_to_draw = entity.position_y
                self.window.blit(entity.image, (pos_x_to_draw, pos_y_to_draw))

    def frame_rendering(self):
        self.draw_background()
        self.draw_group_of_entities(self.sceneries)
        self.draw_group_of_entities(self.items)
        self.draw_group_of_entities(self.solids)
        self.draw_group_of_entities(self.characters)
        self.draw_player()

    def physics(self):
        self.player.physics()

    def updating_independent_world_parameters(self):

        self.player.update_sprite()

        for solid in self.solids:
            solid.update_sprite()
        for character in self.characters:
            character.update_sprite()
        for scenery in self.sceneries:
            scenery.update_sprite()
        for item in self.items:
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
                        image_name = self.get_entity_image_by_type_and_suffix(entity["type"], image_suffix)
                        self.load_entity_from_file(image_name=image_name, type_name=entity["type"],
                                                   coords=(entity["x"], entity["y"]))
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
                                self.load_entity_from_file(image_name=image_name, type_name=entity["macro"],
                                                           coords=(x, y))

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

    def load_entity_from_file(self, image_name, type_name, coords):
        new_entity = None
        if type_name in self.solids_type_names:
            new_entity = Solid(self, image_name, type_name)
        if type_name in self.characters_type_names:
            new_entity = Character(self, image_name, type_name)
        if type_name in self.sceneries_type_names:
            new_entity = Scenery(self, image_name, type_name)
        if type_name in self.items_type_names:
            new_entity = Item(self, image_name, type_name)

        # for convenience, the entity file is stored with a coordinate system,
        # where the axes start in the lower left corner
        # Therefore, the Y axis turns over
        new_entity.position_x = coords[0]
        new_entity.position_y = int(self.window.get_height() - coords[1] - new_entity.image.get_height())
        self.add_entity(new_entity)
        print(f"entity: {type_name}, {image_name}, "
              f"x: {new_entity.position_x} y: {new_entity.position_y}")

    def add_entity(self, entity):
        if entity.type_name in self.solids_type_names:
            self.solids.append(entity)
        if entity.type_name in self.characters_type_names:
            self.characters.append(entity)
        if entity.type_name in self.sceneries_type_names:
            self.sceneries.append(entity)
        if entity.type_name in self.items_type_names:
            self.items.append(entity)
