#!/usr/bin/env python3
import numpy as np
from time import sleep
from colorsys import hsv_to_rgb
from scipy.ndimage import convolve
import os
if os.name == 'nt': import msvcrt # for Windows keyboard input
else: import sys, termios, tty, select # for Linux keyboard input

sim_size = (os.get_terminal_size().lines, os.get_terminal_size().columns)

class SmoothLife:

    def __init__(self):
        self.array = np.random.choice([True, False], size=sim_size , p=[.4, .6])
        radius = 10  # 10-12 seem stable, 5 makes smoothmazes!
        x, y = np.ogrid[-radius:radius+1, -radius:radius+1]
        dists = np.sqrt(x**2 + y**2)
        self.kouter = np.where(dists <= radius, 1, 0)
        self.kinner = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
        self.kouter[radius-1:radius+2, radius-1:radius+2] -= self.kinner

    def update(self):
        prev = self.array.copy()
        self.near = convolve(self.array.astype(np.uint8), self.kouter, mode='wrap') / np.sum(self.kouter)
        center = convolve(self.array.astype(np.uint8), self.kinner, mode='wrap') / 9
        self.array[:] = 0
        rl1 = (center >= .5) & (self.near >= .26) & (self.near <= .46) #live 1, if center >= .5 and .26 <= self.near <= .46
        rl2 = (center < .5) & (self.near >= .27) & (self.near <= .36) #birth 1, if center < .5 and .27 <= self.near <= .36
        self.array[rl1 | rl2] = True
        if (self.array == prev).all(): self.array = np.random.choice([True, False], size=sim_size, p=[.4, .6])
        self.print_state()

    def print_state(self):
        output = "\x1b[H"
        for i in range(self.array.shape[0]):
            row_cells = []
            for j in range(self.array.shape[1]):
                if self.array[i,j]:
                    color = [int(c*255) for c in hsv_to_rgb(self.near[i,j],1,1)] #/360
                    row_cells.append(f'\x1b[48;2;{color[0]};{color[1]};{color[2]}m \x1b[0m')
                else:
                    row_cells.append(f"\x1b[{'47' if self.array[i,j] else '40'}m \x1b[0m")
            output += ''.join(row_cells) + "\n"
        print(output[:-1], end='\r')

if __name__ == '__main__':
    try:
        print('\n' * (sim_size[0]-1))  # preserves terminal
        print('\x1b[?25l\x1b]0;SmoothLife',end='\a',flush=True)
        sim_space = SmoothLife()
        if os.name == 'posix': # if on Linux
            oldsettings = termios.tcgetattr(sys.stdin) # store old terminal settings
            tty.setcbreak(sys.stdin) # set terminal to cbreak mode (so input doesn't wait for enter)
        # Main simulation loop
        while ...:
            sim_space.update()
            sleep(0.05)
            if os.name == 'nt' and msvcrt.kbhit() and msvcrt.getch() in (b'\x1b',b'q'): break # ESC or q to quit
            elif os.name == 'posix' and sys.stdin in select.select([sys.stdin],[],[],0)[0] and sys.stdin.read(1) in ('\x1b','q'): break
    except KeyboardInterrupt: pass # catch Ctrl+C
    finally: # ensures these run even if program is interrupted, so terminal functions properly on exit
        if os.name == 'posix': termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldsettings) # restore terminal settings
        print('\x1b[?25h')
