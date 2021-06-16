import numpy as np
import re

with open('patterns/enterprise.rle') as file : contents = file.read().splitlines()

print(contents)
data = ''
dline = len(contents)
for num, line in enumerate(contents):
    if line.startswith('x'):
        x,y = [int(s) for s in re.findall(r'\d+',line)][:2]
        dline = num+1
    if num >= dline : data += line

pattern = np.zeros((x,y),np.int16)
splitdata = [s for s in re.split("([0-9]*[^0-9])", data) if s != ""]
print(splitdata)

cx, cy = 0, 0
for sd in splitdata:
    if sd[0].isdigit():
        #print(sd[:-1]) # number
        #print(sd[-1]) # data
        for c in range(int(sd[:-1])):
            if sd[-1] == 'b' : pattern[cx+c,cy] = 0
            elif sd[-1] == 'o' : pattern[cx+c,cy] = 1
            elif sd[-1] == '$':
                cy += 1
                cx = 0
        if sd[-1] == 'b' or sd[-1] == 'o' : cx += int(sd[:-1])
    elif sd == '!': pass #return pattern
    elif sd == '$':
        cy += 1
        cx = 0
    elif sd == 'b':
        pattern[cx,cy] = 0
        cx += 1
    elif sd == 'o':
        pattern[cx,cy] = 1
        cx += 1
print(pattern)
