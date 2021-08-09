from math import floor, ceil

import pygame.time
from pygame import K_p

from common_functions import *


def map_editor(data):
    SAVDIR = "maps/"
    running = True
    data.click = False
    pygame.event.clear()
    paint = False
    speed = 800 // data.fps

    tile_set, tile_set_w, tile_set_h = load_tileset('resources/tileset/16x16DungeonTileset.v4.png', 32, 32)

    # scaling of tile_set
    scale = 100
    scaled_tile_set = tile_set
    for x in range(tile_set_w):
        for y in range(tile_set_h):
            scaled_tile_set[x][y] = pygame.transform.scale(tile_set[x][y], (scale, scale)).convert_alpha()

    half_screen_width = data.screen.get_width() // 2
    half_screen_height = data.screen.get_height() // 2

    # player
    player_entity = PlayerData(data.screen, (255, 255, 255), scale)

    # for map editing
    placement_height, selected_tile_x, selected_tile_y = 0, 0, 0
    m_w, m_h = int(ceil(1 + data.screen.get_width() / scale / 2)), int(ceil(1 + data.screen.get_height() / scale / 2))

    map = SAVDIR + "m1.mapfile"

    current_map = GameMap(map)
    preview_bg = pygame.transform.scale(tile_set[2][0], (max(20, scale), max(20, scale))).convert_alpha()

    # load map

    current_map.load_map()

    while running:
        mx, my = pygame.mouse.get_pos()

        # probably not needed when map is done

        data.screen.fill((255, 255, 255))

        draw_text('game', data.default_font, (255, 255, 255), data.screen, 20, 20, 20, 20)

        # map loop
        player_tile_x, player_tile_y = int(player_entity.x // scale), int(player_entity.y // scale)

        map_layer_0, map_layer_1, map_layer_2, map_layer_3 = \
            current_map.get_near(m_w, m_h, player_tile_x, player_tile_y, scale)

        # map layering
        n1, n2, n3, n4 = current_map.get_near(1, 1, player_tile_x, player_tile_y, scale)

        player_entity.physics([*n1, *n2, *n3, *n4],
                              scale, player_entity, half_screen_width, half_screen_height)

        for each in [*map_layer_0, *map_layer_1]:
            each.blit_tile(data.screen, scaled_tile_set, player_entity, scale, half_screen_width,
                           half_screen_height)

        player_entity.draw_player()

        for each in [*map_layer_2, *map_layer_3]:
            each.blit_tile(data.screen, scaled_tile_set, player_entity, scale, half_screen_width,
                           half_screen_height)

        # edit tool and GUI
        preview = pygame.transform.scale(tile_set[selected_tile_x][selected_tile_y], (scale, scale))
        data.screen.blit(preview_bg, (50, 50))
        data.screen.blit(preview, (50, 50))

        mc_x, mc_y = int((mx + player_entity.x - half_screen_width) // scale), \
                     int((my + player_entity.y - half_screen_height) // scale)

        draw_text(f'X: {str(mc_x)}  Y:{str(mc_y)}', data.default_font, (255, 255, 255), data.screen, 50, 50, 20, 20)
        draw_text(f'Height:{str(placement_height)}', data.default_font, (255, 255, 255), data.screen, 50, 70, 20, 20)
        draw_text(f'FPS:{str(floor(data.mainClock.get_fps()))}', data.default_font, (255, 255, 255), data.screen,
                  50, 90, 20, 20)

        # GUI recalculation

        button_data = [

        ]
        # create buttons
        data.button_list = []
        for each in button_data:
            buffer = list(each)
            x = GameButton(*buffer)
            data.button_list.append(x)

        # draw buttons and check for collisons

        for each in data.button_list:
            each.draw_button()

            if each.collidepoint(mx, my):
                if data.click:
                    each.goto_dest()

        # key events that are repeating and/or are at once
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:  player_entity.up(speed)
        if keys[pygame.K_s]:  player_entity.down(speed)
        if keys[pygame.K_a]:  player_entity.left(speed)
        if keys[pygame.K_d]:  player_entity.right(speed)

        if keys[pygame.K_ESCAPE]:
            current_map.save_map()
            running = False

        key_events = pygame.event.get()

        # key events that we do only once
        for event in key_events:
            if event.type == KEYDOWN:
                if event.key == K_DOWN:
                    if selected_tile_y < tile_set_h - 1:
                        selected_tile_y += 1
                elif event.key == K_UP:
                    if selected_tile_y > 0:
                        selected_tile_y -= 1
                elif event.key == K_RIGHT:
                    if selected_tile_x < tile_set_w - 1:
                        selected_tile_x += 1
                elif event.key == K_LEFT:
                    if selected_tile_x > 0:
                        selected_tile_x -= 1
                if event.key == K_p:
                    paint = not paint
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    if placement_height < 3:
                        placement_height += 1
                elif event.button == 5:
                    if placement_height > 0:
                        placement_height -= 1

        if paint:
            mouse_p = pygame.mouse.get_pressed()
            if mouse_p[0]:  current_map.set_tile(placement_height, mc_x, mc_y, 0, selected_tile_x,
                                                 selected_tile_y)
            if mouse_p[1]:
                tm, selected_tile_x, selected_tile_y = current_map.get_tile(placement_height, mc_x, mc_y)
            if mouse_p[2]:
                current_map.remove_tile(placement_height, mc_x, mc_y)
        else:
            for event in key_events:
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        current_map.set_tile(placement_height, mc_x, mc_y, 0, selected_tile_x, selected_tile_y)
                    if event.button == 2:
                        tm, selected_tile_x, selected_tile_y = current_map.get_tile(placement_height, mc_x, mc_y)
                    if event.button == 3:
                        current_map.remove_tile(placement_height, mc_x, mc_y)

        pygame.display.update()
        data.mainClock.tick(data.fps)
