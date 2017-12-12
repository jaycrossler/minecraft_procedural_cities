import Decoration
from Map import Map
import mcpi.block as block
import VoxelGraphics as vg


# -----------------------
def decorate_moat(obj, options=Map()):
    # TODO: FINISH
    moat_type = options.options.moat or "clear"
    radius = options.moat_width or 2
    height = -1 * abs(options.moat_depth or (radius + 2))

    points = []
    for i, vec in enumerate(obj.vertices):
        next_vec = obj.vertices[(i + 1) % len(obj.vertices)]
        print("---MOAT LINE:", vec, next_vec, height, radius)

        p1, p2 = vg.move_points_together(vec, next_vec, -radius)
        points.extend(vg.triangular_prism(p1, p2, height=height, radius=radius, sloped=True))

    obj.points = points
    obj.points_edges = []

    obj.material = block.WATER.id
    # if moat_type=="ice":

    return obj


# -----------------------
Decoration.Decoration("moat", decorate_moat)
