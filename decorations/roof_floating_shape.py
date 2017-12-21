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
    variables.append(Map(var="roof_shape_floating", choices=[False, False, True]))
    variables.append(Map(var="roof_shape_tight", choices=[.4, .5, .6, .7, .7, .8, .9]))
    variables.append(Map(var="roof_shape_height_multiplier", choices=[.5, .8, 1, 1.3, 1.5, 2, 2.5, 3]))
    variables.append(Map(var="roof_shape_color_pattern", choices=["RainbowGlass", "OldStoneWall", "WoodBlends"]))
    variables.append(Map(var="roof_shape_object", choices=["sphere"])) #, "cone", "cylinder", "box"]))


# -----------------------
def decorate_roof_shape(obj, options=Map()):
    settings = options.options

    if settings.roof_shape_color_pattern == "RainbowGlass":
        material = Texture1D.COMMON_TEXTURES.RainbowGlass
    elif settings.roof_shape_color_pattern == "OldStoneWall":
        material = Texture1D.COMMON_TEXTURES.OldStoneWall
    elif settings.roof_shape_color_pattern == "WoodBlends":
        material = Texture1D.COMMON_TEXTURES.WoodBlends
    elif settings.roof_shape_color_pattern == "Glow":  # TODO: Glow not working
        material = Texture1D.COMMON_TEXTURES.Glow
    else:
        material = Blocks.match(settings.roof_material)

    if not material:
        material = obj.material

    boundaries = vg.bounds(options.corner_vectors)

    min_radius = min(boundaries.x_radius, boundaries.z_radius)

    if settings.roof_shape_object == "cylinder":
        func = vg.cylinder
        height = min_radius * (settings.roof_shape_height_multiplier or 1)
    elif settings.roof_shape_object == "cone":
        func = vg.cone
        height = min_radius * (settings.roof_shape_height_multiplier or 1)
    elif settings.roof_shape_object == "box":
        func = vg.box
        height = min_radius * (settings.roof_shape_height_multiplier or 1)

    else:  # sphere
        func = vg.sphere
        height = None

    if settings.roof_shape_floating:
        sides = func(vg.up(boundaries.center, min_radius), min_radius, tight=settings.roof_shape_tight, height=height)
    else:
        sides = func(boundaries.center, min_radius, tight=settings.roof_shape_tight, height=height, options=Map(min_y_pct=.5))

    roof_lists = list()
    roof_lists.append(Map(blocks=sides, material=material))
    obj.features.append(Feature("roof", boundaries.center, Map(block_lists=roof_lists)))

    obj.points_edges = []
    return obj


# -----------------------
init()
Decoration.Decoration(kind="roof_floating_shape", callback=decorate_roof_shape, namespace=file_name,
                      variables=variables, materials=materials)
