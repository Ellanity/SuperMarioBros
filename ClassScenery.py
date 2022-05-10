from ClassEntity import Entity


class Scenery(Entity):
    def __init__(self, level, image_name=None, type_name=None):
        super().__init__(level=level, image_name=image_name, type_name=type_name)
        self.have_physics = False

    def action(self):
        if self.have_physics:
            self.physics()
