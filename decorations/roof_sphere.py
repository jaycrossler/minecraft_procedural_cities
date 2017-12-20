import Decoration
from Map import Map
import VoxelGraphics as vg
from V3 import V3
import Texture1D
from Feature import Feature
import Blocks

import sys

file_name = sys.argv[0][::-1][3:][::-1]
variables = []
materials = []


def init():
    variables.append(Map(var="roof_sphere_floating", choices=[False, False, True]))
    variables.append(Map(var="roof_sphere_tight", choices=[.4, .5, .6, .7, .7, .8, .9]))
    variables.append(Map(var="roof_sphere_color_pattern", choices=[False, False, "rainbow_glass"]))


# -----------------------
def decorate_roof_sphere(obj, options=Map()):
    settings = options.options
    # if settings.roof_sphere_color_pattern == "rainbow_glass":
    #     material = Texture1D.COMMON_TEXTURES.RainbowGlass
    # else:
    material = Blocks.match(settings.roof_material)

    if material:
        obj.material = material

    boundaries = vg.bounds(options.corner_vectors)

    min_radius = min(boundaries.x_radius, boundaries.z_radius) + 1

    if settings.roof_sphere_floating:
        sides = vg.sphere(vg.up(boundaries.center, min_radius), min_radius, tight=settings.roof_sphere_tight,
                          options=Map())

    else:
        sides = vg.sphere(boundaries.center, min_radius, tight=settings.roof_sphere_tight, options=Map(start_y_pct=.5))

    roof_lists = list()
    roof_lists.append(Map(blocks=sides, material=obj.material))
    obj.features.append(Feature("roof", boundaries.center, Map(block_lists=roof_lists)))

    obj.points_edges = []
    return obj


# -----------------------
init()
Decoration.Decoration(kind="roof_sphere", callback=decorate_roof_sphere, namespace=file_name,
                      variables=variables, materials=materials)
