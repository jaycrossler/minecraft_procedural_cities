import Decoration
from Map import Map
import Blocks
import VoxelGraphics as vg

import sys
file_name = sys.argv[0][::-1][3:][::-1]
variables = []
materials = []


def init():
    variables.append(Map(var="moat", choices=["clear", "icy", "weeds"]))


# -----------------------
def decorate_moat(obj, options=Map()):
    # TODO: FINISH
    moat_type = options.options.moat or "clear"
    radius = options.moat_width or 2
    height = -1 * abs(options.moat_depth or (radius + 2))
    obj.material_clear = Blocks.GRASS

    points = []
    for i, vec in enumerate(obj.vertices):
        next_vec = obj.vertices[(i + 1) % len(obj.vertices)]
        print("---MOAT LINE:", vec, next_vec, height, radius)

        p1, p2 = vg.move_points_together(vec, next_vec, -radius)
        points.extend(vg.triangular_prism(p1, p2, height=height, radius=radius, sloped=True))

    obj.points = points
    obj.points_edges = []

    obj.material = Blocks.WATER
    # if moat_type=="ice":

    return obj


# -----------------------
init()
Decoration.Decoration(kind="moat", callback=decorate_moat, namespace=file_name, variables=variables,
                      materials=materials)
