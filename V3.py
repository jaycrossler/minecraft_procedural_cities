#
# Code by Alexander Pruss and under the MIT license
# From https://github.com/arpruss/raspberryjammod/blob/master/mcpipy/drawing.py
#
from math import *
from numbers import Number


class V3(tuple):
    def __new__(cls,*args):
        if len(args) == 1:
           return tuple.__new__(cls,tuple(*args))
        else:
           return tuple.__new__(cls,args)

    def dot(self,other):
        return self[0]*other[0]+self[1]*other[1]+self[2]*other[2]

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def z(self):
        return self[2]

    def __add__(self,other):
        other = tuple(other)
        return V3(self[0]+other[0],self[1]+other[1],self[2]+other[2])

    def __radd__(self,other):
        other = tuple(other)
        return V3(self[0]+other[0],self[1]+other[1],self[2]+other[2])

    def __sub__(self,other):
        other = tuple(other)
        return V3(self[0]-other[0],self[1]-other[1],self[2]-other[2])

    def __rsub__(self,other):
        other = tuple(other)
        return V3(other[0]-self[0],other[1]-self[1],other[2]-self[2])

    def __neg__(self):
        return V3(-self[0],-self[1],-self[2])

    def __pos__(self):
        return self

    def len2(self):
        return self[0]*self[0]+self[1]*self[1]+self[2]*self[2]

    def __abs__(self):
        return sqrt(self.len2())

    def __round__(self, n=None):
        return V3(round(self[0]),round(self[1]),round(self[2]))

    def __div__(self,other):
        if isinstance(other,Number):
            y = float(other)
            return V3(self[0]/y,self[1]/y,self[2]/y)
        else:
            return NotImplemented

    def __mul__(self,other):
        if isinstance(other,Number):
            return V3(self[0]*other,self[1]*other,self[2]*other)
        else:
            other = tuple(other)
            # cross product
            return V3(self[1]*other[2]-self[2]*other[1],self[2]*other[0]-self[0]*other[2],self[0]*other[1]-self[1]*other[0])

    def __rmul__(self,other):
        return self.__mul__(other)

    def __repr__(self):
        return "V3"+repr(tuple(self))

    def ifloor(self):
        return V3(int(floor(self[0])),int(floor(self[1])),int(floor(self[2])))

    def iceil(self):
        return V3(int(ceil(self[0])),int(ceil(self[1])),int(ceil(self[2])))