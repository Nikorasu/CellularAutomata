#!/usr/bin/env python3
import numpy as np
from time import sleep
from colorsys import hsv_to_rgb
from scipy.ndimage import convolve
import os
if os.name == 'nt': import msvcrt # for Windows keyboard input
else: import sys, termios, tty, select # for Linux keyboard input

sim_size = (os.get_terminal_size().lines, os.get_terminal_size().columns)
density = 0.58
cycles = 12

class CellularAutomata:

    def __init__(self):
        self.array = np.random.choice([True, False], size=sim_size, p=[density, 1-density])#np.zeros(sim_size, dtype=np.bool_)
        #self.array[[1, -2], :] = self.array[:, [1, -2]] = 1
        self.array[[0, -1], :] = self.array[:, [0, -1]] = 1
        self.neighbors = np.zeros(sim_size, dtype=np.uint8)

    def iterate(self):
        self.countNeighbors()
        #self.neighbors = convolve(self.array.astype(np.uint8), np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]]), mode='constant', cval=1) #mode='wrap')
        #If a cell has > 4 "wall" neighbors, it becomes wall. Otherwise if cell has <=4, it becomes empty floor.
        self.array = self.neighbors > 4
        
    def countNeighbors(self):
        #p_array = np.pad(self.array, pad_width=1, mode='constant', constant_values=True)
        self.neighbors[:] = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if (dx, dy) != (0, 0):
                    shifted = np.roll(self.array, (dx, dy), (0, 1))
                    #np.add(self.neighbors, shifted[1:-1, 1:-1], out=self.neighbors)
                    np.add(self.neighbors, shifted, out=self.neighbors)

def print_state(array):
    output = "\x1b[H"
    for i in range(array.shape[0]):
        row_cells = []
        for j in range(array.shape[1]):
            #color = [int(c*255) for c in hsv_to_rgb(array[i,j],1,1)] #/360
            #row_cells.append(f'\x1b[48;2;{color[0]};{color[1]};{color[2]}m \x1b[0m')
            row_cells.append(f'\x1b[48;2;{array[i,j]*255};{array[i,j]*255};{array[i,j]*255}m \x1b[0m')
        output += ''.join(row_cells) + "\n"
    print(output[:-1], end='\r')

if __name__ == '__main__':
    try:
        print('\n' * (sim_size[0]-1))  # preserves terminal
        print('\x1b[?25l\x1b]0;mapgen',end='\a',flush=True)
        sim_space = CellularAutomata()
        if os.name == 'posix': # if on Linux
            oldsettings = termios.tcgetattr(sys.stdin) # store old terminal settings
            tty.setcbreak(sys.stdin) # set terminal to cbreak mode (so input doesn't wait for enter)
        # Main simulation loop
        while cycles>0:
            cycles -= 1            
            sim_space.iterate()
            sleep(0.2)
            print_state(sim_space.array)
            if os.name == 'nt' and msvcrt.kbhit() and msvcrt.getch() in (b'\x1b',b'q'): break # ESC or q to quit
            elif os.name == 'posix' and sys.stdin in select.select([sys.stdin],[],[],0)[0] and sys.stdin.read(1) in ('\x1b','q'): break
    except KeyboardInterrupt: pass # catch Ctrl+C
    finally: # ensures these run even if program is interrupted, so terminal functions properly on exit
        if os.name == 'posix': termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldsettings) # restore terminal settings
        print('\x1b[?25h')
