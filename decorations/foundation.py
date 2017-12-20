import Decoration
from Map import Map
import Blocks
import VoxelGraphics as vg

import sys
file_name = sys.argv[0][::-1][3:][::-1]
variables = []
materials = []


def init():
    pass


# -----------------------
def decorate_foundation(obj, options=Map()):
    # TODO: FINISH
    return obj


# -----------------------
init()
Decoration.Decoration(kind="foundation", callback=decorate_foundation, namespace=file_name, variables=variables,
                      materials=materials)
