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
#   TODO: Add a river running through town
#   TODO: Buildings and roads along terrain
#
# Test Buildings:
#   b = Building(False, Map(sides=4, height=7, radius=6, windows="window_line_double", roof="pointy"))
#   b = Building(False, Map(sides=6, height=5, radius=8, windows="window_line", roof="pointy_lines",
#                material=block.WOOL.id, material_edges=block.GOLD_BLOCK.id))
##############################################################################################################
import mcpi
import Texture1D
import numpy as np
import Blocks as blocks
import time

import mcpi.block as block
import math
import MinecraftHelpers as helpers
import VoxelGraphics as vg
import BuildingStyler as bs
import BuildingPoly as bp
import Farmzones as fz
import Castle as castle
from Map import Map
from V3 import V3

helpers.connect()


# -----------------------
# Polygon helper class to store, build, and create blocks
class Neighborhoods(object):
    def __init__(self, zones, options=Map()):
        self.style = options.style
        self.buildings = []
        self.zones = []

        for part in zones:
            self.zones.append(part)
            p1 = vg.up(part.p1,1)
            p2 = vg.up(part.p2,1)
            p1, p2 = vg.rectangle_inner(p1, p2,2)
            self.buildings.append(Building(False, Map(p1=p1, p2=p2)))

    def build(self):
        for b in self.buildings:
            b.build()

    def clear(self):
        for b in self.buildings:
            b.clear()


# -----------------------
# Polygon helper class to store, build, and create blocks
class Streets(object):
    def __init__(self, zones, options=Map()):
        # TODO: Set width 1 or 2 of roads

        self.style = options.style or "blacktop"
        for z in zones:
            z.p1 = vg.up(z.p1,-1)
            z.p2 = vg.up(z.p2,-1)

        self.zones = zones
        self.options = options
        self.blocks, self.inner_blocks = vg.partitions_to_blocks(zones, options)

    def build(self):
        if self.style == "blacktop":
            color = block.OBSIDIAN.id
        else:
            color = block.DIRT.id

        for pos in self.blocks:
            helpers.create_block(pos, color)

    def clear(self):
        for pos in self.blocks:
            helpers.create_block(pos, block.GRASS.id)


# -----------------------
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
            # If position isn't set, use the player position
            if pos is False:
                pos = helpers.my_tile_pos()

        # If "force_height" not passed in as an option, then pick height of the terrain at the x,z point
        # if not options.force_height:
        #     setattr(pos, "y", helpers.get_height(pos))

        self.options = options
        self.radius = options.radius or vg.rand_in_range(4,10)
        self.options = bs.random_options(self.options)
        self.center = V3(pos.x, pos.y, pos.z)

        self.biome = "Plains" # TODO: self.biome.title(options.biome or helpers.biome_at(pos))

        rand_max = min(max(math.ceil(self.radius*2.5), 6),40) # keep buildings between 4-40 height
        self.height = options.height or vg.rand_in_range(4,rand_max)
        self.corner_vectors = []

        self.material = options.material or block.STONE.id
        self.material_edges = options.material_edges or block.IRON_BLOCK.id # TODO: Change based on biome, have rand list

        self.name = options.name or self.biome + " house"

        # Style the polygon based on kind and options
        self = bs.building_styler(self, options)

        # Create the walls and major polygons
        self.polys = self.create_polys(options)

    def build(self):
        for poly in self.polys:
            poly.draw()

        for poly in self.polys:
            if not poly.options.skip_edges:
                poly.draw_edges()

        for poly in self.polys:
            if not poly.options.skip_features:
                poly.draw_features()

    def clear(self):
        for poly in self.polys:
            poly.clear()

    def data(self):
        # TODO: Find how to return this as an iterable data object
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
            # TODO: Pass in point where front door is, determine facing from that
            p = bp.BuildingPoly('wall', [p1, p2], data_so_far.copy(height=self.height, facing=facing))
            polys.append(p)

        roof_vectors = [vg.up(v,self.height) for v in corner_vectors]
        polys.append(bp.BuildingPoly("roof", roof_vectors, data_so_far.copy(corner_vectors = roof_vectors)))
        # insert foundation so that it is drawn first:
        polys.insert(0,bp.BuildingPoly("foundation", [vg.up(v,-1) for v in corner_vectors], data_so_far.copy(corner_vectors = corner_vectors)))

        self.corner_vectors = corner_vectors

        return polys


# --------------------------------------------------------------------
# City Building
# --------------------------------------------------------------------

def city(size=0, layout="castle", farms=False, buildings=False, streets=True):
    # Testing location numbers
    mid_point = V3(30,0,120)

    if size > 0:
        mid1 = V3(mid_point.x-size, mid_point.y, mid_point.z-size)
        mid2 = V3(mid_point.x+size, mid_point.y, mid_point.z+size)
    else:
        mid1, mid2 = V3(0, 0, 60), V3(50, 0, 110)

    print("Building zone and streetmap using layout:", layout)
    if layout == "castle":
        all_zones = castle.build_castle_streetmap(mid1, mid2, Map(min_x=min(size-10,60), min_z=min(size-10,60)))
    else:
        all_zones = vg.partition(mid1, mid2, Map(minx=7, minz=7))
    print("-",len(all_zones), "zones identified")

    farm_zones = []
    building_zones = []
    castle_zone = False

    #Sort zones
    for zone in all_zones:
        if zone.width < 8 or zone.depth < 8:
            farm_zones.append(zone)
        else:
            building_zones.append(zone)

    print("-",len(farm_zones), " farm zones identified")

    #Make the largest zone a castle
    if not castle_zone:
        largest = 0
        largest_index = -1
        for i, zone in enumerate(building_zones):
            size = (zone.width * zone.depth) + min(zone.width,zone.depth)**2
            if size>largest:
                largest = size
                largest_index = i
                castle_zone = zone
        building_zones.pop(largest_index)

    print("-",len(building_zones), " building zones identified")
    print("- Castle size", castle_zone.width, "width by", castle_zone.depth, "depth by", castle_zone.height, "height")

    # Turn zones into creations
    s = Streets(all_zones, Map(style="blacktop"))
    f = fz.Farmzones(farm_zones)
    n = Neighborhoods(building_zones)
    c = castle.Castle(options=castle_zone)

    z = [all_zones,farm_zones,building_zones,castle_zone]

    #Build the creations
    if (streets): s.build()
    if (farms): f.build()
    if (buildings): n.build()
    c.build()

    return Map(s=s, f=f, n=n, c=c, z=z)


def test_c():
    c = castle.Castle(False, Map(p1=V3(0, -1, 90), p2=V3(59, -1, 149)))
    print("Building Castle")
    c.build()
    return c
