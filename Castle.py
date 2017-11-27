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

        corner_vectors = []
        for i in range(0, sides):
            p1 = vg.point_along_circle(False, False, sides, i, Map(p1=options.p1, p2=options.p2))
            p2 = vg.point_along_circle(False, False, sides, i+1, Map(p1=options.p1, p2=options.p2))
            corner_vectors.append(p1)

            facing = "front" if i == 1 else "side"
            #TODO: Pass in point where front door is, determine facing from that
            p = bp.BuildingPoly('wall', [p1, p2], data_so_far.copy(height=self.height, facing=facing))
            polys.append(p)

        # roof_vectors = [vg.up(v,self.height) for v in corner_vectors]
        # polys.append(BuildingPoly("roof", roof_vectors, data_so_far.copy(corner_vectors = roof_vectors)))
        #insert foundation so that it is drawn first:
        # polys.insert(0,BuildingPoly("foundation", [vg.up(v,-1) for v in corner_vectors], data_so_far.copy(corner_vectors = corner_vectors)))

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
