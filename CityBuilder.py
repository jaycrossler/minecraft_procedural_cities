#############################################################################################################
# Procedural Building creation functions for MineCraft.  Uses mcpi to connect to RaspberryJuice on SpigotMC
#
#   TODO: Pointy roof drawing weird on one axis
#   TODO: Have floors with each allowing different polylgon/size settings
#   TODO: Stairs or ladders between floors
#   TODO: Building cost to create building
#   TODO: Add a river running through town
#   TODO: Buildings and roads along terrain
#
##############################################################################################################
import Texture1D
from MCShape import MCShape
import mcpi.block as block
import Blocks

import MinecraftHelpers as helpers
import VoxelGraphics as vg
from Farmzones import Farmzones
from Castle import Castle, build_castle_streetmap
from Map import Map
from V3 import V3
from Building import Streets, Neighborhoods

from decorations import *

# import glob
# import importlib.util
# modules = glob.glob('decorations/*.py')
# for i, module in enumerate(modules):
#     spec = importlib.util.spec_from_file_location("decoration" + str(i), module)
#     foo = importlib.util.module_from_spec(spec)
#     spec.


helpers.connect()


# --------------------------------------------------------------------
# City Building
# --------------------------------------------------------------------

def city(size=0, layout="castle", farms=False, buildings=False, streets=True, castle=True):
    # Testing location numbers
    mid_point = V3(30, 0, 120)

    if size > 0:
        mid1 = V3(mid_point.x - size, mid_point.y, mid_point.z - size)
        mid2 = V3(mid_point.x + size, mid_point.y, mid_point.z + size)
    else:
        mid1, mid2 = V3(0, 0, 60), V3(50, 0, 110)

    print("Building zone and street-map using layout:", layout)
    if layout == "castle":
        all_zones = build_castle_streetmap(mid1, mid2, Map(min_x=min(size - 10, 60), min_z=min(size - 10, 60)))
    else:
        all_zones = vg.partition(mid1, mid2, Map(minx=7, minz=7))
    print("-", len(all_zones), "zones identified")

    farm_zones = []
    building_zones = []
    castle_zone = False

    # Sort zones
    for zone in all_zones:
        if zone.width < 8 or zone.depth < 8:
            farm_zones.append(zone)
        else:
            building_zones.append(zone)

    print("-", len(farm_zones), " farm zones identified")

    # Make the largest zone a castle
    if not castle_zone:
        largest = 0
        largest_index = -1
        for i, zone in enumerate(building_zones):
            size = (zone.width * zone.depth) + min(zone.width, zone.depth) ** 2
            if size > largest:
                largest = size
                largest_index = i
                castle_zone = zone
        building_zones.pop(largest_index)

    print("-", len(building_zones), " building zones identified")
    print("- Castle size", castle_zone.width, "width by", castle_zone.depth, "depth by", castle_zone.height, "height")

    # Turn zones into creations
    s = Streets(all_zones, Map(style="blacktop"))
    f = Farmzones(farm_zones)
    n = Neighborhoods(building_zones)
    c = Castle(options=castle_zone)

    z = [all_zones, farm_zones, building_zones, castle_zone]

    # Build the creations
    if streets: s.build()
    if farms: f.build()
    if buildings: n.build()
    if castle: c.build()

    class Temp:
        def __init__(self, s, f, n, c, z):
            self.s = s
            self.f = f
            self.n = n
            self.c = c
            self.zones = z

        def clear(self):
            self.s.clear()
            self.f.clear()
            self.n.clear()
            self.c.clear()

    return Temp(s=s, f=f, n=n, c=c, z=z)


def test_c():
    c = Castle(False, Map(p1=V3(0, -1, 90), p2=V3(59, -1, 149)))
    print("Building Castle")
    c.build()
    return c


if __name__ == "__main__":
    import time
    c = city(80)

    time.sleep(10)
    c.clear()
