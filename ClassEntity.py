import pygame


# A class from which all types of entities on the level are inherited,
# common characteristics inherent in all types of objects
class Entity(pygame.sprite.Sprite):
    type_name = ""

    def __init__(self, level=None, image_name=None, type_name=None):
        super().__init__()
        self.data_to_jump = dict()
        self.level = level
        # POSITION
        self.position_x = 0
        self.position_y = 0
        # CONTENT
        self.content = list()
        self.quantity_of_content = 0
        # SPRITE
        self.current_image = 0
        self.set_of_images = list()
        self.sets_of_images = list()
        self.animation_speed = 0.2
        self.mask = pygame.mask.Mask((0, 0), False)
        self.turned_right = True
        self.path_to_sprite = ""
        # MOVEMENT
        self.speed = 0
        self.state = {"Large": False,
                      "Fire": False,
                      "Star": False,
                      "Move": False,
                      "Up": False,
                      "Death": False,
                      "Immortal": False}
        self.move_left = False
        self.move_right = False
        self.have_physics = False
        self.move_when_player_x = 0
        # JUMP
        self.jump_speed = 0
        self.max_jump_height = 0
        self.start_jump_height = 0
        self.jumped_up = False
        self.moved_up = False

        # SPRITE
        self.image = None
        if image_name is not None and type_name is not None:
            self.type_name = type_name
            try:
                self.set_image(image_name)
            except Exception as ex1:
                print("No img, check set >", ex1)
                try:
                    self.load_sets_of_images()
                    self.update_sprite()
                    self.animate(animation_speed=0)
                except Exception as ex2:
                    print("No set of images >", ex2)
            self.path_to_sprite = image_name

    def additional_input_data(self):
        pass

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

    def movement_up(self):
        max_jump_height = self.max_jump_height
        jump_speed = self.jump_speed
        if len(self.data_to_jump) > 0:
            max_jump_height = self.data_to_jump["max_jump_height"]
            jump_speed = self.data_to_jump["jump_speed"]

        if not self.jumped_up:
            if self.start_jump_height == 0:
                self.start_jump_height = self.position_y
                self.moved_up = True
            elif self.start_jump_height - self.position_y <= max_jump_height and self.moved_up:
                self.position_y -= jump_speed
                self.update_sprite()
            else:
                self.jumped_up = True
        else:
            if self.position_y < self.start_jump_height:
                self.position_y += jump_speed
            else:
                self.position_y = self.start_jump_height
                self.start_jump_height = 0
                self.moved_up = False
                self.jumped_up = False
                self.data_to_jump.clear()

        self.update_sprite()

    def physics(self, ignore_solid=False):
        if ignore_solid:
            self.position_y += self.jump_speed / 2
            return

        intersections = self.get_intersections(self.level.solids)
        have_fulcrum = False

        for intersection in intersections:
            if intersection["type_y"] == "bottom":
                self.position_y = intersection["sprite"].position_y - self.image.get_height()
                self.update_sprite()
                have_fulcrum = True
                break

        if not have_fulcrum:
            self.position_y += self.jump_speed / 2
            self.update_sprite()
            new_intersections = self.get_intersections(self.level.solids)
            for new_intersection in new_intersections:
                if new_intersection["type_y"] == "bottom":
                    self.position_y = new_intersection["sprite"].position_y - self.image.get_height()
                    self.state["Up"] = False
                    self.update_sprite()
                    break
        self.update_sprite()

    def get_intersections(self, sprites_group):
        intersections = list()
        for sprite in sprites_group:
            # pygame.sprite.collide_mask(self, sprite)
            # here it was possible to make intersections by masks,
            # but then something bad happens during the animation
            if pygame.sprite.collide_rect(self, sprite):
                type_of_intersection_y = str()
                type_of_intersection_x = str()
                # vertical intersections
                if self.position_y >= sprite.position_y >= self.position_y - self.image.get_height() and \
                        self.position_x + self.image.get_width() >= sprite.position_x and \
                        self.position_x <= sprite.position_x + sprite.image.get_width():
                    type_of_intersection_y = "top"
                if sprite.position_y + max(10, int(self.jump_speed / 2 + 1)) >= \
                        self.position_y + self.image.get_height() >= sprite.position_y and \
                        self.position_x + self.image.get_width() >= sprite.position_x and \
                        self.position_x <= sprite.position_x + sprite.image.get_width():
                    type_of_intersection_y = "bottom"
                # horizontal
                if sprite.position_x < self.position_x and \
                        self.position_y + self.image.get_height() >= sprite.position_y + 4:
                    type_of_intersection_x = "left"
                if sprite.position_x > self.position_x and \
                        self.position_y + self.image.get_height() >= sprite.position_y + 4:
                    type_of_intersection_x = "right"

                if type_of_intersection_y != "" or type_of_intersection_x != "":
                    intersections.append({"sprite": sprite,
                                          "type_y": type_of_intersection_y,
                                          "type_x": type_of_intersection_x})
        return intersections

    def movement_right(self, cant_go_beyond_screen=False):
        obstacle = None
        intersections = self.get_intersections(self.level.solids)
        for intersection in intersections:
            if intersection["type_x"] == "right":
                obstacle = intersection
        if obstacle is None:
            self.position_x += self.speed  # go right (+)
            self.update_sprite()
            # check new obstacle after movement
            new_obstacle = None
            intersections = self.get_intersections(self.level.solids)
            for intersection in intersections:
                if intersection["type_x"] == "right":
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
        obstacle = None
        intersections = self.get_intersections(self.level.solids)
        for intersection in intersections:
            if intersection["type_x"] == "left":
                obstacle = intersection
        if obstacle is None:
            self.position_x -= self.speed  # go left (-)
            self.update_sprite()
            # check new after movement obstacle
            new_obstacle = None
            intersections = self.get_intersections(self.level.solids)
            for intersection in intersections:
                if intersection["type_x"] == "left":
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

    def action(self):
        pass

    def load_sets_of_images(self):
        pass

    def destroy(self):
        pass
