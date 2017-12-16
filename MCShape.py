#############################################################################################################
# Procedural Building creation functions for MineCraft.  Uses mcpi to connect to RaspberryJuice on SpigotMC
##############################################################################################################
import MinecraftHelpers as helpers
import VoxelGraphics as vg
from Map import Map
import mcpi.block as block
import Decoration


# -----------------------
# Polygon helper class to store, build, and create blocks
class MCShape(object):
    def __init__(self, kind, vertices=None, options=Map()):
        if vertices is None:
            vertices = []
        self.kind = kind
        self.facing = options.facing
        self.material = options.material
        self.material_edges = options.material_edges  # TODO: Different colors for different edges
        self.features = []
        self.options = options
        self.vertices = options.vertices = vertices
        self.decorations = []
        self.points = []
        self.points_edges = []
        self.bottom_line = self.top_line = self.left_line = self.right_line = self.height = None

        # Build default points, vertices, and settings for every poly
        # these might get changed later with a styler (in decorate)

        self.decorations.append(Map(kind="colorize", options=options))

        if len(vertices) == 1:
            self.decorations.append(Map(kind="standing line", options=options))
        elif len(vertices) == 2:
            self.decorations.append(Map(kind="standing rectangle", options=options))
        else:
            self.decorations.append(Map(kind="flat rectangle", options=options))

        # Add a decoration based on what kind of shape
        self.decorations.append(Map(kind=kind, options=options))

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
        material = block.GRASS.id if self.kind == "foundation" else block.AIR.id
        helpers.draw_point_list(self.points, material)
        helpers.draw_point_list(self.points_edges, material)

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
        decorations_list = Decoration.get_matching_decorations(self.decorations)
        for d in decorations_list:
            self = d["callback"](self, d["options"])

    def __str__(self):
        return '- Shape within ' + str(vg.bounds(self.points)) + ', having ' + str(len(self.features)) + ' features'

    def __repr__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))

        return ', '.join(sb)
