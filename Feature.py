from Map import Map
import MinecraftHelpers as helpers
import mcpi.block as block
from V3 import *
import VoxelGraphics as vg
import Texture1D


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
            self.blocks.append(Map(pos=pos, id=block.DOOR_WOOD.id, data=door_code))
            self.blocks.append(Map(pos=vg.up(pos), id=block.DOOR_WOOD.id, data=8))
            # self.blocks_to_not_draw.append(V3(pos.x, pos.y+1, pos.z))
        elif kind == "window":
            if options.window_style == "glass random":
                self.blocks.append(Map(pos=pos, id=block.GLASS_PANE.id, data=1))

            elif options.window_style == "open_slit_and_above" and options.windows not in ["window_line", "window_line_double"]:
                self.blocks.append(Map(pos=vg.up(pos), id=44, data=13))
                self.blocks.append(Map(pos=pos, id=44, data=5))
                around = vg.points_around([pos, vg.up(pos)])
                for b in around:
                    self.blocks.append(Map(pos=b, id=block.STONE.id))

            else:
                self.blocks.append(Map(pos=pos, id=block.GLASS_PANE.id, data=1))

        elif kind == "bed":
            self.blocks.append(Map(pos=pos, id=block.BED.id))  # TODO: Add 2 beds or 4 beds with spacing

        elif kind == "spacing":
            self.add_blocks(pos, block.AIR.id)
        elif kind == "flowers":
            self.add_blocks(pos, options.material)
        elif kind == "fence":
            self.add_blocks(pos, options.material)
        elif kind == "roof":
            for block_list in options.block_lists:
                self.add_blocks(block_list.blocks, block_list.material)

    def add_blocks(self, blocks, material):
        if type(blocks) is list:
            for b in blocks:
                self.blocks.append(Map(pos=b, id=material))
        else:
            self.blocks.append(Map(pos=blocks, id=material))

    def draw(self):
        for i, item in enumerate(self.blocks):
            if i == 0 and type(item.id) == Texture1D.Texture1D:
                item.id.reset_between_objects()

                if not item.id.options.bounds:
                    item.id.options.bounds = vg.bounds(self.blocks)

                # TODO: This won't reset Texture Gradients if there are multiple per Feature

            helpers.create_block(item.pos, item.id, item.data)

    def clear(self):
        for item in self.blocks:
            helpers.create_block(item.pos, block.AIR.id)

    def __str__(self):
        return "-- Feature of kind " + str(self.kind) + " with " + str(len(self.blocks)) + " blocks"

    def __repr__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))

        return ', '.join(sb)