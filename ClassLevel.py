import json
import pygame
import time
import math


from ClassPlayer import Player
from ClassSolid import Solid
from ClassItem import Item
from ClassCharacter import Character
from ClassScenery import Scenery
from ClassParticle import Particle
from ClassScore import Score


class Level:

    def __init__(self, window):
        # Main window, to draw everything there is
        self.window = window

        # common data
        self.file_name = ""
        self.data = None

        # time
        self.pause = False
        self.time_start = 0
        self.time_range = 0
        self.time_pause_range = 0
        self.time_pause_stop = 0
        self.time_pause_start = 0
        self.time_left = 0
        self.have_time = True

        # Two coordinate systems
        #
        # the first system is the coordinates of the main window (to draw)
        # it is in the self.window object
        #
        # the second system is the coordinates inside the level
        self.coordinate_level_left_border = 0  # used to move the screen + a reference point for rendering
        self.coordinate_level_max_right_point = self.window.get_width()
        self.length = 0
        self.player_win_x = 0
        self.player_x_to_disappear = 0
        self.win_sound = False
        self.loose_sound = False

        # All in-game entities
        self.sceneries = list()
        self.solids = list()
        self.items = list()
        self.characters = list()
        self.particles = list()

        # Different entities have different names.
        # Lists are required to separate entities into groups by name
        self.sceneries_type_names = ["BrickPlain", "Bush1", "Bush2", "Bush3",
                                     "Cloud1", "Cloud2", "Cloud3", "HillSmall",
                                     "HillLarge", "Castle", "Flag", "Flagpole"]
        self.solids_type_names = ["Floor", "Stone", "Brick", "Block", "PipeHorizontal",
                                  "PipeVertical", "PipeCapHorizontal", "PipeCapVertical", "PipeCrossroad"]
        self.items_type_names = ["Coin", "MushroomBig", "MushroomLive", "FlowerFire"]
        self.characters_type_names = ["Goomba"]
        self.particles_type_names = ["BrickPart", "Score"]
        #
        self.sets_of_images = {}
        self.load_sets_of_images()
        self.sets_of_sounds = {}
        self.load_sets_of_sounds()
        # ################
        self.player = Player(self, "", "Mario")
        self.additional_input_data()

    def additional_input_data(self):
        pass

    def draw_background(self, color):
        self.window.fill(color)

    def draw_player(self):
        self.player.state["Move"] = False
        self.player.animate()  # (animation_speed=0.2)
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

    def display_stats(self, score, time_, world, coins, lives):
        self.display_stat("SCORE", str(score), 1, 5)
        self.display_stat("TIME",  str(time_), 2, 5)
        self.display_stat("WORLD", str(world), 3, 5)
        self.display_stat("COINS", str(coins), 4, 5)
        self.display_stat("LIVES", str(lives), 5, 5)

    def display_stat(self, stat_name, stat, serial_number, quantity_stats):
        font = pygame.font.Font("font/ARCADECLASSIC.TTF", 36)
        white = (255, 255, 255)
        block_width = self.window.get_width() / quantity_stats
        text_stat_name = font.render(stat_name, True, white)
        text_stat_count = font.render(stat, True, white)

        pos_x_for_stat_name = block_width * (serial_number - 1) + ((block_width - text_stat_name.get_width()) / 2)
        pos_x_for_stat_count = block_width * (serial_number - 1) + ((block_width - text_stat_count.get_width()) / 2)

        self.window.blit(text_stat_name, (pos_x_for_stat_name, 10))
        self.window.blit(text_stat_count, (pos_x_for_stat_count, 36))

    def frame_rendering(self):
        if self.pause:
            return

        self.draw_background((153, 204, 255))
        self.draw_group_of_entities(self.sceneries)
        self.draw_group_of_entities(self.items)
        self.draw_group_of_entities(self.solids)
        self.draw_group_of_entities(self.characters)
        self.draw_group_of_entities(self.particles)
        self.draw_player()

        must_display_stats = True
        if not self.pause:
            time_now = time.time()
            if self.player.time_win != 0:
                time_now = self.player.time_win
            self.time_left = self.time_range - (time_now - self.time_start) + self.time_pause_range

            if self.time_left <= 0:
                self.time_left = 0
                self.win_window()
                must_display_stats = False
            elif self.time_left >= 0 and self.player.time_win != 0 and self.player.state["Invisible"]:
                self.player.time_win += 1
                self.player.score += 50

        if must_display_stats:
            self.display_stats(self.player.score, int(self.time_left), self.data["name"],
                               self.player.coins, self.player.lives)

        if self.time_left <= 0:
            if self.have_time:
                self.player.state["Large"] = False
                self.player.state["Fire"] = False
                self.player.was_killed = True
                self.have_time = False
            self.player.death()

    def updating_independent_world_parameters(self):
        if self.pause:
            return

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
        for particle in self.particles:
            particle.action()
            particle.update_sprite()

    def move_screen(self):
        # self.player.image.get_width() +
        if self.player.position_x + self.player.image.get_width() + int(self.window.get_width() / 10 * 4) < self.length:
            line_of_screen_movement = int(self.window.get_width() / 10 * 6)  # 60% of screen size
            if self.player.position_x - self.coordinate_level_left_border > line_of_screen_movement:
                self.coordinate_level_left_border += self.player.speed

    def load_level_from_file(self, file_name):
        self.file_name = file_name

        # reading json from file
        try:
            with open(file_name, 'r') as file:
                self.data = json.load(file)
        except Exception as ex:
            print(ex)

        # player start pos
        print(self.player.sets_of_images)
        self.player.position_x = self.data["player"]["start_x"]
        self.player.position_y = int(self.window.get_height() -
                                     self.data["player"]["start_y"] - self.player.image.get_height())

        # Convert data to level objects
        if self.data is not None:
            self.length = self.data["length"]
            self.player_win_x = self.data["player_win_x"]
            self.player_x_to_disappear = self.data["player_x_to_disappear"]
            if self.data["time"] != "Infinity":
                self.time_start = time.time()
                self.time_range = int(self.data["time"])
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
                                # Due to the fact that in pygame the coordinate axes are located as badly as possible,
                                # and I decided to use a normal coordinate system,
                                # the y axis should be converted when reading from a file
                                # (0,0) .---------->        x_width = image.get_width()    # ^ quantity_vertical
                                #       |          x        y_height = image.get_height()  # |---,---,---,
                                #       |                                                  # |---|---|---|
                                #       |y                                                 # |---'---'---'----->
                                #                                                             quantity_horizontal
                                # __________________________________________________________________________________
                                #         _pygame_                                           _my_coordinate_axes_
                                try:
                                    image = pygame.image.load(f"{image_name}.png")
                                    block_width = image.get_width()
                                    block_height = image.get_height()
                                    x = column * block_width + entity["x"]
                                    y = row * block_height + entity["y"]
                                    new_entity = self.get_entity_from_file(json_data=entity, image_suffix=image_suffix,
                                                                           coords=(x, y))
                                    self.add_entity(new_entity)
                                except Exception as ex:
                                    print(ex)

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
        if type_name in self.particles_type_names:
            image_name = f"img/Particle/{image_pre_designation}"
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
        elif type_name in self.particles_type_names:
            new_entity = Particle(self, image_name, type_name)

        # for convenience, the entity file is stored with a coordinate system,
        # where the axes start in the lower left corner
        # Therefore, the Y axis turns over
        if coords is None:
            coords = (int(json_data["x"]), int(json_data["y"]))
        new_entity.position_x = coords[0]
        new_entity.position_y = int(self.window.get_height() - coords[1] - new_entity.image.get_height())

        if "quantity_of_content" in json_data:
            new_entity.quantity_of_content = int(json_data["quantity_of_content"])
        if "content" in json_data:
            for i in range(0, new_entity.quantity_of_content):
                new_entity.content.append(self.get_entity_from_file(json_data["content"], image_suffix))
                self.add_entity(new_entity.content[-1])

        if "move_when_player_x" in json_data:
            new_entity.move_when_player_x = int(json_data["move_when_player_x"])

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
        if entity.type_name in self.particles_type_names:
            self.particles.append(entity)

    def destroy_entity(self, entity):
        try:
            entity.destroy()
        except Exception as ex:
            print(ex)
        try:
            if entity.type_name in self.solids_type_names:
                self.solids.remove(entity)
            if entity.type_name in self.characters_type_names:
                self.characters.remove(entity)
            if entity.type_name in self.sceneries_type_names:
                self.sceneries.remove(entity)
            if entity.type_name in self.items_type_names:
                self.items.remove(entity)
            if entity.type_name in self.particles_type_names:
                self.particles.remove(entity)
        except Exception as ex:
            print(ex)

    def load_sets_of_images(self):
        try:
            # SOLIDS
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

            # MARIO
            # simple
            path_to_sprite = "img/Mario"
            self.sets_of_images[f"{path_to_sprite}/Invisible"] = [pygame.image.load(f"{path_to_sprite}/Small/6.png")]

            self.sets_of_images[f"{path_to_sprite}/Small/Up"] = [pygame.image.load(f"{path_to_sprite}/Small/5.png")]
            self.sets_of_images[f"{path_to_sprite}/Small/Move"] = \
                [pygame.image.load(f"{path_to_sprite}/Small/{i}.png") for i in range(1, 5)]
            self.sets_of_images[f"{path_to_sprite}/Small/Stay"] = [pygame.image.load(f"{path_to_sprite}/Small/1.png")]
            self.sets_of_images[f"{path_to_sprite}/Small/Death"] = [pygame.image.load(f"{path_to_sprite}/Small/0.png")]

            self.sets_of_images[f"{path_to_sprite}/Large/Up"] = [pygame.image.load(f"{path_to_sprite}/Large/5.png")]
            self.sets_of_images[f"{path_to_sprite}/Large/Move"] = \
                [pygame.image.load(f"{path_to_sprite}/Large/{i}.png") for i in range(1, 5)]
            self.sets_of_images[f"{path_to_sprite}/Large/BigBoost"] = \
                [pygame.image.load(f"{path_to_sprite}/BigBoost/{i}.png") for i in range(1, 4)]
            self.sets_of_images[f"{path_to_sprite}/Large/Stay"] = [pygame.image.load(f"{path_to_sprite}/Large/1.png")]
            self.sets_of_images[f"{path_to_sprite}/Large/Death"] = [pygame.image.load(f"{path_to_sprite}/Small/0.png")]
            # immortal
            # 6.png is empty
            self.sets_of_images[f"{path_to_sprite}/Small/Immortal/Up"] = \
                [pygame.image.load(f"{path_to_sprite}/Small/{i}.png") for i in range(5, 7)]
            self.sets_of_images[f"{path_to_sprite}/Small/Immortal/Move"] = \
                [pygame.image.load(f"{path_to_sprite}/Small/{math.ceil(i / 2)}.png") for i in range(1, 9)]
            for i in range(1, 9, 2):
                self.sets_of_images[f"{path_to_sprite}/Small/Immortal/Move"][i] = \
                    pygame.image.load(f"{path_to_sprite}/Small/6.png")
            self.sets_of_images[f"{path_to_sprite}/Small/Immortal/Stay"] = \
                [pygame.image.load(f"{path_to_sprite}/Small/{i}.png") for i in range(1, 7, 5)]

            self.sets_of_images[f"{path_to_sprite}/Large/Immortal/Up"] = \
                [pygame.image.load(f"{path_to_sprite}/Large/{i}.png") for i in range(5, 7)]
            self.sets_of_images[f"{path_to_sprite}/Large/Immortal/Move"] = \
                [pygame.image.load(f"{path_to_sprite}/Large/{math.ceil(i / 2)}.png") for i in range(1, 9)]
            for i in range(1, 9, 2):
                self.sets_of_images[f"{path_to_sprite}/Large/Immortal/Move"][i] = \
                    pygame.image.load(f"{path_to_sprite}/Large/6.png")
            self.sets_of_images[f"{path_to_sprite}/Large/Immortal/Stay"] = \
                [pygame.image.load(f"{path_to_sprite}/Large/{i}.png") for i in range(1, 7, 5)]
            # star

            # ITEMS
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

            # PARTICLES
            path_to_sprite = "img/Particle"
            self.sets_of_images[f"{path_to_sprite}/BrickPart"] = \
                [pygame.image.load(f"{path_to_sprite}/BrickPart/{i}.png") for i in range(1, 5)]

            # CHARACTERS
            path_to_sprite = "img/Character"
            self.sets_of_images[f"{path_to_sprite}/Goomba/Move"] = \
                [pygame.image.load(f"{path_to_sprite}/Goomba/{i}.png") for i in range(1, 3)]
            self.sets_of_images[f"{path_to_sprite}/Goomba/Death"] = \
                [pygame.image.load(f"{path_to_sprite}/Goomba/{i}.png") for i in range(3, 5)]

        except Exception as ex:
            print(ex)

    def load_sets_of_sounds(self):
        try:
            # ALL
            self.sets_of_sounds["BreakBlock"] = pygame.mixer.Sound(f"sounds/smb_breakblock.wav") #
            self.sets_of_sounds["Bump"] = pygame.mixer.Sound(f"sounds/smb_bump.wav") #
            self.sets_of_sounds["Coin"] = pygame.mixer.Sound(f"sounds/smb_coin.wav") #
            self.sets_of_sounds["Flagpole"] = pygame.mixer.Sound(f"sounds/smb_flagpole.wav") #
            self.sets_of_sounds["GameOver"] = pygame.mixer.Sound(f"sounds/smb_gameover.wav") #
            self.sets_of_sounds["JumpSmall"] = pygame.mixer.Sound(f"sounds/smb_jumpsmall.wav") #
            self.sets_of_sounds["JumpLarge"] = pygame.mixer.Sound(f"sounds/smb_jumpbig.wav") #
            self.sets_of_sounds["Kick"] = pygame.mixer.Sound(f"sounds/smb_kick.wav") #
            self.sets_of_sounds["MarioDie"] = pygame.mixer.Sound(f"sounds/smb_mariodie.wav") #
            self.sets_of_sounds["PowerUp"] = pygame.mixer.Sound(f"sounds/smb_powerup.wav") #
            self.sets_of_sounds["StageClear"] = pygame.mixer.Sound(f"sounds/smb_stageclear.wav") ####
            self.sets_of_sounds["WorldClear"] = pygame.mixer.Sound(f"sounds/smb_worldclear.wav") #
        except Exception as ex:
            print("Sound error > ", ex)

    def show_score(self, coords, score):
        score_obj = Score(score, self)
        score_obj.position_x = coords[0]
        score_obj.position_y = coords[1]
        self.particles.append(score_obj)
        pass

    # player death variants ending
    def restart(self):

        self.pause = False
        self.player.can_move = True
        self.coordinate_level_left_border = 0
        # [feature] you can abuse the death and the final time if comment out next line
        self.time_pause_range = 0

        # In-game entities
        self.sceneries.clear()
        self.solids.clear()
        self.items.clear()
        self.characters.clear()
        self.particles.clear()

        self.load_level_from_file(self.file_name)

    def loose(self):
        if not self.loose_sound:
            self.sets_of_sounds["GameOver"].play()
            self.loose_sound = True

        self.pause = True
        self.draw_background((0, 0, 0))

        font = pygame.font.Font("font/ARCADECLASSIC.TTF", 64)
        text_loose = font.render("LOOSE", True, (255, 255, 255))
        self.window.blit(text_loose, (self.window.get_width() / 2 - text_loose.get_width() / 2,
                                      self.window.get_height() / 2 - text_loose.get_height() / 2))

        font = pygame.font.Font("font/ARCADECLASSIC.TTF", 32)
        text_restart = font.render("press  R  to  restart", True, (255, 255, 255))
        self.window.blit(text_restart, (self.window.get_width() / 2 - text_restart.get_width() / 2,
                                      self.window.get_height() / 2 - text_restart.get_height() / 2 + text_loose.get_height()))

    def game_pause(self):
        if not self.pause:
            self.pause = True
            self.time_pause_start = time.time()
        else:
            self.pause = False
            self.time_pause_stop = time.time()
            self.time_pause_range += self.time_pause_stop - self.time_pause_start
        self.player.can_move = not self.pause

    def win_window(self):
        if not self.win_sound:
            self.sets_of_sounds["WorldClear"].play()
            self.win_sound = True

        self.draw_background((0, 0, 0))

        font = pygame.font.Font("font/ARCADECLASSIC.TTF", 64)
        text_loose = font.render("win", True, (255, 255, 255))
        self.window.blit(text_loose, (self.window.get_width() / 2 - text_loose.get_width() / 2,
                                      self.window.get_height() / 2 - text_loose.get_height() / 2))

        font = pygame.font.Font("font/ARCADECLASSIC.TTF", 32)
        text_restart = font.render(f"your  score  {self.player.score}", True, (255, 255, 255))
        self.window.blit(text_restart, (self.window.get_width() / 2 - text_restart.get_width() / 2,
                                        self.window.get_height() / 2 - text_restart.get_height() / 2 - \
                                        text_loose.get_height()))

        font = pygame.font.Font("font/ARCADECLASSIC.TTF", 32)
        text_restart = font.render("press  R  to  restart", True, (255, 255, 255))
        self.window.blit(text_restart, (self.window.get_width() / 2 - text_restart.get_width() / 2,
                                        self.window.get_height() / 2 - text_restart.get_height() / 2 + \
                                        text_loose.get_height()))

