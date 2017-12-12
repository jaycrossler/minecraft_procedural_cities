from Map import Map
import MinecraftHelpers as helpers
import mcpi.block as block
from V3 import *


# -----------------------
# Polygon helper class to store, build, and create features such as windows or doors

class Feature(object):
    def __init__(self, kind, pos, options=Map()):
        self.kind = kind
        self.pos = pos
        self.facing = options.facing
        self.cardinality = options.cardinality
        self.blocks = []
        self.blocks_to_not_draw = []

        if kind == "door":
            if options.door_inside:
                door_pattern = "swne"
            else:
                door_pattern = "nesw"
            door_code = door_pattern.index(options.cardinality[-1:])
            self.blocks.append(Map(pos=V3(pos.x, pos.y, pos.z), id=block.DOOR_WOOD.id, data=door_code))
            self.blocks.append(Map(pos=V3(pos.x, pos.y + 1, pos.z), id=block.DOOR_WOOD.id, data=8))
            # self.blocks_to_not_draw.append(V3(pos.x, pos.y+1, pos.z))
        elif kind == "window":
            self.blocks.append(Map(pos=pos, id=block.GLASS_PANE.id, data=1))
        elif kind == "bed":
            self.blocks.append(Map(pos=pos, id=block.BED.id))
        elif kind == "spacing":
            self.blocks.append(Map(pos=pos, id=block.AIR.id))

    def draw(self):
        for item in self.blocks:
            helpers.create_block(item.pos, item.id, item.data)

    def clear(self):
        for item in self.blocks:
            helpers.create_block(item.pos, block.AIR.id)

    def info(self):
        return "Feature: " + self.kind + " with " + str(len(self.blocks)) + " blocks"
