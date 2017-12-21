#############################################################################################################
# Procedural Building voxel drawing functions for MineCraft.
##############################################################################################################

# import mcpi
import math
import numpy as np
from Map import Map
import MinecraftHelpers as helpers
from numbers import Integral
from V3 import *

TO_RADIANS = 3.1415926 / 180.
TO_DEGREES = 180. / 3.1415926
ICOS = [1, 0, -1, 0]
ISIN = [0, 1, 0, -1]
NUM_MAX = 12345678


def get_seed():
    # TODO: Return the world seed, add in x,y,z
    return np.random.randint(65000)


def init_with_seed(seed):
    np.random.seed(seed)


def rand_in_range(min, max):
    return np.random.randint(min, max)


def point_along_circle(center, radius, points, num, options=Map()):
    # If it's a rectangle, send in the points passed in
    if points == 4 and options.p1 and options.p2:
        p1 = options.p1
        p2 = options.p2
        num = num % 4
        if num == 0:
            return V3(min(p1.x, p2.x), p1.y, min(p1.z, p2.z))
        elif num == 1:
            return V3(max(p1.x, p2.x), p1.y, min(p1.z, p2.z))
        elif num == 2:
            return V3(max(p1.x, p2.x), p1.y, max(p1.z, p2.z))
        elif num == 3:
            return V3(min(p1.x, p2.x), p1.y, max(p1.z, p2.z))

    # Otherwise, find the points based on how far along a circle it is
    if not options.precision:
        options.precision = 1
    if not options.direction:
        options.direction = "y"

    # If aiming to have a 17x17 building (center + 8 in both directions),
    #   set r=8 and multiply so that the radius entered is 11.3
    #   also rotate everything by 1/8th to that sides aren't diagonal
    if options.align_to_cells:
        radius *= 1.4125
        if not options.rotation:
            options.rotation = 1 / (points * 2)  # TODO: Verify this works for hexagons

    if not options.rotation:
        options.rotation = 0

    # find the angle
    theta = (options.rotation + (num / points)) * 2 * math.pi

    width = ((2 * options.width) / radius) or 1
    depth = ((2 * options.depth) / radius) or 1

    if options.direction is "y":
        x = center.x + (radius * math.cos(theta) * width)
        y = center.y
        z = center.z + (radius * math.sin(theta) * depth)
    else:
        print("NOT YET IMPLEMENTED - circle points along X,Z axis")

    return V3(round(x, options.precision), round(y, options.precision), round(z, options.precision))


def evaluate_3d_range(pos, x_min, x_max, y_min, y_max, z_min, z_max, func):
    # Evaluate a range of x,y,z and return points that match func
    points = []
    for y in range(int(y_min), int(y_max)):
        for z in range(int(z_min), int(z_max)):
            for x in range(int(x_min), int(x_max)):
                if func(x, y, z):
                    points.append(V3(pos.x + x, pos.y + y, pos.z + z))
    return points


def inside_vector(p1, center, p2=None):
    if p1 and p2:
        p = p1 + p2
        p = p * .5
    else:
        p = p1

    xz_cardinality = cardinality(p, center, as_vector=True)
    y = 0
    if p.y < center.y:
        y = 1
    elif p.y > center.y:
        y = -1

    return V3(xz_cardinality.x, y, xz_cardinality.z)


def angle_between(p1a, p1b, p2a, p2b):
    return (math.atan2(p2b - p1b, p2a - p1a) * (180.0 / math.pi) + 360) % 360


def cardinality(p1, p2, as_vector=False):
    angle = angle_between(p1.x, p1.z, p2.x, p2.z)
    c = "e" if not as_vector else V3(1, 0, 0)
    if 22.5 < angle <= 67.5:
        c = "se" if not as_vector else V3(1, 0, 1)
    elif 67.5 < angle <= 112.5:
        c = "s" if not as_vector else V3(0, 0, 1)
    elif 112.5 < angle <= 157.5:
        c = "sw" if not as_vector else V3(-1, 0, 1)
    elif 157.5 < angle <= 202.5:
        c = "w" if not as_vector else V3(-1, 0, 0)
    elif 202.5 < angle <= 247.5:
        c = "nw" if not as_vector else V3(-1, 0, -1)
    elif 247.5 < angle <= 292.5:
        c = "n" if not as_vector else V3(0, 0, -1)
    elif 292.5 < angle <= 337.5:
        c = "ne" if not as_vector else V3(1, 0, -1)
    return c


def points_spaced(points, options=Map()):
    if not options.every:
        options.every = 1

    new_points = []

    if options.every == 1:
        new_points = points
    else:
        for i, vec in enumerate(points):
            if i % options.every == 0:
                new_points.append(vec)

    return new_points


def extrude(points, options=Map()):
    spacing = options.spacing or V3(0, 0, 0)
    size = options.size or V3(0, 0, 0)

    new_points = []

    if not spacing == V3(0, 0, 0):
        for i, vec in enumerate(points, 1):
            new_points.append(V3(vec.x + spacing.x, vec.y + spacing.y, vec.z + spacing.z))

    # TODO: Should extrusion be affected by size?  Should x,y,z work independently?

    if not size == V3(0, 0, 0):
        for i, vec in enumerate(points, 1):
            for x in range(abs(size.x)):
                n = -1 if size.x < 0 else 1
                new_points.append(V3(vec.x + (n * x), vec.y, vec.z))

            for y in range(abs(size.y)):
                n = -1 if size.y < 0 else 1
                new_points.append(V3(vec.x, vec.y + (n * y), vec.z))

            for z in range(abs(size.z)):
                n = -1 if size.z < 0 else 1
                new_points.append(V3(vec.x, vec.y, vec.z + (n * z)))

    return new_points


def middle_of_line(points, options=Map()):
    # Map(center=true, max_width=2, point_per=10)
    if not options.point_per:
        options.point_per = 20
    if not options.max_width:
        options.max_width = 2
    if not options.min:
        options.min = 3

    point_count = len(points)
    num = 1
    new_points = []
    if options.center and point_count >= options.min:
        if point_count >= options.point_per:
            num = options.max_width
        mid = math.floor(point_count / 2) - 1
        new_points.append(points[mid])
        if num > 1:
            new_points.append(points[mid + 1])

    return new_points


