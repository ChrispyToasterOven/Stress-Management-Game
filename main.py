import pygame
from pygame.locals import *
import sys
import game_objects
import os

pygame.init()

main_clock = pygame.time.Clock()
tickspeed = 60

white = 255, 255, 255
black = 0, 0, 0

window_width = 1380
window_height = 780
window_surface = pygame.display.set_mode((window_width, window_height), 0, 16)

game_objects.init_game()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.key == K_g:
                game_objects.show_grid = not game_objects.show_grid

            if event.key == K_t:
                game_objects.book_bg.turn_page()

            if event.key == K_r:
                game_objects.play_music("title_screen.mp3")

            if event.key == K_s:
                game_objects.game.change_scene("info_big_picture")

            if event.key == K_a:
                game_objects.game.add_smile(pygame.mouse.get_pos())

    window_surface.fill(black)

    fps = main_clock.get_fps()
    game_objects.update_game((window_width, window_height))
    game_objects.render_all(window_surface, fps)

    pygame.display.update()
    main_clock.tick(tickspeed)
