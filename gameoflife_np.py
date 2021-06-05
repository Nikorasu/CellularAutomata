#!/usr/bin/env python3
import pygame as pg
import numpy as np
from csv import reader

'''
My attempt at a Game of Life simulation, using NumPy.
Copyright (c) 2021  Nikolaus Stromberg  nikorasu85@gmail.com
'''

FLLSCRN = False          # True for Fullscreen, or False for Window
WIDTH = 1000             # default 800
HEIGHT = 1000            # default 800
PRATIO = 1                # starting cell pixel size
FPS = 60                 # 30-90
VSYNC = True             # limit frame rate to refresh rate
SHOWFPS = True           # show framerate debug



class LifeGrid():
    def __init__(self, bigSize, patcoords):
        self.size = (bigSize[0]//PRATIO, bigSize[1]//PRATIO)
        self.grid = np.zeros(self.size, np.int16)
        cenA_x = self.size[0]//2
        cenA_y = self.size[1]//2
        for x,y in patcoords:
            self.grid[cenA_x+x, cenA_y+y] = 1
        #self.grid[cenA_x:cenA_x+patcoords.shape[0],cenA_y:cenA_y+patcoords.shape[1]] = patcoords
        #self.grid = np.random.randint(0, 100, self.size, np.int16)
        #self.grid[self.grid <= 0.1 * 100] = 1
        #self.grid[self.grid > 0.1 * 100] = 0
        self.neighbor_counts = np.zeros(self.size, np.int16)

    def runLife(self):
        self.neighbor_counts[:] = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if (dx, dy) != (0, 0):
                    shifted = np.roll(self.grid, (dx, dy), (0, 1))
                    np.add(self.neighbor_counts, shifted, out=self.neighbor_counts)

        alive = self.grid > 0
        two = self.neighbor_counts == 2
        three = self.neighbor_counts == 3

        self.grid[:] = 0  # zero out the current grid

        # lots of unnecessary copying here, but it's so elegant - Ghast's wizardry
        self.grid[(alive & (two | three)) | ((~alive) & three)] = 1
        '''
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
        '''

    def poke(self, pos, valtog):
        spot = ((pos[0]-2)//PRATIO), ((pos[1]-2)//PRATIO)
        #if spot[0]==self.size[0] : spot = 0,spot[1]
        #if spot[1]==self.size[1] : spot = spot[0],0
        self.grid[spot] = valtog


def main():
    pg.init()  # prepare window
    pg.display.set_caption("Life")
    # setup fullscreen or window mode
    if FLLSCRN:
        currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
        screen = pg.display.set_mode(currentRez, pg.SCALED | pg.NOFRAME | pg.FULLSCREEN, vsync=VSYNC)
    else: screen = pg.display.set_mode((WIDTH, HEIGHT), pg.SCALED, vsync=VSYNC)

    cur_w, cur_h = screen.get_size()
    scaled_x, scaled_y = cur_w//PRATIO, cur_h//PRATIO
    centerx, centery = scaled_x//2, scaled_y//2
    #lifeLayer = LifeGrid((cur_w, cur_h))

    outimg = pg.Surface((scaled_x,scaled_y)).convert()

    patcoords = set()
    with open('patterns/symfiller') as patfile:
        pattern = reader(patfile)
        patcoords = { (int(x), int(y)) for x,y in pattern }
        #np.array([[int(x), int(y)] for x,y in pattern])

    lifeLayer = LifeGrid((cur_w, cur_h), patcoords)

    '''
    lifeLayer = LifeGrid({  # Lidka
        (centerx+0, centery+0): 1,
        (centerx-1, centery+0): 1,
        (centerx-1, centery+1): 1,
        (centerx-2, centery+2): 1,
        (centerx-3, centery+2): 1,
        (centerx-4, centery+2): 1,
        (centerx+2, centery-2): 1,
        (centerx+2, centery-3): 1,
        (centerx+3, centery-2): 1,
        (centerx+4, centery-2): 1,
        (centerx+4, centery+0): 1,
        (centerx+4, centery+1): 1,
        (centerx+4, centery+2): 1,
    })'''

    simFrame = 1  # starting speed
    toggler = False
    updateDelayer = 0
    clock = pg.time.Clock()
    if SHOWFPS : font = pg.font.Font(None, 30)
    adjust_x, adjust_y = 0, 0

    # main loop
    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return
            elif e.type == pg.MOUSEBUTTONDOWN:
                mousepos = pg.mouse.get_pos()
                if e.button == 1:
                    lifeLayer.poke(mousepos, 1)  # 16777215
                if e.button == 3:
                    lifeLayer.poke(mousepos, 0)
            elif e.type == pg.KEYDOWN and e.key == pg.K_SPACE:
                toggler = not toggler

        dt = clock.tick(FPS) / 100

        if toggler : updateDelayer+=1
        if updateDelayer>=simFrame:
            updateDelayer=0
            lifeLayer.runLife()

        screen.fill(0)

        pg.surfarray.blit_array(outimg, lifeLayer.grid * 0xFFFFFF)

        rescaled_img = pg.transform.scale(outimg, (cur_w, cur_h))
        screen.blit(rescaled_img, (0,0))

        # if true, displays the fps in the upper left corner, for debugging
        if SHOWFPS : screen.blit(font.render(str(int(clock.get_fps())), True, [0,200,0]), (8, 8))

        pg.display.update()


if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
