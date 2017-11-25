#############################################################################################################
# Helper functions for MineCraft.  Uses mcpi to connect to RaspberryJuice on SpigotMC
##############################################################################################################
import mcpi
from mcpi.minecraft import Minecraft
import mcpi.block as block
import math
import numpy as np
from V3 import V3

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

def my_tile_pos():
    try:
        pos = mc.player.getTilePos()        
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

def create_block(p, blocktype, data=None):
    try:
        if not data:
            mc.setBlock(p.x, p.y, p.z, blocktype)
        else:
            mc.setBlock(p.x, p.y, p.z, blocktype, data)
    except AttributeError:
        print("ERROR: Can't write block - didn't have valid x,y,z:", p, blocktype, "type", type(p))

def create_block_filled_box(p1, p2, blocktype, data=None):
    if not data:
        mc.setBlocks(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, blocktype)
    else:
        mc.setBlocks(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, blocktype, data)

def create_box_centered_on(x,y,z,w,h,l, blocktype, data=None):
    if not data:
        mc.setBlocks(x-w, y, z-l, x+w, y+h, z+l, blocktype)
    else:
        mc.setBlocks(x-w, y, z-l, x+w, y+h, z+l, blocktype, data)

def create_blocks_from_pointlist(points, blocktype, data=None, blocks_to_not_draw=[]):
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


def bulldoze(player_pos = my_tile_pos(), radius=40):
    debug("Bulldozing " + str(radius) + "x around player...")    
    debug(player_pos)
    create_box_centered_on(player_pos.x, player_pos.y, player_pos.z, radius,radius,radius, block.AIR.id)
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

