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
from Map import Map
from V3 import V3

helpers.connect()

#Testing location numbers
corner1, corner2 = V3(-60, 0, 40), V3(120, 0, 200)
mid1, mid2 = V3(0, 0, 60), V3(50, 0, 110)

#-----------------------
# Polygon helper class to store, build, and create blocks
class Farmzones(object):
    def __init__(self, zones, options=Map()):
        min_size = options.min_size or 0
        max_size = options.max_size or 7
        self.road_blocks, self.farm_blocks = vg.partitions_to_blocks(zones, Map(min_size=min_size, max_size=max_size, or_mix=True))
        self.style = options.style or "cane"

    def build(self):
        if self.style == "cane":
            for i, p1 in enumerate(self.farm_blocks):
                if (i % 8) == 0:
                    helpers.create_block(p1,block.WATER.id)
                else:
                    helpers.create_block(p1,block.FARMLAND.id)
                    helpers.create_block(V3(p1.x,p1.y+1,p1.z),block.SUGAR_CANE.id)
                    helpers.create_block(V3(p1.x,p1.y+2,p1.z),block.SUGAR_CANE.id)

    def clear(self):
        if self.style == "cane":
            for p1 in self.farm_blocks:
                helpers.create_block(p1,block.DIRT.id)
                helpers.create_block(V3(p1.x,p1.y+1,p1.z),block.AIR.id)
                helpers.create_block(V3(p1.x,p1.y+2,p1.z),block.AIR.id)

