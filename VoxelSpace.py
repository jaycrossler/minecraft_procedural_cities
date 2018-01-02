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
# from shapely.geometry import Point
# from shapely.geometry.polygon import Polygon
import collections
import networkx as nx


# TODO: Average out the dists of all cells per shell

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
    for poly_id, poly in enumerate(polys):

        lines = []
        for line_id, p1 in enumerate(poly):
            lines.append(p1[0])
            lines.append(p1[1])

        if poly_id == zone_data.center_id:
            color = 'red'
        elif poly_id in zone_data.first:
            color = 'green'
        elif poly_id in zone_data.second:
            color = 'yellow'
        elif poly_id in zone_data.third:
            color = 'brown'
        elif poly_id in zone_data.fourth:
            color = 'cyan'
        else:
            color = helpers.choose_one(colors)
            color = webcolors.rgb_to_hex(color)

        draw.polygon(lines, fill=color)

    for poly_id, poly in enumerate(polys):
        for line_id, p1 in enumerate(poly):
            p2 = poly[(line_id + 1) % len(poly)]

            is_outer = False
            is_river = False

            for w_poly, w_id in zone_data.outer_walls:
                if w_poly == poly_id and w_id == line_id:
                    is_outer = True
                    break
            for r_poly, r_id in zone_data.river_edges:
                if r_poly == poly_id and r_id == line_id:
                    is_river = True
                    break

            if is_outer:
                draw.line((p1[0], p1[1], p2[0], p2[1]), fill='black', width=7)

            if is_river:
                draw.line((p1[0], p1[1], p2[0], p2[1]), fill='blue', width=9)


def add_points_to_image(points, draw, fill_line_bg='blue', fill_line_fg='orange', c_size=2):
    for point in points:
        p = (int(point[0]), int(point[1]))
        draw.ellipse((p[0] - c_size, p[1] - c_size, p[0] + c_size, p[1] + c_size), fill=fill_line_fg,
                     outline=fill_line_bg)


def add_ids_to_image(points, draw, fill_line_bg='blue'):
    for id, point in enumerate(points):
        p = (int(point[0]) - 5, int(point[1]))
        draw.text(p, str(id), fill=fill_line_bg)


def add_line_segments_to_image(lines, draw, fill_line_bg='blue', c_size=2, skip_last=False):
    for id, p1 in enumerate(lines):
        if skip_last and id == len(lines)-1:
            break

        p2 = lines[(id + 1) % len(lines)]
        draw.line((p1[0], p1[1], p2[0], p2[1]), fill=fill_line_bg, width=c_size)


def dist_points(p1, p2):
    return vg.dist(Map(x=p1[0], y=p1[1], z=0), Map(x=p2[0], y=p2[1], z=0))


def move_points_outwards(points, distance_multiplier=0.8, zone_data=Map(), band=180):
    center_point = points[zone_data.center_id]
    zone_data.first = []
    zone_data.second = []
    zone_data.third = []
    zone_data.fourth = []

    for p2, point in enumerate(points):
        to_point = points[p2]

        dist = dist_points(center_point, to_point)
        angle = vg.angle_between(center_point[0], center_point[1], to_point[0], to_point[1])
        rad = math.radians(angle)
        band_name = None
        band_mult = 1

        if dist < band * .9:  # Green
            band_name = 'first'
            band_mult = .6
        elif dist < band * 1.35:  # Yellow
            band_name = 'second'
            band_mult = .7
        elif dist < band * 1.7:  # Brown
            band_name = 'third'
            band_mult = .8
        # elif dist < band * 2.1:  # Black
        #     band_name = 'fourth'
        #     band_mult = .9

        if band_name:
            points[p2][0] = center_point[0] + (math.cos(rad) * distance_multiplier * band_mult * dist)
            points[p2][1] = center_point[1] + (math.sin(rad) * distance_multiplier * band_mult * dist)
            zone_data[band_name].append(p2)

    return points, zone_data


