#############################################################################################################
# Procedural Building creation functions for MineCraft.  Uses mcpi to connect to RaspberryJuice on SpigotMC
# Import via python command line:
#   exec(open("py/buildings.py").read())
# Usage:
#   b = Building()
#   b.build()
# or
#   options = Map({},name="Mansion", height=20, depth=20, width=30)
#   b = Building(mcpi.vec3.Vec3(42,0,42), options)
#   b.build
##############################################################################################################
import mcpi
from mcpi.minecraft import Minecraft
import mcpi.block as block
import numpy as np
import time
import math

mc = Minecraft.create()




#-----------------------
# Polygon helper class to store, build, and create blocks
class BuildingPoly(object):
    def __init__(self, kind, pos1, pos2, options):
        self.kind = kind
        self.pos1 = pos1
        self.pos2 = pos2
        self.direction = options.direction
        self.material = options.material
    
    def create(self):
        mc.setBlocks(self.pos1.x, self.pos1.y, self.pos1.z, self.pos2.x, self.pos2.y, self.pos2.z, self.material)
    
    def clear(self):
        mc.setBlocks(self.pos1.x, self.pos1.y, self.pos1.z, self.pos2.x, self.pos2.y, self.pos2.z, block.AIR.id)
#-----------------------

# Main class for creating a building along with settings
class Building(object):    

    def __init__(self, pos=False, options=False):
        if not options:
            options = Map()

        self.seed = options.seed or get_seed()
        np.random.seed(self.seed)

        #If position isn't set, use the player position
        if pos is False:
            pos = mc.player.getTilePos()
        
        #If "force_height" not passed in as an option, then pick height of the terrain at the x,z point
        if not options.force_height:
            pos.y = mc.getHeight(pos.x, pos.z)

        self.center = pos
        self.x = pos.x
        self.y = pos.y
        self.z = pos.z
        self.biome = options.biome or biome_at(pos)
        self.biome = self.biome.title() #NOTE: Title-cases biome, PLAINS becomes Plains

        self.width = options.width or np.random.randint(8,30)
        self.height = options.height or np.random.randint(6,10)
        self.depth = options.depth or np.random.randint(8,30)
        
        self.material = options.material or block.STONE.id #TODO: Change based on biome, have rand list
        
        self.name = options.name or self.biome + " house"
        self.polys = self.create_polys()


    def build(self):
        for poly in self.polys:
            poly.create()

    def clear(self):
        for poly in self.polys:
            poly.clear()

    def data(self):
        #TODO: Find how to return this as an iterable data object
        d = Map()
        d.center = self.center
        d.biome = self.biome
        d.width = self.width
        d.height = self.height
        d.depth = self.depth
        d.material = self.material
        d.name = self.name
        return d

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
        polys.append(BuildingPoly('roof', c + sw + up, c + ne + up, data_so_far))
        polys.append(BuildingPoly('wall', c + sw + dn, c + se + up, data_so_far.copy(direction="Front")))
        polys.append(BuildingPoly('wall', c + se + dn, c + ne + up, data_so_far.copy(direction="Side")))
        polys.append(BuildingPoly('wall', c + ne + dn, c + nw + up, data_so_far.copy(direction="Back")))
        polys.append(BuildingPoly('wall', c + nw + dn, c + sw + up, data_so_far.copy(direction="Side")))
        polys.append(BuildingPoly('foundation', c + sw + dn, c + ne + dn, data_so_far))
        return polys

# Recreate the building with same settings and latest rendering code
def NewB(building):
    options = building.data()
    newb = Building(options['center'], options)
    building.clear()
    newb.build()
    return newb



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



# TreeDict like version of JavaScript objects
class DotDict(dict):
    def __init__(self, **kwds):
        self.update(kwds)
        self.__dict__ = self



class Map(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]

    def extend (self, **new_keys):
        for key in new_keys:
            self[key] = new_keys[key]
        return self

    def copy (self, **new_keys):
        item = Map({})
        for key in self:
            item[key] = self[key]
        for key in new_keys:
            item[key] = new_keys[key]
        return item
