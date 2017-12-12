import Decoration
from Map import Map
import mcpi.block as block
import VoxelGraphics as vg
from V3 import V3
from Feature import Feature


# -----------------------
def decorate_castle_outer_wall(obj, options):
    height = options.options.roof_battlement_height or 1
    spacing = options.options.roof_battlement_space or 2

    # TODO: Add in inner and outer, create walkway and arrow slits

    # TODO: Add X,Z outward from center as option
    roof_line = vg.getLine(options.p1.x, options.p1.y + height, options.p1.z, options.p2.x, options.p2.y + height,
                           options.p2.z)
    obj.points.extend(vg.points_spaced(roof_line, Map(every=spacing)))

    mid_points = vg.middle_of_line(obj.bottom(), Map(center=True, max_width=2, point_per=10))
    for vec in mid_points:
        obj.features.append(
            Feature("door", vec, Map(cardinality=obj.cardinality, door_inside=options.options.door_inside)))

    return obj


# -----------------------
Decoration.Decoration("castle_outer_wall", decorate_castle_outer_wall)
