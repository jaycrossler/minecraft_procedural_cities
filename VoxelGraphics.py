#############################################################################################################
# Procedural Building voxel drawing functions for MineCraft.  
##############################################################################################################

# import mcpi
import math
import numpy as np
from Map import Map
# from mcpi.vec3 import Vec3 as point
import MinecraftHelpers as helpers
from numbers import Integral
from V3 import *

TO_RADIANS = pi / 180.
TO_DEGREES = 180. / pi
ICOS = [1,0,-1,0]
ISIN = [0,1,0,-1]


def get_seed():
    # TODO: Return the world seed, add in x,y,z
    return np.random.randint(65000)

def init_with_seed(seed):
    np.random.seed(seed)

def rand_in_range(min, max):
    return np.random.randint(min,max)

def point_along_circle(center, radius, points, num, options=Map()):
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
            options.rotation = 1 / (points*2) #TODO: Verify this works for hexagons

    if not options.rotation:
        options.rotation = 0

    #find the angle 
    theta = (options.rotation + (num/points)) * 2 * math.pi

    if options.direction is "y":
        x = center.x + (radius * math.cos(theta))
        y = center.y
        z = center.z + (radius * math.sin(theta))

    return V3(round(x,options.precision), round(y,options.precision), round(z,options.precision))

def vertices_rounded(points):
    # for i, v in enumerate(points):
    #     points[i] = v.ifloor()
    return points

def points_spaced(points, options=Map()):
    if not options.every:
        options.every = 1

    new_points = []

    if options.every == 1:
        new_points = points
    else:
        for i, vec in enumerate(points,1):
            if i % options.every == 0:
                new_points.append(vec)

    return new_points


def extrude(points, options=Map()):    
    if not options.space_x:
        options.space_x = 0
    if not options.space_y:
        options.space_y = 0
    if not options.space_z:
        options.space_z = 0

    new_points = []

    for i, vec in enumerate(points, 1):
        new_points.append(V3(vec.x + options.space_x, vec.y + options.space_y, vec.z + options.space_z))

    return new_points


def middle_of_line(points, options=Map()):
    #Map(center=true, max_width=2, point_per=10)
    if not options.point_per:
        options.point_per = 20
    if not options.max_width:
        options.max_width = 2
    if not options.min:
        options.min = 3

    point_count = len(points)
    num = 1
    new_points = []
    if options.center and point_count >= options.min:
        if point_count >= options.point_per:
            num = options.max_width
        mid = math.floor(point_count/2)-1
        new_points.append(points[mid])
        if num > 1:
            new_points.append(points[mid+1])

    return new_points

def highest(face_points):
    high = -300
    for p in face_points:
        if p.y > high:
            high = p.y
    return high

def lowest(face_points):
    low = 300
    for p in face_points:
        if p.y < low:
            low = p.y
    return low

def poly_point_edges(face_points, options=Map()):
    #TODO: Pass in cardinality to know which to return
    left_x = points_along_poly(face_points, Map(side = "left_x"))
    right_x = points_along_poly(face_points, Map(side = "right_x"))
    left_z = points_along_poly(face_points, Map(side = "left_z"))
    right_z = points_along_poly(face_points, Map(side = "right_z"))
    top = points_along_poly(face_points, Map(side = "top"))
    bottom = points_along_poly(face_points, Map(side = "bottom"))

    out = [top, bottom]
    out.extend([left_x,right_x] if len(left_x) < len(left_z) else [left_z,right_z])
    return out


def points_along_poly(face_points, options=Map()):
    side = options.side or "bottom"

    points = []

    #Y searching
    if side == "top":
        highest = -300
        for p in face_points:
            if p.y > highest:
                highest = p.y

        for p in face_points:
            if p.y == highest:
                points.append(p)
    elif side == "bottom":
        lowest = 300
        for p in face_points:
            if p.y < lowest:
                lowest = p.y

        for p in face_points:
            if p.y == lowest:
                points.append(p)

    #x searching
    if side == "left_x":
        highest = -300
        for p in face_points:
            if p.x > highest:
                highest = p.x

        for p in face_points:
            if p.x == highest:
                points.append(p)

    elif side == "right_x":
        lowest = 300
        for p in face_points:
            if p.x < lowest:
                lowest = p.x

        for p in face_points:
            if p.x == lowest:
                points.append(p)

    #z searching
    if side == "left_z":
        highest = -300
        for p in face_points:
            if p.z > highest:
                highest = p.z

        for p in face_points:
            if p.z == highest:
                points.append(p)

    elif side == "right_z":
        lowest = 300
        for p in face_points:
            if p.z < lowest:
                lowest = p.z

        for p in face_points:
            if p.z == lowest:
                points.append(p)

    return points

