#############################################################################################################
# Procedural Building creation functions for MineCraft.  Uses mcpi to connect to RaspberryJuice on SpigotMC
# Import via python command line:
#   exec(open("Building.py").read())
# Usage:
#   b = Building()
#   b.build()
# or
#   options = Map(name="Mansion", height=20, radius=5, sides=6)
#   b = Building(V3(42,0,42), options)
#   b.build()
#
#   TODO: Pointy roof drawing weird on one axis
#   TODO: Have floors with each allowing different polylgon/size settings
#   TODO: Stairs or ladders between floors
#   TODO: Building cost to create building
#   TODO: Largest neighborhood building is castle or tower
#   TODO: Add a river running through town
#   TODO: Buildings and roads along terrain
#
# Test Buildings:
#   b = Building(False, Map(sides=4, height=7, radius=6, windows="window_line_double", roof="pointy"))
#   b = Building(False, Map(sides=6, height=5, radius=8, windows="window_line", roof="pointy_lines", material=block.WOOL.id, material_edges=block.GOLD_BLOCK.id))
##############################################################################################################
import mcpi
import mcpi.block as block
import math
import MinecraftHelpers as helpers
import VoxelGraphics as vg
import BuildingStyler as bs
import BuildingPoly as bp
import Castle as castle
from Map import Map
from V3 import V3

helpers.connect()

#Testing location numbers
mid1, mid2 = V3(0, 0, 60), V3(50, 0, 110)
mid_point = V3(30,0,120)

#-----------------------
# Polygon helper class to store, build, and create blocks
class Farmzone(object):
    def __init__(self, p1, p2, options=Map()):
        self.crop = options.crop or np.random.choice(["cane","wheat","carrot","potato"])
        self.blocks = []

        rim, inner_rec = rectangle(p1, p2)
        for block in rim+inner_rec:
            if not block in self.blocks and type(block) == V3:
                self.blocks.append(block)

        self.center = V3(round(abs(p2.x-p1.x)), p1.y, round(abs(p2.z-p1.z)))

    def build(self):
        for i, vec in enumerate(self.blocks):
            if vec == self.center:
                helpers.create_block(p1,block.WATER.id) #TODO: Add rows of water
                plus2 = vg.up(vec,3)
                helpers.create_block(plus2,block.GLASS.id)
                for v2 in vg.next_to(plus2):
                    helpers.create_block(v2,block.TORCH.id)
            else:
                helpers.create_block(vec,block.FARMLAND.id)

        if self.crop == "cane":
            for i, p1 in enumerate(self.blocks):
                if not vec == self.center:
                    helpers.create_block(vg.up(p1),block.SUGAR_CANE.id)
                    helpers.create_block(vg.up(p1,2),block.SUGAR_CANE.id)
        elif self.crop == "wheat":
            for i, p1 in enumerate(self.blocks):
                if not vec == self.center:
                    helpers.create_block(vg.up(p1),59,0x7)
        elif self.crop == "carrot":
            for i, p1 in enumerate(self.blocks):
                if not vec == self.center:
                    helpers.create_block(vg.up(p1),141,0x7)
        elif self.crop == "potato":
            for i, p1 in enumerate(self.blocks):
                if not vec == self.center:
                    helpers.create_block(vg.up(p1),142,0x7)

    def clear(self):
        for i, vec in enumerate(self.blocks):
            if vec == self.center:
                helpers.create_block(vec,block.GRASS.id)
                plus2 = vg.up(vec,3)
                for v2 in vg.next_to(plus2):
                    helpers.create_block(v2,block.AIR.id)
                helpers.create_block(plus2,block.AIR.id)
            else:
                helpers.create_block(vec,block.FARMLAND.id)

        if self.crop == "cane":
            for p1 in self.blocks:
                helpers.create_block(vg.up(p1),block.AIR.id)
                helpers.create_block(vg.up(p1,2),block.AIR.id)
        elif self.crop in ["wheat","carrot","potato"]:
            for i, p1 in enumerate(self.blocks):
                if not vec == self.center:
                    helpers.create_block(vg.up(p1),block.AIR.id)

