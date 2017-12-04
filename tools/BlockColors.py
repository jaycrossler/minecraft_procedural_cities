# Get http://minecraft-ids.grahamedgecombe.com/images/sprites/items-27.png and calculate colors
# from the block icons

from PIL import Image
import math
import numpy as np

im = Image.open("items-27.png")
x_count = 27
y_count = 27
width = math.floor(im.width / x_count)
height = math.floor(im.height / y_count)
TRANSPARENT = (0,0,0)

def block_main_colors(id):
    col = id % x_count
    row = math.floor(id / x_count)

    box = (col*width, row*height, (col+1)*width, (row+1)*height)
    block = im.crop(box)

    quan = block.quantize(colors=5, kmeans=3)
    block_top = quan.convert('RGB')

    all_colors = block_top.getcolors()
    if (not all_colors or len(all_colors) == 0):
        print("BLOCK:", id, "getcolors() not working", box)
        return TRANSPARENT, TRANSPARENT, TRANSPARENT

    sorted_colors = sorted(all_colors)
    colors = [x for x in sorted_colors if x[1] != TRANSPARENT]

    if len(colors) > 2:
        return colors[-1][1], colors[-2][1], colors[-3][1]
    elif len(colors) > 1:
        return colors[-1][1], colors[-2][1], TRANSPARENT
    elif len(colors) > 0:
        return colors[-1][1], TRANSPARENT, TRANSPARENT
    else:
        return TRANSPARENT, TRANSPARENT, TRANSPARENT

def process():
    for i in range(0,x_count*y_count):
        main, second, third = block_main_colors(i)
        # print("BLOCK: ", i, main, second, third)
        print("{\"lookup_id\":"+str(i)+", \"main_color\":"+str(main)+", \"second_color\":"+str(second)+", \"third_color\":"+str(third)+"},")
