#############################################################################################################
# Procedural Building voxel drawing functions for MineCraft.  
##############################################################################################################

import mcpi
import math
import numpy as np
from Map import Map

def get_seed():
    # TODO: Return the world seed, add in x,y,z
    return np.random.randint(65000)

def init_with_seed(seed):
    np.random.seed(seed)

def point_along_circle(center, radius, points, num, options=False):
    if not options:
        options = Map()

    if not options.direction:
        options.direction = "y"

    if not options.precision:
        options.precision = 1

    # If aiming to have a 17x17 building (center + 8 in both directions),
    #   set r=8 and multiply so that the radius entered is 11.3
    #   also rotate everything by 1/8th to that sides aren't diagonal
    if options.align_to_cells:
        radius *= 1.4125;
        if not options.rotation:
            options.rotation = 0.125

    if not options.rotation:
        options.rotation = 0

    #find the angle 
    theta = (options.rotation + (num/points)) * 2 * math.pi

    if options.direction is "y":
        x = center.x + (radius * math.cos(theta))
        y = center.y
        z = center.z + (radius * math.sin(theta))

    return mcpi.vec3.Vec3(round(x,options.precision), round(y,options.precision), round(z,options.precision))