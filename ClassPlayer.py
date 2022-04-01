from ClassCharacter import Character


class Player(Character):

    def __init__(self, level, image_name=None, type_name=None):
        super().__init__(level=level, image_name=image_name, type_name=type_name)

        self.speed = 10 # 5
        self.set_image("img/MarioSmall/1")

        self.jump_speed = 25
        self.max_jump_height = 195
        self.jumped_up = False

        self.position_x = 0
        self.position_y = 300