def highest(face_points):
    high = -30000
    for p in face_points:
        if p.y > high:
            high = p.y
    return high


def lowest(face_points):
    low = 30000
    for p in face_points:
        if p.y < low:
            low = p.y
    return low


def poly_point_edges(face_points, options=Map()):
    # TODO: Pass in cardinality to know which to return
    left_x = points_along_poly(face_points, Map(side="left_x"))
    right_x = points_along_poly(face_points, Map(side="right_x"))
    left_z = points_along_poly(face_points, Map(side="left_z"))
    right_z = points_along_poly(face_points, Map(side="right_z"))
    top = points_along_poly(face_points, Map(side="top"))
    bottom = points_along_poly(face_points, Map(side="bottom"))

    left = left_x if len(left_x) < len(left_z) else left_z
    right = right_x if len(right_x) < len(right_z) else right_z

    out = top
    out.extend(bottom)
    out.extend(left)
    out.extend(right)
    return out, top, bottom, left, right


def rectangular_face(p1, p2, h):
    points = []
    left_line = []
    right_line = []
    top_line = []
    bottom_line = getLine(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z)
    width = len(bottom_line)

    for y in range(h):
        for i, vec in enumerate(bottom_line):
            new_point = V3(vec.x, vec.y + y, vec.z)
            # Add it to a line or the center point mass
            if y == h - 1:
                top_line.append(new_point)
            elif i == 0:
                left_line.append(new_point)
            elif i == width - 1:
                right_line.append(new_point)
            else:
                points.append(new_point)

    return points, top_line, bottom_line, left_line, right_line


def next_to(p, num=1):
    ps = []
    ps.append(Map(point=V3(p.x - num, p.y, p.z), dir=4))
    ps.append(Map(point=V3(p.x + num, p.y, p.z), dir=3))
    ps.append(Map(point=V3(p.x, p.y, p.z - num), dir=1))
    ps.append(Map(point=V3(p.x, p.y, p.z + num), dir=2))
    return ps


def points_around(points, cardinality="e"):
    around = []

    if cardinality in ["e", "w"]:
        for p in points:
            around.append(p + V3(-1, -1, 0))
            around.append(p + V3(-1, 0, 0))
            around.append(p + V3(-1, 1, 0))
            around.append(p + V3(0, -1, 0))
            around.append(p + V3(0, 1, 0))
            around.append(p + V3(1, -1, 0))
            around.append(p + V3(1, 0, 0))
            around.append(p + V3(1, 1, 0))
    else:
        for p in points:
            around.append(p + V3(0, -1, -1))
            around.append(p + V3(0, 0, -1))
            around.append(p + V3(0, 1, -1))
            around.append(p + V3(0, -1, 0))
            around.append(p + V3(0, 1, 0))
            around.append(p + V3(0, -1, 1))
            around.append(p + V3(0, 0, 1))
            around.append(p + V3(0, 1, 1))

    around = list(set(around))
    for p in points:
        around.remove(p)

    return around


def rectangle_inner(p1, p2, num):
    p1, p2 = min_max_points(p1, p2)
    return V3(p1.x + num, p1.y, p1.z + num), V3(p2.x - num, p2.y, p2.z - num)


def rectangle(p1, p2):
    rim = []
    left_line = []
    right_line = []
    top_line = []
    inner_points = []

    # TODO: Work with multiple axis
    if p1.y == p2.y:
        # Flat on ground (Y Axis)
        x_line = getLine(p1.x, p1.y, p1.z, p2.x, p1.y, p1.z)
        width = len(x_line)
        h = int(round(abs(p2.z - p1.z)))

        for z in range(h):
            for i, vec in enumerate(x_line):
                new_point = V3(vec.x, vec.y, vec.z + z)
                if z == h - 1:
                    top_line.append(new_point)
                elif i == 0:
                    left_line.append(new_point)
                elif i == width - 1:
                    right_line.append(new_point)
                else:
                    inner_points.append(new_point)
    else:
        print("ERROR - NOT YET IMPLEMENTED, TRYING TO MAKE A Non-Y RECTANGLE")

    rim.extend(top_line)
    rim.extend(x_line)
    rim.extend(left_line)
    rim.extend(right_line)

    return rim, inner_points  # , top_line, x_line, left_line, right_line


def up(v, amount=1):
    return V3(v.x, v.y + amount, v.z)


def bounds(face_points):
    out = Map()
    x_high = y_high = z_high = -NUM_MAX
    x_low = y_low = z_low = NUM_MAX

    for p in face_points:
        if "pos" in p:
            point = p.pos
        else:
            point = p

        if point.x > x_high: x_high = point.x
        if point.y > y_high: y_high = point.y
        if point.z > z_high: z_high = point.z

        if point.x < x_low: x_low = point.x
        if point.y < y_low: y_low = point.y
        if point.z < z_low: z_low = point.z

    out.highest = int(y_high)
    out.lowest = int(y_low)
    out.x_high = int(x_high)
    out.x_low = int(x_low)
    out.z_high = int(z_high)
    out.z_low = int(z_low)

    out.center = V3((out.x_high + out.x_low) * .5, (out.highest + out.lowest) * .5, (out.z_high + out.z_low) * .5)
    out.x_radius = out.x_high - out.center.x + 1
    out.y_radius = out.highest - out.center.y + 1
    out.z_radius = out.z_high - out.center.z + 1

    return out


