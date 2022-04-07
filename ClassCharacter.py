from ClassEntity import Entity


class Character(Entity):
    def __init__(self, level, image_name=None, type_name=None):
        super().__init__(level=level, image_name=image_name, type_name=type_name)
        # move
        self.speed = 0
        # jump
        self.jump_speed = 30
        self.max_jump_height = 150
        self.start_jump_height = 0
        self.jumped_up = False
        # sprite
        self.turned_right = True
        self.current_image = 0
        self.state = {"move": False, "up": False, "death": False}

    """def movement_right(self, cant_go_beyond_screen=False):
        # sprite
        self.state["move"] = True
        if not self.turned_right:
            self.turned_right = True
        # movement
        obstacle = None
        self.update_sprite()
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
                self.state["move"] = False
                self.update_sprite()
                self.position_x = new_obstacle["sprite"].position_x - self.image.get_width()
        else:
            self.state["move"] = False
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
        self.state["move"] = True
        if self.turned_right:
            self.turned_right = False
        # movement
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
                self.state["move"] = False
                self.position_x = new_obstacle["sprite"].position_x + new_obstacle["sprite"].image.get_width()
        else:
            self.position_x = obstacle["sprite"].position_x + obstacle["sprite"].image.get_width()
        # additional condition
        if cant_go_beyond_screen:
            if self.position_x < self.level.coordinate_level_left_border:
                self.position_x = self.level.coordinate_level_left_border
        self.update_sprite()
"""

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

    def movement_fall_after_jump(self):
        self.jumped_up = True

    def movement_down(self):
        pass  # entrance to the underworld through a pipe

    def interaction_with_entity(self, entity, intersection_x, intersection_y):
        pass