def points_within_dist(points, center_id, dist=50):
    selected = []

    center = points[center_id]
    for id, point in enumerate(points):
        distance = dist_points(center, point)
        if distance <= dist and point is not center:
            selected.append(id)
    return selected


def zones_around_point(points, center_id, num=10):
    center = points[center_id]
    p2 = points[center_id + 1]
    dist = dist_points(center, p2)
    selected = points_within_dist(points, center_id, dist)

    while len(selected) < num:
        dist += 1.1
        selected.extend(points_within_dist(points, center_id, dist))
        selected = list(set(selected))

    return selected


def zones_rivers(polys, river_segments):
    all_rivers = []
    for seg_id, water_p1 in enumerate(river_segments):
        if seg_id == len(river_segments) - 1:
            break

        water_p2 = river_segments[(seg_id + 1) % len(river_segments)]

        for zone_id, poly in enumerate(polys):
            for line_id, p1 in enumerate(poly):
                p2 = poly[(line_id + 1) % len(poly)]

                is_river = False
                if (p1[0] == water_p1[0] and p1[1] == water_p1[1]) and (p2[0] == water_p2[0] and p2[1] == water_p2[1]):
                    is_river = True
                elif (p2[0] == water_p1[0] and p2[1] == water_p1[1]) and (p1[0] == water_p2[0] and p1[1] == water_p2[1]):
                    is_river = True

                if is_river:
                    all_rivers.append((zone_id, line_id))

    return all_rivers


def zones_outer_walls(polys, zone_ids, prec=5):
    # Make a list of all of the walls of points in zone_ids
    all_walls = []
    for zone_id in zone_ids:
        poly = polys[zone_id]
        for wall_id, wall in enumerate(poly):
            # Find walls both p1->p2 and p2->p1
            wall_next = poly[(wall_id + 1) % len(poly)]
            w1t = (int(round(wall[0] / prec) * prec), int(round(wall[1] / prec) * prec),
                   int(round(wall_next[0] / prec) * prec), int(round(wall_next[1] / prec) * prec))
            w2t = (int(round(wall_next[0] / prec) * prec), int(round(wall_next[1] / prec) * prec),
                   int(round(wall[0] / prec) * prec), int(round(wall[1] / prec) * prec))
            all_walls.append(w1t)
            all_walls.append(w2t)

    # Only take items with no duplicates
    no_dupe_walls = [item for item, count in collections.Counter(all_walls).items() if count == 1]

    # Find which walls have segments with no duplicates
    walls_out = []
    for zone_id in zone_ids:
        poly = polys[zone_id]
        for wall_id, wall in enumerate(poly):
            wall_next = poly[(wall_id + 1) % len(poly)]
            w1t = (int(round(wall[0] / 5) * 5), int(round(wall[1] / 5) * 5), int(round(wall_next[0] / 5) * 5),
                   int(round(wall_next[1] / 5) * 5))
            w2t = (int(round(wall_next[0] / 5) * 5), int(round(wall_next[1] / 5) * 5), int(round(wall[0] / 5) * 5),
                   int(round(wall[1] / 5) * 5))
            if w1t in no_dupe_walls or w2t in no_dupe_walls:
                walls_out.append((zone_id, wall_id))

    return walls_out


def stretch_out(polys, P, rows=11, cols=11, dist=6):
    for i, poly in enumerate(polys):
        row = math.floor(i / rows)
        col = i % cols
        col_space = col * dist
        row_space = row * dist

        for point in poly:
            point[0] += col_space
            point[1] += row_space

    for i, point in enumerate(P):
        row = math.floor(i / rows)
        col = i % cols
        col_space = col * dist
        row_space = row * dist
        point[0] += col_space
        point[1] += row_space

    return polys, P


