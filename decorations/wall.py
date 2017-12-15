import math
import Decoration
from Map import Map
import mcpi.block as block
import VoxelGraphics as vg
from V3 import V3
from Feature import Feature
from Texture1D import COLOR_MAPS

import sys
file_name = sys.argv[0][::-1][3:][::-1]
variables = []
materials = []


# -----------------------
def init():
    variables.append(Map(var="windows", choices=["window_line", "window_line_double", "window_slits"]))
    # variables.append(Map(var="wall_type", choices=["building_inner", "building_outer", "castle_wall"]))
    # materials.extend([Map(name="wall", material=COMMON_TEXTURES.OldStoneWall)])
    # materials.extend([Map(name="wall_base", material=(4, 0))])
    # materials.extend([Map(name="wall_edges", material=(1, 0))])

    variables.append(Map(var="window_style", choices=["open_slit_and_above", "glass"]))
    variables.append(Map(var="door_inside", choices=[True, False]))
    variables.append(Map(var="outside", choices=["flowers", "trees", "grass", "fence", False]))


def decorate_wall(obj, options):

    if options.options.windows == "window_line":
        spaced_points = vg.extrude(obj.bottom(), Map(spacing=V3(0, math.ceil(obj.height / 2), 0)))
        for vec in spaced_points:
            obj.features.append(Feature("window", vec, options=options.options))

    elif options.options.windows == "window_line_double":
        spaced_points = vg.extrude(obj.bottom(), Map(spacing=V3(0, math.ceil(obj.height / 2), 0)))
        spaced_points2 = vg.extrude(spaced_points, Map(spacing=V3(0, 1, 0)))
        for vec in spaced_points + spaced_points2:
            obj.features.append(Feature("window", vec, options=options.options))

    elif options.options.windows == "window_slits":
        spaced_points = vg.points_spaced(obj.bottom(), Map(every=5))
        spaced_points = vg.extrude(spaced_points, Map(spacing=V3(0, math.ceil(obj.height / 2), 0)))
        spaced_points2 = vg.extrude(spaced_points, Map(spacing=V3(0, 1, 0)))
        for vec in spaced_points + spaced_points2:
            obj.features.append(Feature("spacing", vec))

    else:
        spaced_points = vg.points_spaced(obj.bottom(), Map(every=3))
        spaced_points = vg.extrude(spaced_points, Map(spacing=V3(0, math.ceil(obj.height / 2), 0)))
        for vec in spaced_points:
            obj.features.append(Feature("window", vec, options=options.options))

    mid_points = vg.middle_of_line(obj.bottom(), Map(center=True, max_width=2, point_per=10))
    for vec in mid_points:
        obj.features.append(
            Feature("door", vec, Map(cardinality=obj.cardinality, door_inside=options.options.door_inside)))

    return obj


# -----------------------
init()
Decoration.Decoration(kind="wall", callback=decorate_wall, namespace=file_name, variables=variables,
                      materials=materials)
