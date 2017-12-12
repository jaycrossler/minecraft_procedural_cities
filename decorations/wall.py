import math
import Decoration
from Map import Map
import mcpi.block as block
import VoxelGraphics as vg
from V3 import V3
from Feature import Feature


# -----------------------
def decorate_wall(obj, options):
    if options.options.windows == "window_line":
        spaced_points = vg.extrude(obj.bottom(), Map(spacing=V3(0, math.ceil(obj.height / 2), 0)))
        for vec in spaced_points:
            obj.features.append(Feature("window", vec))

    elif options.options.windows == "window_line_double":
        spaced_points = vg.extrude(obj.bottom(), Map(spacing=V3(0, math.ceil(obj.height / 2), 0)))
        spaced_points2 = vg.extrude(spaced_points, Map(spacing=V3(0, 1, 0)))
        for vec in spaced_points + spaced_points2:
            obj.features.append(Feature("window", vec))

    elif options.options.windows == "window_slits":
        spaced_points = vg.points_spaced(obj.bottom(), Map(every=3))
        spaced_points = vg.extrude(spaced_points, Map(spacing=V3(0, math.ceil(obj.height / 2), 0)))
        spaced_points2 = vg.extrude(spaced_points, Map(spacing=V3(0, 1, 0)))
        for vec in spaced_points + spaced_points2:
            obj.features.append(Feature("spacing", vec))

    else:
        spaced_points = vg.points_spaced(obj.bottom(), Map(every=3))
        spaced_points = vg.extrude(spaced_points, Map(spacing=V3(0, math.ceil(obj.height / 2), 0)))
        for vec in spaced_points:
            obj.features.append(Feature("window", vec))

    mid_points = vg.middle_of_line(obj.bottom(), Map(center=True, max_width=2, point_per=10))
    for vec in mid_points:
        obj.features.append(
            Feature("door", vec, Map(cardinality=obj.cardinality, door_inside=options.options.door_inside)))

    return obj



# -----------------------
Decoration.Decoration("wall", decorate_wall)
