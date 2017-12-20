import Decoration
from Map import Map
import VoxelGraphics as vg
from V3 import V3
from Feature import Feature
import Blocks

import sys

file_name = sys.argv[0][::-1][3:][::-1]
variables = []
materials = []


def init():
    variables.append(Map(var="roof_triangular_sloped", choices=[-2, -1, -.5, -.25, 0, 0, 0, .25, .5, 1, 2]))
    variables.append(Map(var="roof_triangular_stairs", choices=[True, False]))
    variables.append(Map(var="roof_triangular_end_cap_out", choices=[0, 1, 2, 2, 3]))
    variables.append(Map(var="roof_triangular_overhang", choices=[0, 0, 0, 1, 2]))
    variables.append(Map(var="roof_triangular_chop_pct", choices=[0]))  # , 0, 0, 0, 0, .1, .2, .3, .4, .5]))


# -----------------------
def decorate_roof_triangular(obj, options=Map()):
    settings = options.options

    material = Blocks.match(settings.roof_material)
    if material:
        obj.material = material

    p1, p2, radius, ends, sides = vg.best_points_for_triangular_roof(options.corner_vectors)
    chop_pct = settings.roof_triangular_chop_pct or 0

    radius += settings.roof_triangular_overhang

    height = radius
    if round(height) == int(height):
        height += 1

    if settings.roof_triangular_stairs or settings.roof_triangular_end_cap_in:
        # It's a more complex roof, build it as a Feature
        roof_lists = vg.prism_roof(p1, p2, height=height, radius=radius, chop_pct=chop_pct,
                                   sloped=settings.roof_triangular_sloped, material=obj.material,
                                   endpoint_out=settings.roof_triangular_end_cap_out)

        obj.features.append(Feature("roof", p1, Map(block_lists=roof_lists)))

    else:
        # Nothing fancy, color each block all the same type
        roof = vg.triangular_prism(p1, p2, height=height, radius=radius, chop_pct=chop_pct,
                                   sloped=settings.roof_triangular_sloped)
        obj.points.update(roof)

    obj.points_edges = []

    return obj


# -----------------------
init()
Decoration.Decoration(kind="roof_triangular", callback=decorate_roof_triangular, namespace=file_name,
                      variables=variables, materials=materials)
