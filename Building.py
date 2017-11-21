#############################################################################################################
# Procedural Building creation functions for MineCraft.  Uses mcpi to connect to RaspberryJuice on SpigotMC
# Import via python command line:
#   exec(open("Building.py").read())
# Usage:
#   b = Building()
#   b.build()
# or
#   options = Map(name="Mansion", height=20, radius=5, sides=6)
#   b = Building(V3(42,0,42), options)
#   b.build
#
#   TODO: Pointy roof drawing weird on one axis
#
# Test Buildings:
#   b = Building(False, Map(sides=4, height=7, radius=6, windows="window_line_double", roof="pointy"))
#   b = Building(False, Map(sides=6, height=5, radius=8, windows="window_line", roof="pointy_lines", material=block.WOOL.id, material_edges=block.GOLD_BLOCK.id))
##############################################################################################################
import mcpi
import mcpi.block as block
import math
import MinecraftHelpers as helpers
import VoxelGraphics as vg
from Map import Map
from V3 import V3

helpers.connect()

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
        if kind == "window":
            self.blocks.append(Map(pos=pos, id=block.GLASS_PANE.id, data=1))
        if kind == "bed":
            self.blocks.append(Map(pos=pos, id=block.BED.id))
    
    def draw(self):
        for item in self.blocks:
            helpers.create_block(item.pos, item.id, item.data)

    def clear(self):
        for item in self.blocks:
            helpers.create_block(item.pos, block.AIR.id)

    def info(self):
        return "Feature: " + self.kind + " with " + str(len(self.blocks)) +" blocks"

#-----------------------
# Polygon helper class to store, build, and create blocks
class BuildingPoly(object):
    def __init__(self, kind, vertices, options=Map()):
        self.kind = kind
        self.vertices = vertices
        self.facing = options.facing
        self.material = options.material
        self.material_edges = options.material_edges
        self.height = vg.highest(vertices) - vg.lowest(vertices) + 1
        self.cardinality = options.cardinality
        self.features = []
        self.points = vg.unique_points(vg.getFace(self.vertices))
        self.points_edges = vg.poly_point_edges(self.points)

        if kind=="wall":
            if options.options.windows == "window_line":
                spaced_points = vg.extrude(self.bottom(), Map(space_y = math.ceil(self.height/2)))
                for vec in spaced_points:
                    self.features.append(Feature("window", vec))

            elif options.options.windows == "window_line_double":
                spaced_points = vg.extrude(self.bottom(), Map(space_y = math.floor(self.height/2)))
                spaced_points2 = vg.extrude(spaced_points, Map(space_y = 1))
                for vec in spaced_points+spaced_points2:
                    self.features.append(Feature("window", vec))

            else:
                spaced_points = vg.points_spaced(self.bottom(), Map(every=3))
                spaced_points = vg.extrude(spaced_points, Map(space_y = math.ceil(self.height/2)))
                for vec in spaced_points:
                    self.features.append(Feature("window", vec))

            mid_points = vg.middle_of_line(self.bottom(), Map(center=True, max_width=2, point_per=10))
            for vec in mid_points:
                self.features.append(Feature("door", vec, Map(cardinality=self.cardinality, door_inside=options.options.door_inside)))

        if kind=="roof":
            if str.startswith(options.options.roof, "pointy"):
                height = options.options.roof_pointy_height or options.radius
                pointy = V3(options.center.x, options.center.y+options.height+height, options.center.z)

                for i,vec in enumerate(options.corner_vectors):
                    roof_line = vg.getLine(vec.x, vec.y+1, vec.z, pointy.x, pointy.y+1, pointy.z)
                    self.points_edges += roof_line

                    if not options.options.roof == "pointy_lines":
                        next_roof_point = options.corner_vectors[(i+1)%len(options.corner_vectors)]

                        #Triangle to pointy face
                        triangle_face = [vec, pointy, next_roof_point]
                        roof_face = vg.unique_points(vg.getFace([V3(v.x, v.y+1, v.z) for v in triangle_face])) 
                        self.points = self.points.union(roof_face)

    
    def draw(self):
        # helpers.create_block_filled_box(self.pos1, self.pos2, self.material)
        blocks_to_not_draw = []
        for feature in self.features:
            blocks_to_not_draw += feature.blocks_to_not_draw;

        helpers.create_blocks_from_pointlist(self.points, self.material, blocks_to_not_draw=blocks_to_not_draw)
        if self.material_edges:
            helpers.create_blocks_from_pointlist(self.points_edges, self.material_edges, blocks_to_not_draw=blocks_to_not_draw)

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

    def info(self):
        stro = []
        stro.append(" - Polygon: " + self.kind + " with " + str(self.vertices) + " points, height " + str(self.height) + ", and " +str(len(self.points)) +" blocks")
        for f in self.features:
            stro.append("  -- " + f.info())
        return stro

