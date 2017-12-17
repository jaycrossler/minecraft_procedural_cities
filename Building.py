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
# Test Buildings:
#   b = Building(False, Map(sides=4, height=7, radius=6, windows="window_line_double", roof="pointy"))
#   b = Building(False, Map(sides=6, height=5, radius=8, windows="window_line", roof="pointy_lines",
#                material=block.WOOL.id, material_edges=block.GOLD_BLOCK.id))
##############################################################################################################
import numpy as np

import mcpi.block as block
import math
import MinecraftHelpers as helpers
import VoxelGraphics as vg
from MCShape import MCShape
from Map import Map
from V3 import V3
from Decoration import DECORATIONS_LIBRARY


# -----------------------
# Polygon helper class to store, build, and create blocks
class Neighborhoods(object):
    def __init__(self, zones, options=Map()):
        self.style = options.style
        self.buildings = []
        self.zones = []

        for part in zones:
            self.zones.append(part)
            p1 = vg.up(part.p1, 1)
            p2 = vg.up(part.p2, 1)
            p1, p2 = vg.rectangle_inner(p1, p2, 1)
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
            z.p1 = vg.up(z.p1, -1)
            z.p2 = vg.up(z.p2, -1)

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
        self.polys = []

        if options.p1 and options.p2:
            p1, p2 = vg.min_max_points(options.p1, options.p2)
            options.width = abs(p2.x - p1.x) - 2
            options.depth = abs(p2.z - p1.z) - 2
            options.radius = math.floor(min(options.width, options.depth) / 2)
            pos = V3(round((p1.x + p2.x) / 2), p1.y, round((p1.z + p2.z) / 2))
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
        self.radius = options.radius or vg.rand_in_range(4, 10)
        self.options = choose_random_options(self.options)
        self.center = V3(pos.x, pos.y, pos.z)

        self.biome = "Plains"  # TODO: self.biome.title(options.biome or helpers.biome_at(pos))

        rand_max = min(max(math.ceil(self.radius * 2.5), 6), 40)  # keep buildings between 4-40 height
        self.height = options.height or vg.rand_in_range(4, rand_max)
        self.corner_vectors = []

        self.material = options.material or block.STONE.id
        self.material_edges = options.material_edges or block.IRON_BLOCK.id  # TODO: Change based on biome, have rand list

        self.name = options.name or self.biome + " house"

        # Create the walls and major polygons
        self.create_polys(options)

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

    def __str__(self):
        return "Building with " + str(self.sides) + " sides and height " + str(self.height) + ', having ' +\
               str(len(self.polys)) + ' major shapes'

    def __repr__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))

        return ', '.join(sb)

    def create_polys(self, options=Map()):
        polys = self.polys
        data_so_far = self.data()

        sides = data_so_far.sides or 4

        if options.outside:
            corners, lines = helpers.corners_from_bounds(options.p1, options.p2, sides, self.center, self.radius, options.width, options.depth)
            polys.append(MCShape(["garden"], corners, data_so_far.copy(corner_vectors=corners, lines=lines)))
            options.p1, options.p2 = vg.rectangle_inner(options.p1, options.p2, 1)

        # Build Walls
        corners, lines = helpers.corners_from_bounds(options.p1, options.p2, sides, self.center, self.radius, options.width, options.depth)
        for i, l in enumerate(lines):
            facing = "front" if i == 1 else "side"
            # TODO: Pass in point where front door is, determine facing from that
            p = MCShape(["standing rectangle", "wall"], l, data_so_far.copy(height=self.height, facing=facing))
            polys.append(p)

        # Build Roof and Foundation
        roof_vectors = [vg.up(v, self.height) for v in corners]
        polys.append(MCShape(["flat rectangle", "roof"], roof_vectors, data_so_far.copy(corner_vectors=roof_vectors)))
        polys.insert(0, MCShape(["flat rectangle", "foundation"], [vg.up(v, -1) for v in corners],
                                data_so_far.copy(corner_vectors=corners)))

        self.corner_vectors = corners
        self.polys = polys


# -----------------------
def choose_random_options(options=Map()):
    for d in DECORATIONS_LIBRARY:
        if d.variables:
            for var in d.variables:
                var_name = var["var"]
                choices = var["choices"]

                if var_name not in options:
                    options[var_name] = np.random.choice(choices)

    return options
