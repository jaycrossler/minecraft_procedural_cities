#############################################################################################################
# Procedural Building voxel drawing functions for MineCraft.
##############################################################################################################

import math
import mcpi.block as block
import numpy as np
import VoxelGraphics as vg
from Map import Map
import MinecraftHelpers as helpers
from V3 import *

#-----------------------
# Polygon helper class to store, build, and create blocks
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
            self.blocks.append(Map(pos=V3(pos.x, pos.y+1, pos.z), id=block.DOOR_WOOD.id, data=8))
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
        return "Feature: " + self.kind + " with " + str(len(self.blocks)) +" blocks"

#-----------------------
def random_options(options=Map()):
    if not options.windows:
        options.windows = np.random.choice(["window_line_double", "window_line", "window_slits"])
    if not options.roof:
        options.roof = np.random.choice(["pointy", "pointy_lines", "battlement", False])
    if not options.material:
        options.color_scheme = r = np.random.choice(["gold_white", "grey_iron", "grey_stone", "blue_white"])
        if r == "gold_white":
            options.material=block.WOOL.id
            options.material_edges=block.GOLD_BLOCK.id
        elif r == "grey_iron":
            options.material=block.STONE_BRICK.id
            options.material_edges=block.IRON_BLOCK.id
        elif r == "grey_stone":
            options.material=block.STONE_SLAB_DOUBLE.id
            options.material_edges=block.IRON_BLOCK.id
        elif r == "blue_white":
            options.material=block.WOOL.id
            options.material_edges=block.LAPIS_LAZULI_BLOCK.id
        elif r == "brown":
            options.material=block.SAND.id
            options.material_edges=block.SANDSTONE.id
    if not options.roof_pointy_height:
        options.roof_pointy_height = round(np.random.random()*(options.radius or 5)*3)
    if not options.roof_battlement_height:
        options.roof_battlement_height = np.random.choice([1,2,3]) #TODO: Have it go straight up
    if not options.roof_battlement_space:
        options.roof_battlement_space = np.random.choice([1,2,3])
    if not options.door_inside:
        options.door_inside = np.random.choice([True,False])
    if not options.outside:
        options.outside = np.random.choice(["flowers","trees","grass","fence",False])

    return options

#-----------------------
def building_poly_styler(obj, kind, options=Map()):

    if kind=="wall":
        return building_poly_styler_wall(obj, options)
    elif kind=="roof":
        return building_poly_styler_roof(obj, options)
    elif kind=="castle_outer_wall":
        return building_poly_styler_castle_outer_wall(obj, options)
    elif kind=="castle_wall_tower":
        return building_poly_styler_castle_wall_tower(obj, options)

# -----------------------
def building_styler(obj, options=Map()):
    #TODO: Move these create blocks to add a Feature or BuildingFeature
    if options.outside and options.p1 and options.p2:
        p1, p2 = vg.rectangle_inner(options.p1, options.p2, -1)
        rec, none = vg.rectangle(p1, p2)
        material = False
        if options.outside == "flowers":
            for i,v in enumerate(rec):
                material = block.FLOWER_YELLOW.id if (i%2)==0 else block.FLOWER_CYAN.id
                helpers.create_block(v,material)
        elif options.outside == "trees":
            for i,v in enumerate(rec):
                if (i%3)==0:
                    helpers.create_block(v,block.SAPLING.id)
        elif options.outside == "grass":
            for i,v in enumerate(rec):
                if (i%2)==0:
                    helpers.create_block(v,block.GRASS_TALL.id)
        elif options.outside == "fence":
            for i,v in enumerate(rec):
                helpers.create_block(v,block.FENCE.id)
    return obj



