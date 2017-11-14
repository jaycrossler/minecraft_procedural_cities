#############################################################################################################
# Procedural Building creation functions for MineCraft.  Uses mcpi to connect to RaspberryJuice on SpigotMC
# Import via python command line:
#   exec(open("py/buildings.py").read())
# Usage:
#   b = Building()
# or
#   b = Building(mcpi.vec3.Vec3(42,0,42), name="Mansion", height=20, depth=20, width=30, biome="Plains")
##############################################################################################################
import mcpi
from mcpi.minecraft import Minecraft
import mcpi.block as block
import numpy as np
import time
import math

mc = Minecraft.create()


# TreeDict like version of JavaScript objects
class DotDict(dict):
    def __init__(self, **kwds):
        self.update(kwds)
        self.__dict__ = self


# Polygon helper class to store, build, and create blocks
class BuildingPoly(object):
    def __init__(self, kind, pos1, pos2, **options):
        self.kind = kind
        self.pos1 = pos1
        self.pos2 = pos2
        self.material = options.material

    def create(self):
        mc.setBlocks(self.pos1.x, self.pos1.y, self.pos1.z, self.pos2.x, self.pos2.y, self.pos2.z, self.material)

    def clear(self):
        mc.setBlocks(self.pos1.x, self.pos1.y, self.pos1.z, self.pos2.x, self.pos2.y, self.pos2.z, block.AIR.id)

# Main class for creating a building along with settings
class Building(object):
    def __init__(self, pos=False, **options):
        self.seed = opts(options,'seed', get_seed())
        np.random.seed(self.seed)

        #If position isn't set, use the player position
        if pos is False:
            pos = mc.player.GetTilePos()
        
        #If "force_height" not passed in as an option, then pick height of the terrain at the x,z point
        if "force_height" not in options:
            pos.y = mc.getHeight(pos.x, pos.z)

        self.center = pos
        self.x = pos.x
        self.y = pos.y
        self.z = pos.z
        self.biome = opts(options,'biome', biome_at(pos)).title() #NOTE: Title-cases resume, PLAINS becomes Plains

        self.width = opts(options,'width', np.random.randint(8,30))
        self.height = opts(options,'height', np.random.randint(6,10))
        self.depth = opts(options,'depth', np.random.randint(8,30))
        
        self.material = block.STONE.id #TODO: Change based on biome, have rand list
        
        self.name = opts(options,'name', self.biome + " house")
        self.polys = create_polys(self)


    def build(self):
        for poly in self.polys:
            poly.create()

    def clear(self):
        for poly in self.polys:
            poly.clear()

    def data(self):
        #TODO: Find how to return this as an iterable data object
        d = {}
        d['center'] = self['center']
        d['biome'] = self['biome']
        d['width'] = self['width']
        d['height'] = self['height']
        d['depth'] = self['depth']
        d['material'] = self['material']
        d['name'] = self['name']
        return d



# Recreate the building with same settings and latest rendering code
def NewB(building):
    options = building.data()
    newb = Building(options['center'], *options)
    building.clear()
    newb.build()
    return newb

#TODO: Move these into a namespace
def create_polys(building):
    #NOTE: Currently, only creates a box
    
    sw = mcpi.vec3.Vec3(-math.floor(building.width/2), 0, -math.floor(building.depth/2))
    se = mcpi.vec3.Vec3(-math.floor(building.width/2), 0, math.floor(building.depth/2))
    ne = mcpi.vec3.Vec3(math.ceil(building.width/2), 0, math.ceil(building.depth/2))
    nw = mcpi.vec3.Vec3(math.ceil(building.width/2), 0, -math.ceil(building.depth/2))
    up = mcpi.vec3.Vec3(0, building.height, 0)
    dn = mcpi.vec3.Vec3(0, -1, 0)
    c = building.center

    polys = []
    data_so_far = building.data()
    polys.append(BuildingPoly('roof', c + sw + up, c + ne + up, *data_so_far))
    polys.append(BuildingPoly('wall', c + sw + dn, c + se + up, *data_so_far))
    polys.append(BuildingPoly('wall', c + se + dn, c + ne + up, *data_so_far))
    polys.append(BuildingPoly('wall', c + ne + dn, c + nw + up, *data_so_far))
    polys.append(BuildingPoly('wall', c + nw + dn, c + sw + up, *data_so_far))
    polys.append(BuildingPoly('foundation', c + sw + dn, c + ne + dn, *data_so_far))
    return polys


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
        biome = "Plains"
    return biome

def get_seed():
    # TODO: Return the world seed, add in x,y,z
    return np.random.randint(65000)

# Helper function to look up options in dict
def opts(options, v_name, def_val=False):
    if v_name in options:
        return options[v_name]
    else:
        return def_val
