import Decoration
from Map import Map
import mcpi.block as block
import VoxelGraphics as vg
from V3 import V3
from Feature import Feature

import sys

file_name = sys.argv[0][::-1][3:][::-1]
variables = []
materials = []


# -----------------------
def decorate_castle_wall_tower(obj, options):
    height = options.options.roof_battlement_height or 1
    spacing = options.options.roof_battlement_space or 2

    # TODO: Add in battlements, wood roof, stairway, torches
    points = vg.cylinder(options.center, radius=3, height=obj.height or 10)
    obj.points.extend(points)

    return obj


# -----------------------
Decoration.Decoration(kind="castle_wall_tower", callback=decorate_castle_wall_tower, namespace=file_name,
                      variables=variables, materials=materials)