# -----------------------
def building_poly_styler_roof(obj, options=Map()):
    if options.options.roof and str.startswith(options.options.roof, "pointy"):
        height = options.options.roof_pointy_height or options.radius
        pointy = V3(options.center.x, options.center.y+options.height+height, options.center.z)

        for i,vec in enumerate(options.corner_vectors):
            roof_line = vg.getLine(vec.x, vec.y+1, vec.z, pointy.x, pointy.y+1, pointy.z)
            obj.points_edges += roof_line

            if not options.options.roof == "pointy_lines":
                next_roof_point = options.corner_vectors[(i+1)%len(options.corner_vectors)]

                #Triangle to pointy face
                triangle_face = [vec, pointy, next_roof_point]
                roof_face = vg.unique_points(vg.getFace([V3(v.x, v.y+1, v.z) for v in triangle_face]))
                obj.points = obj.points.union(roof_face)

    if options.options.roof and str.startswith(options.options.roof, "battlement"):
        height = options.options.roof_battlement_height or 1
        spacing = options.options.roof_battlement_space or 2

        for i,vec in enumerate(options.corner_vectors):
            next_roof_point = options.corner_vectors[(i+1)%len(options.corner_vectors)]
            #TODO: Add X,Z outward from center as option
            roof_line = vg.getLine(vec.x, vec.y+height, vec.z, next_roof_point.x, next_roof_point.y+height, next_roof_point.z)

            obj.points = obj.points.union(vg.points_spaced(roof_line, Map(every=spacing)))

    return obj


# -----------------------
def building_poly_styler_wall(obj, options):

    if options.options.windows == "window_line":
        spaced_points = vg.extrude(obj.bottom(), Map(spacing = V3(0,math.ceil(obj.height/2),0)))
        for vec in spaced_points:
            obj.features.append(Feature("window", vec))

    elif options.options.windows == "window_line_double":
        spaced_points = vg.extrude(obj.bottom(), Map(spacing = V3(0,math.ceil(obj.height/2),0)))
        spaced_points2 = vg.extrude(spaced_points, Map(spacing = V3(0,1,0)))
        for vec in spaced_points+spaced_points2:
            obj.features.append(Feature("window", vec))

    elif options.options.windows == "window_slits":
        spaced_points = vg.points_spaced(obj.bottom(), Map(every=3))
        spaced_points = vg.extrude(spaced_points, Map(spacing = V3(0,math.ceil(obj.height/2),0)))
        spaced_points2 = vg.extrude(spaced_points, Map(spacing = V3(0,1,0)))
        for vec in spaced_points+spaced_points2:
            obj.features.append(Feature("spacing", vec))

    else:
        spaced_points = vg.points_spaced(obj.bottom(), Map(every=3))
        spaced_points = vg.extrude(spaced_points, Map(spacing = V3(0,math.ceil(obj.height/2),0)))
        for vec in spaced_points:
            obj.features.append(Feature("window", vec))


    mid_points = vg.middle_of_line(obj.bottom(), Map(center=True, max_width=2, point_per=10))
    for vec in mid_points:
        obj.features.append(Feature("door", vec, Map(cardinality=obj.cardinality, door_inside=options.options.door_inside)))

    return obj

# -----------------------
def building_poly_styler_castle_outer_wall(obj, options):

    height = options.options.roof_battlement_height or 1
    spacing = options.options.roof_battlement_space or 2

    #TODO: Add in inner and outer, create walkway and arrow slits

    #TODO: Add X,Z outward from center as option
    roof_line = vg.getLine(options.p1.x, options.p1.y+height, options.p1.z, options.p2.x, options.p2.y+height, options.p2.z)
    obj.points.extend(vg.points_spaced(roof_line, Map(every=spacing)))

    mid_points = vg.middle_of_line(obj.bottom(), Map(center=True, max_width=2, point_per=10))
    for vec in mid_points:
        obj.features.append(Feature("door", vec, Map(cardinality=obj.cardinality, door_inside=options.options.door_inside)))

    return obj

# -----------------------
def building_poly_styler_castle_wall_tower(obj, options):

    height = options.options.roof_battlement_height or 1
    spacing = options.options.roof_battlement_space or 2

    #TODO: Add in battlements, wood roof, stairway, torches

    return obj
