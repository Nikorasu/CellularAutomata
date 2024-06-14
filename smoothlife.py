#!/usr/bin/env python3
import numpy as np
from time import sleep
#from colorsys import hsv_to_rgb
from scipy.ndimage import convolve
import os
if os.name == 'nt': import msvcrt # for Windows keyboard input
else: import sys, termios, tty, select # for Linux keyboard input

# by Nik Stromberg  nikorasu85@gmail.com  Copyright (c) 2024
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
        nearby = convolve(self.array.astype(np.uint8), self.kouter, mode='wrap') / np.sum(self.kouter)
        center = convolve(self.array.astype(np.uint8), self.kinner, mode='wrap') / 9
        self.array[:] = 0
        rl1 = (center >= .5) & (nearby >= .26) & (nearby <= .46)
        rl2 = (center < .5) & (nearby >= .27) & (nearby <= .36)
        self.array[rl1 | rl2] = True

def print_state(array):
    output = "\x1b[H"
    for i in range(array.shape[0]):
        row_cells = []
        for j in range(array.shape[1]):
            #color = [int(c*255) for c in hsv_to_rgb(array[i,j],1,1)] #/360
            row_cells.append(f"\x1b[{'47' if array[i,j] else '40'}m \x1b[0m")
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
            print_state(sim_space.array)
            if os.name == 'nt' and msvcrt.kbhit() and msvcrt.getch() in (b'\x1b',b'q'): break # ESC or q to quit
            elif os.name == 'posix' and sys.stdin in select.select([sys.stdin],[],[],0)[0] and sys.stdin.read(1) in ('\x1b','q'): break
    except KeyboardInterrupt: pass # catch Ctrl+C
    finally: # ensures these run even if program is interrupted, so terminal functions properly on exit
        if os.name == 'posix': termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldsettings) # restore terminal settings
        print('\x1b[?25h')
