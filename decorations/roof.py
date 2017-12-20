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
    variables.append(Map(var="roof", choices=["triangular" ,"triangular","triangular","triangular", "pointy", "pointy_lines", "battlement", False]))
    variables.append(Map(var="roof_battlement_height", choices=[1, 2, 3]))
    variables.append(Map(var="roof_triangular_sloped", choices=[-2, -1, -.5, -.25, 0, 0, 0, .25, .5, 1, 2]))
    variables.append(Map(var="roof_triangular_stairs", choices=[True, False]))
    variables.append(Map(var="roof_triangular_end_cap_out", choices=[0, 1, 2, 2, 3]))
    variables.append(Map(var="roof_triangular_overhang", choices=[0, 0, 0, 1, 2]))
    variables.append(Map(var="roof_triangular_chop_pct", choices=[0])) #, 0, 0, 0, 0, .1, .2, .3, .4, .5]))
    variables.append(Map(var="roof_battlement_space", choices=[1, 2, 3]))
    variables.append(Map(var="roof_pointy_multiplier", choices=[0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.5]))
    variables.append(Map(var="roof_material",
                         choices=["Oak Wood", "Cobblestone", "Brick", "Stone Brick", "Nether Brick", "Sandstone",
                                  "Spruce Wood", "Birch Wood", "Jungle Wood", "Quartz", "Acacia Wood", "Dark Oak Wood",
                                  "Red Sandstone", "Purpur"]))

# -----------------------
def decorate_roof(obj, options=Map()):
    settings = options.options
    if not settings.roof:
        return obj

    material = Blocks.match(settings.roof_material)
    if material:
        obj.material = material

    if str.startswith(settings.roof, "pointy"):
        height = settings.roof_pointy_multiplier * options.radius
        pointy = V3(options.center.x, options.center.y + options.height + height, options.center.z)

        for i, vec in enumerate(options.corner_vectors):
            roof_line = vg.getLine(vec.x, vec.y + 1, vec.z, pointy.x, pointy.y + 1, pointy.z)
            obj.points_edges += roof_line

            if not settings.roof == "pointy_lines":
                next_roof_point = options.corner_vectors[(i + 1) % len(options.corner_vectors)]

                # Triangle to pointy face
                triangle_face = [vec, pointy, next_roof_point]
                roof_face = vg.unique_points(vg.getFace([V3(v.x, v.y + 1, v.z) for v in triangle_face]))
                obj.points = obj.points.union(roof_face)

    elif str.startswith(settings.roof, "triangular"):
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
    elif str.startswith(settings.roof, "battlement"):
        height = settings.roof_battlement_height or 1
        spacing = settings.roof_battlement_space or 2

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