#-----------------------
# Polygon helper class to store, build, and create blocks
class Neighborhoods(object):
    def __init__(self, zones, options=Map()):
        min_size = options.min_size or 9
        self.style = options.style
        self.buildings = []
        self.zones = []

        for part in zones:
            if (min_size <= part.width) and (min_size <= part.height):
                self.zones.append(part)
                p1 = V3(part.p1.x, part.p1.y+1, part.p1.z)
                p2 = V3(part.p2.x, part.p2.y+1, part.p2.z)
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
        self.p1 = p1
        self.p2 = p2
        self.minx = options.minx or 7
        self.minz = options.minz or 7
        self.style = options.style or "blacktop"

        self.options = options
        # self.blocks_on_side = []
        # self.inner_zones = []

        self.zones = vg.partition(V3(p1.x, p1.y-1, p1.z), V3(p2.x, p2.y-1, p2.z), self.minx, self.minz)
        #TODO: Set width 1 or 2
        #TODO: shrink rect by 1 and draw perimeter

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
# Polygon helper class to store, build, and create blocks
class BuildingPoly(object):
    def __init__(self, kind, vertices, options=Map()):
        self.kind = kind
        self.facing = options.facing
        self.material = options.material
        self.material_edges = options.material_edges #TODO: Different colors for different edges
        self.features = []

        if len(vertices) == 2:
            #If two points are given, assume it's for the bottom line, then draw that as a wall

            #TODO: Add width for the wall - how to add end lines to that?
            p1 = vertices[0]
            p2 = vertices[1]
            h = options.height or 5
            self.vertices = vertices_with_up = [p1, p2, V3(p2.x, p2.y+h, p2.z), V3(p1.x, p1.y+h, p1.z)] # points straight up
            self.height = options.height or (vg.highest(vertices_with_up) - vg.lowest(vertices_with_up) + 1)
            self.cardinality = vg.cardinality(p1,p2)
            self.points, self.top_line, self.bottom_line, self.left_line, self.right_line = vg.rectangular_face(p1, p2, h)
        else:
            #It's a non-y-rectangular-shaped polygon, so use a different getFace builder function
            self.vertices = vertices
            self.height = options.height or (vg.highest(vertices) - vg.lowest(vertices) + 1)
            self.cardinality = options.cardinality
            self.points = vg.unique_points(vg.getFace(self.vertices))
            x, self.top_line, self.bottom_line, self.left_line, self.right_line = vg.poly_point_edges(self.points)

        self.points_edges = self.top_line + self.bottom_line + self.left_line + self.right_line

        #Style the polygon based on kind and options
        self = bs.building_poly_styler(self, kind, options)

    def draw(self):
        blocks_to_not_draw = []
        for feature in self.features:
            blocks_to_not_draw += feature.blocks_to_not_draw;

        helpers.create_blocks_from_pointlist(self.points, self.material, blocks_to_not_draw=blocks_to_not_draw)

    def draw_edges(self):
        blocks_to_not_draw = []
        for feature in self.features:
            blocks_to_not_draw += feature.blocks_to_not_draw;

        if self.material_edges:
            helpers.create_blocks_from_pointlist(self.points_edges, self.material_edges, blocks_to_not_draw=blocks_to_not_draw)

    def draw_features(self):
        for feature in self.features:
            feature.draw()

    
    def clear(self):
        material = block.GRASS.id if self.kind == "foundation" else block.AIR.id
        helpers.create_blocks_from_pointlist(self.points, material)
        helpers.create_blocks_from_pointlist(self.points_edges, material)
        for feature in self.features:
            feature.clear()

    def bottom(self):
        if not hasattr(self, "bottom_line"):
            self.bottom_line = vg.points_along_poly(self.points, Map(side="bottom"))
        return self.bottom_line

    def top(self):
        if not hasattr(self, "top_line"):
            self.top_line = vg.points_along_poly(self.points, Map(side="top"))
        return self.top_line

    def left(self):
        if not hasattr(self, "left_line"):
            self.left_line = vg.points_along_poly(self.points, Map(side="left_x"))
        return self.left_line

    def right(self):
        if not hasattr(self, "right_line"):
            self.right_line = vg.points_along_poly(self.points, Map(side="right_x"))
        return self.right_line

    #TODO: Inside and outside point?

    def info(self):
        stro = []
        stro.append(" - Polygon: " + self.kind + " with " + str(self.vertices) + " points, height " + str(self.height) + ", and " +str(len(self.points)) +" blocks")
        for f in self.features:
            stro.append("  -- " + f.info())
        return stro

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

        rand_max = max(math.ceil(self.radius*2.5), 6)
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
            p = BuildingPoly('wall', [p1, p2], data_so_far.copy(height=self.height, facing=facing))
            polys.append(p)

        roof_vectors = [V3(v.x, v.y+self.height, v.z) for v in corner_vectors]
        polys.append(BuildingPoly("roof", roof_vectors, data_so_far.copy(corner_vectors = roof_vectors)))
        #insert foundation so that it is drawn first:
        polys.insert(0,BuildingPoly("foundation", [V3(v.x, v.y-1, v.z) for v in corner_vectors], data_so_far.copy(corner_vectors = corner_vectors))) 

        self.corner_vectors = corner_vectors

        return polys

def prep():
    helpers.debug("Bulldozing building zone...")
    helpers.create_block_filled_box(V3(corner1.x, corner1.y-1, corner1.z), V3(corner2.x, corner2.y-3, corner2.z), block.GRASS.id, data=None)
    helpers.create_block_filled_box(V3(corner1.x, corner1.y, corner1.z), V3(corner2.x, corner2.y+40, corner2.z), block.AIR.id, data=None)
    helpers.debug("...Finished bulldozing")

def t1():
    return Building(False, Map(sides=4, height=7, radius=6, windows="window_line_double", roof="pointy"))

def t2():
    return Building(False, Map(sides=6, height=5, radius=8, windows="window_line", roof="pointy_lines", material=block.WOOL.id, material_edges=block.GOLD_BLOCK.id))

def t3():
    return Building(False, Map(sides=4, height=20, radius=6, windows="window_slits", roof="battlement", material=block.STONE_BRICK.id, material_edges=block.IRON_BLOCK.id))

def streets():
    s = Streets(mid1, mid2, Map(minx=20, miny=20, style="blacktop", min_size=6))
    f = Farmzones(s.zones)
    n = Neighborhoods(s.zones)
    s.build()
    f.build()
    n.build()
    return s, f, n