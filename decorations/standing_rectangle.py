import Decoration
import VoxelGraphics as vg

import sys

file_name = sys.argv[0][::-1][3:][::-1]
variables = []
materials = []


# -----------------------
def init():
    pass


def build_basic_shape(obj, options):
    vertices = options.vertices

    # TODO: Add width for the wall - how to add end lines to that?

    options.p1 = p1 = vertices[0]
    options.p2 = p2 = vertices[1]

    obj.inside_vector = vg.inside_vector(p1=p1, center=options.center, p2=p2)
    obj.outside_vector = obj.inside_vector * -1

    h = options.height or 5
    if h > 1:
        obj.vertices = vertices_with_up = [p1, p2, vg.up(p2, h), vg.up(p1, h)]  # points straight up
        obj.height = options.height or (vg.highest(vertices_with_up) - vg.lowest(vertices_with_up) + 1)
        obj.points, obj.top_line, obj.bottom_line, obj.left_line, obj.right_line = vg.rectangular_face(p1, p2, h)
        obj.points_edges = obj.top_line + obj.bottom_line + obj.left_line + obj.right_line
    else:
        obj.vertices = [p1, p2]  # points straight up
        obj.height = h
        obj.points_edges = obj.points = obj.top_line = obj.bottom_line = vg.getLine(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z)
        obj.left_line = obj.points[0]
        obj.right_line = obj.points[-1]

    obj.cardinality = vg.cardinality(p1, p2)
    return obj


# -----------------------
init()
Decoration.Decoration(kind="standing rectangle", callback=build_basic_shape, namespace=file_name, variables=variables,
                      materials=materials)