#-----------------------
# Polygon helper class to store, build, and create blocks
class Farmzones(object):
    def __init__(self, zones, options=Map()):
        min_size = options.min_size or 0
        max_size = options.max_size or 9
        self.farms = []

        for part in zones:
            valid = (min_size <= part.width <= max_size) or (min_size <= part.depth <= max_size)
            if valid:
                p1, p2 = vg.rectangle_inner(part.p1, part.p2, 1)
                self.farms.append(Farmzone(p1, p2))

    def build(self):
        for farm in self.farms:
            farm.build()

    def clear(self):
        for farm in self.farms:
            farm.clear()

#-----------------------
# Polygon helper class to store, build, and create blocks
class Neighborhoods(object):
    def __init__(self, zones, options=Map()):
        min_size = options.min_size or 9
        self.style = options.style
        self.buildings = []
        self.zones = []

        for part in zones:
            if (min_size <= part.width) and (min_size <= part.depth):
                self.zones.append(part)
                p1 = vg.up(part.p1,1)
                p2 = vg.up(part.p2,1)
                p1, p2 = rectangle_inner(p1, p2,2)
                self.buildings.append(Building(False, Map(p1=p1, p2=p2)))

    def build(self):
        for b in self.buildings:
            b.build()

    def clear(self):
        for b in self.buildings:
            b.clear()

#-----------------------
# Polygon helper class to store, build, and create blocks
class Streets(object):
    def __init__(self, p1, p2, options=Map()):
        self.p1 = vg.up(p1,-1)
        self.p2 = vg.up(p2,-1)
        self.minx = options.minx or 7
        self.minz = options.minz or 7
        self.style = options.style or "blacktop"

        self.options = options

        if options.layout == "castle":
            self.zones = castle.build_castle_streetmap(self.p1, self.p2, options)
        else:
            #TODO: Set width 1 or 2
            self.zones = vg.partition(self.p1, self.p2, self.minx, self.minz)

        self.blocks, x = vg.partitions_to_blocks(self.zones, options)

    def build(self,min_size=0):
        if self.style == "blacktop":
            color = block.OBSIDIAN.id
        else:
            color = block.DIRT.id

        for pos in self.blocks:
            helpers.create_block(pos, color)

    def clear(self):
        for pos in self.blocks:
            helpers.create_block(pos, block.GRASS.id)


#-----------------------
# Main class for creating a building along with settings
class Building(object):
    def __init__(self, pos=False, options=Map()):
        if not helpers.mc:
            helpers.mc = helpers.connect()

        self.seed = options.seed or vg.get_seed()
        vg.init_with_seed(self.seed)
        self.sides = options.sides or 4

        if options.p1 and options.p2:
            p1, p2 = vg.min_max_points(options.p1, options.p2)
            options.width = abs(p2.x - p1.x) - 2
            options.depth = abs(p2.z - p1.z) - 2
            options.radius = math.floor(min(options.width, options.depth)/2)
            pos = V3(round((p1.x+p2.x)/2) , p1.y, round((p1.z+p2.z)/2))
            if options.sides == 4:
                options.p1 = p1
                options.p2 = p2
        else:
            #If position isn't set, use the player position
            if pos is False:
                pos = helpers.my_tile_pos()

        #If "force_height" not passed in as an option, then pick height of the terrain at the x,z point
        # if not options.force_height:
        #     setattr(pos, "y", helpers.get_height(pos))

        self.options = options
        self.radius = options.radius or vg.rand_in_range(4,10)
        self.options = bs.random_options(self.options)
        self.center = V3(pos.x, pos.y, pos.z)

        self.biome = "Plains" #TODO: self.biome.title(options.biome or helpers.biome_at(pos))

        rand_max = min(max(math.ceil(self.radius*2.5), 6),40) #keep buildings between 4-40 height
        self.height = options.height or vg.rand_in_range(4,rand_max)
        self.corner_vectors = []

        self.material = options.material or block.STONE.id
        self.material_edges = options.material_edges or block.IRON_BLOCK.id #TODO: Change based on biome, have rand list

        self.name = options.name or self.biome + " house"

        #Style the polygon based on kind and options
        self = bs.building_styler(self, options)

        #Create the walls and major polygons
        self.polys = self.create_polys(options)

    def build(self):
        for poly in self.polys:
            poly.draw()

        for poly in self.polys:
            poly.draw_edges()

        for poly in self.polys:
            poly.draw_features()

    def clear(self):
        for poly in self.polys:
            poly.clear()

    def data(self):
        #TODO: Find how to return this as an iterable data object
        d = Map()
        d.center = self.center
        d.biome = self.biome
        d.height = self.height
        d.radius = self.radius
        d.sides = self.sides
        d.material = self.material
        d.material_edges = self.material_edges
        d.name = self.name
        d.options = self.options
        return d

    def info(self, show=True):
        stro = ["Building with " + str(self.sides) + " sides and height " + str(self.height)]
        for p in self.polys:
            stro += p.info()

        if show:
            for s in stro:
                print (s)
        else:
            return stro

    def create_polys(self, options=Map()):
        polys = []
        data_so_far = self.data()

        sides = data_so_far.sides or 4

        corner_vectors = []
        for i in range(0, sides):
            p1 = vg.point_along_circle(self.center, self.radius, sides, i, Map(align_to_cells=True, width=options.width, depth=options.depth, p1=options.p1, p2=options.p2))
            p2 = vg.point_along_circle(self.center, self.radius, sides, i+1, Map(align_to_cells=True, width=options.width, depth=options.depth, p1=options.p1, p2=options.p2))
            corner_vectors.append(p1)

            facing = "front" if i == 1 else "side"
            #TODO: Pass in point where front door is, determine facing from that
            p = bp.BuildingPoly('wall', [p1, p2], data_so_far.copy(height=self.height, facing=facing))
            polys.append(p)

        roof_vectors = [vg.up(v,self.height) for v in corner_vectors]
        polys.append(bp.BuildingPoly("roof", roof_vectors, data_so_far.copy(corner_vectors = roof_vectors)))
        #insert foundation so that it is drawn first:
        polys.insert(0,bp.BuildingPoly("foundation", [vg.up(v,-1) for v in corner_vectors], data_so_far.copy(corner_vectors = corner_vectors)))

        self.corner_vectors = corner_vectors

        return polys