def points_along_poly(face_points, options=Map()):
    side = options.side or "bottom"
    points = []

    # Y searching
    if side == "top":
        highest = -30000
        for p in face_points:
            if p.y > highest:
                highest = p.y

        for p in face_points:
            if p.y == highest:
                points.append(p)
    elif side == "bottom":
        lowest = 30000
        for p in face_points:
            if p.y < lowest:
                lowest = p.y

        for p in face_points:
            if p.y == lowest:
                points.append(p)

    # x searching
    if side == "left_x":
        highest = -30000
        for p in face_points:
            if p.x > highest:
                highest = p.x

        for p in face_points:
            if p.x == highest:
                points.append(p)

    elif side == "right_x":
        lowest = 30000
        for p in face_points:
            if p.x < lowest:
                lowest = p.x

        for p in face_points:
            if p.x == lowest:
                points.append(p)

    # z searching
    if side == "left_z":
        highest = -30000
        for p in face_points:
            if p.z > highest:
                highest = p.z

        for p in face_points:
            if p.z == highest:
                points.append(p)

    elif side == "right_z":
        lowest = 30000
        for p in face_points:
            if p.z < lowest:
                lowest = p.z

        for p in face_points:
            if p.z == lowest:
                points.append(p)

    return points


def unique_points(point_generator):
    done = set()

    if type(point_generator) == list:
        # multiple generators
        for gen in point_generator:
            for p in gen:
                if p not in done:
                    done.add(p)
    else:
        # just one generator
        for p in point_generator:
            if p not in done:
                done.add(p)
    return done


def rand_triangular(low, mid, high):
    return round(np.random.triangular(low, mid, high))


def min_max_points(p1, p2):
    x_min = min(p1.x, p2.x)
    x_max = max(p1.x, p2.x)
    z_min = min(p1.z, p2.z)
    z_max = max(p1.z, p2.z)
    p1 = V3(x_min, p1.y, z_min)
    p2 = V3(x_max, p2.y, z_max)
    return p1, p2


def dists(p1, p2, inclusive=True):
    # returns voxel distances between points
    inc = 1 if inclusive else 0

    width = abs(p2.x - p1.x) + inc
    height = abs(p2.y - p1.y) + inc
    depth = abs(p2.z - p1.z) + inc

    return width, height, depth


def ninths(p1, p2, preset_w, preset_z, double=True):
    # takes [preset1, preset2] rectangle out of [p1,p2] rectangle, then partitions the rest
    partitions = []

    # TODO: Don't always centralize
    show_t = show_b = show_l = show_r = False

    width, null, depth = dists(p1, p2)
    if width > (preset_w + 2):
        show_l = show_r = True
    elif width > (preset_w + 1):
        show_l = True

    if depth > (preset_z + 2):
        show_t = show_b = True
    elif depth > (preset_z + 1):
        show_t = True

    preset_w = min(preset_w, width - 1)
    preset_z = min(preset_z, depth - 1)

    w_h = math.floor(((width - preset_w) / 2))
    d_h = math.floor(((depth - preset_z) / 2))

    x1 = p1.x
    x2 = p1.x + w_h
    x3 = p1.x + w_h + preset_w
    x4 = p2.x

    a = p1.z
    b = p1.z + d_h
    c = p1.z + d_h + preset_z
    d = p2.z

    # a1 - a2 - a3 - a4
    # b1 - b2 - b3 - b4
    # c1 - c2 - c3 - c4
    # d1 - d2 - d3 - d2

    padding = 0 if (double == False or w_h == 0 or d_h == 0) else 1

    # First Row
    if show_t and show_l: partitions.append(Map(p1=V3(x1, p1.y, a), p2=V3(x2 - padding, p1.y, b - padding)))
    if show_t: partitions.append(Map(p1=V3(x2, p1.y, a), p2=V3(x3 - padding, p1.y, b - padding)))
    if show_t and show_r: partitions.append(Map(p1=V3(x3, p1.y, a), p2=V3(x4, p1.y, b - padding)))
    # Mid Row
    if show_l: partitions.append(Map(p1=V3(x1, p1.y, b), p2=V3(x2 - padding, p1.y, c - padding)))
    partitions.append(Map(p1=V3(x2, p1.y, b), p2=V3(x3 - padding, p1.y, c - padding), largest=True))
    if show_r: partitions.append(Map(p1=V3(x3, p1.y, b), p2=V3(x4, p1.y, c - padding)))
    # Bottom Row
    if show_b and show_l: partitions.append(Map(p1=V3(x1, p1.y, c), p2=V3(x2 - padding, p1.y, d)))
    if show_b: partitions.append(Map(p1=V3(x2, p1.y, c), p2=V3(x3 - padding, p1.y, d)))
    if show_b and show_r: partitions.append(Map(p1=V3(x3, p1.y, c), p2=V3(x4, p1.y, d)))

    # Add in width and depth info
    out = []
    for i, ninth in enumerate(partitions):
        ninth.iteration = 0
        ninth.width, null, ninth.depth = dists(ninth.p1, ninth.p2)
        if (ninth.width) > 1 and (ninth.depth) > 1:
            out.append(ninth)

    return out


def partition(p1, p2, min_x=15, min_z=15, rate=1.01, rate_dec=.01, iterations=0, ignore_small=False):
    # Take a square, and recursively break in down until it's around min_x, min_z
    p1, p2 = min_max_points(p1, p2)

    recs = []
    width = p2.x - p1.x + 1
    depth = p2.z - p1.z + 1

    # If the square is too small, return just the square
    if width < min_x or depth < min_z or np.random.rand() > rate:
        # print(iterations, "Too small, returning ", p1, p2, "w:", width, "h:", depth)
        if False:  # ignore_small:
            return []
        else:
            return [Map(p1=p1, p2=p2, iteration=iterations, width=width, depth=depth)]

    # Otherwise, cut the square into smaller pieces
    if width > depth:
        mid = rand_triangular(0, width / 2, width)

        pmid1 = V3(p1.x + mid, p1.y, p2.z)
        pmid2 = V3(p1.x + mid, p1.y, p1.z)

        # print(iterations, "Cutting length wise, size ", width, "x", depth, "at mid", mid)
        recs.extend(partition(p1, pmid1, min_x, min_z, rate - rate_dec, rate_dec, iterations + 1))
        recs.extend(partition(pmid2, p2, min_x, min_z, rate - rate_dec, rate_dec, iterations + 1))
    else:
        mid = rand_triangular(0, depth / 2, depth)

        pmid1 = V3(p2.x, p1.y, p1.z + mid)
        pmid2 = V3(p1.x, p1.y, p1.z + mid)

        # print(iterations, "Cutting depth wise, size ", width, "x", depth, "at mid", mid)
        recs.extend(partition(p1, pmid1, min_x, min_z, rate - rate_dec, rate_dec, iterations + 1))
        recs.extend(partition(pmid2, p2, min_x, min_z, rate - rate_dec, rate_dec, iterations + 1))

    return recs


