#############################################################################################################
# Helper functions for MineCraft.  Uses mcpi to connect to RaspberryJuice on SpigotMC
##############################################################################################################
import mcpi
from mcpi.minecraft import Minecraft
import mcpi.block as block
import math
import time
from libraries import webcolors
import re
import numpy as np
from Map import Map
from V3 import V3
import VoxelGraphics as vg
import Blocks
import Texture1D

# MineCraft connection link
mc = False
BLOCK_DRAW_INCREMENTER = 0


def connect():
    try:
        mc = mcpi.minecraft.Minecraft.create()
        return mc
    except ConnectionRefusedError:
        print("CONNECTION ERROR #6 - Can't connect to server")
        return False


mc = connect()


def debug(msg):
    mc.postToChat(str(msg))


def my_pos(trunc=True):
    try:
        pos = mc.player.getPos()
    except mcpi.connection.RequestError:
        pos = V3(0, 0, 0)
    if trunc:
        return V3(math.floor(pos.x), math.floor(pos.y), math.floor(pos.z))
    else:
        return V3(pos.x, pos.y, pos.z)


def my_dir():
    try:
        d = mc.player.getDirection()
    except mcpi.connection.RequestError:
        d = V3(0, 0, 0)
    return V3(d.x, d.y, d.z)


def my_rot():
    try:
        d = mc.player.getRotation()
    except mcpi.connection.RequestError:
        d = 0

    out = ""
    if d > 315 or d < 45:
        out = "s"
    elif d < 135:
        out = "e"
    elif d < 225:
        out = "n"
    elif d < 315:
        out = "w"

    return out


def my_tile_pos(clamp_to_ground=True):
    try:
        pos = mc.player.getTilePos()
        if clamp_to_ground:
            height = get_height(pos)
            pos.y = height
    except mcpi.connection.RequestError:
        print("CONNECTION ERROR #1 - Can't get Player Tile Pos")
        pos = V3(0, 0, 0)
    return V3(pos.x, pos.y, pos.z)


def get_height(pos):
    out = 0
    try:
        # pos.y = mc.getHeight(pos.x, pos.z)
        out = mc.getHeight(pos.x, pos.z)
    except mcpi.connection.RequestError:
        print("CONNECTION ERROR #2 - Can't get Height at tile")
    return out


def biome_at(pos):
    """

    NOTE: To add this capability mod the RaspberryJuice/RemoteSessions.java code then build with maven:

       } else if (c.equals("world.getBiome")) {
           Location loc = parseRelativeBlockLocation(args[0], args[1], args[2]);
          Biome biome = world.getBiome((int)loc.getX(), (int)loc.getZ());
          send(biome);

    Then to /Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages/mcpi/minecraft.py
       def getBiome(self, *args):
           return int(self.conn.sendReceive(b"world.getBiome", intFloor(args)))
   """
    try:
        biome = mc.player.getBiome(pos.x, pos.z)
    except mcpi.connection.RequestError:
        print("CONNECTION ERROR #3 - Can't get Biome data")
        biome = "Plains"
        # TODO: This is still erroring out consistently, explore
    return biome


def move_me_to(p):
    try:
        mc.player.setPos(p)
    except mcpi.connection.RequestError:
        print("CONNECTION ERROR #4 - Can't move player")


def read_block(p):
    mc.getBlock(p)


# TODO: Make this a MShape Class with all the stuff from BuildingPoly
def draw_point_list(points, material, data=None, options=Map()):
    # Remove empty blocks from list
    if options.blocks_to_not_draw:
        points = [i for i in points if i not in options.blocks_to_not_draw]

    # Find material if texture
    if type(material) == Texture1D.Texture1D:
        if material.options.gradient:
            bounds = vg.bounds(points)
            # Find low then high, calc difference, get color at dist, draw all at that height
            if material.axis == "y":
                bounds_lowest = bounds.lowest
                bounds_highest = bounds.highest
            elif material.axis == "x":
                bounds_lowest = bounds.x_low
                bounds_highest = bounds.x_high
            else:
                # if material.axis == "z":
                bounds_lowest = bounds.z_low
                bounds_highest = bounds.z_high

            # for each step along axis, draw the right color at that slice
            steps = bounds_highest - bounds_lowest + 1
            for slice_step in range(bounds_lowest, bounds_highest + 1):
                colored_points = []
                for point in points:
                    if (material.axis == "x" and point.x == slice_step) or \
                            (material.axis == "y" and point.y == slice_step) or \
                            (material.axis == "z" and point.z == slice_step):
                        colored_points.append(point)

                step = slice_step - bounds_lowest
                block_at_slice = material.block(Map(step=step, steps=steps))
                if options.info:
                    print("Material used:", step, steps, block_at_slice)

                draw_point_list(points=colored_points, material=block_at_slice["id"], data=block_at_slice["data"])
            return points

        else:
            # Texture but not gradient
            material = material.material

    # Regular material

    # Update the incrementer
    global BLOCK_DRAW_INCREMENTER
    BLOCK_DRAW_INCREMENTER = 0

    # Now that we know the block info from all options, Draw the Points
    for p in points:
        material_now, data_now = find_block_info(material, data=data, options=options)
        try:
            if not data_now:
                mc.setBlock(p.x, p.y, p.z, material_now)
            else:
                mc.setBlock(p.x, p.y, p.z, material_now, data_now)
        except TypeError:
            print("Error crating block", material_now)


