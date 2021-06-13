#!/usr/bin/env python3
import pygame as pg
import numpy as np
from csv import reader

'''
My attempt at a Game of Life simulation, using NumPy.
Copyright (c) 2021  Nikolaus Stromberg  nikorasu85@gmail.com
'''

FLLSCRN = False          # True for Fullscreen, or False for Window
WIDTH = 1200             # default 800
HEIGHT = 800             # default 800
PRATIO = 5               # starting cell pixel size
FPS = 60                 # 30-90
VSYNC = True             # limit frame rate to refresh rate
SHOWFPS = True           # show framerate debug


class LifeGrid():
    def __init__(self, maxSize, patcoords):
        self.size = maxSize
        self.grid = np.zeros(self.size, np.int16)
        cenA_x = self.size[0]//2
        cenA_y = self.size[1]//2
        for x,y in patcoords:
            self.grid[cenA_x+x, cenA_y+y] = 1
        self.neighbors = np.copy(self.grid)

    def runLife(self):
        # if storing count in grid for color, reset grid [anything above 1] = 1
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


def main():
    pg.init()  # prepare window
    pg.display.set_caption("Life")
    # setup fullscreen or window mode
    nativeRez = (pg.display.Info().current_w, pg.display.Info().current_h)
    if FLLSCRN : screen = pg.display.set_mode(nativeRez, pg.SCALED | pg.NOFRAME | pg.FULLSCREEN, vsync=VSYNC)
    else: screen = pg.display.set_mode((WIDTH, HEIGHT), pg.SCALED, vsync=VSYNC)

    cSize = PRATIO
    full_w, full_h = nativeRez
    win_w, win_h = screen.get_size()
    zoomed_w, zoomed_h = win_w//cSize, win_h//cSize
    centerx, centery = zoomed_w//2, zoomed_h//2

    patcoords = set()
    with open('patterns/symfiller') as patfile:
        pattern = reader(patfile)
        patcoords = { (int(x), int(y)) for x,y in pattern }

    #patcoords = {(0,0),(-1,0),(-1,1),(-2,2),(-3,2),(-4,2),  # Lidka
    #            (2,-2),(2,-3),(3,-2),(4,-2),(4,0),(4,1),(4,2)}
    #patcoords = {(0,0),(0,1),(0,2),(1,0),(-1,1),(3,0),(4,0),(4,-1)}  # 7468M
    #patcoords = {(0,0),(0,1),(0,2),(1,0),(-1,1)}  # R-pentomino

    lifeLayer = LifeGrid(nativeRez, patcoords)

    colors = np.array([0, 0x999999, 0x008000, 0x0000FF, 0xFFFF00, 0xFFA500, 0xFF4500, 0xFF0000, 0xFF00FF])

    simFrame = 1  # starting speed
    toggler = False
    updateDelayer = 0
    clock = pg.time.Clock()
    if SHOWFPS : font = pg.font.Font(None, 30)
    adjust_x, adjust_y = (full_w//2)-centerx, (full_h//2)-centery

    # main loop
    while True:
        clock.tick(FPS)

        for e in pg.event.get():
            if e.type == pg.QUIT : return
            elif e.type == pg.MOUSEBUTTONDOWN:
                mousepos = pg.mouse.get_pos()
                if e.button == 1 : lifeLayer.poke(mousepos, cSize, adjust_x, adjust_y, 1)
                if e.button == 3 : lifeLayer.poke(mousepos, cSize, adjust_x, adjust_y, 0)
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_q or e.key == pg.K_ESCAPE : return
                elif e.key == pg.K_SPACE or e.key==pg.K_KP_ENTER or e.key==pg.K_RETURN : toggler = not toggler
                elif e.key == pg.K_KP1 or e.key == pg.K_1 : simFrame = 1
                elif e.key == pg.K_KP2 or e.key == pg.K_2 : simFrame = 3
                elif e.key == pg.K_KP3 or e.key == pg.K_3 : simFrame = 5
                elif e.key == pg.K_KP4 or e.key == pg.K_4 : simFrame = 8
                elif e.key == pg.K_KP5 or e.key == pg.K_5 : simFrame = 11
                elif e.key == pg.K_KP6 or e.key == pg.K_6 : simFrame = 15
                elif e.key == pg.K_KP7 or e.key == pg.K_7 : simFrame = 20
                elif e.key == pg.K_KP8 or e.key == pg.K_8 : simFrame = 28
                elif e.key == pg.K_KP9 or e.key == pg.K_9 : simFrame = 42
                if e.key == pg.K_UP and adjust_y > 0:
                    adjust_y -= zoomed_h//10
                    if adjust_y < 0 : adjust_y = 0
                if e.key == pg.K_DOWN and adjust_y < full_h:
                    adjust_y += zoomed_h//10
                    if adjust_y+zoomed_h > full_h: adjust_y = full_h-zoomed_h
                if e.key == pg.K_LEFT and adjust_x > 0:
                    adjust_x -= zoomed_w//10
                    if adjust_x < 0 : adjust_x = 0
                if e.key == pg.K_RIGHT and adjust_x < full_w:
                    adjust_x += zoomed_w//10
                    if adjust_x+zoomed_w > full_w: adjust_x = full_w-zoomed_w
                if e.key == pg.K_KP_MINUS and cSize > 1:
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
                if e.key == pg.K_KP_PLUS and cSize < 12:
                    old_cx, old_cy = centerx, centery
                    cSize += 1
                    zoomed_w, zoomed_h = win_w//cSize, win_h//cSize
                    centerx, centery = zoomed_w//2, zoomed_h//2
                    adjust_x += (old_cx - centerx)
                    adjust_y += (old_cy - centery)

        if toggler : updateDelayer+=1
        if updateDelayer>=simFrame:
            updateDelayer=0
            lifeLayer.runLife()

        screen.fill(0)
        zoomed_w, zoomed_h = win_w//cSize, win_h//cSize
        outimg = pg.Surface((zoomed_w, zoomed_h)).convert()
        color_grid = colors[lifeLayer.neighbors]# * lifeLayer.grid
        pg.surfarray.blit_array(outimg, color_grid[adjust_x:adjust_x+zoomed_w, adjust_y:adjust_y+zoomed_h])# * 16777215)
        # 16777215 0xFFFFFF
        rescaled_img = pg.transform.scale(outimg, (win_w, win_h))
        screen.blit(rescaled_img, (0,0))
        # if true, displays the fps in the upper left corner, for debugging
        if SHOWFPS : screen.blit(font.render(str(int(clock.get_fps())), True, [0,200,0]), (8, 8))

        pg.display.update()


if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
