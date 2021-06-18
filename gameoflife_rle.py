#!/usr/bin/env python3
import pygame as pg
import numpy as np
import re

'''
Conway's Game of Life simulation, using NumPy, and with RLE support!
Copyright (c) 2021  Nikolaus Stromberg  nikorasu85@gmail.com
'''

PATFILE = 'patterns/64mil.rle'
SHOWGEN = True          # show generation count
MAPSIZE = 2000          # size of available simulation space
COLOR = False           # start with color mode, or black and white
PRATIO = 5              # starting size of individual cells
WIDTH = 1200            # window width, default 1200
HEIGHT = 800            # window height, default 800
FLLSCRN = False         # True for fullscreen, False for window
FPS = 60                # overall target framerate/limit
VSYNC = True            # limit frame rate to refresh rate
SHOWFPS = True          # show framerate debug

class LifeGrid():
    def __init__(self, maxSize, pattern):
        self.size = maxSize
        self.grid = np.zeros(self.size, np.int16)
        cen_x = (self.size[0]//2) - (pattern.shape[0]//2)
        cen_y = (self.size[1]//2) - (pattern.shape[1]//2)
        self.grid[cen_x:cen_x+pattern.shape[0], cen_y:cen_y+pattern.shape[1]] = pattern
        self.neighbors = np.copy(self.grid)

    def runLife(self):
        self.neighbors[:] = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if (dx, dy) != (0, 0):
                    shifted = np.roll(self.grid, (dx, dy), (0, 1))
                    np.add(self.neighbors, shifted, out=self.neighbors)

        alive = self.grid > 0
        twos = self.neighbors == 2
        threes = self.neighbors == 3

        self.grid[:] = 0  # zero out the current grid
        # lots of unnecessary copying here, but it's so elegant - Ghast's wizardry
        self.grid[(alive & (twos | threes)) | ((~alive) & threes)] = 1

    def poke(self, pos, cSize, off_x, off_y, status):
        spot = ((pos[0]-2)//cSize)+off_x, ((pos[1]-4)//cSize)+off_y  # edge rounding weird
        if spot[0]==self.size[0] : spot = 0,spot[1]
        if spot[1]==self.size[1] : spot = spot[0],0
        self.grid[spot] = status
        self.neighbors[spot] = status

def readRLE(contents):
    data = ''
    dline = len(contents)

    for num, line in enumerate(contents):
        if line.startswith('x'):
            x,y = [int(s) for s in re.findall(r'\d+',line)][:2]
            dline = num+1
        if num >= dline : data += line

    pattern = np.zeros((x,y), np.int16)
    splitdata = [s for s in re.split("([0-9]*[^0-9])", data) if s != ""]

    cx, cy = 0, 0
    for sd in splitdata:
        if sd[0].isdigit():
            for c in range(int(sd[:-1])):
                if sd[-1] == 'b' : pattern[cx+c,cy] = 0
                elif sd[-1] == 'o' : pattern[cx+c,cy] = 1
                elif sd[-1] == '$':
                    cy += 1
                    cx = 0
            if sd[-1] == 'b' or sd[-1] == 'o' : cx += int(sd[:-1])
        elif sd == '!': return pattern
        elif sd == '$':
            cy += 1
            cx = 0
        elif sd == 'b':
            pattern[cx,cy] = 0
            cx += 1
        elif sd == 'o':
            pattern[cx,cy] = 1
            cx += 1

def main():
    pg.init()  # prepare window
    pg.display.set_caption("Life")
    # setup fullscreen or window mode
    nativeRez = (pg.display.Info().current_w, pg.display.Info().current_h)
    if FLLSCRN : screen = pg.display.set_mode(nativeRez, pg.SCALED | pg.NOFRAME | pg.FULLSCREEN, vsync=VSYNC)
    else: screen = pg.display.set_mode((WIDTH, HEIGHT), pg.SCALED, vsync=VSYNC)

    simFrame = 1  # starting speed
    cSize = PRATIO
    colorTog = COLOR
    full_w, full_h = MAPSIZE, MAPSIZE
    win_w, win_h = screen.get_size()
    zoomed_w, zoomed_h = win_w//cSize, win_h//cSize
    centerx, centery = zoomed_w//2, zoomed_h//2
    adjust_x, adjust_y = (full_w//2)-centerx, (full_h//2)-centery

    try:
        with open(PATFILE) as file : contents = file.read().splitlines()
        pattern = readRLE(contents)
    except:
        pattern = np.array([[0, 1, 1], [1, 1, 0], [0, 1, 0]])  # R-pentomino

    life = LifeGrid((full_w,full_h), pattern)
    colors = np.array([0, 0x999999, 0x008000, 0x0000FF, 0xFFFF00, 0xFFA500, 0xFF4500, 0xFF0000, 0xFF00FF])

    toggler = False
    genCount, updateDelayer = 0, 0
    clock = pg.time.Clock()
    font = pg.font.Font(None, 30)  # if SHOWFPS:

    # main loop
    while True:
        clock.tick(FPS)
        for e in pg.event.get():
            if e.type == pg.QUIT : return
            elif e.type == pg.MOUSEBUTTONDOWN:
                mousepos = pg.mouse.get_pos()
                if e.button == 1 : life.poke(mousepos, cSize, adjust_x, adjust_y, 1)
                if e.button == 3 : life.poke(mousepos, cSize, adjust_x, adjust_y, 0)
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_q or e.key == pg.K_ESCAPE : return
                elif e.key==pg.K_SPACE or e.key==pg.K_KP_ENTER or e.key==pg.K_RETURN : toggler = ~toggler
                elif e.key == pg.K_KP1 or e.key == pg.K_1 : simFrame = 1
                elif e.key == pg.K_KP2 or e.key == pg.K_2 : simFrame = 3
                elif e.key == pg.K_KP3 or e.key == pg.K_3 : simFrame = 5
                elif e.key == pg.K_KP4 or e.key == pg.K_4 : simFrame = 8
                elif e.key == pg.K_KP5 or e.key == pg.K_5 : simFrame = 11
                elif e.key == pg.K_KP6 or e.key == pg.K_6 : simFrame = 15
                elif e.key == pg.K_KP7 or e.key == pg.K_7 : simFrame = 20
                elif e.key == pg.K_KP8 or e.key == pg.K_8 : simFrame = 28
                elif e.key == pg.K_KP9 or e.key == pg.K_9 : simFrame = 42
                elif e.key == pg.K_KP0 or e.key == pg.K_0 or e.key == pg.K_c : colorTog = ~colorTog
                if (e.key == pg.K_w or e.key == pg.K_i or e.key == pg.K_UP) and adjust_y > 0:
                    adjust_y -= zoomed_h//10
                    if adjust_y < 0 : adjust_y = 0
                if (e.key == pg.K_s or e.key == pg.K_k or e.key == pg.K_DOWN) and adjust_y < full_h:
                    adjust_y += zoomed_h//10
                    if adjust_y+zoomed_h > full_h: adjust_y = full_h-zoomed_h
                if (e.key == pg.K_a or e.key == pg.K_j or e.key == pg.K_LEFT) and adjust_x > 0:
                    adjust_x -= zoomed_w//10
                    if adjust_x < 0 : adjust_x = 0
                if (e.key == pg.K_d or e.key == pg.K_l or e.key == pg.K_RIGHT) and adjust_x < full_w:
                    adjust_x += zoomed_w//10
                    if adjust_x+zoomed_w > full_w: adjust_x = full_w-zoomed_w
                if (e.key == pg.K_MINUS or e.key == pg.K_KP_MINUS) and cSize > 1:
                    old_cx, old_cy = centerx, centery
                    cSize -= 1
                    zoomed_w, zoomed_h = win_w//cSize, win_h//cSize
                    centerx, centery = zoomed_w//2, zoomed_h//2
                    adjust_x += (old_cx - centerx)
                    adjust_y += (old_cy - centery)
                    if adjust_x+zoomed_w > full_w : adjust_x -= (adjust_x + zoomed_w) - full_w
                    elif adjust_x < 0 : adjust_x = 0
                    if adjust_y+zoomed_h > full_h : adjust_y -= (adjust_y + zoomed_h) - full_h
                    elif adjust_y < 0 : adjust_y = 0
                if (e.key == pg.K_EQUALS or e.key == pg.K_KP_PLUS) and cSize < 12:
                    old_cx, old_cy = centerx, centery
                    cSize += 1
                    zoomed_w, zoomed_h = win_w//cSize, win_h//cSize
                    centerx, centery = zoomed_w//2, zoomed_h//2
                    adjust_x += (old_cx - centerx)
                    adjust_y += (old_cy - centery)

        if toggler : updateDelayer += 1
        if updateDelayer>=simFrame:
            genCount, updateDelayer = genCount+1, 0
            life.runLife()

        zoomed_w, zoomed_h = win_w//cSize, win_h//cSize
        outimg = pg.Surface((zoomed_w, zoomed_h)).convert()

        if colorTog:
            color_grid = colors[life.neighbors]# * life.grid
            pg.surfarray.blit_array(outimg, color_grid[adjust_x:adjust_x+zoomed_w, adjust_y:adjust_y+zoomed_h])
        else:  # 16777215 0xFFFFFF
            pg.surfarray.blit_array(outimg,life.grid[adjust_x:adjust_x+zoomed_w,adjust_y:adjust_y+zoomed_h]*16777215)

        rescaled_img = pg.transform.scale(outimg, (win_w, win_h))
        screen.fill(0)
        screen.blit(rescaled_img, (0,0))
        if SHOWGEN:
            gentxt = font.render(str(genCount), True, [100,100,100])
            gentxt_rect = gentxt.get_rect(center=(win_w/2, 20))
            screen.blit(gentxt, gentxt_rect)
        # displays the fps in the upper left corner, for debugging
        if SHOWFPS : screen.blit(font.render(str(int(clock.get_fps())), True, [0,200,0]), (8, 8))
        pg.display.update()

if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