# TODO: Move this into a Texture1D option
def find_block_info(material, data=None, options=Map()):
    if type(material) == list:
        global BLOCK_DRAW_INCREMENTER
        if options.choice_type == "rotate":
            block_id = BLOCK_DRAW_INCREMENTER % (len(material))
            material = material[block_id]
            BLOCK_DRAW_INCREMENTER += 1
        elif options.choice_type == "rebound":
            group = math.ceil(BLOCK_DRAW_INCREMENTER / (len(material)))
            block_id = BLOCK_DRAW_INCREMENTER % (len(material))
            if group % 2 == 0:
                block_id = len(material) - 1 - block_id
            material = material[block_id]
            BLOCK_DRAW_INCREMENTER += 1
        else:  # Random
            material = np.random.choice(material)

    elif type(material) == Texture1D:
        block_obj = material.block()
        data = block_obj["data"]
        material = block_obj["id"]

    elif type(material) == Map and "id" in material:
        data = material["data"] if "data" in material else None
        material = material["id"]

    elif type(material) == tuple:
        if len(material) == 2:
            data = material[1]
            material = material[0]
        elif len(material) == 3:
            block_color = Blocks.closest_by_color(material)
            data = block_color["data"]
            material = block_color["id"]

    if type(material) == dict:
        block_id = material["id"]
        data = material["data"] or data or None
        material = block_id

    if type(material) == tuple and len(material) == 2:
        material, data = material

    if material is None:
        print("ERROR - material is None")
    elif type(material) == Map:
        print("ERROR - Map material passed in:", material)
    elif type(material) == block.Block:
        material = material.id
    else:
        try:
            material = int(material)
        except:
            print("ERROR CONVERTING MATERIAL", type(material))

    if type(data) == Map:
        print("ERROR - Map material Data passed in:", data)
    elif data is None:
        # do nothing
        pass

    if data is not None:
        data = int(data)
    return material, data


def create_block(p, material=block.STONE.id, data=None, options=Map(choice_type="random")):
    try:
        material, data = find_block_info(material, data=data, options=options)

        if not data:
            if material is None:
                raise TypeError("No material passed in")
            else:
                mc.setBlock(p.x, p.y, p.z, material)
        else:
            mc.setBlock(p.x, p.y, p.z, material, data)
    except AttributeError:
        print("ERROR: Can't write block - didn't have valid x,y,z:", p, material, "type", type(p))


def create_block_filled_box(p1, p2, material=block.STONE.id, data=None, options=Map()):
    try:
        material, data = find_block_info(material, data=data, options=options)

        if not data:
            mc.setBlocks(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, material)
        else:
            mc.setBlocks(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, material, data)
    except AttributeError:
        print("ERROR: Can't write blocks - didn't have valid x,y,z:", p1, material, "type", type(p1))


def create_box_centered_on(x, y, z, w, h, l, material=block.STONE.id, data=None):
    if not data:
        mc.setBlocks(x - w, y, z - l, x + w, y + h, z + l, material)
    else:
        mc.setBlocks(x - w, y, z - l, x + w, y + h, z + l, material, data)


def corners_from_bounds(p1, p2, sides, center, radius, width, depth):
    corner_vectors = []
    lines = []
    for i in range(0, sides):
        v1 = vg.point_along_circle(center, radius, sides, i, Map(align_to_cells=True, width=width, depth=depth, p1=p1, p2=p2))
        v2 = vg.point_along_circle(center, radius, sides, i+1, Map(align_to_cells=True, width=width, depth=depth, p1=p1, p2=p2))
        corner_vectors.append(v1)
        lines.append((v1, v2))

    return corner_vectors, lines


