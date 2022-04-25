from ClassParticle import Particle
from ClassEntity import Entity


class Solid(Entity):
    def __init__(self, level, image_name=None, type_name=None):
        super().__init__(image_name=image_name, type_name=type_name)
        self.level = level
        self.load_sets_of_images()

        # JUMP starter pack
        self.jump_speed = 5
        self.max_jump_height = 15
        self.start_jump_height = 0
        self.jumped_up = False
        self.moved_up = False
        # SPRITE
        self.animation_speed = 0.1

    def update_sprite(self):
        path_to_sprite = "img/Solid"

        if self.type_name == "Block" and self.content is not None:
            path_to_sprite += "/Block"
            if self.quantity_of_content != 0:
                self.set_of_images = self.level.sets_of_images[f"{path_to_sprite}/Content"]
            else:
                self.set_of_images = self.level.sets_of_images[f"{path_to_sprite}/NoContent"]

        if self.type_name == "Brick" and self.content is not None:
            path_to_sprite += "/Brick"
            if (self.quantity_of_content > 0 and len(self.content) > 0) or len(self.content) <= 0:
                self.set_of_images = self.level.sets_of_images[f"{path_to_sprite}/Content"]
            else:
                self.set_of_images = self.level.sets_of_images[f"{path_to_sprite}/NoContent"]

        if self.image is not None:
            self.recalculate_the_mask()
            self.recalculate_the_rect()

    def action(self):
        if self.moved_up:
            self.movement_up()
            # all content moves with the block
            for entity in self.content:
                if not entity.moved_up:
                    entity.position_y = self.position_y
                    if entity.position_y > self.position_y:
                        entity.position_y = self.position_y
            # items on top of the solid
            # when the block jumps, the item on top should also jump
            intersections = self.get_intersections(self.level.items)
            for intersection in intersections:
                if intersection["type_y"] == "top" and intersection["sprite"] not in self.content:
                    item = intersection["sprite"]
                    if not item.moved_up:
                        item.start_jump_height = self.position_y - self.image.get_height()
                    item.jumped_up = False
                    item.moved_up = True
                    # if the item is on a certain part of the block, then item should rotate
                    # print("jump", item.max_jump_height, item.start_jump_height, item.position_y, item.jump_speed)
                    if (item.turned_right and item.position_x + item.image.get_width() <
                        self.position_x + self.image.get_width() / 3) or \
                            (not item.turned_right and item.position_x >
                             self.position_x + (self.image.get_width() / 3 * 2)):
                        item.turned_right = not item.turned_right

    def destroy(self):
        if self.type_name == "Brick":
            path_to_sprite = "img/Particle/BrickPart"

            particles = [Particle(self.level, path_to_sprite, "BrickPart") for _ in range(0, 4)]

            particles[0].turned_right = False
            particles[0].position_x = self.position_x
            particles[0].position_y = self.position_y
            particles[0].start_jump_height = self.position_y - 48

            particles[1].turned_right = False
            particles[1].position_x = self.position_x
            particles[1].position_y = self.position_y + self.image.get_height()
            particles[1].start_jump_height = self.position_y

            particles[2].position_x = self.position_x + self.image.get_width()
            particles[2].position_y = self.position_y
            particles[2].start_jump_height = self.position_y - 48

            particles[3].position_x = self.position_x + self.image.get_width()
            particles[3].position_y = self.position_y + self.image.get_height()
            particles[3].start_jump_height = self.position_y

            for particle in particles:
                particle.have_physics = True
                particle.state["Move"] = True
                # jump
                particle.moved_up = True
                particle.max_jump_height = 0
                # add to lvl
                self.level.add_entity(particle)