def edge_graph_from_polys(polys, prec=5):
    edge_graph = nx.Graph()

    for poly_id, poly in enumerate(polys):
        for wall_id, wall in enumerate(poly):
            wall_next = poly[(wall_id + 1) % len(poly)]
            w1 = (int(round(wall[0] / prec) * prec), int(round(wall[1] / prec) * prec))
            w2 = (int(round(wall_next[0] / prec) * prec), int(round(wall_next[1] / prec) * prec))
            dist = dist_points(w1, w2)

            if (w1[0] == w2[0] and w1[1] == w2[1]) or (w1[0] in [0, width] and w2[0] in [0, height]):
                pass
                # Duplicate points
            else:
                edge_graph.add_node(w1)
                edge_graph.add_node(w2)
                if w1[0] in [0, width] or w2[0] in [0, height]:
                    dist += 1000

                edge_graph.add_edge(w1, w2, weight=dist)
                # print("Cell", poly_id, "Adding edge: ", (w1, w2, dist))

    return edge_graph


def round_edge_points(polys, precision, width, height):
    for poly_id, poly in enumerate(polys):
        for wall_id, wall in enumerate(poly):
            wall[0] = int(round(wall[0] / precision) * precision)
            wall[1] = int(round(wall[1] / precision) * precision)

            if wall[0] < 0:
                wall[0] = 0
            if wall[0] > width:
                wall[0] = width
            if wall[1] < 0:
                wall[1] = 0
            if wall[1] > height:
                wall[1] = height

    return polys


def edge_point_closest_to(polys, x, y):
    closest_point = None
    closest_dist = 1000000

    for edge_id, edge_pt in enumerate(polys):
        dist = dist_points(edge_pt, (x, y))
        if dist < closest_dist:
            closest_dist = dist
            closest_point = edge_pt
    return int(round(closest_point[0])), int(round(closest_point[1]))


if __name__ == '__main__':
    width = 1200
    height = 1200
    chaos = 0.08
    rows = 11
    cols = 11
    zones = 10
    round_precision = 5
    stretch = 6

    im = Image.new('RGBA', (width + (cols + 2) * stretch, height + (rows + 2) * stretch))
    draw = ImageDraw.Draw(im)

    # Build cells and colorize them
    zone_data = Map()

    # np.random.seed(41)

    points = voronoi_cells(rows, cols, width, height, chaos)
    center_point_id = int(cols * (rows - 1) / 2 + (cols - 1) / 2)
    zone_data.center_id = center_point_id

    points, zone_data = move_points_outwards(points, distance_multiplier=1, band=int((width + height) / rows),
                                             zone_data=zone_data)

    central_points = zones_around_point(points, zone_data.center_id, zones)
    central_zones = [points[id] for id in central_points]

    polys = voronoi_polygons.polygons(points)
    polys = round_edge_points(polys, round_precision, width, height)
    zone_data.outer_walls = zones_outer_walls(polys, central_points)

    zone_data.edge_graph = edge_graph_from_polys(polys)
    r1 = edge_point_closest_to(zone_data.edge_graph.nodes, 0, height * .7)
    r2 = edge_point_closest_to(zone_data.edge_graph.nodes, width, height *.55)
    # print("Checking for", r1, "to", r2)
    river = nx.shortest_path(zone_data.edge_graph, r1, r2, weight='weight')
    zone_data.river_edges = zones_rivers(polys, river)

    polys, points = stretch_out(polys, points, stretch)

    colors = color_range((0, 255, 0), (0, 0, 0), 16)
    add_cells_to_image(polys, colors, draw, zone_data=zone_data)
    add_points_to_image(points, draw)

    add_points_to_image(central_zones, draw, fill_line_bg='gold', c_size=9)
    add_points_to_image([points[zone_data.center_id]], draw, fill_line_bg='red', c_size=5)
    add_ids_to_image(points, draw)
    # add_line_segments_to_image(river, draw, fill_line_bg='gold', c_size=9, skip_last=True)
    # add_line_segments_to_image(river, draw, fill_line_bg='blue', c_size=7, skip_last=True)

    im.show()
