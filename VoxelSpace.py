#############################################################################################################
# Procedural Building voxel drawing functions for MineCraft.
##############################################################################################################

from PIL import Image, ImageDraw
import math
import numpy as np
import MinecraftHelpers as helpers
from V3 import *
from libraries import voronoi_polygons, webcolors
import VoxelGraphics as vg
from Map import Map


def voronoi_cells(rows=11, cols=11, width_pixels=1000, height_pixels=1000, chaos=0.09):
    P = np.random.random((rows * cols, 2))

    for i, p in enumerate(P):
        row = math.floor(i / rows)
        col = i % cols

        pixels_per_col = width_pixels / cols
        pixels_per_row = height_pixels / rows

        p[0] = (width_pixels * chaos * p[0]) + (col * pixels_per_col - (chaos * pixels_per_col)) + (pixels_per_col / 2)
        p[1] = (height_pixels * chaos * p[1]) + (row * pixels_per_row - (chaos * pixels_per_row)) + (pixels_per_row / 2)

    return P


def color_range(one, two, steps=16):
    r = one[0] - two[0]
    g = one[1] - two[1]
    b = one[2] - two[2]

    colors = []
    for i in range(steps):
        # mult = round(255 / steps * i)
        col = (one[0] - round(r / steps * i), one[1] - round(g / steps * i), one[2] - round(b / steps * i))
        colors.append(col)

    return colors


def add_cells_to_image(polys, colors, draw, fill_line_bg='#000011', fill_line_fg='white', zone_data=Map()):
    for id, poly in enumerate(polys):

        lines = []
        for i, line in enumerate(poly):
            lines.append(line[0])
            lines.append(line[1])

        if id == zone_data.center_id:
            color = 'red'
        elif id in zone_data.first:
            color = 'green'
        elif id in zone_data.second:
            color = 'yellow'
        elif id in zone_data.third:
            color = 'blue'
        elif id in zone_data.fourth:
            color = 'cyan'
        else:
            color = helpers.choose_one(colors)
            color = webcolors.rgb_to_hex(color)

        draw.polygon(lines, fill=color)

        for i, line in enumerate(poly):
            l2 = poly[(i + 1) % len(poly)]

            draw.line((line[0], line[1], l2[0], l2[1]), fill=fill_line_bg, width=3)
            draw.line((line[0], line[1], l2[0], l2[1]), fill=fill_line_fg)


def add_points_to_image(points, draw, fill_line_bg='blue', fill_line_fg='yellow', c_size=2):
    for point in points:
        p = (int(point[0]), int(point[1]))
        draw.ellipse((p[0] - c_size, p[1] - c_size, p[0] + c_size, p[1] + c_size), fill=fill_line_fg,
                     outline=fill_line_bg)


def point_dir(point_id, dir="n", dist=1, cols=11):
    if dir == "n":
        return point_id - (cols * dist)
    elif dir == "s":
        return point_id + (cols * dist)
    elif dir == "e":
        return point_id + dist
    elif dir == "w":
        return point_id - dist
    elif dir == "ne":
        return point_id - (cols * dist) + 1
    elif dir == "se":
        return point_id + (cols * dist) + 1
    elif dir == "sw":
        return point_id + (cols * dist) - 1
    elif dir == "nw":
        return point_id - (cols * dist) - 1


def move_points_outwards(points, distance_multiplier=0.8, rows=11, cols=11, zone_data=Map(), band=180):
    center_point_id = int(cols * (rows - 1) / 2 + (cols - 1) / 2)
    center_point = points[center_point_id]
    zone_data.center_id = center_point_id
    zone_data.first = []
    zone_data.second = []
    zone_data.third = []
    zone_data.fourth = []

    # for dir in ["nw", "n", "ne", "w", "e", "sw", "s", "se"]:
    #     p2 = point_dir(center_point_id, dir=dir, dist=1, cols=cols)
    for p2, point in enumerate(points):
        to_point = points[p2]

        dist = vg.dist(Map(x=center_point[0], y=center_point[1], z=0), Map(x=to_point[0], y=to_point[1], z=0))
        angle = vg.angle_between(center_point[0], center_point[1], to_point[0], to_point[1])
        rad = math.radians(angle - 90)
        if dist < band * .9:  # Green
            points[p2][0] = center_point[0] + (math.sin(rad) * distance_multiplier * .6 * dist)
            points[p2][1] = center_point[1] + (math.cos(rad) * distance_multiplier * .6 * dist)
            zone_data.first.append(p2)
        elif dist < band * 1.35:  # Yellow
            points[p2][0] = center_point[0] + (math.sin(rad) * distance_multiplier * .7 * dist)
            points[p2][1] = center_point[1] + (math.cos(rad) * distance_multiplier * .7 * dist)
            zone_data.second.append(p2)
        elif dist < band * 1.7:  # Blue
            points[p2][0] = center_point[0] + (math.sin(rad) * distance_multiplier * .8 * dist)
            points[p2][1] = center_point[1] + (math.cos(rad) * distance_multiplier * .8 * dist)
            zone_data.third.append(p2)
        elif dist < band * 2.1:  # Black
            points[p2][0] = center_point[0] + (math.sin(rad) * distance_multiplier * .9 * dist)
            points[p2][1] = center_point[1] + (math.cos(rad) * distance_multiplier * .9 * dist)
            zone_data.fourth.append(p2)

    return points, zone_data


if __name__ == '__main__':
    width = 1200
    height = 1200
    chaos = 0.08
    rows = 11
    cols = 11

    im = Image.new('RGBA', (width, height))
    draw = ImageDraw.Draw(im)

    # Build cells and colorize them
    zone_data = Map()
    P = voronoi_cells(rows, cols, width, height, chaos)
    points, zone_data = move_points_outwards(P, distance_multiplier=0.8, rows=rows, cols=cols,
                                             band=int((width + height) / rows))

    polys = voronoi_polygons.polygons(points)

    colors = color_range((0, 0, 255), (0, 0, 0), 32)
    add_cells_to_image(polys, colors, draw, zone_data=zone_data)
    add_points_to_image(P, draw)

    add_points_to_image([P[11 * 5 + 5]], draw, fill_line_bg='red', c_size=5)

    im.show()
