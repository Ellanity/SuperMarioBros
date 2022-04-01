import pygame
import sys
from pygame.locals import *
from ClassLevel import Level

pygame.init()
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("Super Mario Bros")
clock = pygame.time.Clock()


def main():
    lvl = Level(screen)
    lvl.load_level_from_file("lvl/1.json")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    lvl.player.movement_fall_after_jump()

        # keys
        if pygame.key.get_pressed()[K_RIGHT]:
            lvl.player.movement_right(cant_go_beyond_screen=True)
            lvl.move_screen()
        if pygame.key.get_pressed()[K_LEFT]:
            lvl.player.movement_left(cant_go_beyond_screen=True)
        if pygame.key.get_pressed()[K_UP]:
            lvl.player.movement_up()

        lvl.updating_independent_world_parameters()
        lvl.frame_rendering()

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
