import Decoration
from Map import Map
import Blocks
import VoxelGraphics as vg
from Feature import Feature
import numpy as np
from MinecraftHelpers import flatten_list_of_lists

import sys

file_name = sys.argv[0][::-1][3:][::-1]
variables = []
materials = []


def init():
    variables.append(Map(var="outside", choices=["flowers", "trees", "grass", "fence", None, None]))


# -----------------------
def decorate_outside(obj, options=Map()):

    obj.points = []
    obj.points_edges = []
    obj.material_clear = Blocks.AIR

    border = flatten_list_of_lists([vg.get_line_from_points(l[0], l[1]) for l in options.lines])

    if options.options.outside == "flowers":
        flowers_1 = []
        flowers_2 = []
        for i, b in enumerate(border):
            # TODO: Refactor to have multiple numbers of flowers

            if (i % 2) == 0:
                flowers_1.append(b)
            else:
                flowers_2.append(b)

        colors = Blocks.kind("Flower")
        np.random.shuffle(colors)

        obj.features.append(Feature("flowers", flowers_1, Map(material=colors[0])))
        obj.features.append(Feature("flowers", flowers_2, Map(material=colors[1])))

    elif options.options.outside == "trees":
        trees = []
        for i, b in enumerate(border):
            if (i % 3) == 0:
                trees.append(b)

        colors = Blocks.kind("Sapling")
        np.random.shuffle(colors)

        obj.features.append(Feature("flowers", trees, Map(material=colors[0])))

    elif options.options.outside == "grass":
        trees = []
        for i, b in enumerate(border):
            if (i % 3) == 0:
                trees.append(b)

        obj.features.append(Feature("flowers", trees, Map(material=Blocks.DOUBLETALLGRASS)))

    elif options.options.outside == "fence":
        fence_type = np.random.random_integers(188, 192)
        obj.features.append(Feature("fence", border, Map(material=fence_type)))

    return obj


# -----------------------
init()
Decoration.Decoration(kind="garden", callback=decorate_outside, namespace=file_name, variables=variables,
                      materials=materials)
