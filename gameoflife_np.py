#!/usr/bin/env python3
import pygame as pg
import numpy as np

'''
My attempt at a Game of Life simulation, using NumPy.
Copyright (c) 2021  Nikolaus Stromberg  nikorasu85@gmail.com
'''

FLLSCRN = False          # True for Fullscreen, or False for Window
WIDTH = 1000             # default 800
HEIGHT = 1000            # default 800
FPS = 60                 # 30-90
PRATIO = 10              # Pixel Size
SIMSPEED = 2             # Frames between Sim updates
SHOWFPS = True          # show framerate debug


class LifeGrid():
    def __init__(self, bigSize):
        self.size = (bigSize[0]//PRATIO, bigSize[1]//PRATIO)
        self.image = pg.Surface(self.size).convert()
        self.img_array = pg.surfarray.array2d(self.image)

    def runLife(self):
        laststate = np.copy(self.img_array)
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                neighbors = 0
                neighbors = np.sum(laststate[x - 1 : x + 2, y - 1 : y + 2]) / 16777215  # - laststate[x,y]
                # rules
                if self.img_array[x,y] and not 3 <= neighbors <= 4:
                    self.img_array[x,y] = 0
                elif neighbors == 3:
                    self.img_array[x,y] = 16777215

    def poke(self, pos, valtog):
        spot = ((pos[0]-2)//PRATIO), ((pos[1]-2)//PRATIO)
        if spot[0]==self.size[0] : spot = 0,spot[1]
        if spot[1]==self.size[1] : spot = spot[0],0
        self.img_array[spot] = valtog


def main():
    pg.init()  # prepare window
    pg.display.set_caption("Life")
    # setup fullscreen or window mode
    if FLLSCRN:
        currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
        screen = pg.display.set_mode(currentRez, pg.SCALED | pg.NOFRAME | pg.FULLSCREEN, vsync=1)
    else: screen = pg.display.set_mode((WIDTH, HEIGHT), pg.SCALED, vsync=1)

    cur_w, cur_h = screen.get_size()
    screenSize = (cur_w, cur_h)
    toggler = False

    lifeLayer = LifeGrid(screenSize)

    clock = pg.time.Clock()
    if SHOWFPS : font = pg.font.Font(None, 30)
    updateDelayer = 0

    # main loop
    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return
            elif e.type == pg.MOUSEBUTTONDOWN:
                mousepos = pg.mouse.get_pos()
                if e.button == 1:
                    lifeLayer.poke(mousepos, 16777215)
                if e.button == 3:
                    lifeLayer.poke(mousepos, 0)
            elif e.type == pg.KEYDOWN and e.key == pg.K_SPACE:
                toggler = not toggler

        dt = clock.tick(FPS) / 100

        if toggler : updateDelayer+=1
        if updateDelayer>=SIMSPEED:
            updateDelayer=0
            lifeLayer.runLife()

        screen.fill(0)

        pg.surfarray.blit_array(lifeLayer.image, lifeLayer.img_array)

        rescaled_img = pg.transform.scale(lifeLayer.image, (cur_w, cur_h))
        screen.blit(rescaled_img, (0,0))

        # if true, displays the fps in the upper left corner, for debugging
        if SHOWFPS : screen.blit(font.render(str(int(clock.get_fps())), True, [0,200,0]), (8, 8))

        pg.display.update()


if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
