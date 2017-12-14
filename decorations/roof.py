import Decoration
from Map import Map
import mcpi.block as block
import VoxelGraphics as vg
from V3 import V3

import sys
file_name = sys.argv[0][::-1][3:][::-1]
variables = []
materials = []


def init():
    variables.append(Map(var="roof", choices=["pointy", "pointy_lines", "battlement", False]))
    variables.append(Map(var="roof_battlement_height", choices=[1, 2, 3]))
    variables.append(Map(var="roof_battlement_space", choices=[1, 2, 3]))
    variables.append(Map(var="roof_pointy_multiplier", choices=[0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.5]))


# -----------------------
def decorate_roof(obj, options=Map()):

    if options.options.roof and str.startswith(options.options.roof, "pointy"):
        height = options.options.roof_pointy_multiplier * options.radius
        pointy = V3(options.center.x, options.center.y + options.height + height, options.center.z)

        for i, vec in enumerate(options.corner_vectors):
            roof_line = vg.getLine(vec.x, vec.y + 1, vec.z, pointy.x, pointy.y + 1, pointy.z)
            obj.points_edges += roof_line

            if not options.options.roof == "pointy_lines":
                next_roof_point = options.corner_vectors[(i + 1) % len(options.corner_vectors)]

                # Triangle to pointy face
                triangle_face = [vec, pointy, next_roof_point]
                roof_face = vg.unique_points(vg.getFace([V3(v.x, v.y + 1, v.z) for v in triangle_face]))
                obj.points = obj.points.union(roof_face)

    if options.options.roof and str.startswith(options.options.roof, "battlement"):
        height = options.options.roof_battlement_height or 1
        spacing = options.options.roof_battlement_space or 2

        for i, vec in enumerate(options.corner_vectors):
            next_roof_point = options.corner_vectors[(i + 1) % len(options.corner_vectors)]
            # TODO: Add X,Z outward from center as option
            roof_line = vg.getLine(vec.x, vec.y + height, vec.z, next_roof_point.x, next_roof_point.y + height,
                                   next_roof_point.z)

            obj.points = obj.points.union(vg.points_spaced(roof_line, Map(every=spacing)))

    return obj


# -----------------------
init()
Decoration.Decoration(kind="roof", callback=decorate_roof, namespace=file_name, variables=variables,
                      materials=materials)
