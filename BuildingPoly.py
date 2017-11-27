#############################################################################################################
# Procedural Building creation functions for MineCraft.  Uses mcpi to connect to RaspberryJuice on SpigotMC
##############################################################################################################
import mcpi
import mcpi.block as block
import MinecraftHelpers as helpers
import VoxelGraphics as vg
import BuildingStyler as bs
from Map import Map
from V3 import V3

#-----------------------
# Polygon helper class to store, build, and create blocks
class BuildingPoly(object):
    def __init__(self, kind, vertices, options=Map()):
        self.kind = kind
        self.facing = options.facing
        self.material = options.material
        self.material_edges = options.material_edges #TODO: Different colors for different edges
        self.features = []

        if len(vertices) == 2:
            #If two points are given, assume it's for the bottom line, then draw that as a wall

            #TODO: Add width for the wall - how to add end lines to that?
            p1 = vertices[0]
            p2 = vertices[1]
            h = options.height or 5
            self.vertices = vertices_with_up = [p1, p2, vg.up(p2,h), vg.up(p1,h)] # points straight up
            self.height = options.height or (vg.highest(vertices_with_up) - vg.lowest(vertices_with_up) + 1)
            self.cardinality = vg.cardinality(p1,p2)
            self.points, self.top_line, self.bottom_line, self.left_line, self.right_line = vg.rectangular_face(p1, p2, h)
        else:
            #It's a non-y-rectangular-shaped polygon, so use a different getFace builder function
            self.vertices = vertices
            self.height = options.height or (vg.highest(vertices) - vg.lowest(vertices) + 1)
            self.cardinality = options.cardinality
            self.points = vg.unique_points(vg.getFace(self.vertices))
            x, self.top_line, self.bottom_line, self.left_line, self.right_line = vg.poly_point_edges(self.points)

        self.points_edges = self.top_line + self.bottom_line + self.left_line + self.right_line

        #Style the polygon based on kind and options
        self = bs.building_poly_styler(self, kind, options)

    def draw(self):
        blocks_to_not_draw = []
        for feature in self.features:
            blocks_to_not_draw += feature.blocks_to_not_draw;

        helpers.create_blocks_from_pointlist(self.points, self.material, blocks_to_not_draw=blocks_to_not_draw)

    def draw_edges(self):
        blocks_to_not_draw = []
        for feature in self.features:
            blocks_to_not_draw += feature.blocks_to_not_draw;

        if self.material_edges:
            helpers.create_blocks_from_pointlist(self.points_edges, self.material_edges, blocks_to_not_draw=blocks_to_not_draw)

    def draw_features(self):
        for feature in self.features:
            feature.draw()

    def clear(self):
        material = block.GRASS.id if self.kind == "foundation" else block.AIR.id
        helpers.create_blocks_from_pointlist(self.points, material)
        helpers.create_blocks_from_pointlist(self.points_edges, material)
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

    #TODO: Inside and outside point?

    def info(self):
        stro = []
        stro.append(" - Polygon: " + self.kind + " with " + str(self.vertices) + " points, height " + str(self.height) + ", and " +str(len(self.points)) +" blocks")
        for f in self.features:
            stro.append("  -- " + f.info())
        return stro
