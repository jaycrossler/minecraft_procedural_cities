import Decoration
import VoxelGraphics as vg
import Blocks


import sys
file_name = sys.argv[0][::-1][3:][::-1]
variables = []
materials = []


# -----------------------
def init():
    pass


def build_basic_shape(obj, options):

    vertices = options.vertices

    # It's a non-y-rectangular-shaped polygon, so use a different getFace builder function
    obj.height = options.height or (vg.highest(vertices) - vg.lowest(vertices) + 1)
    obj.cardinality = options.cardinality
    obj.points = vg.unique_points(vg.getFace(obj.vertices))
    null, obj.top_line, obj.bottom_line, obj.left_line, obj.right_line = vg.poly_point_edges(obj.points)
    obj.points_edges = obj.top_line + obj.bottom_line + obj.left_line + obj.right_line

    if options.vertices[0].y > options.center.y:
        obj.material_clear = Blocks.AIR
    else:
        obj.material_clear = Blocks.GRASS

    return obj


# -----------------------
init()
Decoration.Decoration(kind="flat rectangle", callback=build_basic_shape, namespace=file_name, variables=variables,
                      materials=materials)
