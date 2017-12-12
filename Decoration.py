from Map import Map
from MCShape import DECORATIONS_LIBRARY


class Decoration(object):
    def __init__(self, kind, function):
        DECORATIONS_LIBRARY.append(Map(kind=kind, function=function))