#--------------------------------------------------------------------
# Testing functions
#
def prep(size=0):
    if size > 0:
        corner1 = V3(mid_point.x-size, mid_point.y, mid_point.z-size)
        corner2 = V3(mid_point.x+size, mid_point.y, mid_point.z+size)
    else:
        corner1, corner2 = V3(-60, 0, 40), V3(120, 0, 200)

    helpers.debug("Bulldozing building zone...")
    helpers.create_block_filled_box(vg.up(corner1,-1), vg.up(corner2,-3), block.GRASS.id, data=None)
    helpers.create_block_filled_box(vg.up(corner1,0), vg.up(corner2,40), block.AIR.id, data=None)
    helpers.debug("...Finished bulldozing")

def t1():
    return Building(False, Map(sides=4, height=7, radius=6, windows="window_line_double", roof="pointy"))

def t2():
    return Building(False, Map(sides=6, height=5, radius=8, windows="window_line", roof="pointy_lines", material=block.WOOL.id, material_edges=block.GOLD_BLOCK.id))

def t3():
    return Building(False, Map(sides=4, height=20, radius=6, windows="window_slits", roof="battlement", material=block.STONE_BRICK.id, material_edges=block.IRON_BLOCK.id))

def streets(size=0):
    if size > 0:
        mid1 = V3(mid_point.x-size, mid_point.y, mid_point.z-size)
        mid2 = V3(mid_point.x+size, mid_point.y, mid_point.z+size)
    else:
        mid1, mid2 = V3(0, 0, 60), V3(50, 0, 110)

    s = Streets(mid1, mid2, Map(minx=20, miny=20, style="blacktop", layout="castle", min_size=6))

    zones = [x for x in s.zones if not x.largest]
    f = Farmzones(zones)
    n = Neighborhoods(zones)

    castle1 = [x for x in s.zones if x.largest][0]
    c = castle.Castle(False,castle1)

    s.build()
    f.build()
    n.build()
    c.build()

    return s, f, n, c

def test_circles(thickness=1):
    return helpers.test_drawing_function(vg.circle, 1, 7, 0, 0.8, 0.1, thickness=2)

def test_box(thickness=1):
    return helpers.test_drawing_function(vg.box, 1, 7, thickness=2)

def test_sphere(thickness=1):
    return helpers.test_drawing_function(vg.sphere, 1, 8, 0, 0.8, 0.1, higher=8, thickness=2)

def test_cylinder(thickness=1):
    return helpers.test_drawing_function(vg.cylinder, 1, 7, 0, 0.8, 0.1, thickness=2)

def test_cone(thickness=1):
    return helpers.test_drawing_function(vg.cone, 1, 7, 0, 0.8, 0.1, thickness=2)
