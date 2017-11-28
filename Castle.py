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

        width, null, depth = vg.dists(options.p1, options.p2)

        if width > 23 and depth > 23:
            castle_walls = True
            inner_p1, inner_p2 = vg.rectangle_inner(options.p1, options.p2, 6)
        else:
            casle_walls = False
            inner_p1, inner_p2 = options.p1, options.p2

        if castle_walls:
            for i in range(0, sides):
                w1 = vg.point_along_circle(False, False, sides, i, Map(p1=options.p1, p2=options.p2))
                w2 = vg.point_along_circle(False, False, sides, i+1, Map(p1=options.p1, p2=options.p2))

                facing = "front" if i == 1 else "side"
                poly = bp.BuildingPoly('castle_outer_wall', [w1, w2], data_so_far.copy(height=castle_wall_height, facing=facing))
                polys.append(poly)

                poly = bp.BuildingPoly('castle_wall_tower', [w1], data_so_far.copy(height=castle_wall_height, facing=facing))
                polys.append(poly)

        corner_vectors = []
        for i in range(0, sides):
            w1 = vg.point_along_circle(False, False, sides, i, Map(p1=inner_p1, p2=inner_p2))
            w2 = vg.point_along_circle(False, False, sides, i+1, Map(p1=inner_p1, p2=inner_p2))
            corner_vectors.append(w1)

            facing = "front" if i == 1 else "side"
            poly = bp.BuildingPoly('wall', [w1, w2], data_so_far.copy(height=castle_inner_wall_height, facing=facing))
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
        castle_z = options.min_z or width
    else:
        rand_x = max(25,math.ceil(width * .7))
        rand_z = max(25,math.ceil(depth * .7))
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
