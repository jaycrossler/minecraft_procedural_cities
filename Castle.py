#############################################################################################################
# Procedural Building voxel drawing functions for MineCraft.
##############################################################################################################

import math
import mcpi.block as block
import numpy as np
from Building import Building
import VoxelGraphics as vg
from MCShape import MCShape
from Map import Map
from V3 import *
import MinecraftHelpers as helpers


# -----------------------
# Polygon helper class to store, build, and create blocks
class Castle(Building):
    def __init__(self, pos=False, options=Map()):
        options.outside = "none"
        super(self.__class__, self).__init__(pos, options)
        self.kind = options.kind or "old stone"

    # -----------------------

    def create_polys(self, options=Map()):
        polys = self.polys or []
        data_so_far = self.data()

        options.outside = False
        sides = options.sides = 4
        castle_wall_height = options.castle_wall_height or 9
        castle_inner_wall_height = options.castle_inner_wall_height or 18

        p1 = vg.up(options.p1, 1)
        p2 = vg.up(options.p2, 1)

        width, null, depth = vg.dists(p1, p2)
        print("Castle starting points and dimensions", p1, p2, ":", width, "x", depth)
        if (width > 22) and (depth > 22):
            # keep moat width between 4 and 10
            if (width > 26) and (depth > 26):
                moat_width = round(min((width + depth / 2) - 26, 10))
            else:
                moat_width = 4

            # Build Moat
            p1, p2 = vg.rectangle_inner(p1, p2, moat_width / 2)
            corners, lines = helpers.corners_from_bounds(vg.up(p1, -1), vg.up(p2, -1), sides, self.center, self.radius,
                                                         options.width, options.depth)
            p = MCShape(["moat"], corners, data_so_far.copy(height=self.height))
            polys.append(p)

            p1, p2 = vg.rectangle_inner(p1, p2, (moat_width / 2) - 2)

        width, null, depth = vg.dists(p1, p2)
        print("- Castle tower points", p1, p2, " and dimensions:", width, "x", depth)
        if (width > 17) and (depth > 17):

            p1, p2 = vg.rectangle_inner(p1, p2, 2)
            corners, lines = helpers.corners_from_bounds(p1, p2, sides, self.center, self.radius,
                                                         options.width, options.depth)

            for i, l in enumerate(lines):
                facing = "front" if i == 1 else "side"
                p = MCShape(["standing rectangle", "castle_outer_wall"], l, data_so_far.copy(height=castle_wall_height, thickness=3, facing=facing))
                polys.append(p)

            for i, c in enumerate(corners):
                p = MCShape(["standing line", "castle_wall_tower"], [c], data_so_far.copy(height=castle_wall_height, radius=3, facing=facing))
                polys.append(p)

            p1, p2 = vg.rectangle_inner(p1, p2, 4)

        options.p1 = p1
        options.p2 = p2

        self.polys = polys

        # Call the Building's create_poly class to build walls and roof
        super(self.__class__, self).create_polys(options)

    # -----------------------


def build_castle_streetmap(p1, p2, options=Map()):
    width, null, depth = vg.dists(p1, p2)

    # Find a large central rectangle for the castle
    if width < 25 or depth < 25:
        castle_x = options.castle_x or width
        castle_z = options.castle_z or depth
    else:
        rand_x = max(25, math.ceil(width * .75))
        rand_z = max(25, math.ceil(depth * .75))
        castle_x = options.castle_x or min(width, np.random.randint(24, rand_x))
        castle_z = options.castle_z or min(depth, np.random.randint(24, rand_z))

    ninths = vg.ninths(p1, p2, castle_x, castle_z)
    partitions = []
    for ninth in ninths:
        if ninth.largest:
            partitions.append(ninth)
        else:
            w, null, d = vg.dists(ninth.p1, ninth.p2)
            if (w > 5) and (d > 5):
                subparts = vg.partition(ninth.p1, ninth.p2, min_x=options.min_x, min_z=options.min_z)
                partitions.extend(subparts)
            else:
                partitions.append(ninth)

    return partitions


if __name__ == "__main__":
    import time

    c = Castle(False, Map(p1=V3(0, -1, 90), p2=V3(59, -1, 149)))
    print("Building Castle")
    c.build()
    time.sleep(20)
    c.clear()