def partitions_to_blocks(partitions, options=Map()):
    blocks = []
    inner_blocks = []
    min_size = options.min_size or 0
    max_size = options.max_size or 1000

    for part in partitions:
        if options.or_mix:
            valid = (min_size <= part.width <= max_size) or (min_size <= part.depth <= max_size)
        else:
            valid = (min_size <= part.width <= max_size) and (min_size <= part.depth <= max_size)

        if valid:
            p1 = part.p1
            p2 = part.p2
            rec, inner_rec = rectangle(p1, p2)
            for block in rec:
                if not block in blocks and type(block) == V3:
                    blocks.append(block)
            for block in inner_rec:
                if not block in blocks and type(block) == V3:
                    inner_blocks.append(block)

    return blocks, inner_blocks


def square(center, radius, tight=1, height=10, axis="y", filled=False, thickness=1):
    def edge(i):
        return abs(i + .5) >= (radius - thickness)

    if axis == "y":
        def func(x, y, z):
            return True if filled else (edge(x) or edge(z))

        return evaluate_3d_range(center, -radius, radius, 0, 1, -radius, radius, func)
    elif axis == "x":
        def func(x, y, z):
            return True if filled else (edge(y) or edge(z))

        return evaluate_3d_range(center, 0, 1, -radius, radius, -radius, radius, func)
    else:
        def func(x, y, z):
            return True if filled else (edge(x) or edge(y))

        return evaluate_3d_range(center, -radius, radius, -radius, radius, 0, 1, func)


def circle(center, radius, tight=.7, height=10, axis="y", filled=False, thickness=1):
    # Tight defines how constricted the circle is
    if axis == "y":
        def func(x, y, z):
            c = math.sqrt(x * x + z * z)
            return c < (radius - tight) and (True if filled else (c >= (radius - thickness - tight)))

        return evaluate_3d_range(center, -radius, radius, 0, 1, -radius, radius, func)
    elif axis == "x":
        def func(x, y, z):
            c = math.sqrt(y * y + z * z)
            return c < (radius - tight) and (True if filled else (c >= (radius - thickness - tight)))

        return evaluate_3d_range(center, 0, 1, -radius, radius, -radius, radius, func)
    else:
        def func(x, y, z):
            c = math.sqrt(x * x + y * y)
            return c < (radius - tight) and (True if filled else (c >= (radius - thickness - tight)))

        return evaluate_3d_range(center, -radius, radius, -radius, radius, 0, 1, func)


def box(center, radius, tight=1, height=10, filled=False, thickness=1):
    def func(x, y, z):
        def edge(i):
            return abs(i + .5) >= (radius - thickness)

        return True if filled else (edge(x) or edge(y) or edge(z))

    return evaluate_3d_range(center, -radius, radius, -radius, radius, -radius, radius, func)


def build_bounds_for_3d_range(radius, options):
    if options.min_x: min_x = -abs(options.min_x)
    elif options.min_x_pct: min_x = options.min_x_pct * -(2 * radius)
    else: min_x = -radius

    if options.max_x: max_x = options.min_x
    elif options.max_x_pct: max_x = options.max_x_pct * (2 * radius)
    else: max_x = radius

    if options.min_y: min_y = -abs(options.min_y)
    elif options.min_y_pct: min_y = -radius + (options.min_y_pct * (2 * radius))
    else: min_y = -radius

    if options.max_y: max_y = options.min_y
    elif options.max_y_pct: max_y = options.max_y_pct * (2 * radius)
    else: max_y = radius

    if options.min_z: min_z = -abs(options.min_z)
    elif options.min_z_pct: min_z = options.min_z_pct * -(2 * radius)
    else: min_z = -radius

    if options.max_z: max_z = options.min_z
    elif options.max_z_pct: max_z = options.max_z_pct * (2 * radius)
    else: max_z = radius

    return min_x, max_x, min_y, max_y, min_z, max_z    
    

def sphere(center, radius, tight=.5, height=10, filled=False, thickness=1, options=Map()):
    def func(x, y, z):
        c = math.sqrt(x * x + y * y + z * z)
        return c < (radius - tight) and (True if filled else (c >= (radius - thickness - tight)))

    min_x, max_x, min_y, max_y, min_z, max_z = build_bounds_for_3d_range(radius, options)
    return evaluate_3d_range(center, min_x, max_x, min_y, max_y, min_z, max_z, func)


def cylinder(center, radius, tight=.5, height=10, filled=False, thickness=1):
    def func(x, y, z):
        c = math.sqrt(x * x + z * z)
        return c < (radius - tight) and (
            True if filled else (c >= (radius - thickness - tight) or y < thickness or y >= (height - thickness)))

    return evaluate_3d_range(center, -radius, radius, 0, height, -radius, radius, func)


def cone(center, radius, tight=.4, height=10, filled=False, thickness=1):
    def func(x, y, z):
        c = math.sqrt(x * x + z * z)
        outer = c < ((radius * (1 - y / float(height))) - tight)
        inner = c >= ((radius * (1 - y / float(height))) - tight - thickness)
        return outer and (True if filled else (y < thickness or inner))

    return evaluate_3d_range(center, -radius, radius, 0, height, -radius, radius, func)


def rectangular_pyramid(center, radius, tight=.4, height=10, filled=False, thickness=1):
    def func(x, y, z):
        def edge(i, rad):
            return abs(i) >= (rad - thickness)

        rad = (radius * (height - y) / height)
        vert = (-rad < x < rad) and (-rad < z < rad)
        return vert and (True if filled else (edge(x, rad) or edge(z, rad) or y == 0))

    return evaluate_3d_range(center, -radius, radius, 0, height, -radius, radius, func)


