from Map import Map

DECORATIONS_LIBRARY = []


class Decoration(object):
    def __init__(self, kind, callback, namespace="", variables=None, materials=None, validator=None):

        DECORATIONS_LIBRARY.append(Map(kind=kind, callback=callback, namespace=namespace, variables=variables,
                                       materials=materials, validator=validator))


def get_matching_decorations(decorations):
    matching_decorations = []
    for d in decorations:

        for dl in DECORATIONS_LIBRARY:
            if dl["kind"] == d["kind"]:
                dec = dl
                dec["options"] = d["options"]
                matching_decorations.append(dec)

    return matching_decorations