def list_remove_dupes(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def flatten_list_of_lists(input):
    flat = [y for x in input for y in x]
    return list_remove_dupes(flat)


def choose_one(*argv):
    return argv[np.random.randint(0, len(argv) - 1)]


def choice(items):
    return np.random.choice(items)


def pos_in_front(dist=1):
    pos = my_pos()
    d = my_dir()
    x = round(pos.x + (d.x * dist))
    y = round(pos.y + (d.y * dist))
    z = round(pos.z + (d.z * dist))
    return V3(x, y, z)


def scan(show_location=False):
    direction = my_rot()
    target = vg.up(my_pos())

    # print("Facing:", direction)
    if direction == 'w':
        x_range = [1]
        z_range = [-2, -1, 0, 1, 2]
    elif direction == 'e':
        x_range = [-1]
        z_range = [2, 1, 0, -1, -2]
    elif direction == 's':
        x_range = [-3, -2, -1, 0, 1]
        z_range = [0]
    else:
        # n
        x_range = [-2, -1, 0, 1, 2]
        z_range = [-2]

    blocks = []
    for y in [2, 1, 0, -1, -2]:
        text = ""
        for x in x_range:
            for z in z_range:
                new_point = target + V3(x, y, z)
                b = mc.getBlockWithData(new_point.x, new_point.y, new_point.z)

                name = Blocks.name_by_id(b.id, b.data)
                loc = str(new_point.x) + "," + str(new_point.y) + "," + str(
                    new_point.z) + " : " if show_location else ""
                line = "(" + loc + str(b.id) + "," + str(b.data) + ": " + name + ")  "

                text += line.ljust(28)
                blocks.append(b)
        print(text)
    # return blocks


def bulldoze(player_pos=my_pos(), radius=40, ground=True):
    debug("Bulldozing " + str(radius) + "x around player...")
    debug(player_pos)
    print(player_pos)
    create_box_centered_on(player_pos.x, player_pos.y, player_pos.z, radius, radius, radius, block.AIR.id)
    if ground:
        create_box_centered_on(player_pos.x, player_pos.y - 1, player_pos.z, radius, 1, radius, block.GRASS.id)
    debug("...Finished bulldozing")


def spheredoze(player_pos=my_tile_pos(False), radius=40, ground=True):
    debug("Bulldozing " + str(radius) + "x around player...")
    debug(player_pos)

    all_points = vg.sphere(center=player_pos, radius=radius)
    draw_point_list(points=all_points, material=block.AIR.id)

    debug("...Finished bulldozing")


def test_polyhedron():
    # TODO: Revamp this
    import VoxelGraphics as vg

    pos = my_pos()
    points = vg.getFace([(pos.x, pos.y, pos.z), (pos.x + 20, pos.y + 20, pos.z), (pos.x + 20, pos.y + 20, pos.z + 20),
                         (pos.x, pos.y, pos.z + 20)])
    draw_point_list(points, block.GLASS.id)

    n = 20
    for t in range(0, n):
        (x1, z1) = (100 * math.cos(t * 2 * math.pi / n), 80 * math.sin(t * 2 * math.pi / n))
        for p in vg.traverse(V3(pos.x, pos.y - 1, pos.z), V3(pos.x + x1, pos.y - 1, pos.z + z1)):
            create_block(p, block.OBSIDIAN)

    n = 40
    vertices = []
    for t in range(0, n):
        (x1, z1) = (100 * math.cos(t * 2 * math.pi / n), 80 * math.sin(t * 2 * math.pi / n))
        vertices.append((pos.x + x1, pos.y, pos.z + z1))
    points = vg.getFace(vertices)
    draw_point_list(points, block.STAINED_GLASS_BLUE)


def xfrange(start, stop, step):
    i = 0
    while start + i * step < stop:
        yield start + i * step
        i += 1


def test_drawing_function(func, min_x_step=3, max_x_step=11, min_z_step=0, max_z_step=1, z_jumps=1, higher=0,
                          thickness=1, filled=False, material=block.GLOWSTONE_BLOCK, render="rotate"):
    home()
    pos = my_tile_pos()
    pos = V3(pos.x, pos.y + higher, pos.z)

    all_points = []
    x_counter = 0
    for x in range(min_x_step, max_x_step):
        x_counter += (2 * x) + 3
        for i, z in enumerate(xfrange(min_z_step, max_z_step, z_jumps)):
            points = func(V3(pos.x + x_counter, pos.y, pos.z + (i * (max_x_step * 1.8))), x, z, filled=filled,
                          thickness=thickness)
            draw_point_list(points=points, material=material, options=Map(choice_type=render))
            all_points += points

    class Temp():
        def __init__(self, points):
            self.points = points

        def clear(self):
            for p in self.points:
                create_block(p, block.AIR.id)

    return Temp(all_points)


def test_circles(thickness=1):
    return test_drawing_function(vg.circle, 1, 7, 0, 0.8, 0.1, thickness=thickness)


def test_box(thickness=1):
    return test_drawing_function(vg.box, 1, 7, thickness=thickness)


def test_sphere(thickness=1):
    return test_drawing_function(vg.sphere, 1, 8, 0, 0.8, 0.1, higher=8, thickness=thickness)


def test_cylinder(thickness=1):
    return test_drawing_function(vg.cylinder, 1, 7, 0, 0.8, 0.1, thickness=thickness)


def test_cone(thickness=1):
    return test_drawing_function(vg.cone, 1, 7, 0, 0.8, 0.1, thickness=thickness)


def test_pyramid(thickness=1):
    return test_drawing_function(vg.rectangular_pyramid, 1, 7, 0, 0.8, 0.1, thickness=thickness)


def test_shapes(line=True, buff=13, texture_base=89, texture_main="Glass", info=False):
    texture = Texture1D.Texture1D(Map(gradient=True, gradient_type="linear", onlyBlock=True, name_contains=texture_main,
                                      colors=Texture1D.COLOR_MAPS.Rainbow.colors, axis="y"))

    def draw(func, position, radius=5, height=8, material=texture_base, info=False):
        points = func(V3(position.x, position.y, position.z), radius, .7, height=height)
        draw_point_list(points, material, options=Map(info=info))
        return points

    pos = my_tile_pos()

    higher = 8

    all_points = []
    if line is True:
        p1 = V3(pos.x + buff, pos.y, pos.z)
        p2 = V3(pos.x + (buff * 1.8), pos.y, pos.z)
        p3 = V3(pos.x + (buff * 3.3), pos.y, pos.z)
        p4 = V3(pos.x + (buff * 4.5), pos.y, pos.z)
        p5 = V3(pos.x + (buff * 5.7), pos.y, pos.z)
    else:
        p1 = V3(pos.x + buff, pos.y, pos.z)
        p2 = V3(pos.x, pos.y, pos.z)
        p3 = V3(pos.x, pos.y, pos.z - buff)
        p4 = V3(pos.x - buff, pos.y, pos.z)
        p5 = V3(pos.x, pos.y, pos.z + buff)

    all_points.extend(draw(vg.circle, p1, material=texture_base, info=info))
    all_points.extend(draw(vg.sphere, vg.up(p1, higher), radius=5, material=texture, info=info))

    all_points.extend(draw(vg.square, p2, material=texture_base, info=info))
    all_points.extend(draw(vg.box, vg.up(p2, higher), radius=4, material=texture, info=info))

    all_points.extend(draw(vg.circle, p3, material=texture_base, info=info))
    all_points.extend(draw(vg.cone, vg.up(p3, higher / 2), height=9, material=texture, info=info))

    all_points.extend(draw(vg.circle, p4, material=texture_base, info=info))
    all_points.extend(draw(vg.cylinder, vg.up(p4, higher / 2), material=texture, info=info))

    all_points.extend(draw(vg.square, p5, material=texture_base, info=info))
    all_points.extend(draw(vg.rectangular_pyramid, vg.up(p5, higher / 2), height=8, material=texture, info=info))

    class Temp:
        def __init__(self, points):
            self.points = points

        def clear(self):
            for p in self.points:
                create_block(p, block.AIR.id)

    return Temp(all_points)


mid1, mid2 = V3(0, 0, 60), V3(50, 0, 110)
mid_point = V3(30, 0, 120)


def home():
    mc.player.setPos(mid_point)


def prep(size=0, ground=True):
    if size > 0:
        corner1 = V3(mid_point.x - size, mid_point.y, mid_point.z - size)
        corner2 = V3(mid_point.x + size, mid_point.y, mid_point.z + size)
    else:
        corner1, corner2 = V3(-60, 0, 40), V3(120, 0, 200)

    debug("Bulldozing building zone...")
    if ground: create_block_filled_box(vg.up(corner1, -1), vg.up(corner2, -3), block.GRASS.id, data=None)
    create_block_filled_box(vg.up(corner1, 0), vg.up(corner2, 70), block.AIR.id, data=None)
    debug("...Finished bulldozing")


def go_tower():
    move_me_to(V3(-786, 1, 263))


def clear(size=0):
    if size > 0:
        corner1 = V3(mid_point.x - size, mid_point.y, mid_point.z - size)
        corner2 = V3(mid_point.x + size, mid_point.y, mid_point.z + size)
    else:
        corner1, corner2 = V3(-60, 0, 40), V3(120, 0, 200)

    debug("Removing Everything...(fly in 10 seconds)")
    create_block_filled_box(vg.up(corner1, -5), vg.up(corner2, 50), block.AIR.id, data=None)

    debug("...Adding Grass...")
    create_block_filled_box(vg.up(corner1, -1), vg.up(corner2, -1), block.GRASS.id, data=None)

    debug("...Stone underneath...")
    create_block_filled_box(vg.up(corner1, -2), vg.up(corner2, -5), block.STONE.id, data=None)
    debug("...Finished")


if __name__ == "__main__":
    # test_shapes()

    tb = Texture1D.Texture1D(
        Map(gradient=True, only_blocks=True, gradient_type="linear", colors=["red", "blue"], gradient_axis="x"))
    t = test_shapes(texture_base=tb)

    time.sleep(10)
    t.clear()
