#############################################################################################################
# Procedural Building creation functions for MineCraft.  Uses mcpi to connect to RaspberryJuice on SpigotMC
##############################################################################################################
import MinecraftHelpers as helpers
import VoxelGraphics as vg
from Map import Map
import Blocks
import Decoration


# -----------------------
# Polygon helper class to store, build, and create blocks
class MCShape(object):
    def __init__(self, decorations, vertices=None, options=Map()):
        if vertices is None:
            vertices = []
        self.facing = options.facing
        self.material = options.material
        self.material_edges = options.material_edges  # TODO: Different colors for different edges
        self.material_clear = Blocks.AIR
        self.features = []
        self.options = options
        self.vertices = options.vertices = vertices
        self.decorations = decorations
        self.points = []
        self.points_edges = []
        self.bottom_line = self.top_line = self.left_line = self.right_line = self.height = None

        self.decorations.insert(0, "colorize")

        # Style the polygon based on kind and options
        self.decorate()

    def draw(self):
        blocks_to_not_draw = []
        for feature in self.features:
            blocks_to_not_draw += feature.blocks_to_not_draw

        helpers.draw_point_list(self.points, self.material, options=Map(blocks_to_not_draw=blocks_to_not_draw))

    def draw_edges(self):
        blocks_to_not_draw = []
        for feature in self.features:
            blocks_to_not_draw += feature.blocks_to_not_draw

        if self.material_edges:
            helpers.draw_point_list(self.points_edges, self.material_edges,
                                    options=Map(blocks_to_not_draw=blocks_to_not_draw))

    def draw_features(self):
        for feature in self.features:
            feature.draw()

    def clear(self):
        helpers.draw_point_list(self.points, self.material_clear)
        helpers.draw_point_list(self.points_edges, self.material_clear)

        for feature in self.features:
            feature.clear()

    def bottom(self):
        if not hasattr(self, "bottom_line"):
            self.bottom_line = vg.points_along_poly(self.points, Map(side="bottom"))
        return self.bottom_line

    def top(self):
        if not hasattr(self, "top_line"):
            self.top_line = vg.points_along_poly(self.points, Map(side="top"))
        return self.top_line

    def left(self):
        if not hasattr(self, "left_line"):
            self.left_line = vg.points_along_poly(self.points, Map(side="left_x"))
        return self.left_line

    def right(self):
        if not hasattr(self, "right_line"):
            self.right_line = vg.points_along_poly(self.points, Map(side="right_x"))
        return self.right_line

    def decorate(self):
        for decoration in self.decorations:
            decs = [x for x in Decoration.DECORATIONS_LIBRARY if x["kind"].lower() == decoration.lower()]

            if len(decs) > 0:
                for d in decs:
                    self = d["callback"](self, self.options)
            else:
                print("UNKNOWN Decoration: " + str(decoration) + " on shape")

    def __str__(self):
        decs = "+".join(self.decorations[1:])
        return '- [' + decs + '] within ' + str(vg.bounds(self.points)) + ': ' + str(len(self.features)) + ' features'

    def __repr__(self):
        sb = []
        for key in self.__dict__:
            value = self.__dict__[key]
            if type(value) == list and len(value) > 1:
                value = "(" + str(value[0]) + "...)"
            sb.append("{key}='{value}'".format(key=key, value=value))

        return ', '.join(sb)
