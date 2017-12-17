#############################################################################################################
# Procedural Building creation functions for MineCraft.  Uses mcpi to connect to RaspberryJuice on SpigotMC
##############################################################################################################
import mcpi
import mcpi.block as block
import MinecraftHelpers as helpers
import VoxelGraphics as vg
import numpy as np
from Map import Map
from V3 import V3


# -----------------------
# Polygon helper class to store, build, and create blocks
class Farmzone(object):
    def __init__(self, p1, p2, options=Map()):
        self.crop = options.crop or np.random.choice(["cane", "wheat", "carrot", "potato", "cactus"])
        self.blocks = []

        rim, inner_rec = vg.rectangle(p1, p2)
        for block in rim + inner_rec:
            if not block in self.blocks and type(block) == V3:
                self.blocks.append(block)

        self.center = V3(round(abs(p2.x + p1.x) / 2), p1.y, round(abs(p2.z + p1.z) / 2))

    def build(self):
        for i, vec in enumerate(self.blocks):
            if self.crop == "cane":
                if (vec.x % 3) == 0:
                    helpers.create_block(vec, block.WATER.id)
                else:
                    helpers.create_block(vec, block.DIRT.id)
            elif self.crop == "cactus":
                if ((vec.x + vec.z) % 2) == 0:
                    helpers.create_block(vec, block.AIR.id)
                else:
                    helpers.create_block(vec, block.SAND.id)
            else:
                # All other types of crops
                if vec == self.center:
                    helpers.create_block(vec, block.WATER.id)
                    plus2 = vg.up(vec, 3)
                    helpers.create_block(plus2, block.GLOWSTONE_BLOCK.id)
                    for v2 in vg.next_to(plus2):
                        helpers.create_block(v2.point, block.TORCH.id, v2.dir)
                else:
                    helpers.create_block(vec, block.FARMLAND.id)

        if self.crop == "cane":
            for i, vec in enumerate(self.blocks):
                if not (vec.x % 3) == 0:
                    canes = np.random.randint(1, 4)
                    helpers.create_block(vg.up(vec), block.SUGAR_CANE.id)
                    if canes > 1: helpers.create_block(vg.up(vec, 2), block.SUGAR_CANE.id)
                    if canes > 2: helpers.create_block(vg.up(vec, 3), block.SUGAR_CANE.id)
        elif self.crop == "cactus":
            for i, vec in enumerate(self.blocks):
                if ((vec.x + vec.z) % 2) == 1:
                    helpers.create_block(vec, block.SAND.id)
                    cacs = np.random.randint(1, 4)
                    helpers.create_block(vg.up(vec), block.CACTUS.id)
                    if cacs > 1: helpers.create_block(vg.up(vec, 2), block.CACTUS.id)
                    if cacs > 2: helpers.create_block(vg.up(vec, 3), block.CACTUS.id)
        elif self.crop == "wheat":
            for i, vec in enumerate(self.blocks):
                if not vec == self.center:
                    helpers.create_block(vg.up(vec), 59, np.random.randint(0, 8))
        elif self.crop == "carrot":
            for i, vec in enumerate(self.blocks):
                if not vec == self.center:
                    helpers.create_block(vg.up(vec), 141, np.random.randint(0, 8))
        elif self.crop == "potato":
            for i, vec in enumerate(self.blocks):
                if not vec == self.center:
                    helpers.create_block(vg.up(vec), 142, np.random.randint(0, 8))

    def clear(self):
        for i, vec in enumerate(self.blocks):
            helpers.create_block(vec, block.GRASS.id)
            if vec == self.center:
                plus2 = vg.up(vec, 3)
                for v2 in vg.next_to(plus2):
                    helpers.create_block(v2.point, block.AIR.id)
                helpers.create_block(plus2, block.AIR.id)

        if self.crop in ["cane", "cactus"]:
            for p1 in self.blocks:
                helpers.create_block(vg.up(p1), block.AIR.id)
                helpers.create_block(vg.up(p1, 2), block.AIR.id)
                helpers.create_block(vg.up(p1, 3), block.AIR.id)
        elif self.crop in ["wheat", "carrot", "potato"]:
            for i, p1 in enumerate(self.blocks):
                if not vec == self.center:
                    helpers.create_block(vg.up(p1), block.AIR.id)


# -----------------------
# Polygon helper class to store, build, and create blocks
class Farmzones(object):
    def __init__(self, zones, options=Map()):
        self.farms = []

        for part in zones:
            # p1, p2 = vg.rectangle_inner(part.p1, part.p2, 1)
            self.farms.append(Farmzone(part.p1, part.p2))

    def build(self):
        for farm in self.farms:
            farm.build()

    def clear(self):
        for farm in self.farms:
            farm.clear()