def rectangular_pyramid_x(center, radius, tight=.4, height=10, filled=False, thickness=1):
    def func(x, y, z):
        rad = (radius * (height - y) / height)
        vert = (-rad < x < rad) and (-rad < z < rad)
        return vert and (True if filled else (z < thickness))

    return evaluate_3d_range(center, -radius, radius, 0, height, -radius, radius, func)


def triangular_prism(p1, p2, height, radius=2, sloped=False, chop_pct=0, filled=False):
    p1, p2 = min_max_points(p1, p2)

    slope = abs(radius / height)

    faces = []
    h = 0

    grow_limit = radius * chop_pct

    while radius > grow_limit:
        if sloped:
            p1, p2 = move_points_together(p1, p2, 1)

        at_top = (radius - slope) < grow_limit

        corner_vecs = line_thick_into_corners(p1.x, p1.z, p2.x, p2.z, radius)
        p1_1 = V3(corner_vecs[0].x, p1.y + h, corner_vecs[0].y)
        p1_3 = V3(corner_vecs[1].x, p1.y + h, corner_vecs[1].y)

        p2_3 = V3(corner_vecs[2].x, p2.y + h, corner_vecs[2].y)
        p2_1 = V3(corner_vecs[3].x, p2.y + h, corner_vecs[3].y)
        if filled or at_top:
            faces.append(getFace([p1_1, p1_3, p2_3, p2_1]))
        else:
            l1 = get_line_from_points(p1_1, p1_3)
            l2 = get_line_from_points(p1_3, p2_3)
            l3 = get_line_from_points(p2_3, p2_1)
            l4 = get_line_from_points(p2_1, p1_1)
            faces.append(l1 + l2 + l3 + l4)

        radius -= slope
        h += 1 if height > 0 else -1

    out = unique_points(faces)

    return out


def prism_roof(p1, p2, height, radius=2, sloped=0, chop_pct=0, endpoint_out=0, material="Oak Wood",
               endpoint_stairs=True):
    # This is very similar with triangular_prism above, possibly refactor it

    p1, p2 = min_max_points(p1, p2)

    slope = abs(radius / height)
    sloped = slope * sloped

    h = 0
    grow_limit = (height * chop_pct)

    if endpoint_out is not 0:
        sloped = 0

    l1 = []  # end
    l2 = []  # side
    l3 = []  # end
    l4 = []  # side
    l5 = []  # top bar

    material1 = material2 = material3 = material4 = None

    while radius > grow_limit:
        if sloped is not 0:
            p1, p2 = move_points_together(p1, p2, slope)

        corner_vecs = line_thick_into_corners(p1.x, p1.z, p2.x, p2.z, radius)
        p1_1 = V3(corner_vecs[0].x, p1.y + h, corner_vecs[0].y)
        p1_3 = V3(corner_vecs[1].x, p1.y + h, corner_vecs[1].y)

        p2_3 = V3(corner_vecs[2].x, p2.y + h, corner_vecs[2].y)
        p2_1 = V3(corner_vecs[3].x, p2.y + h, corner_vecs[3].y)

        # Determine materials if stairs (on the first level built only)
        if material1 is None:
            center = (p1 + p2) * .5

            is_square = abs(dist(p1_1, p1_3) - dist(p1_3, p2_3)) < 1

            if endpoint_stairs or is_square:
                material1 = stair_facing_point((p1_1 + p1_3) * .5, center, material, True)
                material3 = stair_facing_point((p2_3 + p2_1) * .5, center, material, True)
            else:
                material1 = material3 = material

            material2 = stair_facing_point((p1_3 + p2_3) * .5, center, material, True)
            material4 = stair_facing_point((p2_1 + p1_1) * .5, center, material, True)

        # Build lines to make up roofs  # TODO: Look at this, sometimes weird lines result
        # if radius <= 0.5:
        #     l5.extend(get_line_from_points(p1_3, p2_3))
        #     l5.extend(get_line_from_points(p2_1, p1_1))
        # else:
        l1.extend(get_line_from_points(p1_1, p1_3))
        l3.extend(get_line_from_points(p2_3, p2_1))

        # Move points closer if ends go in
        if endpoint_out:
            p1_3, p2_3 = move_points_together(p1_3, p2_3, -endpoint_out)
            p2_1, p1_1 = move_points_together(p2_1, p1_1, -endpoint_out)
            l2.extend(get_line_from_points(p1_3, p2_3))
            l4.extend(get_line_from_points(p2_1, p1_1))
        else:
            l2.extend(get_line_from_points(p1_3, p2_3))
            l4.extend(get_line_from_points(p2_1, p1_1))

        radius -= slope

        # Fill in top of roof if at top-most level
        if 0 < radius < grow_limit:
            dist_between = dist(p1_3, p2_1)  # TODO: Sometimes should be switched with p2_1 and p1_1
            if dist_between > 2:
                while dist_between > 1:
                    p1_3, null = move_points_together(p1_3, p2_1, 1)
                    p2_3, null = move_points_together(p2_3, p1_1, 1)
                    l5.extend(get_line_from_points(p1_3, p2_3))
                    dist_between -= 1

        h += 1 if height > 0 else -1

    blocks_list = list()
    blocks_list.append(Map(blocks=l1, material=material1))  # TODO: Should this only record stair direction, then
    blocks_list.append(Map(blocks=l3, material=material3))  # calculate the material at render time to apply tex?
    blocks_list.append(Map(blocks=l2, material=material2))
    blocks_list.append(Map(blocks=l4, material=material4))
    blocks_list.append(Map(blocks=l5, material=material))

    return blocks_list


def stair_facing_point(p1, center, material, rising=True):
    facing = cardinality(p1, center)[-1]
    data = ["e", "w", "s", "n"].index(facing)
    if not rising: data += 4

    if 'stair' in material:
        block = material['stair']
    else:
        block = 67

    return block, data


def dist(p1, p2):
    return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2 + (p2.z - p1.z) ** 2)