def unique_points(point_generator):
    done = set()
    for p in point_generator:
        if p not in done:
            done.add(p)
    return done    

#Initially based on scripts from:
#https://github.com/nebogeo/creative-kids-coding-cornwall/blob/master/minecraft/python/dbscode_minecraft.py
def box(pos, size, options=Map()):
    # size should be a vec3
    if not options.material:
        options.material = block.STONE.id
    if not options.create_now:
        options.create_now = False

    points = []
    if options.create_now:        
        helpers.create_block_filled_box(pos.x,pos.y,pos.z,
                pos.x+size.x-1,pos.y+size.y-1,
                pos.z+size.z-1,
                options.material, options.data)
    else:
        for y in reversed(range(0,int(size.y))):
          for z in range(0, int(size.z)):
              for x in range(0, int(size.x)):
                  points.append(V3(pos.x+x,pos.y+y,pos.z+z))
    return points

def sphere(pos, radius, options=Map()):
    if not options.material:
        options.material = block.STONE.id
    if not options.create_now:
        options.create_now = False

    points = []
    radius_range=int(radius)
    for y in range(-radius_range, radius_range):
        for z in range(-radius_range, radius_range):
            for x in range(-radius_range, radius_range):
                if math.sqrt(x*x+y*y+z*z)<radius:
                    if options.create_now:
                        helpers.create_block(V3(pos.x+x,pos.y+y,pos.z+z), options.material)
                    else:
                        points.append(V3(pos.x+x,pos.y+y,pos.z+z))
    return points

def cylinder(pos, radius, height, options=Map()):
    if not options.material:
        options.material = block.STONE.id
    if not options.create_now:
        options.create_now = False

    points = []
    radius_range=int(radius)
    height_range=int(height)
    for y in range(0, height_range):
        for z in range(-radius_range, radius_range):
            for x in range(-radius_range, radius_range):
                if math.sqrt(x*x+z*z)<radius:
                    if options.create_now:
                        helpers.create_block(V3(pos.x+x,pos.y+y,pos.z+z), options.material)
                    else:
                        points.append(V3(pos.x+x,pos.y+y,pos.z+z))
    return points

def cone(pos, radius, height, options=Map()):
    if not options.material:
        options.material = block.STONE.id
    if not options.create_now:
        options.create_now = False

    points = []
    radius=int(radius)
    height=int(height)
    for y in range(0, height):
        for z in range(-radius, radius):
            for x in range(-radius, radius):
                if math.sqrt(x*x+z*z)<(radius*(1-y/float(height))):
                    if options.create_now:
                        helpers.create_block(V3(pos.x+x,pos.y+y,pos.z+z), options.material)
                    else:
                        points.append(V3(pos.x+x,pos.y+y,pos.z+z))
    return points

def toblerone(t,pos,size):
    if not options.material:
        options.material = block.STONE.id
    if not options.create_now:
        options.create_now = False

    points = []    
    for y in reversed(range(0,int(size.y))):
        for z in range(0, int(size.z)):
            for x in range(0, int(size.x)):
                a = size.x*(1-y/float(size.y))*0.5
                if x>size.x/2.0-a and x<a+size.x/2.0:
                    if options.create_now:
                        helpers.create_block(V3(pos.x+x,pos.y+y,pos.z+z), options.material)
                    else:
                        points.append(V3(pos.x+x,pos.y+y,pos.z+z))
    return points

#=====================================================
# Following Code by Alexander Pruss and under the MIT license
# From https://github.com/arpruss/raspberryjammod/blob/master/mcpipy/drawing.py

def makeMatrix(compass,vertical,roll):
    m0 = matrixMultiply(yawMatrix(compass), pitchMatrix(vertical))
    return matrixMultiply(m0, rollMatrix(roll))

