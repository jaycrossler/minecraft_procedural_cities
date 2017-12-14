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
            p1, p2 = vg.rectangle_inner(p1, p2, 2)
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
        self.options = random_options(self.options)
        self.center = V3(pos.x, pos.y, pos.z)

        self.biome = "Plains"  # TODO: self.biome.title(options.biome or helpers.biome_at(pos))

        rand_max = min(max(math.ceil(self.radius * 2.5), 6), 40)  # keep buildings between 4-40 height
        self.height = options.height or vg.rand_in_range(4, rand_max)
        self.corner_vectors = []

        self.material = options.material or block.STONE.id
        self.material_edges = options.material_edges or block.IRON_BLOCK.id  # TODO: Change based on biome, have rand list

        self.name = options.name or self.biome + " house"

        # Style the polygon based on kind and options
        self.building_styler(options)

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
                print(s)
        else:
            return stro

    def create_polys(self, options=Map()):
        polys = []
        data_so_far = self.data()

        sides = data_so_far.sides or 4

        corner_vectors = []
        for i in range(0, sides):
            p1 = vg.point_along_circle(self.center, self.radius, sides, i,
                                       Map(align_to_cells=True, width=options.width, depth=options.depth, p1=options.p1,
                                           p2=options.p2))
            p2 = vg.point_along_circle(self.center, self.radius, sides, i + 1,
                                       Map(align_to_cells=True, width=options.width, depth=options.depth, p1=options.p1,
                                           p2=options.p2))
            corner_vectors.append(p1)

            facing = "front" if i == 1 else "side"
            # TODO: Pass in point where front door is, determine facing from that
            p = MCShape('wall', [p1, p2], data_so_far.copy(height=self.height, facing=facing))
            polys.append(p)

        roof_vectors = [vg.up(v, self.height) for v in corner_vectors]
        polys.append(MCShape("roof", roof_vectors, data_so_far.copy(corner_vectors=roof_vectors)))
        # insert foundation so that it is drawn first:
        polys.insert(0, MCShape("foundation", [vg.up(v, -1) for v in corner_vectors],
                                data_so_far.copy(corner_vectors=corner_vectors)))

        self.corner_vectors = corner_vectors

        return polys

    # -----------------------
    def building_styler(self, options=Map()):

        # TODO: Move these create blocks to add a "garden" Decoration
        if options.outside and options.p1 and options.p2:
            p1, p2 = vg.rectangle_inner(options.p1, options.p2, options.outside_width or -1)
            rec, none = vg.rectangle(p1, p2)

            if options.outside == "flowers":
                for i, v in enumerate(rec):
                    material = block.FLOWER_YELLOW.id if (i % 2) == 0 else block.FLOWER_CYAN.id
                    helpers.create_block(v, material)
            elif options.outside == "trees":
                for i, v in enumerate(rec):
                    if (i % 3) == 0:
                        helpers.create_block(v, block.SAPLING.id)
            elif options.outside == "grass":
                for i, v in enumerate(rec):
                    if (i % 2) == 0:
                        helpers.create_block(v, block.GRASS_TALL.id)
            elif options.outside == "fence":
                for i, v in enumerate(rec):
                    helpers.create_block(v, block.FENCE.id)

        return self


# -----------------------
def random_options(options=Map()):
    for d in DECORATIONS_LIBRARY:
        if d.variables:
            for var in d.variables:
                var_name = var["var"]
                choices = var["choices"]

                if var_name not in options:
                    options[var_name] = np.random.choice(choices)

    # if not options.windows:
    #     options.windows = np.random.choice(["window_line_double", "window_line", "window_slits"])
    # if not options.window_style:
    #     options.windows = np.random.choice(["open_slit_and_above", "glass"])
    # if not options.roof:
    #     options.roof = np.random.choice(["pointy", "pointy_lines", "battlement", False])
    # if not options.moat:
    #     options.moat = np.random.choice(["clear", "icy", "weeds"])

    if not options.material:
        options.color_scheme = r = np.random.choice(["gold_white", "grey_iron", "grey_stone", "blue_white"])
        if r == "gold_white":
            options.material = block.WOOL.id
            options.material_edges = block.GOLD_BLOCK.id
        elif r == "grey_iron":
            options.material = block.STONE_BRICK.id
            options.material_edges = block.IRON_BLOCK.id
        elif r == "grey_stone":
            options.material = block.STONE_SLAB_DOUBLE.id
            options.material_edges = block.IRON_BLOCK.id
        elif r == "blue_white":
            options.material = block.WOOL.id
            options.material_edges = block.LAPIS_LAZULI_BLOCK.id
        elif r == "brown":
            options.material = block.SAND.id
            options.material_edges = block.SANDSTONE.id
    # if not options.roof_pointy_height:
    #     options.roof_pointy_height = round(np.random.random() * (options.radius or 5) * 3)
    # if not options.roof_battlement_height:
    #     options.roof_battlement_height = np.random.choice([1, 2, 3])  # TODO: Have it go straight up
    # if not options.roof_battlement_space:
    #     options.roof_battlement_space = np.random.choice([1, 2, 3])
    # if not options.door_inside:
    #     options.door_inside = np.random.choice([True, False])
    # if not options.outside:
    #     options.outside = np.random.choice(["flowers", "trees", "grass", "fence", False])

    return options