def best_points_for_triangular_roof(corners):
    p1a = (corners[0] + corners[1]) * .5
    p2a = (corners[2] + corners[3]) * .5

    p1b = (corners[3] + corners[0]) * .5
    p2b = (corners[1] + corners[2]) * .5

    if dist(p1a, p2a) > dist(p1b, p2b):
        rad_x = abs(corners[0].x - p1a.x)
        rad_z = abs(corners[0].z - p1b.z)
        end_cap_lines = [[corners[0], corners[1]], [[corners[2], corners[3]]]]
        side_lines = [[corners[1], corners[2]], [[corners[3], corners[0]]]]
        return p1a, p2a, min(rad_x, rad_z), end_cap_lines, side_lines

    else:
        rad_x = abs(corners[0].x - p1a.x)
        rad_z = abs(corners[0].z - p1b.z)
        end_cap_lines = [[corners[3], corners[0]], [[corners[1], corners[2]]]]
        side_lines = [[corners[0], corners[1]], [[corners[2], corners[3]]]]
        return p1b, p2b, min(rad_x, rad_z), end_cap_lines, side_lines


def move_points_together(p1, p2, dist=1):
    diff = p2 - p1

    p1x = p1.x
    p2x = p2.x
    p1y = p1.y
    p2y = p2.y
    p1z = p1.z
    p2z = p2.z

    if diff.x > 0:
        p1x += dist
        p2x -= dist
    elif diff.x < 0:
        p1x -= dist
        p2x += dist

    if diff.y > 0:
        p1y += dist
        p2y -= dist
    elif diff.y < 0:
        p1y -= dist
        p2y += dist

    if diff.z > 0:
        p1z += dist
        p2z -= dist
    elif diff.z < 0:
        p1z -= dist
        p2z += dist

    return V3(p1x, p1y, p1z), V3(p2x, p2y, p2z)


# def triangular_prism_faces(p1, p2, height, width=3, radius=False, sloped=False, filled=False, base=False, ends=False):
#     radius = radius or (((width - 1) / 2) if width > 1 else 1)
#     if radius < 0:
#         return []
#
#     # Find the 6 points that form triangles around p1 and p2
#     corner_vecs = line_thick_into_corners(p1.x, p1.z, p2.x, p2.z, radius)
#     p1_1 = V3(corner_vecs[0].x, p1.y, corner_vecs[0].y)
#     p1_2 = V3(p1.x, p1.y + height, p1.z)
#     p1_3 = V3(corner_vecs[1].x, p1.y, corner_vecs[1].y)
#
#     p2_3 = V3(corner_vecs[2].x, p2.y, corner_vecs[2].y)
#     p2_2 = V3(p2.x, p2.y + height, p2.z)
#     p2_1 = V3(corner_vecs[3].x, p2.y, corner_vecs[3].y)
#
#     faces = []
#     faces.append(getFace([p1_1, p1_2, p2_2, p2_1]))
#     faces.append(getFace([p1_3, p1_2, p2_2, p2_3]))
#     if base: faces.append(getFace([p1_1, p1_3, p2_3, p2_1]))
#     if ends:
#         faces.append(getFace([p1_1, p1_2, p1_3]))
#         faces.append(getFace([p2_1, p2_2, p2_3]))
#
#     if filled and (round(radius) >= 0):
#         faces.extend(triangular_prism_faces(p1, p2, height=height, radius=radius - 1, sloped=sloped))
#
#     return faces


def line_thick_into_corners(x1, y1, x2, y2, thickness=1):
    angle = math.atan2(y2 - y1, x2 - x1)
    p0 = Map(x=0, y=0)
    p1 = Map(x=0, y=0)
    p2 = Map(x=0, y=0)
    p3 = Map(x=0, y=0)

    p0.x = round(x1 + thickness * math.cos(angle + math.pi / 2), 4)
    p0.y = round(y1 + thickness * math.sin(angle + math.pi / 2), 4)
    p1.x = round(x1 + thickness * math.cos(angle - math.pi / 2), 4)
    p1.y = round(y1 + thickness * math.sin(angle - math.pi / 2), 4)
    p2.x = round(x2 + thickness * math.cos(angle - math.pi / 2), 4)
    p2.y = round(y2 + thickness * math.sin(angle - math.pi / 2), 4)
    p3.x = round(x2 + thickness * math.cos(angle + math.pi / 2), 4)
    p3.y = round(y2 + thickness * math.sin(angle + math.pi / 2), 4)

    return [p0, p1, p2, p3]


# Initially based on scripts from:
# https://github.com/nebogeo/creative-kids-coding-cornwall/blob/master/minecraft/python/dbscode_minecraft.py

def toblerone(t, pos, size, options=Map()):
    if not options.create_now:
        options.create_now = False

    points = []
    for y in reversed(range(0, int(size.y))):
        for z in range(0, int(size.z)):
            for x in range(0, int(size.x)):
                a = size.x * (1 - y / float(size.y)) * 0.5
                if x > size.x / 2.0 - a and x < a + size.x / 2.0:
                    if options.create_now:
                        helpers.create_block(V3(pos.x + x, pos.y + y, pos.z + z), options.material)
                    else:
                        points.append(V3(pos.x + x, pos.y + y, pos.z + z))
    return points


# =====================================================
# Following Code by Alexander Pruss and under the MIT license
# From https://github.com/arpruss/raspberryjammod/blob/master/mcpipy/drawing.py

def makeMatrix(compass, vertical, roll):
    m0 = matrixMultiply(yawMatrix(compass), pitchMatrix(vertical))
    return matrixMultiply(m0, rollMatrix(roll))


def applyMatrix(m, v):
    if m is None:
        return v
    else:
        return V3(m[i][0] * v[0] + m[i][1] * v[1] + m[i][2] * v[2] for i in range(3))


def matrixDistanceSquared(m1, m2):
    d2 = 0.
    for i in range(3):
        for j in range(3):
            d2 += (m1[i][j] - m2[i][j]) ** 2
    return d2


