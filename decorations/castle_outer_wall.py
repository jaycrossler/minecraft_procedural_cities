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


def init():
    pass


# -----------------------
def decorate_castle_outer_wall(obj, options):
    height = options.options.roof_battlement_height or 1
    spacing = options.options.roof_battlement_space or 2

    p1 = options.options.p1
    p2 = options.options.p2

    # TODO: Add in inner and outer, create walkway and arrow slits

    # TODO: Add X,Z outward from center as option
    roof_line = vg.getLine(p1.x, p1.y + height, p1.z, p2.x, p2.y + height, p2.z)
    obj.points.extend(vg.points_spaced(roof_line, Map(every=spacing)))

    mid_points = vg.middle_of_line(obj.bottom(), Map(center=True, max_width=2, point_per=10))
    for vec in mid_points:
        obj.features.append(
            Feature("door", vec, Map(cardinality=obj.cardinality, door_inside=options.options.door_inside)))

    return obj


# -----------------------
init()
Decoration.Decoration(kind="castle_outer_wall", callback=decorate_castle_outer_wall, namespace=file_name,
                      variables=variables, materials=materials)
