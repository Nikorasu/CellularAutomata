#!/usr/bin/env python3
import pygame as pg

'''
My attempt at a Game of Life simulation!
Copyright (c) 2021  Nikolaus Stromberg  nikorasu85@gmail.com
'''

FLLSCRN = False          # True for Fullscreen, or False for Window
WIDTH = 1000             # default 800
HEIGHT = 1000            # default 800
FPS = 60                 # 30-90
PRATIO = 10              # Pixel Size
SIMSPEED = 1             # Frames between Sim updates
SHOWFPS = True          # show framerate debug


class LifeGrid():
    def __init__(self, bigSize):
        self.size = (bigSize[0]//PRATIO, bigSize[1]//PRATIO)
        self.dict = {}
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                self.dict[(x,y)] = False
        self.image = pg.Surface(self.size).convert()
        self.img_array = pg.surfarray.array3d(self.image)

    def runLife(self):
        laststate = self.dict.copy()
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                neighbors = 0
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        chX, chY = (x+dx)%self.size[0], (y+dy)%self.size[1]
                        if laststate[(chX,chY)] and (dx,dy) != (0,0):
                            neighbors += 1
                # rules
                if self.dict[(x,y)] and not 2 <= neighbors <= 3:
                    self.dict[(x,y)] = False
                elif neighbors == 3:
                    self.dict[(x,y)] = True
                # update img_array if changed
                if self.dict[x,y] != laststate[x,y]:
                    self.img_array[x,y] = (242,242,242) if self.dict[x,y] else (0,0,0)

    def poke(self, pos, state):
        spot = ((pos[0]-2)//PRATIO), ((pos[1]-2)//PRATIO)  # -3 might fix rounding
        self.dict[spot] = state
        if spot[0]==self.size[0] : spot = 0,spot[1]
        if spot[1]==self.size[1] : spot = spot[0],0
        self.img_array[spot] = (240,240,240) if state else (0,0,0)


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
                    lifeLayer.poke(mousepos, True)
                if e.button == 3:
                    lifeLayer.poke(mousepos, False)
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
