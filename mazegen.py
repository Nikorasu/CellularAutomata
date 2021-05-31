#!/usr/bin/env python3
import pygame as pg

'''
This is a Conway's Game of Life simulation, using dictionary class.
By Nikolaus Stromberg  2021  nikorasu85@gmail.com
Uses methods from github.com/madelyneriksen/game-of-life
'''

FLLSCRN = False          # True for Fullscreen, or False for Window
WIDTH = 1600             # window Width
HEIGHT = 1000            # window Height
SIMFRAME = 2             # frames between sim updates
CSIZE = 10               # starting cell pixel size
FPS = 60                 # 30-90
VSYNC = True             # limit frame rate to refresh rate
SHOWFPS = True           # show framerate debug


class LifeGrid(dict):
    def __init__(self, *args, **kwargs):
        super(LifeGrid, self).__init__(*args, **kwargs)

    def __missing__(self, *args, **kwargs):
        return 0

    def check_cell(self, x: int, y: int):
        #x_coords = (x-1, x, x+1)
        #y_coords = (y-1, y, y+1)
        #total = 0
        #for x_coord in x_coords:
        #    for y_coord in y_coords:
        #        total += self[x_coord, y_coord]
        total = (self[x,(y-1)] + self[x,(y+1)] + self[(x-1),y] +
                self[(x+1),y] + self[(x-1),(y-1)] + self[(x-1),(y+1)] +
                self[(x+1),(y-1)] + self[(x+1),(y+1)])
        live, dead = [], []
        cell = self[x, y]
        # sim rules
        if total == 3 and not cell:
            live.append((x, y))
        elif total == 0 or total in range(5,8) and cell:  # total < 3 or total > 4  # not 2 <= total <= 3
            dead.append((x, y))
        elif cell:
            pass
        return live, dead

    def queue_cells(self):
        cells = []
        for x, y in self.keys():
            # Add all cell neighbors to the function.
            x_coords = (x-1, x, x+1)
            y_coords = (y-1, y, y+1)
            for x_coord in x_coords:
                for y_coord in y_coords:
                    cells.append((x_coord, y_coord))
        return cells

    def play_game(self):
        live, dead = [], []
        for x, y in self.queue_cells():
            step_live, step_dead = self.check_cell(x, y)
            live += step_live
            dead += step_dead
        # Grid doesn't change until every cell is accounted for.
        for x, y in dead:
            if self[x, y]:
                del self[x, y]
        for x, y in live:
            self[x, y] = 1

    def poke(self, pos, cSize, off_x, off_y, alive):
        spot = ((pos[0]-3)//cSize)+off_x, ((pos[1]-4)//cSize)+off_y  # edge rounding weird
        if alive : self[spot] = 1
        elif spot in self.keys() : del self[spot]

def main():
    pg.init()  # prepare window
    pg.display.set_caption("Life")
    # setup fullscreen or window mode
    if FLLSCRN:
        currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
        screen = pg.display.set_mode(currentRez, pg.SCALED | pg.NOFRAME | pg.FULLSCREEN, vsync=VSYNC)
    else: screen = pg.display.set_mode((WIDTH, HEIGHT), pg.SCALED, vsync=VSYNC)

    cSize = CSIZE
    cur_w, cur_h = screen.get_size()
    scaled_x, scaled_y = cur_w//cSize, cur_h//cSize

    centerx, centery = scaled_x//2, scaled_y//2
    lifeLayer = LifeGrid(
        {   # Lidka
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
        }
    )

    toggler = False
    updateDelayer = 0
    clock = pg.time.Clock()
    if SHOWFPS : font = pg.font.Font(None, 30)
    adjust_x, adjust_y = 0, 0

    # main loop
    while True:
        clock.tick(FPS)

        for e in pg.event.get():
            if e.type == pg.QUIT : return
            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    lifeLayer.poke(pg.mouse.get_pos(), cSize, adjust_x, adjust_y, True)
                if e.button == 3:
                    lifeLayer.poke(pg.mouse.get_pos(), cSize, adjust_x, adjust_y, False)
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_q or e.key == pg.K_ESCAPE: return
                if e.key == pg.K_SPACE : toggler = not toggler
                if e.key == pg.K_UP : adjust_y -= scaled_y//10
                if e.key == pg.K_DOWN : adjust_y += scaled_y//10
                if e.key == pg.K_LEFT : adjust_x -= scaled_x//10
                if e.key == pg.K_RIGHT : adjust_x += scaled_x//10
                if e.key == pg.K_KP_MINUS and cSize > 1:
                    old_cx, old_cy = scaled_x//2, scaled_y//2
                    cSize -= 1
                    scaled_x, scaled_y = cur_w//cSize, cur_h//cSize
                    centerx, centery = scaled_x//2, scaled_y//2
                    adjust_x += (old_cx - centerx)
                    adjust_y += (old_cy - centery)
                if e.key == pg.K_KP_PLUS and cSize < 20:
                    old_cx, old_cy = scaled_x//2, scaled_y//2
                    cSize += 1
                    scaled_x, scaled_y = cur_w//cSize, cur_h//cSize
                    centerx, centery = scaled_x//2, scaled_y//2
                    adjust_x += (old_cx - centerx)
                    adjust_y += (old_cy - centery)

        scaled_x, scaled_y = cur_w//cSize, cur_h//cSize
        out_image = pg.Surface((scaled_x, scaled_y)).convert()

        if toggler : updateDelayer+=1
        if updateDelayer>=SIMFRAME:
            updateDelayer=0
            lifeLayer.play_game()

        screen.fill(0)
        out_image.fill(0)

        pixel_array = pg.PixelArray(out_image)

        for x, y in lifeLayer.keys():
            visible_x = (0 + adjust_x) < x < (scaled_x + adjust_x)
            visible_y = (0 + adjust_y) < y < (scaled_y + adjust_y)
            if visible_x and visible_y:
                pixel_array[x - adjust_x, y - adjust_y] = (242,242,242)

        #pg.surfarray.blit_array(out_image, img_array)
        rescaled_img = pg.transform.scale(out_image, (cur_w, cur_h))
        screen.blit(rescaled_img, (0,0))

        # if true, displays the fps in the upper left corner, for debugging
        if SHOWFPS : screen.blit(font.render(str(int(clock.get_fps())), True, [0,200,0]), (8, 8))

        pg.display.update()


if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