def applyMatrix(m,v):
    if m is None:
       return v
    else:
       return V3(m[i][0]*v[0]+m[i][1]*v[1]+m[i][2]*v[2] for i in range(3))

def matrixDistanceSquared(m1,m2):
    d2 = 0.
    for i in range(3):
        for j in range(3):
            d2 += (m1[i][j]-m2[i][j])**2
    return d2

def iatan2(y,x):
    """One coordinate must be zero"""
    if x == 0:
        return 90 if y > 0 else -90
    else:
        return 0 if x > 0 else 180

def icos(angleDegrees):
    """Calculate a cosine of an angle that must be a multiple of 90 degrees"""
    return ICOS[(angleDegrees % 360) // 90]

def isin(angleDegrees):
    """Calculate a sine of an angle that must be a multiple of 90 degrees"""
    return ISIN[(angleDegrees % 360) // 90]

def matrixMultiply(a,b):
    c = [[0,0,0],[0,0,0],[0,0,0]]
    for i in range(3):
        for j in range(3):
            c[i][j] = a[i][0]*b[0][j] + a[i][1]*b[1][j] + a[i][2]*b[2][j]
    return c

def yawMatrix(angleDegrees):
    if isinstance(angleDegrees, Integral) and angleDegrees % 90 == 0:
        return [[icos(angleDegrees), 0, -isin(angleDegrees)],
                [0,          1, 0],
                [isin(angleDegrees), 0, icos(angleDegrees)]]
    else:
        theta = angleDegrees * TO_RADIANS
        return [[math.cos(theta), 0., -math.sin(theta)],
                [0.,         1., 0.],
                [math.sin(theta), 0., math.cos(theta)]]

def rollMatrix(angleDegrees):
    if isinstance(angleDegrees, Integral) and angleDegrees % 90 == 0:
        return [[icos(angleDegrees), -isin(angleDegrees), 0],
                [isin(angleDegrees), icos(angleDegrees),0],
                [0,          0,          1]]
    else:
        theta = angleDegrees * TO_RADIANS
        return [[math.cos(theta), -math.sin(theta), 0.],
                [math.sin(theta), math.cos(theta),0.],
                [0.,          0.,          1.]]

def pitchMatrix(angleDegrees):
    if isinstance(angleDegrees, Integral) and angleDegrees % 90 == 0:
        return [[1,          0,          0],
                [0, icos(angleDegrees),isin(angleDegrees)],
                [0, -isin(angleDegrees),icos(angleDegrees)]]
    else:
        theta = angleDegrees * TO_RADIANS
        return [[1.,          0.,          0.],
                [0., math.cos(theta),math.sin(theta)],
                [0., -math.sin(theta),math.cos(theta)]]

def get2DTriangle(a,b,c):
    """get the points of the 2D triangle"""
    minX = {}
    maxX = {}

    for line in (traverse2D(a,b), traverse2D(b,c), traverse2D(a,c)):
        for p in line:
            minX0 = minX.get(p[1])
            if minX0 == None:
                minX[p[1]] = p[0]
                maxX[p[1]] = p[0]
                yield(p)
            elif p[0] < minX0:
                for x in range(p[0],minX0):
                    yield(x,p[1])
                minX[p[1]] = p[0]
            else:
                maxX0 = maxX[p[1]]
                if maxX0 < p[0]:
                    for x in range(maxX0,p[0]):
                        yield(x,p[1])
                    maxX[p[1]] = p[0]

def getFace(vertices):
    if len(vertices) < 1:
        raise StopIteration
    if len(vertices) <= 2:
        for p in traverse(V3(vertices[0]), V3(vertices[1])):
            yield p
    v0 = V3(vertices[0])
    for i in range(2,len(vertices)):
        for p in traverse(V3(vertices[i-1]), V3(vertices[i])):
            for q in traverse(p, v0):
                yield q

def getTriangle(p1, p2, p3):
    """
    Note that this will return many duplicate poitns
    """
    p1,p2,p3 = V3(p1),V3(p2),V3(p3)

    for u in traverse(p2,p3):
        for w in traverse(p1,u):
             yield w

def frac(x):
    return x - math.floor(x)

def traverse2D(a,b):
    """
    equation of line: a + t(b-a), t from 0 to 1
    Based on Amantides and Woo's ray traversal algorithm with some help from
    http://stackoverflow.com/questions/12367071/how-do-i-initialize-the-t-variables-in-a-fast-voxel-traversal-algorithm-for-ray
    """

    inf = float("inf")

    if b[0] == a[0]:
        if b[1] == a[1]:
            yield (int(math.floor(a[0])),int(math.floor(a[1])))
            return
        tMaxX = inf
        tDeltaX = 0
    else:
        tDeltaX = 1./abs(b[0]-a[0])
        tMaxX = tDeltaX * (1. - frac(a[0]))

    if b[1] == a[1]:
        tMaxY = inf
        tDeltaY = 0
    else:
        tDeltaY = 1./abs(b[1]-a[1])
        tMaxY = tDeltaY * (1. - frac(a[1]))

    endX = int(math.floor(b[0]))
    endY = int(math.floor(b[1]))
    x = int(math.floor(a[0]))
    y = int(math.floor(a[1]))
    if x <= endX:
        stepX = 1
    else:
        stepX = -1
    if y <= endY:
        stepY = 1
    else:
        stepY = -1

    yield (x,y)
    if x == endX:
        if y == endY:
            return
        tMaxX = inf
    if y == endY:
        tMaxY = inf

    while True:
        if tMaxX < tMaxY:
            x += stepX
            yield (x,y)
            if x == endX:
                tMaxX = inf
            else:
                tMaxX += tDeltaX
        else:
            y += stepY
            yield (x,y)
            if y == endY:
                tMaxY = inf
            else:
                tMaxY += tDeltaY

        if tMaxX == inf and tMaxY == inf:
            return

def traverse(a,b):
    """
    equation of line: a + t(b-a), t from 0 to 1
    Based on Amantides and Woo's ray traversal algorithm with some help from
    http://stackoverflow.com/questions/12367071/how-do-i-initialize-the-t-variables-in-a-fast-voxel-traversal-algorithm-for-ray
    """

    inf = float("inf")

    if b.x == a.x:
        if b.y == a.y and b.z == a.z:
            yield a.ifloor()
            return
        tMaxX = inf
        tDeltaX = 0
    else:
        tDeltaX = 1./abs(b.x-a.x)
        tMaxX = tDeltaX * (1. - frac(a.x))

    if b.y == a.y:
        tMaxY = inf
        tDeltaY = 0
    else:
        tDeltaY = 1./abs(b.y-a.y)
        tMaxY = tDeltaY * (1. - frac(a.y))

    if b.z == a.z:
        tMaxZ = inf
        tDeltaZ = 0
    else:
        tDeltaZ = 1./abs(b.z-a.z)
        tMaxZ = tDeltaZ * (1. - frac(a.z))

    end = b.ifloor()
    x = int(floor(a.x))
    y = int(floor(a.y))
    z = int(floor(a.z))
    if x <= end.x:
        stepX = 1
    else:
        stepX = -1
    if y <= end.y:
        stepY = 1
    else:
        stepY = -1
    if z <= end.z:
        stepZ = 1
    else:
        stepZ = -1

    yield V3(x,y,z)

    if x == end.x:
        if y == end.y and z == end.z:
            return
        tMaxX = inf
    if y == end.y:
        tMaxY = inf
    if z == end.z:
        tMaxZ = inf

    while True:
        if tMaxX < tMaxY:
            if tMaxX < tMaxZ:
                x += stepX
                yield V3(x,y,z)
                if x == end.x:
                    tMaxX = inf
                else:
                    tMaxX += tDeltaX
            else:
                z += stepZ
                yield V3(x,y,z)
                if z == end.z:
                    tMaxZ = inf
                else:
                    tMaxZ += tDeltaZ
        else:
            if tMaxY < tMaxZ:
                y += stepY
                yield V3(x,y,z)
                if y == end.y:
                    tMaxY = inf
                else:
                    tMaxY += tDeltaY
            else:
                z += stepZ
                yield V3(x,y,z)
                if z == end.z:
                    tMaxZ = inf
                else:
                    tMaxZ += tDeltaZ

        if tMaxX == inf and tMaxY == inf and tMaxZ == inf:
            return

# Brasenham's algorithm
def getLine(x1, y1, z1, x2, y2, z2):
    line = []
    x1 = int(math.floor(x1))
    y1 = int(math.floor(y1))
    z1 = int(math.floor(z1))
    x2 = int(math.floor(x2))
    y2 = int(math.floor(y2))
    z2 = int(math.floor(z2))
    point = [x1,y1,z1]
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    x_inc = -1 if dx < 0 else 1
    l = abs(dx)
    y_inc = -1 if dy < 0 else 1
    m = abs(dy)
    z_inc = -1 if dz < 0 else 1
    n = abs(dz)
    dx2 = l << 1
    dy2 = m << 1
    dz2 = n << 1

    if l >= m and l >= n:
        err_1 = dy2 - l
        err_2 = dz2 - l
        for i in range(0,l-1):
            line.append(V3(point[0],point[1],point[2]))
            if err_1 > 0:
                point[1] += y_inc
                err_1 -= dx2
            if err_2 > 0:
                point[2] += z_inc
                err_2 -= dx2
            err_1 += dy2
            err_2 += dz2
            point[0] += x_inc
    elif m >= l and m >= n:
        err_1 = dx2 - m;
        err_2 = dz2 - m;
        for i in range(0,m-1):
            line.append(V3(point[0],point[1],point[2]))
            if err_1 > 0:
                point[0] += x_inc
                err_1 -= dy2
            if err_2 > 0:
                point[2] += z_inc
                err_2 -= dy2
            err_1 += dx2
            err_2 += dz2
            point[1] += y_inc
    else:
        err_1 = dy2 - n;
        err_2 = dx2 - n;
        for i in range(0, n-1):
            line.append(V3(point[0],point[1],point[2]))
            if err_1 > 0:
                point[1] += y_inc
                err_1 -= dz2
            if err_2 > 0:
                point[0] += x_inc
                err_2 -= dz2
            err_1 += dy2
            err_2 += dx2
            point[2] += z_inc
    line.append(V3(point[0],point[1],point[2]))
    if point[0] != x2 or point[1] != y2 or point[2] != z2:
        line.append(V3(x2,y2,z2))
    return line


# class Drawing:
#     TO_RADIANS = pi / 180.
#     TO_DEGREES = 180. / pi

#     def __init__(self):
#         self.width = 1
#         self.nib = [(0,0,0)]
#         self.point_array = []

#     def penwidth(self,w):
#         self.width = int(w)
#         if self.width == 0:
#             self.nib = []
#         elif self.width == 1:
#             self.nib = [(0,0,0)]
#         elif self.width == 2:
#             self.nib = []
#             for x in range(-1,1):
#                 for y in range(0,2):
#                     for z in range(-1,1):
#                         self.nib.append((x,y,z))
#         else:
#             self.nib = []
#             r2 = self.width * self.width / 4.
#             for x in range(-self.width//2 - 1,self.width//2 + 1):
#                 for y in range(-self.width//2 - 1, self.width//2 + 1):
#                     for z in range(-self.width//2 -1, self.width//2 + 1):
#                         if x*x + y*y + z*z <= r2:
#                             self.nib.append((x,y,z))

#     def point(self, x, y, z, block, options):
#         for p in self.nib:
#             self.drawPoint(x+p[0],y+p[1],z+p[2],block)

#     def face(self, vertices, block):
#         self.drawPoints(getFace(vertices), block)

#     def line(self, x1,y1,z1, x2,y2,z2, block):
#         self.drawPoints(getLine(x1,y1,z1, x2,y2,z2), block)

#     def drawPoints(self, points, block):
#         if self.width == 1:
#             done = set()
#             for p in points:
#                 if p not in done:
#                     self.mc.setBlock(p, block)
#                     done.add(p)
#         else:
#             done = set()
#             for p in points:
#                 for point in self.nib:
#                     x0 = p[0]+point[0]
#                     y0 = p[1]+point[1]
#                     z0 = p[2]+point[2]
#                     if (x0,y0,z0) not in done:
#                         self.mc.setBlock(x0,y0,z0,block)
#                         done.add((x0,y0,z0))


