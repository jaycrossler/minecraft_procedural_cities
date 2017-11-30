#############################################################################################################
# Helper functions for MineCraft.  Uses mcpi to connect to RaspberryJuice on SpigotMC
##############################################################################################################
import mcpi
from mcpi.minecraft import Minecraft
import mcpi.block as block
import math
import numpy as np
from V3 import V3
import VoxelGraphics as vg

# Minecraft connection link
mc = False

#-----------------------
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

def my_pos():
    try:
        pos = mc.player.getPos()
    except mcpi.connection.RequestError:
        pos =  V3(0,0,0)
    return V3(pos.x, pos.y, pos.z)

def my_tile_pos(clamp_to_ground=True):
    try:
        pos = mc.player.getTilePos()
        if clamp_to_ground:
            height = get_height(pos)
            pos.y = height
    except mcpi.connection.RequestError:
        print("CONNECTION ERROR #1 - Can't get Player Tile Pos")
        pos =  V3(0,0,0)
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
    #NOTE: To add this capability mod the RaspberryJuice/RemoteSessions.java code then build with maven:
    #    } else if (c.equals("world.getBiome")) {
    #        Location loc = parseRelativeBlockLocation(args[0], args[1], args[2]);
    #       Biome biome = world.getBiome((int)loc.getX(), (int)loc.getZ());
    #       send(biome);
    #
    # Then to /Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages/mcpi/minecraft.py
    #    def getBiome(self, *args):
    #        return int(self.conn.sendReceive(b"world.getBiome", intFloor(args)))
    try:
        biome = mc.getBiome(pos.x, pos.z)
    except mcpi.connection.RequestError:
        print("CONNECTION ERROR #3 - Can't get Biome data")
        biome = "Plains"
        #TODO: This is still erroring out consistently, explore
    return biome

def move_me_to(p):
    try:
        mc.player.setPos(p)
    except mcpi.connection.RequestError:
        print("CONNECTION ERROR #4 - Can't move player")
    return biome

def read_block(p):
    mc.getBlock(p)

def draw_point_list(points, blocktype, data=None):
    if not data:
        for p in points:
            mc.setBlock(p.x, p.y, p.z, blocktype)
    else:
        for p in points:
            mc.setBlock(p.x, p.y, p.z, blocktype, data)

def create_block(p, blocktype=block.STONE.id, data=None):
    try:
        if not data:
            mc.setBlock(p.x, p.y, p.z, blocktype)
        else:
            mc.setBlock(p.x, p.y, p.z, blocktype, data)
    except AttributeError:
        print("ERROR: Can't write block - didn't have valid x,y,z:", p, blocktype, "type", type(p))

def create_block_filled_box(p1, p2, blocktype=block.STONE.id, data=None):
    if not data:
        mc.setBlocks(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, blocktype)
    else:
        mc.setBlocks(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, blocktype, data)

def create_box_centered_on(x,y,z,w,h,l, blocktype=block.STONE.id, data=None):
    if not data:
        mc.setBlocks(x-w, y, z-l, x+w, y+h, z+l, blocktype)
    else:
        mc.setBlocks(x-w, y, z-l, x+w, y+h, z+l, blocktype, data)

def create_blocks_from_pointlist(points, blocktype=block.STONE.id, data=None, blocks_to_not_draw=[]):
    for point in points:
        draw_block = True
        if (len(blocks_to_not_draw)>0):
            #TODO: This could be more efficient
            try:
                if (blocks_to_not_draw.index(point)>-1):
                    draw_block = False
            except ValueError:
                draw_block = True

        if draw_block:
            create_block(point, blocktype, data)

def choose_one(*argv):
    return argv[np.random.randint(0, len(argv)-1)]

def choice(list):
    return np.random.choice(list)


def bulldoze(player_pos = my_pos(), radius=40, ground=True):
    debug("Bulldozing " + str(radius) + "x around player...")
    debug(player_pos)
    create_box_centered_on(player_pos.x, player_pos.y, player_pos.z, radius,radius,radius, block.AIR.id)
    if ground:
        create_box_centered_on(player_pos.x, player_pos.y-1, player_pos.z, radius,1,radius, block.GRASS.id)
    debug("...Finished bulldozing")

def test_polyhedron():
    import VoxelGraphics as vg

    pos = my_pos()
    points = vg.getFace([(pos.x,pos.y,pos.z),(pos.x+20,pos.y+20,pos.z),(pos.x+20,pos.y+20,pos.z+20),
         (pos.x,pos.y,pos.z+20)])
    draw_point_list(points, block.GLASS.id)

    n = 20
    for t in range(0,n):
        (x1,z1) = (100*math.cos(t*2*pi/n),80*math.sin(t*2*pi/n))
        for p in traverse(V3(pos.x,pos.y-1,pos.z),V3(pos.x+x1,pos.y-1,pos.z+z1)):
            create_block(p, block.OBSIDIAN)

    n = 40
    vertices = []
    for t in range(0,n):
        (x1,z1) = (100*math.cos(t*2*pi/n),80*math.sin(t*2*pi/n))
        vertices.append((pos.x+x1,pos.y,pos.z+z1))
    points = vg.getFace(vertices)
    draw_point_list(points, block.STAINED_GLASS_BLUE)