def iatan2(y, x):
    """One coordinate must be zero"""
    if x == 0:
        return 90 if y > 0 else -90
    else:
        return 0 if x > 0 else 180


def icos(angleDegrees):
    """Calculate a cosine of an angle that must be a multiple of 90 degrees"""
    return ICOS[(angleDegrees % 360) // 90]


def isin(angleDegrees):
    """Calculate a sine of an angle that must be a multiple of 90 degrees"""
    return ISIN[(angleDegrees % 360) // 90]


def matrixMultiply(a, b):
    c = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for i in range(3):
        for j in range(3):
            c[i][j] = a[i][0] * b[0][j] + a[i][1] * b[1][j] + a[i][2] * b[2][j]
    return c


def yawMatrix(angleDegrees):
    if isinstance(angleDegrees, Integral) and angleDegrees % 90 == 0:
        return [[icos(angleDegrees), 0, -isin(angleDegrees)],
                [0, 1, 0],
                [isin(angleDegrees), 0, icos(angleDegrees)]]
    else:
        theta = angleDegrees * TO_RADIANS
        return [[math.cos(theta), 0., -math.sin(theta)],
                [0., 1., 0.],
                [math.sin(theta), 0., math.cos(theta)]]


def rollMatrix(angleDegrees):
    if isinstance(angleDegrees, Integral) and angleDegrees % 90 == 0:
        return [[icos(angleDegrees), -isin(angleDegrees), 0],
                [isin(angleDegrees), icos(angleDegrees), 0],
                [0, 0, 1]]
    else:
        theta = angleDegrees * TO_RADIANS
        return [[math.cos(theta), -math.sin(theta), 0.],
                [math.sin(theta), math.cos(theta), 0.],
                [0., 0., 1.]]


def pitchMatrix(angleDegrees):
    if isinstance(angleDegrees, Integral) and angleDegrees % 90 == 0:
        return [[1, 0, 0],
                [0, icos(angleDegrees), isin(angleDegrees)],
                [0, -isin(angleDegrees), icos(angleDegrees)]]
    else:
        theta = angleDegrees * TO_RADIANS
        return [[1., 0., 0.],
                [0., math.cos(theta), math.sin(theta)],
                [0., -math.sin(theta), math.cos(theta)]]


def get2DTriangle(a, b, c):
    """get the points of the 2D triangle"""
    min_x = {}
    maxX = {}

    for line in (traverse2D(a, b), traverse2D(b, c), traverse2D(a, c)):
        for p in line:
            min_x0 = min_x.get(p[1])
            if min_x0 == None:
                min_x[p[1]] = p[0]
                maxX[p[1]] = p[0]
                yield (p)
            elif p[0] < min_x0:
                for x in range(p[0], min_x0):
                    yield (x, p[1])
                min_x[p[1]] = p[0]
            else:
                maxX0 = maxX[p[1]]
                if maxX0 < p[0]:
                    for x in range(maxX0, p[0]):
                        yield (x, p[1])
                    maxX[p[1]] = p[0]


def getFace(vertices):
    if len(vertices) < 1:
        raise StopIteration
    if len(vertices) <= 2:
        for p in traverse(V3(vertices[0]), V3(vertices[1])):
            yield p
    v0 = V3(vertices[0])
    for i in range(2, len(vertices)):
        for p in traverse(V3(vertices[i - 1]), V3(vertices[i])):
            for q in traverse(p, v0):
                yield q


def getTriangle(p1, p2, p3):
    """
    Note that this will return many duplicate poitns
    """
    p1, p2, p3 = V3(p1), V3(p2), V3(p3)

    for u in traverse(p2, p3):
        for w in traverse(p1, u):
            yield w


def frac(x):
    return x - math.floor(x)


def traverse2D(a, b):
    """
    equation of line: a + t(b-a), t from 0 to 1
    Based on Amantides and Woo's ray traversal algorithm with some help from
    http://stackoverflow.com/questions/12367071/how-do-i-initialize-the-t-variables-in-a-fast-voxel-traversal-algorithm-for-ray
    """

    inf = float("inf")

    if b[0] == a[0]:
        if b[1] == a[1]:
            yield (int(math.floor(a[0])), int(math.floor(a[1])))
            return
        tMaxX = inf
        tDeltaX = 0
    else:
        tDeltaX = 1. / abs(b[0] - a[0])
        tMaxX = tDeltaX * (1. - frac(a[0]))

    if b[1] == a[1]:
        tMaxY = inf
        tDeltaY = 0
    else:
        tDeltaY = 1. / abs(b[1] - a[1])
        tMaxY = tDeltaY * (1. - frac(a[1]))

    endX = int(math.floor(b[0]))
    endY = int(math.floor(b[1]))
    x = int(math.floor(a[0]))
    y = int(math.floor(a[1]))
    if x <= endX:
        stepX = 1
    else:
        stepX = -1
    if y <= endY:
        stepY = 1
    else:
        stepY = -1

    yield (x, y)
    if x == endX:
        if y == endY:
            return
        tMaxX = inf
    if y == endY:
        tMaxY = inf

    while True:
        if tMaxX < tMaxY:
            x += stepX
            yield (x, y)
            if x == endX:
                tMaxX = inf
            else:
                tMaxX += tDeltaX
        else:
            y += stepY
            yield (x, y)
            if y == endY:
                tMaxY = inf
            else:
                tMaxY += tDeltaY

        if tMaxX == inf and tMaxY == inf:
            return


def traverse(a, b):
    """
    equation of line: a + t(b-a), t from 0 to 1
    Based on Amantides and Woo's ray traversal algorithm with some help from
    http://stackoverflow.com/questions/12367071/how-do-i-initialize-the-t-variables-in-a-fast-voxel-traversal-algorithm-for-ray
    """

    inf = float("inf")

    if b.x == a.x:
        if b.y == a.y and b.z == a.z:
            yield a.ifloor()
            return
        tMaxX = inf
        tDeltaX = 0
    else:
        tDeltaX = 1. / abs(b.x - a.x)
        tMaxX = tDeltaX * (1. - frac(a.x))

    if b.y == a.y:
        tMaxY = inf
        tDeltaY = 0
    else:
        tDeltaY = 1. / abs(b.y - a.y)
        tMaxY = tDeltaY * (1. - frac(a.y))

    if b.z == a.z:
        tMaxZ = inf
        tDeltaZ = 0
    else:
        tDeltaZ = 1. / abs(b.z - a.z)
        tMaxZ = tDeltaZ * (1. - frac(a.z))

    end = b.ifloor()
    x = int(floor(a.x))
    y = int(floor(a.y))
    z = int(floor(a.z))
    if x <= end.x:
        stepX = 1
    else:
        stepX = -1
    if y <= end.y:
        stepY = 1
    else:
        stepY = -1
    if z <= end.z:
        stepZ = 1
    else:
        stepZ = -1

    yield V3(x, y, z)

    if x == end.x:
        if y == end.y and z == end.z:
            return
        tMaxX = inf
    if y == end.y:
        tMaxY = inf
    if z == end.z:
        tMaxZ = inf

    while True:
        if tMaxX < tMaxY:
            if tMaxX < tMaxZ:
                x += stepX
                yield V3(x, y, z)
                if x == end.x:
                    tMaxX = inf
                else:
                    tMaxX += tDeltaX
            else:
                z += stepZ
                yield V3(x, y, z)
                if z == end.z:
                    tMaxZ = inf
                else:
                    tMaxZ += tDeltaZ
        else:
            if tMaxY < tMaxZ:
                y += stepY
                yield V3(x, y, z)
                if y == end.y:
                    tMaxY = inf
                else:
                    tMaxY += tDeltaY
            else:
                z += stepZ
                yield V3(x, y, z)
                if z == end.z:
                    tMaxZ = inf
                else:
                    tMaxZ += tDeltaZ

        if tMaxX == inf and tMaxY == inf and tMaxZ == inf:
            return


def get_line_from_points(p1, p2):
    return getLine(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z)


# Brasenham's algorithm
def getLine(x1, y1, z1, x2, y2, z2):
    line = []
    x1 = int(math.floor(x1))
    y1 = int(math.floor(y1))
    z1 = int(math.floor(z1))
    x2 = int(math.floor(x2))
    y2 = int(math.floor(y2))
    z2 = int(math.floor(z2))
    point = [x1, y1, z1]
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    x_inc = -1 if dx < 0 else 1
    l = abs(dx)
    y_inc = -1 if dy < 0 else 1
    m = abs(dy)
    z_inc = -1 if dz < 0 else 1
    n = abs(dz)
    dx2 = l << 1
    dy2 = m << 1
    dz2 = n << 1

    if l >= m and l >= n:
        err_1 = dy2 - l
        err_2 = dz2 - l
        for i in range(0, l - 1):
            line.append(V3(point[0], point[1], point[2]))
            if err_1 > 0:
                point[1] += y_inc
                err_1 -= dx2
            if err_2 > 0:
                point[2] += z_inc
                err_2 -= dx2
            err_1 += dy2
            err_2 += dz2
            point[0] += x_inc
    elif m >= l and m >= n:
        err_1 = dx2 - m;
        err_2 = dz2 - m;
        for i in range(0, m - 1):
            line.append(V3(point[0], point[1], point[2]))
            if err_1 > 0:
                point[0] += x_inc
                err_1 -= dy2
            if err_2 > 0:
                point[2] += z_inc
                err_2 -= dy2
            err_1 += dx2
            err_2 += dz2
            point[1] += y_inc
    else:
        err_1 = dy2 - n;
        err_2 = dx2 - n;
        for i in range(0, n - 1):
            line.append(V3(point[0], point[1], point[2]))
            if err_1 > 0:
                point[1] += y_inc
                err_1 -= dz2
            if err_2 > 0:
                point[0] += x_inc
                err_2 -= dz2
            err_1 += dy2
            err_2 += dx2
            point[2] += z_inc
    line.append(V3(point[0], point[1], point[2]))
    if point[0] != x2 or point[1] != y2 or point[2] != z2:
        line.append(V3(x2, y2, z2))
    return line

# class Drawing:
#     TO_RADIANS = pi / 180.
#     TO_DEGREES = 180. / pi

#     def __init__(self):
#         self.width = 1
#         self.nib = [(0,0,0)]
#         self.point_array = []

#     def penwidth(self,w):
#         self.width = int(w)
#         if self.width == 0:
#             self.nib = []
#         elif self.width == 1:
#             self.nib = [(0,0,0)]
#         elif self.width == 2:
#             self.nib = []
#             for x in range(-1,1):
#                 for y in range(0,2):
#                     for z in range(-1,1):
#                         self.nib.append((x,y,z))
#         else:
#             self.nib = []
#             r2 = self.width * self.width / 4.
#             for x in range(-self.width//2 - 1,self.width//2 + 1):
#                 for y in range(-self.width//2 - 1, self.width//2 + 1):
#                     for z in range(-self.width//2 -1, self.width//2 + 1):
#                         if x*x + y*y + z*z <= r2:
#                             self.nib.append((x,y,z))

#     def point(self, x, y, z, block, options):
#         for p in self.nib:
#             self.drawPoint(x+p[0],y+p[1],z+p[2],block)

#     def face(self, vertices, block):
#         self.drawPoints(getFace(vertices), block)

#     def line(self, x1,y1,z1, x2,y2,z2, block):
#         self.drawPoints(getLine(x1,y1,z1, x2,y2,z2), block)

#     def drawPoints(self, points, block):
#         if self.width == 1:
#             done = set()
#             for p in points:
#                 if p not in done:
#                     self.mc.setBlock(p, block)
#                     done.add(p)
#         else:
#             done = set()
#             for p in points:
#                 for point in self.nib:
#                     x0 = p[0]+point[0]
#                     y0 = p[1]+point[1]
#                     z0 = p[2]+point[2]
#                     if (x0,y0,z0) not in done:
#                         self.mc.setBlock(x0,y0,z0,block)
#                         done.add((x0,y0,z0))