#-----------------------
# Main class for creating a building along with settings
class Building(object):    

    def __init__(self, pos=False, options=Map()):
        if not helpers.mc:
            helpers.mc = helpers.connect()

        self.seed = options.seed or vg.get_seed()
        vg.init_with_seed(self.seed)

        #If position isn't set, use the player position
        if pos is False:
            pos = helpers.my_tile_pos()
        
        #If "force_height" not passed in as an option, then pick height of the terrain at the x,z point
        # if not options.force_height:
        #     setattr(pos, "y", helpers.get_height(pos))

        self.options = options
        self.center = V3(pos.x, pos.y, pos.z)

        self.x = pos.x
        self.y = pos.y
        self.z = pos.z
        self.biome = "Plains" #TODO: options.biome or helpers.biome_at(pos)
        self.biome = self.biome.title() #Title-cases biome, PLAINS becomes Plains

        self.height = options.height or vg.rand_in_range(4,9)
        self.radius = options.radius or vg.rand_in_range(4,10)
        self.sides = options.sides or 4
        self.corner_vectors = []

        self.material = options.material or block.STONE.id #TODO: Change based on biome, have rand list
        self.material_edges = options.material_edges or block.IRON_BLOCK.id #TODO: Change based on biome, have rand list
        
        self.name = options.name or self.biome + " house"
        self.polys = self.create_polys(options)


    def build(self):
        for poly in self.polys:
            poly.draw()

    def clear(self):
        for poly in self.polys:
            poly.clear()

    def data(self):
        #TODO: Find how to return this as an iterable data object
        d = Map()
        d.center = self.center
        d.biome = self.biome
        d.height = self.height
        d.radius = self.radius
        d.sides = self.sides
        d.material = self.material
        d.material_edges = self.material_edges
        d.name = self.name
        d.options = self.options
        return d

    def info(self, show=True):
        stro = ["Building with " + str(self.sides) + " sides and height " + str(self.height)]
        for p in self.polys:
            stro += p.info()

        if show:
            for s in stro:
                print (s)
        else:
            return stro

    def create_polys(self, options):

        h = self.height
        polys = []
        data_so_far = self.data()

        sides = data_so_far.sides or 4

        corner_vectors = []
        for i in range(0, sides):
            p1 = vg.point_along_circle(self.center, self.radius, sides, i, Map(align_to_cells=True))
            p2 = vg.point_along_circle(self.center, self.radius, sides, i+1, Map(align_to_cells=True))
            corner_vectors.append(p1)

            facing = "front" if i == 1 else "side"
            vertices = [p1, p2, V3(p2.x, p2.y+h, p2.z), V3(p1.x, p1.y+h, p1.z)] # 4 points straight up
            c = vg.cardinality(p1,p2)
            p = BuildingPoly('wall', vertices, data_so_far.copy(facing=facing, cardinality=c))
            polys.append(p)

        roof_vectors = [V3(v.x, v.y+h, v.z) for v in corner_vectors]
        polys.append(BuildingPoly("roof", roof_vectors, data_so_far.copy(corner_vectors = roof_vectors)))
        polys.insert(0,BuildingPoly("foundation", [V3(v.x, v.y-1, v.z) for v in corner_vectors], data_so_far.copy(corner_vectors = corner_vectors))) #add to be drawn first

        self.corner_vectors = corner_vectors

        return polys

# Recreate the building with same settings and latest rendering code
def NewB(building):
    options = building.data()
    newb = Building(options["center"], options)
    building.clear()
    newb.build()
    return newb




