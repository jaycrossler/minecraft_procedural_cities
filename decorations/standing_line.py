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

    #TODO: These are being built at center

    obj.center = options.center = p1 = vertices[0]
    obj.height = h = options.height or 8
    obj.points = []
    obj.points_edges = []  # TODO: Use bottom and top circles for edges?
    obj.vertices = [p1, p1, vg.up(p1, h), vg.up(p1, h)]  # points straight up

    obj.inside_vector = vg.inside_vector(p1=p1, center=options.center)
    obj.outside_vector = obj.inside_vector * -1

    return obj


# -----------------------
init()
Decoration.Decoration(kind="standing line", callback=build_basic_shape, namespace=file_name, variables=variables,
                      materials=materials)
