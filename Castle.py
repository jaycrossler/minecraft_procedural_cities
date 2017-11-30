#############################################################################################################
# Procedural Building voxel drawing functions for MineCraft.
##############################################################################################################

import math
import mcpi.block as block
import numpy as np
from Building import Building
import VoxelGraphics as vg
import BuildingPoly as bp
from Map import Map
import MinecraftHelpers as helpers
from V3 import *

#-----------------------
# Polygon helper class to store, build, and create blocks
class Castle(Building):
    def __init__(self, pos=False, options=Map()):
        options.outside = "none"
        super(self.__class__, self).__init__(pos, options)
        self.kind = options.kind or "old stone"

    def info(self, show=True):
        stro = ["Castle with " + str(self.sides) + " sides and height " + str(self.height)]
        for p in self.polys:
            stro += p.info()

        if show:
            for s in stro:
                print (s)
        else:
            return stro
    #-----------------------

    def create_polys(self, options=Map()):
        polys = []
        data_so_far = self.data()

        sides = 4
        castle_wall_height = options.castle_wall_height or 12
        castle_inner_wall_height = options.castle_inner_wall_height or 18

        p1 = vg.up(options.p1,1)
        p2 = vg.up(options.p2,1)

        # castle_farm = width > 19 and depth > 17

        width, null, depth = vg.dists(p1, p2)
        print("starting ps",p1,p2, "wxd:", width, depth)
        if (width > 22) and (depth > 22):
            #keep moat width between 4 and 10
            if (width > 26) and (depth > 26):
                moat_width = round(min((width+depth/2)-26, 10))
            else:
                moat_width = 4

            p1, p2 = vg.rectangle_inner(p1,p2, moat_width/2)
            outside_vectors = []
            for i in range(0, sides):
                w1 = vg.point_along_circle(False, False, sides, i, Map(p1=vg.up(p1,-1), p2=vg.up(p2,-1), align_to_cells=True))
                outside_vectors.append(w1)

            poly = bp.BuildingPoly("moat", outside_vectors, data_so_far.copy(moat_width=(moat_width/2)-1, material=block.WATER.id, height=1, skip_edges=True, skip_features=True))
            polys.append(poly)
            print("--moat", outside_vectors)
            p1, p2 = vg.rectangle_inner(p1,p2, moat_width/2)

        width, null, depth = vg.dists(p1, p2)
        print("tower ps",p1,p2, "wxd:", width, depth)
        if (width > 17) and (depth > 17):
            p1, p2 = vg.rectangle_inner(p1,p2, 4)
            for i in range(0, sides):
                w1 = vg.point_along_circle(False, False, sides, i, Map(p1=p1, p2=p2, align_to_cells=True))
                w2 = vg.point_along_circle(False, False, sides, i+1, Map(p1=p1, p2=p2, align_to_cells=True))

                facing = "front" if i == 1 else "side"
                poly = bp.BuildingPoly("castle_outer_wall", [w1, w2], data_so_far.copy(height=castle_wall_height, facing=facing, thickness=3))
                polys.append(poly)
                print("--tower line", w1, w2)

                poly = bp.BuildingPoly("castle_wall_tower", [w1], data_so_far.copy(style="castle_wall_tower", height=castle_wall_height, facing=facing, radius=3))
                polys.append(poly)
                print("--tower", w1)

        corner_vectors = []
        p1, p2 = vg.rectangle_inner(p1,p2, 4)
        for i in range(0, sides):
            w1 = vg.point_along_circle(False, False, sides, i, Map(p1=p1, p2=p2, align_to_cells=True))
            w2 = vg.point_along_circle(False, False, sides, i+1, Map(p1=p1, p2=p2, align_to_cells=True))
            corner_vectors.append(w1)

            facing = "front" if i == 1 else "side"
            poly = bp.BuildingPoly("wall", [w1, w2], data_so_far.copy(height=castle_inner_wall_height, facing=facing))
            polys.append(poly)

        roof_vectors = [vg.up(v,castle_inner_wall_height) for v in corner_vectors]
        polys.append(bp.BuildingPoly("roof", roof_vectors, data_so_far.copy(corner_vectors = roof_vectors)))
        #insert foundation so that it is drawn first:
        polys.insert(0,bp.BuildingPoly("foundation", [vg.up(v,-1) for v in corner_vectors], data_so_far.copy(corner_vectors = corner_vectors)))

        self.corner_vectors = corner_vectors

        return polys

    #-----------------------

def build_castle_streetmap(p1,p2,options=Map()):
    width, null, depth = vg.dists(p1, p2)

    #Find a large central rectangle for the castle
    if width < 25 or depth < 25:
        castle_x = options.min_x or width
        castle_z = options.min_z or depth
    else:
        rand_x = max(25,math.ceil(width * .75))
        rand_z = max(25,math.ceil(depth * .75))
        castle_x = options.min_x or min(width, np.random.randint(24,rand_x))
        castle_z = options.min_z or min(depth, np.random.randint(24,rand_z))

    ninths = vg.ninths(p1, p2, castle_x, castle_z)
    partitions = []
    for ninth in ninths:
        if ninth.largest:
            partitions.append(ninth)
        else:
            w, null, d = vg.dists(ninth.p1, ninth.p2)
            if (w > 5) and (d > 5):
                subparts = vg.partition(ninth.p1, ninth.p2)
                partitions.extend(subparts)
            else:
                partitions.append(ninth)

    return partitions