def xfrange(start, stop, step):
    i = 0
    while start + i * step < stop:
        yield start + i * step
        i += 1

def test_drawing_function(func, min_x_step=3, max_x_step=11, min_z_step=0, max_z_step=1, z_jumps=1, higher=0, thickness=1, filled=False):
    pos = my_tile_pos(False)
    pos = V3(pos.x, pos.y + higher, pos.z)

    all_points=[]
    x_counter = 0
    for x in range (min_x_step,max_x_step):
        x_counter += (2*x) + 3
        for i,z in enumerate(xfrange(min_z_step, max_z_step, z_jumps)):
            points = func(V3(pos.x + x_counter, pos.y, pos.z + (i * (max_x_step*1.8))), x, z, filled=filled, thickness=thickness)
            draw_point_list(points=points, blocktype=block.GLOWSTONE_BLOCK)
            all_points+=points

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

def test_shapes(line=True):
    def draw(func, pos, radius=5, height=8):
        points = func(V3(pos.x, pos.y, pos.z), radius, .7, height=height)

        g = 95
        b_colors = [block.GLOWSTONE_BLOCK,g,g,g,g,g,g,g,g,g,g,g,g]
        colors = [False,0,0,14,14,1,4,5,3,11,2,10,10]

        for elev in range(0,13):
            colored_points = []
            for point in points:
                if point.y == elev:
                    colored_points.append(point)
            draw_point_list(points=colored_points, blocktype=b_colors[elev], data=colors[elev])
        return points

    pos = my_tile_pos()

    buff = 10
    higher = 8

    all_points = []
    if line==True:
        p1 = V3(pos.x+buff, pos.y, pos.z)
        p2 = V3(pos.x+(buff*1.8), pos.y, pos.z-4)
        p3 = V3(pos.x+(buff*3.3), pos.y, pos.z)
        p4 = V3(pos.x+(buff*4.5), pos.y, pos.z)
    else:
        p1 = V3(pos.x+buff, pos.y, pos.z)
        p2 = V3(pos.x-4, pos.y, pos.z+buff)
        p3 = V3(pos.x, pos.y, pos.z-buff)
        p4 = V3(pos.x-buff, pos.y, pos.z)

    all_points.extend(draw(vg.circle, p1))
    all_points.extend(draw(vg.sphere, vg.up(p1,higher-1)))

    all_points.extend(draw(vg.square, p2, radius=8))
    all_points.extend(draw(vg.box, vg.up(p2,higher/2), radius=8))

    all_points.extend(draw(vg.circle, p3))
    all_points.extend(draw(vg.cone, vg.up(p3,higher/2), height=9))

    all_points.extend(draw(vg.circle, p4))
    all_points.extend(draw(vg.cylinder, vg.up(p4,higher/2)))

    class Temp():
        def __init__(self, points):
            self.points = points

        def clear(self):
            for p in self.points:
                create_block(p, block.AIR.id)
    return Temp(all_points)


mid1, mid2 = V3(0, 0, 60), V3(50, 0, 110)
mid_point = V3(30,0,120)

def home():
    mc.player.setPos(mid_point)

def prep(size=0, ground=True):
    if size > 0:
        corner1 = V3(mid_point.x-size, mid_point.y, mid_point.z-size)
        corner2 = V3(mid_point.x+size, mid_point.y, mid_point.z+size)
    else:
        corner1, corner2 = V3(-60, 0, 40), V3(120, 0, 200)

    debug("Bulldozing building zone...")
    if ground: create_block_filled_box(vg.up(corner1,-1), vg.up(corner2,-3), block.GRASS.id, data=None)
    create_block_filled_box(vg.up(corner1,0), vg.up(corner2,70), block.AIR.id, data=None)
    debug("...Finished bulldozing")

def clear(size=0):
    if size > 0:
        corner1 = V3(mid_point.x-size, mid_point.y, mid_point.z-size)
        corner2 = V3(mid_point.x+size, mid_point.y, mid_point.z+size)
    else:
        corner1, corner2 = V3(-60, 0, 40), V3(120, 0, 200)

    debug("Removing Everything...(fly in 10 seconds)")
    create_block_filled_box(vg.up(corner1,-5), vg.up(corner2,50), block.AIR.id, data=None)

    debug("...Adding Grass...")
    create_block_filled_box(vg.up(corner1,-1), vg.up(corner2,-1), block.GRASS.id, data=None)

    debug("...Stone underneath...")
    create_block_filled_box(vg.up(corner1,-2), vg.up(corner2,-5), block.STONE.id, data=None)
    debug("...Finished")
