import Decoration
from Map import Map
import Blocks

import sys

file_name = sys.argv[0][::-1][3:][::-1]
variables = []
materials = []


def init():
    variables.append(Map(var="color_scheme", choices=["gold_white", "grey_iron", "grey_stone", "blue_white"]))


def colorize(obj, options):
    # TODO: Move to a materials manager for overall color schemes
    r = options.options.color_scheme

    if not options.options.material:
        if r == "gold_white":
            obj.material = Blocks.WHITEWOOL
            obj.material_edges = Blocks.GOLDBLOCK
        elif r == "grey_iron":
            obj.material = Blocks.STONEBRICKS
            obj.material_edges = Blocks.IRONBLOCK
        elif r == "grey_stone":
            obj.material = Blocks.DOUBLESTONESLAB
            obj.material_edges = Blocks.IRONBLOCK
        elif r == "blue_white":
            obj.material = Blocks.WHITEWOOL
            obj.material_edges = Blocks.LAPISLAZULIBLOCK
        elif r == "brown":
            obj.material = Blocks.SAND
            obj.material_edges = Blocks.SANDSTONE
    return obj

init()
Decoration.Decoration(kind="colorize", callback=colorize, namespace=file_name, variables=variables,
                      materials=materials)
