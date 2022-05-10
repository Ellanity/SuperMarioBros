import pygame
import sys
from pygame.locals import *
from ClassLevel import Level

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("Super Mario Bros")
clock = pygame.time.Clock()


def main():
    pygame.mixer.music.load("sounds/main_theme.mp3")
    pygame.mixer.music.set_volume(0.2)
    lvl = Level(screen)
    lvl.load_level_from_file("lvl/1.json")
    pygame.mixer.music.play(-1)
    while True:
        paused = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    lvl.player.movement_fall_after_jump()
                if event.key == pygame.K_p:
                    if not paused:
                        lvl.game_pause()
                        paused = True
                if event.key == pygame.K_r:
                    del lvl
                    lvl = Level(screen)
                    lvl.load_level_from_file("lvl/1.json")

        if not lvl.pause and \
                lvl.player.lives > 0 and \
                not lvl.player.state["Death"] and \
                lvl.player.character_management:
            # keys
            # user movement
            if pygame.key.get_pressed()[K_RIGHT]:
                lvl.player.movement_right(cant_go_beyond_screen=True)
                lvl.move_screen()
            if pygame.key.get_pressed()[K_LEFT]:
                lvl.player.movement_left(cant_go_beyond_screen=True)
            if pygame.key.get_pressed()[K_UP]:
                lvl.player.movement_up()

            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

        if lvl.player.state["Death"]:
            pygame.mixer.music.rewind()
            pygame.mixer.music.pause()
        if lvl.player.win:
            pygame.mixer.music.pause()

        # updating screen
        lvl.updating_independent_world_parameters()
        lvl.frame_rendering()

        pygame.display.flip()
        clock.tick(40)


if __name__ == "__main__":
    main()
