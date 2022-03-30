from ClassEntity import Entity


class Solid(Entity):
    def __init__(self, level, image_name=None, type_name=None):
        super().__init__(image_name=image_name, type_name=type_name)
        self.level = level
