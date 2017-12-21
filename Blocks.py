#############################################################################################################
# Better Python MCPI Blocks Library
##############################################################################################################

import math
import re
from Map import Map
from libraries import webcolors
import sys
# this is a pointer to the module object instance itself.
this = sys.modules[__name__]

DEBUG_MODE = 1  # 0 = Print errors, 1 = Throw Errors


def block(description):
    out = None
    if type(description) == int:
        out = block_by_id(description)
    elif type(description) == str:

        found = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', description)

        if not found:
            try:
                out = match(description, "Block")
            except ValueError:
                try:
                    target_color = webcolors.name_to_rgb(description)
                    out = closest_by_color(target_color, Map(only_blocks=True))
                except ValueError:
                    out = like(description, "Block")
        else:
            target_color = webcolors.hex_to_rgb(description)
            out = closest_by_color(target_color, Map(only_blocks=True))
    elif type(description) == tuple and len(description) == 3:
        out = closest_by_color(description, Map(only_blocks=True))
    elif type(description) == tuple and len(description) == 2:
        out = block_by_id(description)

    return out


def block_by_id(block_id, data=0):

    if type(block_id) == tuple and len(block_id) == 2:
        data = block_id[1]
        block_id = block_id[0]

    b = [x for x in block_library if x["id"] == block_id and x["data"] == data]
    if len(b) == 0:
        b = [x for x in block_library if x["id"] == block_id]

    return b[0] if b else {"name": "Unknown", "id": 0, "data": 0}


def name_by_id(block_id, data=0):

    if type(block_id) == tuple and len(block_id) == 2:
        data = block_id[1]
        block_id = block_id[0]

    b = [x for x in block_library if x["id"] == block_id and x["data"] == data]
    if len(b) == 0:
        b = [x for x in block_library if x["id"] == block_id]

    out = "Unknown"
    if b and len(b) > 0 and b[0] and b[0]["name"]:
        out = b[0]["name"]
    return out


def match(name, only_blocks="Block"):
    # Return first item matching the name entered
    if only_blocks:
        b = [x for x in block_library if (x["name"].lower() == name.lower()) and ("kind" in x) and (x["kind"] == only_blocks)]
    else:
        b = [x for x in block_library if x["name"].lower() == name.lower()]
    if len(b) > 0:
        return b[0]
    else:
        raise ValueError("Error - blocks.match(\"" + str(name) + "\") - unrecognized block name")


def like(name, only_blocks="Block"):
    # Returns all items with names with substrings matching
    if only_blocks:
        b = [x for x in block_library if (x["name"].lower().find(name.lower()) > -1) and ("kind" in x) and (x["kind"] == only_blocks)]
    else:
        b = [x for x in block_library if x["name"].lower().find(name.lower()) > -1]
    if len(b) > 0:
        return b
    else:
        error_string = "Error - blocks.like(\"" + str(name) + "\") - unrecognized block name, returning air"
        if DEBUG_MODE == 1:
            raise ValueError(error_string)
        else:
            print(error_string)

        return [block_library[0]]


def kind(kind="Flower"):
    b = [x for x in block_library if ("kind" in x) and (x["kind"].lower().find(kind.lower()) > -1)]
    if len(b) > 0:
        return b
    else:
        error_string = "Error - blocks.kind(\"" + str(name) + "\") - unrecognized block name, returning air"
        if DEBUG_MODE == 1:
            raise ValueError(error_string)
        else:
            print(error_string)

        return [block_library[0]]


def id_and_data(name):
    b = [x for x in block_library if x["name"].lower() == name.lower()]
    if len(b) > 0:
        return b[0]["id"], b[0]["data"]
    else:
        return 0, 0


def color_as_hex(color):
    target_color = color
    if type(color) == tuple and len(color) == 3:
        target_color = webcolors.rgb_to_hex(color)
    elif type(color) == str:
        found = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color)
        if found:
            target_color = color
        else:
            target_color = webcolors.name_to_hex(color)
    return target_color


def color_as_rgb(color):
    target_color = color
    if type(color) == tuple and len(color) == 3:
        target_color = color
    elif type(color) == str:
        found = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color)
        if found:
            target_color = webcolors.hex_to_rgb(color)
        else:
            target_color = webcolors.name_to_rgb(color)
    return target_color


def color_distance(c1, c2):
    (r1, g1, b1) = c1
    (r2, g2, b2) = c2
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)


def closest_by_color(color, options=Map()):
    if type(color) == str:
        found = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color)

        if not found:
            target_color = webcolors.name_to_rgb(color)
        else:
            target_color = webcolors.hex_to_rgb(color)

    elif type(color) == tuple and len(color) == 3:
        target_color = color
    else:
        error_string = "Error - blocks.closest_by_color(\"" + str(color) + "\") - invalid color in closest_by_color"
        if DEBUG_MODE == 1:
            raise ValueError(error_string)
        else:
            print(error_string)

        target_color = color

    closest = None
    closest_num = 10000
    for b in block_library:
        if options.name_contains:
            if b["name"].lower().find(options.name_contains.lower()) == -1:
                continue

        if options.only_blocks:
            if ("kind" not in b) or (b["kind"] != "Block"):
                continue

        if "main_color" in b:
            dist = color_distance(target_color, b["main_color"])
            if dist < closest_num:
                closest_num = dist
                closest = b

    return closest


def icon(name, show_it=True):
    from PIL import Image

    b = like(name)

    x_count = 27
    y_count = 27

    im = Image.open("tools/items-27.png")

    width = math.floor(im.width / x_count)
    height = math.floor(im.height / y_count)

    blocks = []
    for img in b:
        image_id = img["id_in_image"]

        col = image_id % x_count
        row = math.floor(image_id / x_count)

        box = (col*width, row*height, (col+1)*width, (row+1)*height)
        block = im.crop(box)
        if show_it:
            block.show()
        blocks.append(block)
    return blocks


# Block colors Painstakenly extracted from http://www.minecraft-servers-list.org/ide-list/ using Pillow
#  and merged with list of all blocks

block_library = [{'name': 'Air', 'id': 0, 'data': 0, 'kind': 'Block', 'id_in_image': 0, 'main_color': (0, 0, 0), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Stone', 'id': 1, 'data': 0, 'kind': 'Block', 'id_in_image': 1, 'main_color': (95, 95, 95), 'second_color': (89, 89, 89), 'third_color': (57, 57, 57)},
 {'name': 'Granite', 'id': 1, 'data': 1, 'kind': 'Block', 'id_in_image': 27, 'main_color': (73, 51, 43), 'second_color': (108, 83, 74), 'third_color': (94, 67, 57)},
 {'name': 'Polished Granite', 'id': 1, 'data': 2, 'kind': 'Block', 'id_in_image': 28, 'main_color': (72, 51, 43), 'second_color': (156, 110, 93), 'third_color': (99, 69, 57)},
 {'name': 'Diorite', 'id': 1, 'data': 3, 'kind': 'Block', 'id_in_image': 2, 'main_color': (90, 90, 92), 'second_color': (149, 149, 151), 'third_color': (211, 211, 214)},
 {'name': 'Polished Diorite', 'id': 1, 'data': 4, 'kind': 'Block', 'id_in_image': 29, 'main_color': (92, 92, 93), 'second_color': (145, 145, 147), 'third_color': (209, 209, 212)},
 {'name': 'Andesite', 'id': 1, 'data': 5, 'kind': 'Block', 'id_in_image': 54, 'main_color': (88, 88, 88), 'second_color': (52, 52, 52), 'third_color': (148, 148, 148)},
 {'name': 'Polished Andesite', 'id': 1, 'data': 6, 'kind': 'Block', 'id_in_image': 55, 'main_color': (88, 88, 89), 'second_color': (54, 54, 55), 'third_color': (141, 142, 143)},
 {'name': 'Grass', 'id': 2, 'data': 0, 'kind': 'Block', 'id_in_image': 364, 'main_color': (51, 36, 25), 'second_color': (75, 53, 36), 'third_color': (91, 83, 47)},
 {'name': 'Dirt', 'id': 3, 'data': 0, 'kind': 'Block', 'id_in_image': 493, 'main_color': (82, 57, 39), 'second_color': (112, 79, 54), 'third_color': (56, 40, 27)},
 {'name': 'Coarse Dirt', 'id': 3, 'data': 1, 'kind': 'Block', 'id_in_image': 494, 'main_color': (46, 33, 23), 'second_color': (74, 52, 35), 'third_color': (108, 76, 52)},
 {'name': 'Podzol', 'id': 3, 'data': 2, 'kind': 'Block', 'id_in_image': 495, 'main_color': (75, 53, 31), 'second_color': (47, 33, 20), 'third_color': (102, 72, 41)},
 {'name': 'Cobblestone', 'id': 4, 'data': 0, 'stair': 67, 'kind': 'Block', 'id_in_image': 621, 'main_color': (90, 90, 90), 'second_color': (50, 50, 50), 'third_color': (151, 151, 151)},
 {'name': 'Oak Wood Plank', 'id': 5, 'data': 0, 'kind': 'Block', 'id_in_image': 106, 'main_color': (98, 80, 48), 'second_color': (174, 142, 87), 'third_color': (137, 111, 71)},
 {'name': 'Spruce Wood Plank', 'id': 5, 'data': 1, 'kind': 'Block', 'id_in_image': 133, 'main_color': (72, 54, 32), 'second_color': (48, 36, 22), 'third_color': (114, 85, 50)},
 {'name': 'Birch Wood Plank', 'id': 5, 'data': 2, 'kind': 'Block', 'id_in_image': 160, 'main_color': (87, 79, 54), 'second_color': (135, 125, 86), 'third_color': (117, 106, 71)},
 {'name': 'Jungle Wood Plank', 'id': 5, 'data': 3, 'kind': 'Block', 'id_in_image': 187, 'main_color': (73, 52, 36), 'second_color': (109, 78, 54), 'third_color': (50, 34, 23)},
 {'name': 'Acacia Wood Plank', 'id': 5, 'data': 4, 'kind': 'Block', 'id_in_image': 214, 'main_color': (89, 48, 26), 'second_color': (168, 91, 50), 'third_color': (116, 64, 36)},
 {'name': 'Dark Oak Wood Plank', 'id': 5, 'data': 5, 'kind': 'Block', 'id_in_image': 241, 'main_color': (29, 18, 8), 'second_color': (41, 26, 12), 'third_color': (42, 27, 12)},
 {'name': 'Oak Sapling', 'id': 6, 'data': 0, 'kind': 'Sapling', 'id_in_image': 538, 'main_color': (0, 100, 0), 'second_color': (148, 100, 40), 'third_color': (73, 204, 37)},
 {'name': 'Spruce Sapling', 'id': 6, 'data': 1, 'kind': 'Sapling', 'id_in_image': 565, 'main_color': (35, 33, 18), 'second_color': (57, 90, 57), 'third_color': (80, 54, 26)},
 {'name': 'Birch Sapling', 'id': 6, 'data': 2, 'kind': 'Sapling', 'id_in_image': 592, 'main_color': (81, 116, 45), 'second_color': (207, 227, 186), 'third_color': (100, 141, 56)},
 {'name': 'Jungle Sapling', 'id': 6, 'data': 3, 'kind': 'Sapling', 'id_in_image': 619, 'main_color': (52, 57, 11), 'second_color': (42, 103, 19), 'third_color': (55, 128, 32)},
 {'name': 'Acacia Sapling', 'id': 6, 'data': 4, 'kind': 'Sapling', 'id_in_image': 646, 'main_color': (114, 85, 10), 'second_color': (121, 146, 30), 'third_color': (103, 126, 23)},
 {'name': 'Dark Oak Sapling', 'id': 6, 'data': 5, 'kind': 'Sapling', 'id_in_image': 673, 'main_color': (19, 85, 17), 'second_color': (84, 57, 25), 'third_color': (106, 78, 42)},
 {'name': 'Bedrock', 'id': 7, 'data': 0, 'kind': 'Block', 'id_in_image': 685, 'main_color': (83, 83, 83), 'second_color': (31, 31, 31), 'third_color': (41, 41, 41)},
 {'name': 'Flowing Water', 'id': 8, 'data': 0, 'kind': 'Block', 'id_in_image': 696, 'main_color': (17, 38, 106), 'second_color': (38, 87, 238), 'third_color': (21, 55, 160)},
 {'name': 'Still Water', 'id': 9, 'data': 0, 'kind': 'Block', 'id_in_image': 188, 'main_color': (17, 38, 106), 'second_color': (38, 87, 238), 'third_color': (21, 55, 160)},
 {'name': 'Flowing Lava', 'id': 10, 'data': 0, 'kind': 'Block', 'id_in_image': 56, 'main_color': (96, 30, 3), 'second_color': (157, 47, 4), 'third_color': (148, 85, 17)},
 {'name': 'Still Lava', 'id': 11, 'data': 0, 'kind': 'Block', 'id_in_image': 85, 'main_color': (96, 30, 3), 'second_color': (157, 47, 4), 'third_color': (148, 85, 17)},
 {'name': 'Sand', 'id': 12, 'data': 0, 'kind': 'Block', 'id_in_image': 135, 'main_color': (110, 106, 80), 'second_color': (158, 153, 113), 'third_color': (220, 212, 160)},
 {'name': 'Red Sand', 'id': 12, 'data': 1, 'kind': 'Block', 'id_in_image': 136, 'main_color': (90, 46, 17), 'second_color': (169, 88, 33), 'third_color': (118, 66, 27)},
 {'name': 'Gravel', 'id': 13, 'data': 0, 'kind': 'Block', 'id_in_image': 88, 'main_color': (94, 87, 86), 'second_color': (51, 47, 46), 'third_color': (161, 151, 150)},
 {'name': 'Gold Ore', 'id': 14, 'data': 0, 'kind': 'Block', 'id_in_image': 8, 'main_color': (93, 93, 93), 'second_color': (57, 57, 57), 'third_color': (152, 152, 143)},
 {'name': 'Iron Ore', 'id': 15, 'data': 0, 'kind': 'Block', 'id_in_image': 219, 'main_color': (94, 93, 92), 'second_color': (57, 57, 57), 'third_color': (150, 144, 140)},
 {'name': 'Coal Ore', 'id': 16, 'data': 0, 'kind': 'Block', 'id_in_image': 91, 'main_color': (95, 95, 95), 'second_color': (50, 50, 50), 'third_color': (89, 89, 89)},
 {'name': 'Oak Wood', 'id': 17, 'data': 0, 'kind': 'Block', 'stair': 53, 'id_in_image': 298, 'main_color': (46, 37, 22), 'second_color': (175, 142, 88), 'third_color': (99, 79, 48)},
 {'name': 'Spruce Wood', 'id': 17, 'data': 1, 'kind': 'Block', 'stair': 134, 'id_in_image': 299, 'main_color': (29, 18, 8), 'second_color': (175, 142, 88), 'third_color': (105, 84, 51)},
 {'name': 'Birch Wood', 'id': 17, 'data': 2, 'kind': 'Block', 'stair': 135, 'id_in_image': 300, 'main_color': (164, 164, 160), 'second_color': (112, 112, 109), 'third_color': (175, 142, 88)},
 {'name': 'Jungle Wood', 'id': 17, 'data': 3, 'kind': 'Block', 'stair': 136, 'id_in_image': 301, 'main_color': (42, 33, 13), 'second_color': (174, 140, 87), 'third_color': (72, 54, 22)},
 {'name': 'Oak Leaves', 'id': 18, 'data': 0, 'kind': 'Block', 'id_in_image': 13, 'main_color': (18, 47, 6), 'second_color': (33, 84, 11), 'third_color': (57, 145, 19)},
 {'name': 'Spruce Leaves', 'id': 18, 'data': 1, 'kind': 'Block', 'id_in_image': 40, 'main_color': (18, 47, 6), 'second_color': (33, 84, 11), 'third_color': (57, 145, 19)},
 {'name': 'Birch Leaves', 'id': 18, 'data': 2, 'kind': 'Block', 'id_in_image': 67, 'main_color': (18, 47, 6), 'second_color': (33, 84, 11), 'third_color': (57, 145, 19)},
 {'name': 'Jungle Leaves', 'id': 18, 'data': 3, 'kind': 'Block', 'id_in_image': 94, 'main_color': (18, 45, 5), 'second_color': (34, 86, 10), 'third_color': (58, 147, 18)},
 {'name': 'Sponge', 'id': 19, 'data': 0, 'kind': 'Block', 'id_in_image': 352, 'main_color': (95, 96, 41), 'second_color': (205, 206, 91), 'third_color': (136, 136, 56)},
 {'name': 'Wet Sponge', 'id': 19, 'data': 1, 'kind': 'Block', 'id_in_image': 353, 'main_color': (90, 89, 33), 'second_color': (155, 151, 51), 'third_color': (49, 52, 34)},
 {'name': 'Glass', 'id': 20, 'data': 0, 'kind': 'Block', 'id_in_image': 14, 'main_color': (150, 162, 163), 'second_color': (218, 248, 254), 'third_color': (90, 108, 111)},
 {'name': 'Lapis Lazuli Ore', 'id': 21, 'data': 0, 'kind': 'Block', 'id_in_image': 311, 'main_color': (93, 93, 93), 'second_color': (17, 41, 93), 'third_color': (58, 58, 58)},
 {'name': 'Lapis Lazuli Block', 'id': 22, 'data': 0, 'kind': 'Block', 'id_in_image': 386, 'main_color': (22, 40, 83), 'second_color': (17, 29, 55), 'third_color': (39, 74, 146)},
 {'name': 'Dispenser', 'id': 23, 'data': 0, 'kind': 'Block', 'id_in_image': 406, 'main_color': (42, 42, 42), 'second_color': (96, 96, 96), 'third_color': (86, 86, 86)},
 {'name': 'Sandstone', 'id': 24, 'data': 0, 'kind': 'Block', 'stair': 128, 'id_in_image': 417, 'main_color': (218, 210, 158), 'second_color': (111, 108, 83), 'third_color': (154, 148, 106)},
 {'name': 'Chiseled Sandstone', 'id': 24, 'data': 1, 'kind': 'Block', 'id_in_image': 418, 'main_color': (106, 102, 75), 'second_color': (215, 207, 156), 'third_color': (142, 137, 108)},
 {'name': 'Smooth Sandstone', 'id': 24, 'data': 2, 'kind': 'Block', 'id_in_image': 419, 'main_color': (100, 97, 73), 'second_color': (215, 207, 156), 'third_color': (140, 135, 106)},
 {'name': 'Note Block', 'id': 25, 'data': 0, 'kind': 'Block', 'id_in_image': 259, 'main_color': (41, 31, 25), 'second_color': (75, 48, 34), 'third_color': (106, 70, 50)},
 {'name': 'Bed', 'id': 26, 'data': 0, 'kind': 'Block', 'double': True, 'id_in_image': 422, 'main_color': (224, 224, 225), 'second_color': (146, 25, 25), 'third_color': (116, 4, 4)},
 {'name': 'Powered Rail', 'id': 27, 'data': 0, 'kind': 'Block', 'id_in_image': 469, 'main_color': (164, 164, 164), 'second_color': (104, 104, 104), 'third_color': (212, 159, 36)},
 {'name': 'Detector Rail', 'id': 28, 'data': 0, 'kind': 'Block', 'id_in_image': 99, 'main_color': (165, 164, 164), 'second_color': (105, 104, 104), 'third_color': (95, 76, 45)},
 {'name': 'Sticky Piston', 'id': 29, 'data': 0, 'kind': 'Block', 'id_in_image': 396, 'main_color': (41, 41, 39), 'second_color': (86, 86, 83), 'third_color': (103, 86, 51)},
 {'name': 'Cobweb', 'id': 30, 'data': 0, 'id_in_image': 496, 'main_color': (206, 206, 206), 'second_color': (221, 221, 221), 'third_color': (237, 237, 237)},
 {'name': 'Dead Shrub', 'id': 31, 'data': 0, 'kind': 'Block', 'id_in_image': 73, 'main_color': (148, 100, 40), 'second_color': (91, 52, 6), 'third_color': (0, 0, 0)},
 {'name': 'Tall Grass', 'id': 31, 'data': 1, 'kind': 'Flower', 'id_in_image': 100, 'main_color': (53, 139, 40), 'second_color': (41, 108, 31), 'third_color': (46, 119, 34)},
 {'name': 'Fern', 'id': 31, 'data': 2, 'kind': 'Block', 'id_in_image': 127, 'main_color': (44, 130, 43), 'second_color': (33, 98, 33), 'third_color': (63, 187, 62)},
 {'name': 'Dead Shrub', 'id': 32, 'data': 0, 'kind': 'Block', 'id_in_image': 424, 'main_color': (148, 100, 40), 'second_color': (91, 52, 6), 'third_color': (0, 0, 0)},
 {'name': 'Piston', 'id': 33, 'data': 0, 'kind': 'Block', 'id_in_image': 521, 'main_color': (41, 41, 39), 'second_color': (84, 84, 84), 'third_color': (106, 85, 51)},
 {'name': 'Piston Head', 'id': 34, 'data': 0, 'kind': 'Block', 'id_in_image': 532, 'main_color': (173, 141, 86), 'second_color': (110, 86, 51), 'third_color': (116, 94, 57)},
 {'name': 'White Wool', 'id': 35, 'data': 0, 'kind': 'Block', 'id_in_image': 371, 'main_color': (162, 162, 162), 'second_color': (225, 225, 225), 'third_color': (117, 117, 117)},
 {'name': 'Orange Wool', 'id': 35, 'data': 1, 'kind': 'Block', 'id_in_image': 398, 'main_color': (173, 94, 40), 'second_color': (118, 67, 32), 'third_color': (117, 60, 21)},
 {'name': 'Magenta Wool', 'id': 35, 'data': 2, 'kind': 'Block', 'id_in_image': 541, 'main_color': (96, 37, 101), 'second_color': (142, 50, 150), 'third_color': (196, 88, 206)},
 {'name': 'Light Blue Wool', 'id': 35, 'data': 3, 'kind': 'Block', 'id_in_image': 542, 'main_color': (82, 107, 158), 'second_color': (54, 71, 107), 'third_color': (108, 142, 213)},
 {'name': 'Yellow Wool', 'id': 35, 'data': 4, 'kind': 'Block', 'id_in_image': 543, 'main_color': (100, 93, 14), 'second_color': (159, 148, 22), 'third_color': (200, 186, 28)},
 {'name': 'Lime Wool', 'id': 35, 'data': 5, 'kind': 'Block', 'id_in_image': 544, 'main_color': (47, 152, 38), 'second_color': (30, 98, 24), 'third_color': (60, 196, 48)},
 {'name': 'Pink Wool', 'id': 35, 'data': 6, 'kind': 'Block', 'id_in_image': 545, 'main_color': (159, 91, 110), 'second_color': (112, 74, 84), 'third_color': (222, 147, 167)},
 {'name': 'Gray Wool', 'id': 35, 'data': 7, 'kind': 'Block', 'id_in_image': 546, 'main_color': (38, 38, 38), 'second_color': (54, 54, 54), 'third_color': (70, 70, 70)},
 {'name': 'Light Gray Wool', 'id': 35, 'data': 8, 'kind': 'Block', 'id_in_image': 547, 'main_color': (153, 160, 160), 'second_color': (98, 103, 103), 'third_color': (83, 86, 86)},
 {'name': 'Cyan Wool', 'id': 35, 'data': 9, 'kind': 'Block', 'id_in_image': 548, 'main_color': (27, 82, 105), 'second_color': (38, 114, 147), 'third_color': (19, 57, 73)},
 {'name': 'Purple Wool', 'id': 35, 'data': 10, 'kind': 'Block', 'id_in_image': 425, 'main_color': (101, 41, 154), 'second_color': (70, 30, 105), 'third_color': (60, 22, 92)},
 {'name': 'Blue Wool', 'id': 35, 'data': 11, 'kind': 'Block', 'id_in_image': 452, 'main_color': (19, 26, 78), 'second_color': (38, 50, 152), 'third_color': (28, 37, 113)},
 {'name': 'Brown Wool', 'id': 35, 'data': 12, 'kind': 'Block', 'id_in_image': 479, 'main_color': (43, 25, 14), 'second_color': (69, 41, 22), 'third_color': (88, 53, 28)},
 {'name': 'Green Wool', 'id': 35, 'data': 13, 'kind': 'Block', 'id_in_image': 506, 'main_color': (39, 55, 17), 'second_color': (27, 38, 12), 'third_color': (54, 75, 23)},
 {'name': 'Red Wool', 'id': 35, 'data': 14, 'kind': 'Block', 'id_in_image': 533, 'main_color': (82, 22, 20), 'second_color': (116, 31, 28), 'third_color': (142, 39, 35)},
 {'name': 'Black Wool', 'id': 35, 'data': 15, 'kind': 'Block', 'id_in_image': 540, 'main_color': (14, 11, 11), 'second_color': (23, 20, 20), 'third_color': (32, 28, 28)},
 {'name': 'Dandelion', 'id': 37, 'data': 0, 'kind': 'Flower', 'id_in_image': 570, 'main_color': (226, 233, 2), 'second_color': (22, 135, 0), 'third_color': (16, 99, 0)},
 {'name': 'Poppy', 'id': 38, 'data': 0, 'kind': 'Flower', 'id_in_image': 581, 'main_color': (165, 3, 8), 'second_color': (17, 110, 0), 'third_color': (22, 135, 0)},
 {'name': 'Blue Orchid', 'id': 38, 'data': 1, 'kind': 'Flower', 'id_in_image': 582, 'main_color': (36, 166, 237), 'second_color': (44, 137, 5), 'third_color': (28, 118, 11)},
 {'name': 'Allium', 'id': 38, 'data': 2, 'kind': 'Flower', 'id_in_image': 583, 'main_color': (185, 104, 251), 'second_color': (214, 169, 251), 'third_color': (106, 176, 72)},
 {'name': 'Azure Bluet', 'id': 38, 'data': 3, 'kind': 'Flower', 'id_in_image': 584, 'main_color': (222, 228, 236), 'second_color': (81, 142, 47), 'third_color': (242, 242, 156)},
 {'name': 'Red Tulip', 'id': 38, 'data': 4, 'kind': 'Flower', 'id_in_image': 585, 'main_color': (84, 153, 50), 'second_color': (65, 139, 28), 'third_color': (96, 177, 56)},
 {'name': 'Orange Tulip', 'id': 38, 'data': 5, 'kind': 'Flower', 'id_in_image': 586, 'main_color': (83, 156, 46), 'second_color': (54, 126, 18), 'third_color': (69, 138, 35)},
 {'name': 'White Tulip', 'id': 38, 'data': 6, 'kind': 'Flower', 'id_in_image': 587, 'main_color': (74, 146, 39), 'second_color': (49, 121, 13), 'third_color': (230, 230, 230)},
 {'name': 'Pink Tulip', 'id': 38, 'data': 7, 'kind': 'Flower', 'id_in_image': 588, 'main_color': (79, 149, 45), 'second_color': (56, 125, 21), 'third_color': (226, 178, 226)},
 {'name': 'Oxeye Daisy', 'id': 38, 'data': 8, 'kind': 'Flower', 'id_in_image': 22, 'main_color': (238, 238, 238), 'second_color': (80, 148, 47), 'third_color': (53, 119, 20)},
 {'name': 'Brown Mushroom', 'id': 39, 'data': 0, 'kind': 'Flower', 'id_in_image': 212, 'main_color': (112, 87, 70), 'second_color': (145, 109, 85), 'third_color': (204, 153, 120)},
 {'name': 'Red Mushroom', 'id': 40, 'data': 0, 'kind': 'Flower', 'id_in_image': 622, 'main_color': (227, 27, 29), 'second_color': (154, 23, 28), 'third_color': (218, 218, 218)},
 {'name': 'Gold Block', 'id': 41, 'data': 0, 'kind': 'Block', 'id_in_image': 633, 'main_color': (171, 161, 50), 'second_color': (252, 246, 85), 'third_color': (129, 123, 40)},
 {'name': 'Iron Block', 'id': 42, 'data': 0, 'kind': 'Block', 'id_in_image': 644, 'main_color': (171, 171, 171), 'second_color': (231, 231, 231), 'third_color': (119, 119, 119)},
 {'name': 'Double Stone Slab', 'id': 43, 'data': 0, 'kind': 'Block', 'id_in_image': 267, 'main_color': (154, 154, 154), 'second_color': (106, 106, 106), 'third_color': (85, 85, 85)},
 {'name': 'Double Sandstone Slab', 'id': 43, 'data': 1, 'kind': 'Block', 'id_in_image': 294, 'main_color': (218, 210, 158), 'second_color': (111, 108, 83), 'third_color': (154, 148, 106)},
 {'name': 'Double Wooden Slab', 'id': 43, 'data': 2, 'kind': 'Block', 'id_in_image': 321, 'main_color': (98, 80, 48), 'second_color': (174, 142, 87), 'third_color': (137, 111, 71)},
 {'name': 'Double Cobblestone Slab', 'id': 43, 'data': 3, 'kind': 'Block', 'id_in_image': 348, 'main_color': (90, 90, 90), 'second_color': (50, 50, 50), 'third_color': (151, 151, 151)},
 {'name': 'Double Brick Slab', 'id': 43, 'data': 4, 'kind': 'Block', 'id_in_image': 375, 'main_color': (86, 48, 37), 'second_color': (96, 85, 81), 'third_color': (119, 66, 52)},
 {'name': 'Double Stone Brick Slab', 'id': 43, 'data': 5, 'kind': 'Block', 'id_in_image': 402, 'main_color': (103, 103, 103), 'second_color': (70, 70, 70), 'third_color': (55, 55, 55)},
 {'name': 'Double Nether Brick Slab', 'id': 43, 'data': 6, 'kind': 'Block', 'id_in_image': 429, 'main_color': (43, 21, 25), 'second_color': (23, 12, 14), 'third_color': (41, 21, 25)},
 {'name': 'Double Quartz Slab', 'id': 43, 'data': 7, 'kind': 'Block', 'id_in_image': 456, 'main_color': (102, 101, 98), 'second_color': (151, 149, 145), 'third_color': (236, 233, 226)},
 {'name': 'Stone Slab', 'id': 44, 'data': 0, 'kind': 'Block', 'id_in_image': 651, 'main_color': (97, 97, 97), 'second_color': (148, 148, 148), 'third_color': (165, 165, 165)},
 {'name': 'Sandstone Slab', 'id': 44, 'data': 1, 'kind': 'Block', 'id_in_image': 652, 'main_color': (217, 210, 158), 'second_color': (111, 107, 82), 'third_color': (153, 148, 105)},
 {'name': 'Wooden Slab', 'id': 44, 'data': 2, 'kind': 'Block', 'id_in_image': 653, 'main_color': (100, 82, 49), 'second_color': (175, 142, 88), 'third_color': (137, 111, 71)},
 {'name': 'Cobblestone Slab', 'id': 44, 'data': 3, 'kind': 'Block', 'id_in_image': 654, 'main_color': (95, 95, 95), 'second_color': (152, 152, 152), 'third_color': (86, 86, 86)},
 {'name': 'Brick Slab', 'id': 44, 'data': 4, 'kind': 'Block', 'id_in_image': 655, 'main_color': (81, 48, 39), 'second_color': (162, 143, 137), 'third_color': (53, 29, 23)},
 {'name': 'Stone Brick Slab', 'id': 44, 'data': 5, 'kind': 'Block', 'id_in_image': 656, 'main_color': (96, 96, 96), 'second_color': (55, 55, 55), 'third_color': (142, 142, 142)},
 {'name': 'Nether Brick Slab', 'id': 44, 'data': 6, 'kind': 'Block', 'id_in_image': 657, 'main_color': (22, 11, 13), 'second_color': (43, 21, 25), 'third_color': (37, 19, 22)},
 {'name': 'Quartz Slab', 'id': 44, 'data': 7, 'kind': 'Block', 'id_in_image': 658, 'main_color': (238, 236, 229), 'second_color': (149, 147, 143), 'third_color': (102, 100, 97)},
 {'name': 'Bricks', 'id': 45, 'data': 0, 'kind': 'Block', 'id_in_image': 669, 'main_color': (86, 48, 37), 'second_color': (96, 85, 81), 'third_color': (119, 66, 52)},
 {'name': 'TNT', 'id': 46, 'data': 0, 'kind': 'Block', 'id_in_image': 672, 'main_color': (97, 29, 11), 'second_color': (149, 46, 17), 'third_color': (95, 95, 95)},
 {'name': 'Bookshelf', 'id': 47, 'data': 0, 'kind': 'Block', 'id_in_image': 25, 'main_color': (98, 83, 42), 'second_color': (37, 32, 21), 'third_color': (174, 142, 87)},
 {'name': 'Moss Stone', 'id': 48, 'data': 0, 'kind': 'Block', 'id_in_image': 52, 'main_color': (51, 88, 51), 'second_color': (98, 98, 98), 'third_color': (143, 143, 143)},
 {'name': 'Obsidian', 'id': 49, 'data': 0, 'kind': 'Block', 'id_in_image': 79, 'main_color': (9, 9, 14), 'second_color': (22, 19, 32), 'third_color': (52, 42, 75)},
 {'name': 'Torch', 'id': 50, 'data': 0, 'id_in_image': 268, 'main_color': (151, 119, 72), 'second_color': (59, 46, 27), 'third_color': (110, 87, 53)},
 {'name': 'Fire', 'id': 51, 'data': 0, 'id_in_image': 295, 'main_color': (183, 79, 8), 'second_color': (218, 152, 29), 'third_color': (198, 107, 12)},
 {'name': 'Monster Spawner', 'id': 52, 'data': 0, 'id_in_image': 322, 'main_color': (24, 36, 46), 'second_color': (19, 29, 36), 'third_color': (16, 22, 26)},
 {'name': 'Oak Wood Stairs', 'id': 53, 'data': 0, 'kind': 'Block', 'id_in_image': 349, 'main_color': (99, 81, 49), 'second_color': (174, 142, 87), 'third_color': (137, 111, 71)},
 {'name': 'Chest', 'id': 54, 'data': 0, 'kind': 'Block', 'interactive': True, 'id_in_image': 376, 'main_color': (39, 34, 26), 'second_color': (113, 80, 28), 'third_color': (77, 54, 18)},
 {'name': 'Redstone Wire', 'id': 55, 'data': 0, 'interactive': True, 'id_in_image': 403, 'main_color': (175, 0, 0), 'second_color': (253, 0, 0), 'third_color': (214, 0, 0)},
 {'name': 'Diamond Ore', 'id': 56, 'data': 0, 'kind': 'Block', 'id_in_image': 430, 'main_color': (93, 93, 93), 'second_color': (57, 57, 57), 'third_color': (145, 149, 152)},
 {'name': 'Diamond Block', 'id': 57, 'data': 0, 'kind': 'Block', 'id_in_image': 457, 'main_color': (101, 170, 167), 'second_color': (74, 117, 115), 'third_color': (26, 104, 100)},
 {'name': 'Crafting Table', 'id': 58, 'data': 0, 'kind': 'Block', 'interactive': True, 'id_in_image': 484, 'main_color': (29, 23, 14), 'second_color': (95, 77, 46), 'third_color': (150, 111, 70)},
 {'name': 'Wheat Crops', 'id': 59, 'data': 0, 'id_in_image': 511, 'main_color': (94, 105, 14), 'second_color': (22, 38, 0), 'third_color': (147, 166, 5)},
 {'name': 'Farmland', 'id': 60, 'data': 0, 'kind': 'Block', 'id_in_image': 675, 'main_color': (83, 56, 36), 'second_color': (112, 78, 51), 'third_color': (56, 40, 27)},
 {'name': 'Furnace', 'id': 61, 'data': 0, 'kind': 'Block', 'interactive': True, 'id_in_image': 676, 'main_color': (92, 92, 92), 'second_color': (27, 27, 27), 'third_color': (55, 55, 55)},
 {'name': 'Burning Furnace', 'id': 62, 'data': 0, 'kind': 'Block', 'interactive': True, 'id_in_image': 677, 'main_color': (38, 38, 38), 'second_color': (92, 92, 92), 'third_color': (138, 138, 138)},
 {'name': 'Standing Sign Block', 'id': 63, 'data': 0, 'id_in_image': 678, 'main_color': (159, 132, 77), 'second_color': (105, 84, 50), 'third_color': (46, 33, 12)},
 {'name': 'Oak Door Block', 'id': 64, 'data': 0, 'kind': 'Block', 'double': True, 'id_in_image': 679, 'main_color': (159, 132, 77), 'second_color': (105, 84, 51), 'third_color': (65, 52, 33)},
 {'name': 'Ladder', 'id': 65, 'data': 0, 'kind': 'Block', 'interactive': True, 'id_in_image': 680, 'main_color': (97, 76, 40), 'second_color': (168, 132, 78), 'third_color': (142, 115, 60)},
 {'name': 'Rail', 'id': 66, 'data': 0, 'kind': 'Block', 'interactive': True, 'id_in_image': 681, 'main_color': (95, 76, 44), 'second_color': (164, 164, 164), 'third_color': (104, 104, 104)},
 {'name': 'Cobblestone Stairs', 'id': 67, 'data': 0, 'kind': 'Block', 'id_in_image': 682, 'main_color': (101, 101, 101), 'second_color': (69, 69, 69), 'third_color': (51, 51, 51)},
 {'name': 'Wall-mounted Sign Block', 'id': 68, 'data': 0, 'id_in_image': 683, 'main_color': (159, 132, 77), 'second_color': (105, 84, 50), 'third_color': (46, 33, 12)},
 {'name': 'Lever', 'id': 69, 'data': 0, 'id_in_image': 684, 'main_color': (112, 89, 55), 'second_color': (117, 117, 117), 'third_color': (60, 47, 28)},
 {'name': 'Stone Pressure Plate', 'id': 70, 'data': 0, 'id_in_image': 686, 'main_color': (121, 121, 121), 'second_color': (86, 86, 86), 'third_color': (142, 142, 142)},
 {'name': 'Iron Door Block', 'id': 71, 'data': 0, 'kind': 'Block', 'double': True, 'id_in_image': 687, 'main_color': (205, 205, 205), 'second_color': (149, 149, 149), 'third_color': (109, 109, 109)},
 {'name': 'Wooden Pressure Plate', 'id': 72, 'data': 0, 'id_in_image': 688, 'main_color': (174, 142, 88), 'second_color': (103, 84, 50), 'third_color': (138, 112, 72)},
 {'name': 'Redstone Ore', 'id': 73, 'data': 0, 'kind': 'Block', 'id_in_image': 689, 'main_color': (93, 93, 93), 'second_color': (57, 57, 57), 'third_color': (96, 1, 1)},
 {'name': 'Glowing Redstone Ore', 'id': 74, 'data': 0, 'kind': 'Block', 'id_in_image': 690, 'main_color': (93, 93, 93), 'second_color': (57, 57, 57), 'third_color': (96, 1, 1)},
 {'name': 'Redstone Torch (off)', 'id': 75, 'data': 0, 'id_in_image': 691, 'main_color': (72, 27, 17), 'second_color': (56, 38, 22), 'third_color': (151, 119, 72)},
 {'name': 'Redstone Torch (on)', 'id': 76, 'data': 0, 'id_in_image': 692, 'main_color': (253, 0, 0), 'second_color': (151, 119, 72), 'third_color': (59, 46, 27)},
 {'name': 'Stone Button', 'id': 77, 'data': 0, 'id_in_image': 693, 'main_color': (99, 99, 99), 'second_color': (90, 90, 90), 'third_color': (57, 57, 57)},
 {'name': 'Snow', 'id': 78, 'data': 0, 'kind': 'Block', 'id_in_image': 694, 'main_color': (166, 173, 173), 'second_color': (238, 250, 250), 'third_color': (120, 129, 129)},
 {'name': 'Ice', 'id': 79, 'data': 0, 'kind': 'Block', 'id_in_image': 695, 'main_color': (87, 123, 185), 'second_color': (60, 85, 129), 'third_color': (119, 169, 255)},
 {'name': 'Snow Block', 'id': 80, 'data': 0, 'kind': 'Block', 'id_in_image': 697, 'main_color': (166, 173, 173), 'second_color': (238, 250, 250), 'third_color': (120, 129, 129)},
 {'name': 'Cactus', 'id': 81, 'data': 0, 'kind': 'Block', 'id_in_image': 698, 'main_color': (4, 32, 8), 'second_color': (12, 97, 23), 'third_color': (9, 68, 16)},
 {'name': 'Clay', 'id': 82, 'data': 0, 'kind': 'Block', 'id_in_image': 699, 'main_color': (84, 87, 94), 'second_color': (157, 163, 175), 'third_color': (118, 122, 131)},
 {'name': 'Sugar Canes', 'id': 83, 'data': 0, 'id_in_image': 700, 'main_color': (167, 215, 114), 'second_color': (130, 168, 89), 'third_color': (117, 193, 40)},
 {'name': 'Jukebox', 'id': 84, 'data': 0, 'id_in_image': 26, 'main_color': (40, 30, 25), 'second_color': (74, 48, 34), 'third_color': (108, 71, 51)},
 {'name': 'Oak Fence', 'id': 85, 'data': 0, 'kind': 'Block', 'id_in_image': 53, 'main_color': (95, 78, 47), 'second_color': (171, 140, 86), 'third_color': (137, 111, 71)},
 {'name': 'Pumpkin', 'id': 86, 'data': 0, 'id_in_image': 80, 'main_color': (116, 70, 13), 'second_color': (160, 95, 16), 'third_color': (89, 51, 7)},
 {'name': 'Netherrack', 'id': 87, 'data': 0, 'kind': 'Block', 'id_in_image': 107, 'main_color': (85, 37, 36), 'second_color': (40, 15, 15), 'third_color': (148, 87, 83)},
 {'name': 'Soul Sand', 'id': 88, 'data': 0, 'kind': 'Block', 'id_in_image': 134, 'main_color': (44, 32, 24), 'second_color': (71, 54, 44), 'third_color': (107, 85, 72)},
 {'name': 'Glowstone', 'id': 89, 'data': 0, 'kind': 'Block', 'id_in_image': 161, 'main_color': (54, 43, 20), 'second_color': (94, 78, 44), 'third_color': (79, 56, 16)},
 {'name': 'Nether Portal', 'id': 90, 'data': 0, 'kind': 'Block', 'id_in_image': 215, 'main_color': (40, 2, 98), 'second_color': (79, 11, 166), 'third_color': (54, 1, 144)},
 {'name': "Jack o'Lantern", 'id': 91, 'data': 0, 'id_in_image': 242, 'main_color': (115, 71, 14), 'second_color': (89, 51, 7), 'third_color': (160, 97, 15)},
 {'name': 'Cake Block', 'id': 92, 'data': 0, 'id_in_image': 269, 'main_color': (234, 233, 235), 'second_color': (221, 221, 221), 'third_color': (234, 29, 29)},
 {'name': 'Redstone Repeater Block (off)', 'id': 93, 'data': 0, 'id_in_image': 296, 'main_color': (156, 156, 156), 'second_color': (201, 201, 201), 'third_color': (80, 1, 0)},
 {'name': 'Redstone Repeater Block (on)', 'id': 94, 'data': 0, 'id_in_image': 323, 'main_color': (156, 156, 156), 'second_color': (201, 201, 201), 'third_color': (234, 1, 2)},
 {'name': 'White Stained Glass', 'id': 95, 'data': 0, 'kind': 'Block', 'id_in_image': 350, 'main_color': (255, 255, 255), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Orange Stained Glass', 'id': 95, 'data': 1, 'kind': 'Block', 'id_in_image': 377, 'main_color': (255, 120, 7), 'second_color': (85, 38, 0), 'third_color': (136, 64, 0)},
 {'name': 'Magenta Stained Glass', 'id': 95, 'data': 2, 'kind': 'Block', 'id_in_image': 566, 'main_color': (99, 0, 135), 'second_color': (56, 0, 79), 'third_color': (198, 44, 255)},
 {'name': 'Light Blue Stained Glass', 'id': 95, 'data': 3, 'kind': 'Block', 'id_in_image': 593, 'main_color': (0, 33, 73), 'second_color': (82, 160, 255), 'third_color': (0, 60, 134)},
 {'name': 'Yellow Stained Glass', 'id': 95, 'data': 4, 'kind': 'Block', 'id_in_image': 620, 'main_color': (92, 92, 0), 'second_color': (145, 145, 0), 'third_color': (255, 255, 25)},
 {'name': 'Lime Stained Glass', 'id': 95, 'data': 5, 'kind': 'Block', 'id_in_image': 647, 'main_color': (46, 84, 0), 'second_color': (73, 128, 0), 'third_color': (124, 218, 0)},
 {'name': 'Pink Stained Glass', 'id': 95, 'data': 6, 'kind': 'Block', 'id_in_image': 674, 'main_color': (175, 0, 54), 'second_color': (255, 125, 167), 'third_color': (82, 0, 29)},
 {'name': 'Gray Stained Glass', 'id': 95, 'data': 7, 'kind': 'Block', 'id_in_image': 701, 'main_color': (0, 0, 0), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Light Gray Stained Glass', 'id': 95, 'data': 8, 'kind': 'Block', 'id_in_image': 702, 'main_color': (255, 255, 255), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Cyan Stained Glass', 'id': 95, 'data': 9, 'kind': 'Block', 'id_in_image': 703, 'main_color': (0, 50, 73), 'second_color': (0, 26, 43), 'third_color': (0, 111, 171)},
 {'name': 'Purple Stained Glass', 'id': 95, 'data': 10, 'kind': 'Block', 'id_in_image': 404, 'main_color': (58, 0, 103), 'second_color': (34, 0, 61), 'third_color': (116, 0, 212)},
 {'name': 'Blue Stained Glass', 'id': 95, 'data': 11, 'kind': 'Block', 'id_in_image': 431, 'main_color': (0, 15, 73), 'second_color': (0, 39, 202), 'third_color': (0, 22, 106)},
 {'name': 'Brown Stained Glass', 'id': 95, 'data': 12, 'kind': 'Block', 'id_in_image': 458, 'main_color': (30, 15, 0), 'second_color': (79, 39, 0), 'third_color': (42, 22, 0)},
 {'name': 'Green Stained Glass', 'id': 95, 'data': 13, 'kind': 'Block', 'id_in_image': 485, 'main_color': (29, 43, 0), 'second_color': (79, 119, 0), 'third_color': (42, 64, 0)},
 {'name': 'Red Stained Glass', 'id': 95, 'data': 14, 'kind': 'Block', 'id_in_image': 512, 'main_color': (53, 0, 0), 'second_color': (84, 0, 0), 'third_color': (162, 0, 0)},
 {'name': 'Black Stained Glass', 'id': 95, 'data': 15, 'kind': 'Block', 'id_in_image': 539, 'main_color': (0, 0, 0), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Wooden Trapdoor', 'id': 96, 'data': 0, 'id_in_image': 704, 'main_color': (142, 106, 53), 'second_color': (109, 78, 38), 'third_color': (78, 55, 26)},
 {'name': 'Stone Monster Egg', 'id': 97, 'data': 0, 'id_in_image': 705, 'main_color': (95, 95, 95), 'second_color': (89, 89, 89), 'third_color': (57, 57, 57)},
 {'name': 'Cobblestone Monster Egg', 'id': 97, 'data': 1, 'id_in_image': 706, 'main_color': (90, 90, 90), 'second_color': (50, 50, 50), 'third_color': (151, 151, 151)},
 {'name': 'Stone Brick Monster Egg', 'id': 97, 'data': 2, 'id_in_image': 707, 'main_color': (103, 103, 103), 'second_color': (70, 70, 70), 'third_color': (55, 55, 55)},
 {'name': 'Mossy Stone Brick Monster Egg', 'id': 97, 'data': 3, 'id_in_image': 708, 'main_color': (92, 93, 89), 'second_color': (49, 51, 45), 'third_color': (75, 87, 52)},
 {'name': 'Cracked Stone Brick Monster Egg', 'id': 97, 'data': 4, 'id_in_image': 709, 'main_color': (90, 90, 90), 'second_color': (56, 56, 56), 'third_color': (43, 43, 43)},
 {'name': 'Chiseled Stone Brick Monster Egg', 'id': 97, 'data': 5, 'id_in_image': 710, 'main_color': (88, 88, 88), 'second_color': (55, 55, 55), 'third_color': (41, 41, 41)},
 {'name': 'Stone Brick', 'id': 98, 'data': 0, 'stair': 109, 'kind': 'Block', 'id_in_image': 711, 'main_color': (103, 103, 103), 'second_color': (70, 70, 70), 'third_color': (55, 55, 55)},
 {'name': 'Mossy Stone Bricks', 'id': 98, 'data': 1, 'kind': 'Block', 'id_in_image': 712, 'main_color': (95, 97, 91), 'second_color': (45, 46, 41), 'third_color': (74, 85, 53)},
 {'name': 'Cracked Stone Bricks', 'id': 98, 'data': 2, 'kind': 'Block', 'id_in_image': 713, 'main_color': (92, 92, 92), 'second_color': (46, 46, 46), 'third_color': (142, 142, 142)},
 {'name': 'Chiseled Stone Bricks', 'id': 98, 'data': 3, 'kind': 'Block', 'id_in_image': 714, 'main_color': (88, 88, 88), 'second_color': (55, 55, 55), 'third_color': (41, 41, 41)},
 {'name': 'Red Mushroom Cap', 'id': 99, 'data': 0, 'id_in_image': 715, 'main_color': (92, 70, 54), 'second_color': (58, 43, 33), 'third_color': (137, 103, 80)},
 {'name': 'Brown Mushroom Cap', 'id': 100, 'data': 0, 'id_in_image': 3, 'main_color': (94, 15, 14), 'second_color': (168, 27, 25), 'third_color': (134, 134, 134)},
 {'name': 'Iron Bars', 'id': 101, 'data': 0, 'id_in_image': 30, 'main_color': (95, 93, 92), 'second_color': (157, 155, 154), 'third_color': (131, 121, 111)},
 {'name': 'Glass Pane', 'id': 102, 'data': 0, 'id_in_image': 57, 'main_color': (254, 254, 254), 'second_color': (179, 214, 219), 'third_color': (192, 245, 254)},
 {'name': 'Melon Block', 'id': 103, 'data': 0, 'id_in_image': 81, 'main_color': (95, 102, 27), 'second_color': (153, 153, 34), 'third_color': (123, 132, 34)},
 {'name': 'Pumpkin Stem', 'id': 104, 'data': 0, 'id_in_image': 82, 'main_color': (123, 187, 81), 'second_color': (146, 193, 98), 'third_color': (92, 156, 50)},
 {'name': 'Melon Stem', 'id': 105, 'data': 0, 'id_in_image': 83, 'main_color': (123, 187, 81), 'second_color': (146, 193, 98), 'third_color': (92, 156, 50)},
 {'name': 'Vines', 'id': 106, 'data': 0, 'id_in_image': 84, 'main_color': (24, 60, 8), 'second_color': (30, 76, 10), 'third_color': (36, 92, 11)},
 {'name': 'Oak Fence Gate', 'id': 107, 'data': 0, 'id_in_image': 4, 'main_color': (102, 83, 50), 'second_color': (140, 115, 69), 'third_color': (164, 133, 83)},
 {'name': 'Brick Stairs', 'id': 108, 'data': 0, 'kind': 'Block', 'id_in_image': 31, 'main_color': (97, 54, 42), 'second_color': (119, 66, 51), 'third_color': (143, 103, 92)},
 {'name': 'Stone Brick Stairs', 'id': 109, 'data': 0, 'kind': 'Block', 'id_in_image': 58, 'main_color': (104, 104, 104), 'second_color': (89, 89, 89), 'third_color': (103, 103, 103)},
 {'name': 'Mycelium', 'id': 110, 'data': 0, 'id_in_image': 108, 'main_color': (96, 87, 92), 'second_color': (111, 79, 54), 'third_color': (78, 55, 37)},
 {'name': 'Lily Pad', 'id': 111, 'data': 0, 'id_in_image': 109, 'main_color': (12, 95, 20), 'second_color': (16, 55, 16), 'third_color': (29, 116, 44)},
 {'name': 'Nether Brick', 'id': 112, 'data': 0, 'kind': 'Block', 'stair': 114, 'id_in_image': 110, 'main_color': (43, 21, 25), 'second_color': (23, 12, 14), 'third_color': (41, 21, 25)},
 {'name': 'Nether Brick Fence', 'id': 113, 'data': 0, 'kind': 'Block', 'id_in_image': 111, 'main_color': (44, 21, 25), 'second_color': (36, 20, 23), 'third_color': (22, 12, 14)},
 {'name': 'Nether Brick Stairs', 'id': 114, 'data': 0, 'kind': 'Block', 'id_in_image': 112, 'main_color': (43, 21, 25), 'second_color': (24, 12, 14), 'third_color': (41, 21, 25)},
 {'name': 'Nether Wart', 'id': 115, 'data': 0, 'id_in_image': 5, 'main_color': (98, 16, 13), 'second_color': (141, 18, 20), 'third_color': (57, 23, 19)},
 {'name': 'Enchantment Table', 'id': 116, 'data': 0, 'kind': 'Block', 'id_in_image': 32, 'main_color': (12, 9, 15), 'second_color': (96, 11, 10), 'third_color': (222, 222, 222)},
 {'name': 'Brewing Stand', 'id': 117, 'data': 0, 'kind': 'Block', 'id_in_image': 59, 'main_color': (43, 43, 43), 'second_color': (93, 92, 91), 'third_color': (95, 88, 40)},
 {'name': 'Cauldron', 'id': 118, 'data': 0, 'kind': 'Block', 'id_in_image': 86, 'main_color': (35, 35, 35), 'second_color': (70, 70, 70), 'third_color': (29, 29, 29)},
 {'name': 'End Portal', 'id': 119, 'data': 0, 'id_in_image': 113, 'main_color': (89, 41, 169), 'second_color': (96, 42, 173), 'third_color': (118, 43, 196)},
 {'name': 'End Portal Frame', 'id': 120, 'data': 0, 'id_in_image': 137, 'main_color': (15, 31, 31), 'second_color': (100, 105, 77), 'third_color': (148, 150, 109)},
 {'name': 'End Stone', 'id': 121, 'data': 0, 'id_in_image': 138, 'main_color': (101, 102, 75), 'second_color': (142, 145, 107), 'third_color': (213, 218, 161)},
 {'name': 'Dragon Egg', 'id': 122, 'data': 0, 'id_in_image': 139, 'main_color': (6, 5, 8), 'second_color': (16, 16, 16), 'third_color': (28, 1, 32)},
 {'name': 'Redstone Lamp (inactive)', 'id': 123, 'data': 0, 'id_in_image': 140, 'main_color': (25, 16, 10), 'second_color': (80, 47, 27), 'third_color': (111, 69, 43)},
 {'name': 'Redstone Lamp (active)', 'id': 124, 'data': 0, 'id_in_image': 6, 'main_color': (33, 27, 19), 'second_color': (100, 76, 40), 'third_color': (75, 56, 27)},
 {'name': 'Double Oak Wood Slab', 'id': 125, 'data': 0, 'kind': 'Block', 'id_in_image': 33, 'main_color': (98, 80, 48), 'second_color': (174, 142, 87), 'third_color': (137, 111, 71)},
 {'name': 'Double Spruce Wood Slab', 'id': 125, 'data': 1, 'kind': 'Block', 'id_in_image': 60, 'main_color': (72, 54, 32), 'second_color': (48, 36, 22), 'third_color': (114, 85, 50)},
 {'name': 'Double Birch Wood Slab', 'id': 125, 'data': 2, 'kind': 'Block', 'id_in_image': 87, 'main_color': (87, 79, 54), 'second_color': (135, 125, 86), 'third_color': (117, 106, 71)},
 {'name': 'Double Jungle Wood Slab', 'id': 125, 'data': 3, 'kind': 'Block', 'id_in_image': 114, 'main_color': (73, 52, 36), 'second_color': (109, 78, 54), 'third_color': (50, 34, 23)},
 {'name': 'Double Acacia Wood Slab', 'id': 125, 'data': 4, 'kind': 'Block', 'id_in_image': 141, 'main_color': (89, 48, 26), 'second_color': (168, 91, 50), 'third_color': (116, 64, 36)},
 {'name': 'Double Dark Oak Wood Slab', 'id': 125, 'data': 5, 'kind': 'Block', 'id_in_image': 162, 'main_color': (29, 18, 8), 'second_color': (41, 26, 12), 'third_color': (42, 27, 12)},
 {'name': 'Oak Wood Slab', 'id': 126, 'data': 0, 'kind': 'Block', 'id_in_image': 163, 'main_color': (100, 82, 49), 'second_color': (175, 142, 88), 'third_color': (137, 111, 71)},
 {'name': 'Spruce Wood Slab', 'id': 126, 'data': 1, 'kind': 'Block', 'id_in_image': 164, 'main_color': (71, 53, 33), 'second_color': (115, 86, 50), 'third_color': (48, 36, 22)},
 {'name': 'Birch Wood Slab', 'id': 126, 'data': 2, 'kind': 'Block', 'id_in_image': 165, 'main_color': (87, 79, 54), 'second_color': (164, 146, 102), 'third_color': (212, 201, 139)},
 {'name': 'Jungle Wood Slab', 'id': 126, 'data': 3, 'kind': 'Block', 'id_in_image': 166, 'main_color': (108, 77, 53), 'second_color': (73, 52, 36), 'third_color': (160, 115, 78)},
 {'name': 'Acacia Wood Slab', 'id': 126, 'data': 4, 'kind': 'Block', 'id_in_image': 167, 'main_color': (89, 48, 26), 'second_color': (169, 91, 50), 'third_color': (116, 64, 36)},
 {'name': 'Dark Oak Wood Slab', 'id': 126, 'data': 5, 'kind': 'Block', 'id_in_image': 168, 'main_color': (46, 30, 13), 'second_color': (41, 26, 12), 'third_color': (28, 18, 8)},
 {'name': 'Cocoa', 'id': 127, 'data': 0, 'id_in_image': 7, 'main_color': (86, 44, 14), 'second_color': (44, 18, 5), 'third_color': (118, 69, 27)},
 {'name': 'Sandstone Stairs', 'id': 128, 'data': 0, 'id_in_image': 34, 'main_color': (103, 100, 73), 'second_color': (205, 198, 150), 'third_color': (141, 136, 106)},
 {'name': 'Emerald Ore', 'id': 129, 'data': 0, 'kind': 'Block', 'id_in_image': 61, 'main_color': (91, 91, 91), 'second_color': (47, 50, 48), 'third_color': (15, 91, 37)},
 {'name': 'Ender Chest', 'id': 130, 'data': 0, 'id_in_image': 115, 'main_color': (13, 22, 23), 'second_color': (51, 71, 68), 'third_color': (44, 62, 64)},
 {'name': 'Tripwire Hook', 'id': 131, 'data': 0, 'id_in_image': 142, 'main_color': (71, 58, 36), 'second_color': (107, 87, 53), 'third_color': (142, 142, 142)},
 {'name': 'Tripwire', 'id': 132, 'data': 0, 'id_in_image': 169, 'main_color': (146, 146, 146), 'second_color': (118, 118, 118), 'third_color': (164, 164, 164)},
 {'name': 'Emerald Block', 'id': 133, 'data': 0, 'kind': 'Block', 'id_in_image': 189, 'main_color': (30, 95, 47), 'second_color': (50, 153, 77), 'third_color': (76, 210, 113)},
 {'name': 'Spruce Wood Stairs', 'id': 134, 'data': 0, 'kind': 'Block', 'id_in_image': 190, 'main_color': (44, 33, 20), 'second_color': (71, 54, 32), 'third_color': (106, 79, 47)},
 {'name': 'Birch Wood Stairs', 'id': 135, 'data': 0, 'kind': 'Block', 'id_in_image': 191, 'main_color': (86, 79, 55), 'second_color': (134, 124, 85), 'third_color': (170, 154, 105)},
 {'name': 'Jungle Wood Stairs', 'id': 136, 'data': 0, 'kind': 'Block', 'id_in_image': 192, 'main_color': (107, 77, 54), 'second_color': (72, 51, 35), 'third_color': (160, 116, 82)},
 {'name': 'Command Block', 'id': 137, 'data': 0, 'kind': 'Block', 'id_in_image': 193, 'main_color': (80, 52, 36), 'second_color': (101, 91, 85), 'third_color': (110, 75, 52)},
 {'name': 'Beacon', 'id': 138, 'data': 0, 'id_in_image': 194, 'main_color': (93, 106, 107), 'second_color': (105, 149, 149), 'third_color': (11, 10, 17)},
 {'name': 'Cobblestone Wall', 'id': 139, 'data': 0, 'kind': 'Block', 'id_in_image': 195, 'main_color': (90, 90, 90), 'second_color': (56, 56, 56), 'third_color': (39, 39, 39)},
 {'name': 'Mossy Cobblestone Wall', 'id': 139, 'data': 1, 'kind': 'Block', 'id_in_image': 196, 'main_color': (37, 50, 37), 'second_color': (88, 88, 88), 'third_color': (47, 86, 47)},
 {'name': 'Flower Pot', 'id': 140, 'data': 0, 'id_in_image': 35, 'main_color': (88, 48, 37), 'second_color': (59, 32, 25), 'third_color': (119, 67, 51)},
 {'name': 'Carrots', 'id': 141, 'data': 0, 'id_in_image': 62, 'main_color': (1, 99, 1), 'second_color': (4, 148, 0), 'third_color': (8, 196, 0)},
 {'name': 'Potatoes', 'id': 142, 'data': 0, 'id_in_image': 89, 'main_color': (0, 156, 25), 'second_color': (0, 206, 26), 'third_color': (157, 159, 48)},
 {'name': 'Wooden Button', 'id': 143, 'data': 0, 'id_in_image': 116, 'main_color': (101, 82, 50), 'second_color': (171, 140, 85), 'third_color': (72, 59, 35)},
 {'name': 'Mob Head', 'id': 144, 'data': 0, 'id_in_image': 143, 'main_color': (146, 146, 146), 'second_color': (101, 101, 101), 'third_color': (73, 73, 73)},
 {'name': 'Anvil', 'id': 145, 'data': 0, 'id_in_image': 170, 'main_color': (39, 38, 38), 'second_color': (70, 68, 68), 'third_color': (65, 61, 61)},
 {'name': 'Trapped Chest', 'id': 146, 'data': 0, 'id_in_image': 197, 'main_color': (39, 34, 26), 'second_color': (113, 80, 28), 'third_color': (77, 54, 18)},
 {'name': 'Weighted Pressure Plate (light)', 'id': 147, 'data': 0, 'id_in_image': 216, 'main_color': (252, 244, 85), 'second_color': (109, 105, 32), 'third_color': (159, 153, 46)},
 {'name': 'Weighted Pressure Plate (heavy)', 'id': 148, 'data': 0, 'id_in_image': 217, 'main_color': (230, 230, 230), 'second_color': (159, 159, 159), 'third_color': (98, 98, 98)},
 {'name': 'Redstone Comparator (inactive)', 'id': 149, 'data': 0, 'id_in_image': 218, 'main_color': (149, 148, 148), 'second_color': (65, 65, 63), 'third_color': (35, 10, 7)},
 {'name': 'Redstone Comparator (active)', 'id': 150, 'data': 0, 'id_in_image': 220, 'main_color': (159, 157, 157), 'second_color': (100, 99, 97), 'third_color': (42, 31, 26)},
 {'name': 'Daylight Sensor', 'id': 151, 'data': 0, 'id_in_image': 221, 'main_color': (38, 32, 21), 'second_color': (212, 195, 174), 'third_color': (71, 61, 41)},
 {'name': 'Redstone Block', 'id': 152, 'data': 0, 'kind': 'Block', 'id_in_image': 222, 'main_color': (94, 14, 4), 'second_color': (153, 25, 8), 'third_color': (53, 6, 3)},
 {'name': 'Nether Quartz Ore', 'id': 153, 'data': 0, 'kind': 'Block', 'id_in_image': 223, 'main_color': (38, 16, 16), 'second_color': (82, 38, 37), 'third_color': (103, 86, 81)},
 {'name': 'Hopper', 'id': 154, 'data': 0, 'id_in_image': 224, 'main_color': (70, 70, 70), 'second_color': (54, 54, 54), 'third_color': (89, 89, 89)},
 {'name': 'Quartz', 'id': 155, 'data': 0, 'kind': 'Block', 'stair': 156, 'id_in_image': 9, 'main_color': (102, 101, 98), 'second_color': (151, 149, 145), 'third_color': (236, 233, 226)},
 {'name': 'Chiseled Quartz Block', 'id': 155, 'data': 1, 'kind': 'Block', 'id_in_image': 36, 'main_color': (101, 99, 96), 'second_color': (231, 228, 219), 'third_color': (151, 150, 146)},
 {'name': 'Pillar Quartz Block', 'id': 155, 'data': 2, 'kind': 'Block', 'id_in_image': 63, 'main_color': (147, 145, 139), 'second_color': (233, 229, 222), 'third_color': (104, 103, 100)},
 {'name': 'Quartz Stairs', 'id': 156, 'data': 0, 'kind': 'Block', 'id_in_image': 90, 'main_color': (151, 149, 145), 'second_color': (235, 232, 225), 'third_color': (103, 102, 99)},
 {'name': 'Activator Rail', 'id': 157, 'data': 0, 'id_in_image': 117, 'main_color': (164, 164, 164), 'second_color': (104, 104, 104), 'third_color': (39, 0, 0)},
 {'name': 'Dropper', 'id': 158, 'data': 0, 'kind': 'Block', 'id_in_image': 144, 'main_color': (38, 38, 38), 'second_color': (100, 100, 100), 'third_color': (73, 73, 73)},
 {'name': 'White Stained Clay', 'id': 159, 'data': 0, 'kind': 'Block', 'id_in_image': 171, 'main_color': (132, 112, 102), 'second_color': (91, 77, 69), 'third_color': (209, 177, 161)},
 {'name': 'Orange Stained Clay', 'id': 159, 'data': 1, 'kind': 'Block', 'id_in_image': 198, 'main_color': (102, 53, 23), 'second_color': (70, 36, 16), 'third_color': (162, 84, 38)},
 {'name': 'Magenta Stained Clay', 'id': 159, 'data': 2, 'kind': 'Block', 'id_in_image': 248, 'main_color': (94, 55, 68), 'second_color': (65, 38, 47), 'third_color': (149, 88, 108)},
 {'name': 'Light Blue Stained Clay', 'id': 159, 'data': 3, 'kind': 'Block', 'id_in_image': 249, 'main_color': (71, 68, 87), 'second_color': (113, 108, 137), 'third_color': (48, 46, 59)},
 {'name': 'Yellow Stained Clay', 'id': 159, 'data': 4, 'kind': 'Block', 'id_in_image': 250, 'main_color': (118, 84, 22), 'second_color': (81, 57, 15), 'third_color': (186, 132, 35)},
 {'name': 'Lime Stained Clay', 'id': 159, 'data': 5, 'kind': 'Block', 'id_in_image': 251, 'main_color': (44, 51, 22), 'second_color': (102, 116, 52), 'third_color': (66, 74, 33)},
 {'name': 'Pink Stained Clay', 'id': 159, 'data': 6, 'kind': 'Block', 'id_in_image': 252, 'main_color': (70, 34, 34), 'second_color': (102, 49, 49), 'third_color': (161, 78, 78)},
 {'name': 'Gray Stained Clay', 'id': 159, 'data': 7, 'kind': 'Block', 'id_in_image': 10, 'main_color': (36, 27, 22), 'second_color': (25, 18, 15), 'third_color': (57, 42, 35)},
 {'name': 'Light Gray Stained Clay', 'id': 159, 'data': 8, 'kind': 'Block', 'id_in_image': 37, 'main_color': (58, 46, 42), 'second_color': (85, 67, 61), 'third_color': (135, 106, 97)},
 {'name': 'Cyan Stained Clay', 'id': 159, 'data': 9, 'kind': 'Block', 'id_in_image': 64, 'main_color': (54, 57, 57), 'second_color': (37, 39, 39), 'third_color': (86, 90, 90)},
 {'name': 'Purple Stained Clay', 'id': 159, 'data': 10, 'kind': 'Block', 'id_in_image': 225, 'main_color': (51, 30, 37), 'second_color': (75, 44, 54), 'third_color': (118, 70, 86)},
 {'name': 'Blue Stained Clay', 'id': 159, 'data': 11, 'kind': 'Block', 'id_in_image': 243, 'main_color': (47, 37, 57), 'second_color': (32, 25, 39), 'third_color': (74, 59, 91)},
 {'name': 'Brown Stained Clay', 'id': 159, 'data': 12, 'kind': 'Block', 'id_in_image': 244, 'main_color': (34, 23, 16), 'second_color': (49, 32, 22), 'third_color': (77, 51, 35)},
 {'name': 'Green Stained Clay', 'id': 159, 'data': 13, 'kind': 'Block', 'id_in_image': 245, 'main_color': (48, 52, 26), 'second_color': (33, 36, 18), 'third_color': (76, 83, 42)},
 {'name': 'Red Stained Clay', 'id': 159, 'data': 14, 'kind': 'Block', 'id_in_image': 246, 'main_color': (87, 37, 28), 'second_color': (62, 26, 20), 'third_color': (142, 60, 46)},
 {'name': 'Black Stained Clay', 'id': 159, 'data': 15, 'kind': 'Block', 'id_in_image': 247, 'main_color': (19, 12, 8), 'second_color': (37, 22, 16), 'third_color': (24, 16, 11)},
 {'name': 'White Stained Glass Pane', 'id': 160, 'data': 0, 'id_in_image': 118, 'main_color': (255, 255, 255), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Orange Stained Glass Pane', 'id': 160, 'data': 1, 'id_in_image': 145, 'main_color': (216, 127, 51), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Magenta Stained Glass Pane', 'id': 160, 'data': 2, 'id_in_image': 272, 'main_color': (178, 76, 216), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Light Blue Stained Glass Pane', 'id': 160, 'data': 3, 'id_in_image': 273, 'main_color': (102, 153, 216), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Yellow Stained Glass Pane', 'id': 160, 'data': 4, 'id_in_image': 274, 'main_color': (229, 229, 51), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Lime Stained Glass Pane', 'id': 160, 'data': 5, 'id_in_image': 275, 'main_color': (127, 204, 25), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Pink Stained Glass Pane', 'id': 160, 'data': 6, 'id_in_image': 276, 'main_color': (242, 127, 165), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Gray Stained Glass Pane', 'id': 160, 'data': 7, 'id_in_image': 277, 'main_color': (76, 76, 76), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Light Gray Stained Glass Pane', 'id': 160, 'data': 8, 'id_in_image': 278, 'main_color': (153, 153, 153), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Cyan Stained Glass Pane', 'id': 160, 'data': 9, 'id_in_image': 279, 'main_color': (76, 127, 153), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Purple Stained Glass Pane', 'id': 160, 'data': 10, 'id_in_image': 172, 'main_color': (127, 63, 178), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Blue Stained Glass Pane', 'id': 160, 'data': 11, 'id_in_image': 199, 'main_color': (51, 76, 178), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Brown Stained Glass Pane', 'id': 160, 'data': 12, 'id_in_image': 226, 'main_color': (102, 76, 51), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Green Stained Glass Pane', 'id': 160, 'data': 13, 'id_in_image': 253, 'main_color': (102, 127, 51), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Red Stained Glass Pane', 'id': 160, 'data': 14, 'id_in_image': 270, 'main_color': (153, 51, 51), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Black Stained Glass Pane', 'id': 160, 'data': 15, 'id_in_image': 271, 'main_color': (25, 25, 25), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'Acacia Leaves', 'id': 161, 'data': 0, 'kind': 'Block', 'id_in_image': 280, 'main_color': (17, 42, 6), 'second_color': (30, 77, 10), 'third_color': (56, 141, 18)},
 {'name': 'Dark Oak Leaves', 'id': 161, 'data': 1, 'kind': 'Block', 'id_in_image': 11, 'main_color': (17, 42, 6), 'second_color': (30, 77, 10), 'third_color': (56, 141, 18)},
 {'name': 'Acacia Wood', 'id': 162, 'data': 0, 'kind': 'Block', 'stair': 163, 'id_in_image': 38, 'main_color': (48, 45, 40), 'second_color': (168, 91, 59), 'third_color': (75, 67, 60)},
 {'name': 'Dark Oak Wood', 'id': 162, 'data': 1, 'kind': 'Block', 'stair': 164, 'id_in_image': 65, 'main_color': (33, 26, 15), 'second_color': (25, 19, 11), 'third_color': (88, 70, 46)},
 {'name': 'Acacia Wood Stairs', 'id': 163, 'data': 0, 'kind': 'Block', 'id_in_image': 92, 'main_color': (92, 49, 27), 'second_color': (168, 91, 50), 'third_color': (116, 64, 36)},
 {'name': 'Dark Oak Wood Stairs', 'id': 164, 'data': 0, 'kind': 'Block', 'id_in_image': 119, 'main_color': (41, 26, 12), 'second_color': (29, 18, 8), 'third_color': (44, 28, 12)},
 {'name': 'Slime Block', 'id': 165, 'data': 0, 'kind': 'Block', 'id_in_image': 146, 'main_color': (105, 150, 93), 'second_color': (77, 105, 70), 'third_color': (130, 187, 115)},
 {'name': 'Barrier', 'id': 166, 'data': 0, 'kind': 'Invisible', 'id_in_image': 173, 'main_color': (227, 0, 0), 'second_color': (206, 104, 106), 'third_color': (209, 24, 25)},
 {'name': 'Iron Trapdoor', 'id': 167, 'data': 0, 'id_in_image': 200, 'main_color': (200, 200, 200), 'second_color': (95, 95, 95), 'third_color': (153, 153, 153)},
 {'name': 'Prismarine', 'id': 168, 'data': 0, 'kind': 'Block', 'id_in_image': 227, 'main_color': (49, 87, 77), 'second_color': (72, 106, 96), 'third_color': (100, 166, 149)},
 {'name': 'Prismarine Bricks', 'id': 168, 'data': 1, 'kind': 'Block', 'id_in_image': 254, 'main_color': (52, 88, 78), 'second_color': (76, 113, 102), 'third_color': (103, 168, 150)},
 {'name': 'Dark Prismarine', 'id': 168, 'data': 2, 'kind': 'Block', 'id_in_image': 281, 'main_color': (29, 44, 37), 'second_color': (72, 102, 88), 'third_color': (54, 81, 71)},
 {'name': 'Sea Lantern', 'id': 169, 'data': 0, 'kind': 'Block', 'id_in_image': 297, 'main_color': (90, 101, 96), 'second_color': (139, 151, 145), 'third_color': (217, 230, 222)},
 {'name': 'Hay Bale', 'id': 170, 'data': 0, 'kind': 'Block', 'id_in_image': 302, 'main_color': (95, 80, 10), 'second_color': (81, 45, 9), 'third_color': (173, 144, 16)},
 {'name': 'White Carpet', 'id': 171, 'data': 0, 'id_in_image': 303, 'main_color': (227, 227, 227), 'second_color': (213, 213, 213), 'third_color': (165, 165, 165)},
 {'name': 'Orange Carpet', 'id': 171, 'data': 1, 'id_in_image': 304, 'main_color': (216, 118, 52), 'second_color': (221, 133, 74), 'third_color': (139, 79, 39)},
 {'name': 'Magenta Carpet', 'id': 171, 'data': 2, 'id_in_image': 66, 'main_color': (175, 69, 185), 'second_color': (186, 90, 194), 'third_color': (95, 42, 100)},
 {'name': 'Light Blue Carpet', 'id': 171, 'data': 3, 'id_in_image': 93, 'main_color': (112, 142, 203), 'second_color': (87, 123, 194), 'third_color': (73, 107, 175)},
 {'name': 'Yellow Carpet', 'id': 171, 'data': 4, 'id_in_image': 120, 'main_color': (167, 157, 36), 'second_color': (196, 184, 46), 'third_color': (96, 90, 21)},
 {'name': 'Lime Carpet', 'id': 171, 'data': 5, 'id_in_image': 147, 'main_color': (59, 159, 51), 'second_color': (68, 182, 58), 'third_color': (35, 93, 30)},
 {'name': 'Pink Carpet', 'id': 171, 'data': 6, 'id_in_image': 174, 'main_color': (213, 146, 164), 'second_color': (202, 117, 140), 'third_color': (194, 95, 122)},
 {'name': 'Gray Carpet', 'id': 171, 'data': 7, 'id_in_image': 201, 'main_color': (68, 68, 68), 'second_color': (58, 58, 58), 'third_color': (40, 40, 40)},
 {'name': 'Light Gray Carpet', 'id': 171, 'data': 8, 'id_in_image': 228, 'main_color': (154, 160, 160), 'second_color': (86, 90, 90), 'third_color': (125, 131, 131)},
 {'name': 'Cyan Carpet', 'id': 171, 'data': 9, 'id_in_image': 255, 'main_color': (47, 112, 140), 'second_color': (38, 91, 114), 'third_color': (54, 128, 158)},
 {'name': 'Purple Carpet', 'id': 171, 'data': 10, 'id_in_image': 305, 'main_color': (117, 55, 170), 'second_color': (138, 72, 194), 'third_color': (130, 61, 188)},
 {'name': 'Blue Carpet', 'id': 171, 'data': 11, 'id_in_image': 306, 'main_color': (46, 57, 141), 'second_color': (34, 42, 106), 'third_color': (52, 64, 162)},
 {'name': 'Brown Carpet', 'id': 171, 'data': 12, 'id_in_image': 307, 'main_color': (85, 54, 33), 'second_color': (71, 45, 27), 'third_color': (77, 48, 30)},
 {'name': 'Green Carpet', 'id': 171, 'data': 13, 'id_in_image': 308, 'main_color': (53, 71, 27), 'second_color': (44, 59, 23), 'third_color': (26, 35, 13)},
 {'name': 'Red Carpet', 'id': 171, 'data': 14, 'id_in_image': 12, 'main_color': (148, 50, 47), 'second_color': (153, 53, 49), 'third_color': (96, 33, 31)},
 {'name': 'Black Carpet', 'id': 171, 'data': 15, 'id_in_image': 39, 'main_color': (24, 21, 21), 'second_color': (14, 11, 11), 'third_color': (32, 28, 28)},
 {'name': 'Hardened Clay', 'id': 172, 'data': 0, 'kind': 'Block', 'id_in_image': 282, 'main_color': (80, 49, 35), 'second_color': (151, 93, 67), 'third_color': (147, 88, 61)},
 {'name': 'Block of Coal', 'id': 173, 'data': 0, 'kind': 'Block', 'id_in_image': 309, 'main_color': (9, 9, 9), 'second_color': (21, 21, 21), 'third_color': (36, 36, 36)},
 {'name': 'Packed Ice', 'id': 174, 'data': 0, 'kind': 'Block', 'id_in_image': 324, 'main_color': (71, 84, 106), 'second_color': (103, 122, 155), 'third_color': (166, 197, 249)},
 {'name': 'Sunflower', 'id': 175, 'data': 0, 'id_in_image': 325, 'main_color': (228, 171, 31), 'second_color': (241, 228, 36), 'third_color': (237, 212, 34)},
 {'name': 'Lilac', 'id': 175, 'data': 1, 'id_in_image': 326, 'main_color': (159, 120, 164), 'second_color': (82, 155, 46), 'third_color': (186, 157, 190)},
 {'name': 'Double Tallgrass', 'id': 175, 'data': 2, 'id_in_image': 327, 'main_color': (51, 78, 44), 'second_color': (67, 102, 58), 'third_color': (88, 134, 76)},
 {'name': 'Large Fern', 'id': 175, 'data': 3, 'id_in_image': 328, 'main_color': (54, 83, 47), 'second_color': (87, 134, 76), 'third_color': (68, 104, 59)},
 {'name': 'Rose Bush', 'id': 175, 'data': 4, 'kind': 'Flower', 'id_in_image': 329, 'main_color': (32, 89, 0), 'second_color': (161, 3, 7), 'third_color': (237, 6, 13)},
 {'name': 'Peony', 'id': 175, 'data': 5, 'kind': 'Flower', 'id_in_image': 330, 'main_color': (36, 78, 39), 'second_color': (226, 177, 247), 'third_color': (236, 210, 247)},
 {'name': 'Free-standing Banner', 'id': 176, 'data': 0, 'id_in_image': 331, 'main_color': (151, 151, 151), 'second_color': (86, 68, 41), 'third_color': (235, 235, 235)},
 {'name': 'Wall-mounted Banner', 'id': 177, 'data': 0, 'id_in_image': 332, 'main_color': (151, 151, 151), 'second_color': (86, 68, 41), 'third_color': (235, 235, 235)},
 {'name': 'Inverted Daylight Sensor', 'id': 178, 'data': 0, 'id_in_image': 333, 'main_color': (38, 32, 21), 'second_color': (136, 151, 174), 'third_color': (71, 61, 41)},
 {'name': 'Red Sandstone', 'id': 179, 'data': 0, 'kind': 'Block', 'stair': 180, 'id_in_image': 334, 'main_color': (73, 37, 12), 'second_color': (106, 54, 19), 'third_color': (166, 84, 29)},
 {'name': 'Smooth Red Sandstone', 'id': 179, 'data': 1, 'kind': 'Block', 'id_in_image': 335, 'main_color': (72, 36, 12), 'second_color': (104, 53, 18), 'third_color': (166, 84, 29)},
 {'name': 'Chiseled Red Sandstone', 'id': 179, 'data': 2, 'kind': 'Block', 'id_in_image': 336, 'main_color': (73, 37, 13), 'second_color': (107, 54, 19), 'third_color': (166, 84, 29)},
 {'name': 'Red Sandstone Stairs', 'id': 180, 'data': 0, 'kind': 'Block', 'id_in_image': 121, 'main_color': (107, 54, 19), 'second_color': (75, 38, 13), 'third_color': (166, 84, 29)},
 {'name': 'Double Red Sandstone Slab', 'id': 181, 'data': 0, 'kind': 'Block', 'id_in_image': 148, 'main_color': (73, 37, 12), 'second_color': (106, 54, 19), 'third_color': (166, 84, 29)},
 {'name': 'Red Sandstone Slab', 'id': 182, 'data': 0, 'kind': 'Block', 'id_in_image': 175, 'main_color': (88, 45, 15), 'second_color': (166, 84, 29), 'third_color': (167, 85, 30)},
 {'name': 'Spruce Fence Gate', 'id': 183, 'data': 0, 'kind': 'Block', 'id_in_image': 202, 'main_color': (45, 34, 20), 'second_color': (69, 52, 32), 'third_color': (128, 94, 54)},
 {'name': 'Birch Fence Gate', 'id': 184, 'data': 0, 'kind': 'Block', 'id_in_image': 229, 'main_color': (87, 80, 54), 'second_color': (157, 141, 98), 'third_color': (120, 109, 74)},
 {'name': 'Jungle Fence Gate', 'id': 185, 'data': 0, 'kind': 'Block', 'id_in_image': 256, 'main_color': (75, 54, 38), 'second_color': (103, 72, 48), 'third_color': (51, 35, 23)},
 {'name': 'Dark Oak Fence Gate', 'id': 186, 'data': 0, 'kind': 'Block', 'id_in_image': 283, 'main_color': (37, 24, 11), 'second_color': (28, 18, 8), 'third_color': (24, 15, 7)},
 {'name': 'Acacia Fence Gate', 'id': 187, 'data': 0, 'kind': 'Block', 'id_in_image': 310, 'main_color': (84, 45, 25), 'second_color': (158, 85, 47), 'third_color': (60, 32, 17)},
 {'name': 'Spruce Fence', 'id': 188, 'data': 0, 'kind': 'Block', 'id_in_image': 337, 'main_color': (46, 34, 20), 'second_color': (72, 54, 32), 'third_color': (105, 80, 48)},
 {'name': 'Birch Fence', 'id': 189, 'data': 0, 'kind': 'Block', 'id_in_image': 351, 'main_color': (87, 80, 55), 'second_color': (117, 107, 73), 'third_color': (154, 141, 98)},
 {'name': 'Jungle Fence', 'id': 190, 'data': 0, 'kind': 'Block', 'id_in_image': 354, 'main_color': (74, 53, 37), 'second_color': (103, 73, 49), 'third_color': (51, 35, 23)},
 {'name': 'Dark Oak Fence', 'id': 191, 'data': 0, 'kind': 'Block', 'id_in_image': 355, 'main_color': (38, 25, 11), 'second_color': (28, 18, 8), 'third_color': (35, 23, 10)},
 {'name': 'Acacia Fence', 'id': 192, 'data': 0, 'kind': 'Block', 'id_in_image': 356, 'main_color': (86, 46, 26), 'second_color': (167, 90, 50), 'third_color': (60, 32, 17)},
 {'name': 'Spruce Door Block', 'id': 193, 'data': 0, 'kind': 'Block', 'double': True, 'id_in_image': 357, 'main_color': (116, 86, 51), 'second_color': (81, 81, 81), 'third_color': (73, 54, 33)},
 {'name': 'Birch Door Block', 'id': 194, 'data': 0, 'kind': 'Block', 'double': True, 'id_in_image': 358, 'main_color': (213, 202, 140), 'second_color': (248, 244, 225), 'third_color': (153, 144, 100)},
 {'name': 'Jungle Door Block', 'id': 195, 'data': 0, 'kind': 'Block', 'double': True, 'id_in_image': 359, 'main_color': (178, 130, 94), 'second_color': (160, 116, 85), 'third_color': (145, 105, 77)},
 {'name': 'Acacia Door Block', 'id': 196, 'data': 0, 'kind': 'Block', 'double': True, 'id_in_image': 360, 'main_color': (177, 102, 64), 'second_color': (130, 75, 48), 'third_color': (86, 50, 32)},
 {'name': 'Dark Oak Door Block', 'id': 197, 'data': 0, 'kind': 'Block', 'double': True, 'id_in_image': 361, 'main_color': (71, 46, 22), 'second_color': (38, 24, 11), 'third_color': (17, 11, 5)},
 {'name': 'End Rod', 'id': 198, 'data': 0, 'id_in_image': 362, 'main_color': (108, 102, 99), 'second_color': (159, 152, 147), 'third_color': (76, 54, 76)},
 {'name': 'Chorus Plant', 'id': 199, 'data': 0, 'id_in_image': 363, 'main_color': (44, 23, 44), 'second_color': (79, 45, 79), 'third_color': (105, 85, 105)},
 {'name': 'Chorus Flower', 'id': 200, 'data': 0, 'id_in_image': 41, 'main_color': (46, 27, 46), 'second_color': (101, 87, 101), 'third_color': (78, 51, 78)},
 {'name': 'Purpur', 'id': 201, 'data': 0, 'kind': 'Block', 'stair': 203, 'id_in_image': 68, 'main_color': (103, 76, 103), 'second_color': (162, 115, 162), 'third_color': (74, 53, 74)},
 {'name': 'Purpur Pillar', 'id': 202, 'data': 0, 'kind': 'Block', 'id_in_image': 95, 'main_color': (105, 79, 105), 'second_color': (71, 51, 71), 'third_color': (157, 113, 157)},
 {'name': 'Purpur Stairs', 'id': 203, 'data': 0, 'kind': 'Block', 'id_in_image': 122, 'main_color': (103, 76, 103), 'second_color': (160, 114, 160), 'third_color': (74, 53, 74)},
 {'name': 'Purpur Double Slab', 'id': 204, 'data': 0, 'kind': 'Block', 'id_in_image': 149, 'main_color': (103, 76, 103), 'second_color': (162, 115, 162), 'third_color': (74, 53, 74)},
 {'name': 'Purpur Slab', 'id': 205, 'data': 0, 'kind': 'Block', 'id_in_image': 176, 'main_color': (160, 114, 160), 'second_color': (103, 77, 103), 'third_color': (74, 54, 74)},
 {'name': 'End Stone Bricks', 'id': 206, 'data': 0, 'kind': 'Block', 'id_in_image': 203, 'main_color': (103, 105, 78), 'second_color': (145, 150, 111), 'third_color': (223, 229, 167)},
 {'name': 'Beetroot Seeds', 'id': 207, 'data': 0, 'id_in_image': 230, 'main_color': (133, 111, 74), 'second_color': (222, 176, 117), 'third_color': (0, 0, 0)},
 {'name': 'Grass Path', 'id': 208, 'data': 0, 'id_in_image': 257, 'main_color': (73, 53, 35), 'second_color': (103, 80, 49), 'third_color': (50, 35, 24)},
 {'name': 'End Gateway', 'id': 209, 'data': 0, 'id_in_image': 284, 'main_color': (18, 17, 28), 'second_color': (35, 50, 80), 'third_color': (41, 77, 81)},
 {'name': 'Repeating Command Block', 'id': 210, 'data': 0, 'kind': 'Block', 'id_in_image': 338, 'main_color': (47, 36, 83), 'second_color': (66, 55, 105), 'third_color': (30, 25, 47)},
 {'name': 'Chain Command Block', 'id': 211, 'data': 0, 'kind': 'Block', 'id_in_image': 365, 'main_color': (84, 102, 95), 'second_color': (33, 45, 40), 'third_color': (54, 79, 68)},
 {'name': 'Frosted Ice', 'id': 212, 'data': 0, 'kind': 'Block', 'id_in_image': 378, 'main_color': (75, 106, 160), 'second_color': (51, 73, 110), 'third_color': (118, 167, 252)},
 {'name': 'Magma Block', 'id': 213, 'data': 0, 'kind': 'Block', 'id_in_image': 379, 'main_color': (42, 20, 14), 'second_color': (89, 42, 19), 'third_color': (151, 78, 20)},
 {'name': 'Nether Wart Block', 'id': 214, 'data': 0, 'kind': 'Block', 'id_in_image': 380, 'main_color': (53, 0, 5), 'second_color': (77, 1, 10), 'third_color': (113, 3, 15)},
 {'name': 'Red Nether Brick', 'id': 215, 'data': 0, 'kind': 'Block', 'id_in_image': 381, 'main_color': (45, 2, 9), 'second_color': (82, 3, 16), 'third_color': (29, 0, 5)},
 {'name': 'Bone Block', 'id': 216, 'data': 0, 'kind': 'Block', 'id_in_image': 382, 'main_color': (95, 97, 87), 'second_color': (155, 159, 137), 'third_color': (136, 139, 121)},
 {'name': 'Structure Void', 'id': 217, 'data': 0, 'id_in_image': 383, 'main_color': (15, 93, 100), 'second_color': (26, 80, 86), 'third_color': (75, 106, 109)},
 {'name': 'Observer', 'id': 218, 'data': 0, 'kind': 'Block', 'id_in_image': 384, 'main_color': (33, 33, 33), 'second_color': (90, 90, 90), 'third_color': (39, 37, 37)},
 {'name': 'White Shulker Box', 'id': 219, 'data': 0, 'kind': 'Block', 'id_in_image': 385, 'main_color': (91, 89, 89), 'second_color': (216, 213, 213), 'third_color': (154, 151, 151)},
 {'name': 'Orange Shulker Box', 'id': 220, 'data': 0, 'kind': 'Block', 'id_in_image': 387, 'main_color': (91, 45, 14), 'second_color': (161, 84, 32), 'third_color': (206, 116, 56)},
 {'name': 'Magenta Shulker Box', 'id': 221, 'data': 0, 'kind': 'Block', 'id_in_image': 388, 'main_color': (85, 39, 90), 'second_color': (163, 77, 171), 'third_color': (187, 101, 195)},
 {'name': 'Light Blue Shulker Box', 'id': 222, 'data': 0, 'kind': 'Block', 'id_in_image': 389, 'main_color': (31, 50, 85), 'second_color': (47, 73, 117), 'third_color': (100, 141, 202)},
 {'name': 'Yellow Shulker Box', 'id': 223, 'data': 0, 'kind': 'Block', 'id_in_image': 390, 'main_color': (93, 88, 17), 'second_color': (172, 161, 37), 'third_color': (193, 183, 61)},
 {'name': 'Lime Shulker Box', 'id': 224, 'data': 0, 'kind': 'Block', 'id_in_image': 391, 'main_color': (27, 88, 20), 'second_color': (71, 183, 59), 'third_color': (45, 157, 33)},
 {'name': 'Pink Shulker Box', 'id': 225, 'data': 0, 'kind': 'Block', 'id_in_image': 392, 'main_color': (79, 39, 49), 'second_color': (150, 89, 106), 'third_color': (100, 57, 69)},
 {'name': 'Gray Shulker Box', 'id': 226, 'data': 0, 'kind': 'Block', 'id_in_image': 123, 'main_color': (39, 38, 38), 'second_color': (37, 36, 36), 'third_color': (77, 76, 76)},
 {'name': 'Light Gray Shulker Box', 'id': 227, 'data': 0, 'kind': 'Block', 'id_in_image': 366, 'main_color': (85, 83, 83), 'second_color': (154, 151, 151), 'third_color': (53, 52, 52)},
 {'name': 'Cyan Shulker Box', 'id': 228, 'data': 0, 'kind': 'Block', 'id_in_image': 393, 'main_color': (34, 77, 95), 'second_color': (25, 57, 70), 'third_color': (16, 46, 58)},
 {'name': 'Purple Shulker Box', 'id': 229, 'data': 0, 'kind': 'Block', 'id_in_image': 405, 'main_color': (75, 52, 75), 'second_color': (104, 73, 104), 'third_color': (57, 39, 57)},
 {'name': 'Blue Shulker Box', 'id': 230, 'data': 0, 'kind': 'Block', 'id_in_image': 407, 'main_color': (39, 45, 90), 'second_color': (76, 86, 163), 'third_color': (100, 112, 200)},
 {'name': 'Brown Shulker Box', 'id': 231, 'data': 0, 'kind': 'Block', 'id_in_image': 408, 'main_color': (53, 40, 32), 'second_color': (137, 108, 89), 'third_color': (72, 54, 42)},
 {'name': 'Green Shulker Box', 'id': 232, 'data': 0, 'kind': 'Block', 'id_in_image': 409, 'main_color': (41, 50, 28), 'second_color': (57, 69, 40), 'third_color': (75, 89, 54)},
 {'name': 'Red Shulker Box', 'id': 233, 'data': 0, 'kind': 'Block', 'id_in_image': 410, 'main_color': (93, 37, 35), 'second_color': (194, 88, 85), 'third_color': (181, 75, 72)},
 {'name': 'Black Shulker Box', 'id': 234, 'data': 0, 'kind': 'Block', 'id_in_image': 411, 'main_color': (23, 21, 21), 'second_color': (12, 11, 11), 'third_color': (50, 48, 48)},
 {'name': 'White Glazed Terracotta', 'id': 235, 'data': 0, 'kind': 'Block', 'id_in_image': 412, 'main_color': (155, 158, 157), 'second_color': (106, 108, 107), 'third_color': (245, 250, 249)},
 {'name': 'Orange Glazed Terracotta', 'id': 236, 'data': 0, 'kind': 'Block', 'id_in_image': 413, 'main_color': (13, 94, 94), 'second_color': (103, 48, 6), 'third_color': (157, 86, 20)},
 {'name': 'Magenta Glazed Terracotta', 'id': 237, 'data': 0, 'kind': 'Block', 'id_in_image': 414, 'main_color': (96, 35, 91), 'second_color': (147, 91, 133), 'third_color': (211, 94, 205)},
 {'name': 'Light Blue Glazed Terracotta', 'id': 238, 'data': 0, 'kind': 'Block', 'id_in_image': 415, 'main_color': (25, 82, 108), 'second_color': (21, 44, 84), 'third_color': (42, 116, 141)},
 {'name': 'Yellow Glazed Terracotta', 'id': 239, 'data': 0, 'kind': 'Block', 'id_in_image': 416, 'main_color': (105, 78, 22), 'second_color': (162, 149, 105), 'third_color': (153, 112, 13)},
 {'name': 'Lime Glazed Terracotta', 'id': 240, 'data': 0, 'kind': 'Block', 'id_in_image': 420, 'main_color': (52, 87, 12), 'second_color': (87, 99, 23), 'third_color': (88, 149, 21)},
 {'name': 'Pink Glazed Terracotta', 'id': 241, 'data': 0, 'kind': 'Block', 'id_in_image': 16, 'main_color': (104, 80, 87), 'second_color': (147, 81, 103), 'third_color': (155, 115, 129)},
 {'name': 'Gray Glazed Terracotta', 'id': 242, 'data': 0, 'kind': 'Block', 'id_in_image': 43, 'main_color': (36, 40, 42), 'second_color': (80, 87, 89), 'third_color': (58, 69, 72)},
 {'name': 'Light Gray Glazed Terracotta', 'id': 243, 'data': 0, 'kind': 'Block', 'id_in_image': 70, 'main_color': (88, 91, 92), 'second_color': (136, 138, 138), 'third_color': (32, 78, 80)},
 {'name': 'Cyan Glazed Terracotta', 'id': 244, 'data': 0, 'kind': 'Block', 'id_in_image': 97, 'main_color': (27, 41, 45), 'second_color': (14, 83, 88), 'third_color': (22, 163, 163)},
 {'name': 'Purple Glazed Terracotta', 'id': 245, 'data': 0, 'kind': 'Block', 'id_in_image': 124, 'main_color': (53, 18, 78), 'second_color': (30, 29, 35), 'third_color': (76, 29, 106)},
 {'name': 'Blue Glazed Terracotta', 'id': 246, 'data': 0, 'kind': 'Block', 'id_in_image': 151, 'main_color': (29, 38, 87), 'second_color': (19, 17, 43), 'third_color': (52, 71, 152)},
 {'name': 'Brown Glazed Terracotta', 'id': 247, 'data': 0, 'kind': 'Block', 'id_in_image': 178, 'main_color': (40, 39, 32), 'second_color': (81, 54, 36), 'third_color': (146, 104, 77)},
 {'name': 'Green Glazed Terracotta', 'id': 248, 'data': 0, 'kind': 'Block', 'id_in_image': 205, 'main_color': (39, 50, 16), 'second_color': (79, 102, 32), 'third_color': (55, 72, 21)},
 {'name': 'Red Glazed Terracotta', 'id': 249, 'data': 0, 'kind': 'Block', 'id_in_image': 232, 'main_color': (91, 27, 24), 'second_color': (148, 43, 39), 'third_color': (206, 77, 70)},
 {'name': 'Black Glazed Terracotta', 'id': 250, 'data': 0, 'kind': 'Block', 'id_in_image': 286, 'main_color': (24, 18, 20), 'second_color': (83, 18, 18), 'third_color': (145, 32, 32)},
 {'name': 'White Concrete', 'id': 251, 'data': 0, 'kind': 'Block', 'id_in_image': 313, 'main_color': (131, 135, 136), 'second_color': (89, 92, 92), 'third_color': (207, 213, 214)},
 {'name': 'Orange Concrete', 'id': 251, 'data': 1, 'kind': 'Block', 'id_in_image': 340, 'main_color': (142, 61, 0), 'second_color': (97, 42, 0), 'third_color': (224, 97, 0)},
 {'name': 'Magenta Concrete', 'id': 251, 'data': 2, 'kind': 'Block', 'id_in_image': 435, 'main_color': (73, 20, 68), 'second_color': (169, 48, 159), 'third_color': (107, 30, 101)},
 {'name': 'Light Blue Concrete', 'id': 251, 'data': 3, 'kind': 'Block', 'id_in_image': 436, 'main_color': (22, 87, 126), 'second_color': (15, 59, 86), 'third_color': (35, 137, 198)},
 {'name': 'Yellow Concrete', 'id': 251, 'data': 4, 'kind': 'Block', 'id_in_image': 437, 'main_color': (104, 76, 9), 'second_color': (240, 175, 21), 'third_color': (152, 111, 13)},
 {'name': 'Lime Concrete', 'id': 251, 'data': 5, 'kind': 'Block', 'id_in_image': 438, 'main_color': (59, 107, 15), 'second_color': (40, 73, 10), 'third_color': (93, 168, 24)},
 {'name': 'Pink Concrete', 'id': 251, 'data': 6, 'kind': 'Block', 'id_in_image': 439, 'main_color': (135, 64, 90), 'second_color': (92, 43, 62), 'third_color': (213, 100, 142)},
 {'name': 'Gray Concrete', 'id': 251, 'data': 7, 'kind': 'Block', 'id_in_image': 440, 'main_color': (34, 36, 39), 'second_color': (23, 25, 26), 'third_color': (54, 57, 61)},
 {'name': 'Light Gray Concrete', 'id': 251, 'data': 8, 'kind': 'Block', 'id_in_image': 441, 'main_color': (54, 54, 49), 'second_color': (125, 125, 115), 'third_color': (79, 79, 72)},
 {'name': 'Cyan Concrete', 'id': 251, 'data': 9, 'kind': 'Block', 'id_in_image': 442, 'main_color': (13, 75, 86), 'second_color': (9, 51, 59), 'third_color': (21, 119, 136)},
 {'name': 'Purple Concrete', 'id': 251, 'data': 10, 'kind': 'Block', 'id_in_image': 367, 'main_color': (43, 13, 67), 'second_color': (64, 20, 99), 'third_color': (100, 31, 156)},
 {'name': 'Blue Concrete', 'id': 251, 'data': 11, 'kind': 'Block', 'id_in_image': 394, 'main_color': (28, 29, 91), 'second_color': (19, 20, 62), 'third_color': (44, 46, 143)},
 {'name': 'Brown Concrete', 'id': 251, 'data': 12, 'kind': 'Block', 'id_in_image': 421, 'main_color': (61, 37, 20), 'second_color': (41, 26, 13), 'third_color': (97, 60, 32)},
 {'name': 'Green Concrete', 'id': 251, 'data': 13, 'kind': 'Block', 'id_in_image': 432, 'main_color': (46, 57, 23), 'second_color': (32, 39, 16), 'third_color': (73, 91, 36)},
 {'name': 'Red Concrete', 'id': 251, 'data': 14, 'kind': 'Block', 'id_in_image': 433, 'main_color': (90, 20, 20), 'second_color': (61, 14, 14), 'third_color': (142, 32, 32)},
 {'name': 'Black Concrete', 'id': 251, 'data': 15, 'kind': 'Block', 'id_in_image': 434, 'main_color': (5, 6, 10), 'second_color': (0, 0, 0), 'third_color': (0, 0, 0)},
 {'name': 'White Concrete Powder', 'id': 252, 'data': 0, 'id_in_image': 443, 'main_color': (143, 144, 144), 'second_color': (226, 227, 228), 'third_color': (99, 100, 100)},
 {'name': 'Orange Concrete Powder', 'id': 252, 'data': 1, 'id_in_image': 444, 'main_color': (144, 84, 20), 'second_color': (98, 56, 12), 'third_color': (231, 135, 35)},
 {'name': 'Magenta Concrete Powder', 'id': 252, 'data': 2, 'id_in_image': 71, 'main_color': (100, 43, 96), 'second_color': (177, 75, 169), 'third_color': (195, 85, 186)},
 {'name': 'Light Blue Concrete Powder', 'id': 252, 'data': 3, 'id_in_image': 98, 'main_color': (32, 79, 94), 'second_color': (46, 114, 135), 'third_color': (72, 180, 212)},
 {'name': 'Yellow Concrete Powder', 'id': 252, 'data': 4, 'id_in_image': 125, 'main_color': (101, 86, 23), 'second_color': (146, 122, 30), 'third_color': (234, 200, 52)},
 {'name': 'Lime Concrete Powder', 'id': 252, 'data': 5, 'id_in_image': 152, 'main_color': (54, 81, 17), 'second_color': (78, 118, 25), 'third_color': (115, 176, 38)},
 {'name': 'Pink Concrete Powder', 'id': 252, 'data': 6, 'id_in_image': 179, 'main_color': (144, 95, 113), 'second_color': (227, 148, 177), 'third_color': (101, 70, 81)},
 {'name': 'Gray Concrete Powder', 'id': 252, 'data': 7, 'id_in_image': 206, 'main_color': (40, 43, 45), 'second_color': (76, 81, 84), 'third_color': (57, 61, 64)},
 {'name': 'Light Gray Concrete Powder', 'id': 252, 'data': 8, 'id_in_image': 233, 'main_color': (88, 88, 84), 'second_color': (155, 155, 148), 'third_color': (65, 65, 62)},
 {'name': 'Cyan Concrete Powder', 'id': 252, 'data': 9, 'id_in_image': 260, 'main_color': (20, 85, 90), 'second_color': (36, 147, 156), 'third_color': (15, 61, 66)},
 {'name': 'Purple Concrete Powder', 'id': 252, 'data': 10, 'id_in_image': 445, 'main_color': (82, 34, 110), 'second_color': (56, 23, 76), 'third_color': (134, 57, 180)},
 {'name': 'Blue Concrete Powder', 'id': 252, 'data': 11, 'id_in_image': 446, 'main_color': (37, 39, 89), 'second_color': (70, 74, 168), 'third_color': (62, 65, 155)},
 {'name': 'Brown Concrete Powder', 'id': 252, 'data': 12, 'id_in_image': 447, 'main_color': (78, 53, 33), 'second_color': (54, 36, 23), 'third_color': (117, 79, 49)},
 {'name': 'Green Concrete Powder', 'id': 252, 'data': 13, 'id_in_image': 448, 'main_color': (42, 51, 19), 'second_color': (86, 106, 39), 'third_color': (59, 72, 29)},
 {'name': 'Red Concrete Powder', 'id': 252, 'data': 14, 'id_in_image': 17, 'main_color': (89, 28, 27), 'second_color': (167, 53, 50), 'third_color': (205, 89, 81)},
 {'name': 'Black Concrete Powder', 'id': 252, 'data': 15, 'id_in_image': 44, 'main_color': (10, 11, 14), 'second_color': (19, 20, 24), 'third_color': (32, 33, 37)},
 {'name': 'Structure Block', 'id': 255, 'data': 0, 'id_in_image': 287, 'main_color': (31, 21, 24), 'second_color': (97, 91, 92), 'third_color': (155, 152, 153)},
 {'name': 'Iron Shovel', 'id': 256, 'data': 0, 'id_in_image': 314, 'main_color': (229, 229, 229), 'second_color': (68, 68, 68), 'third_color': (73, 54, 21)},
 {'name': 'Iron Pickaxe', 'id': 257, 'data': 0, 'id_in_image': 341, 'main_color': (68, 68, 68), 'second_color': (208, 208, 208), 'third_color': (73, 54, 21)},
 {'name': 'Iron Axe', 'id': 258, 'data': 0, 'id_in_image': 368, 'main_color': (213, 213, 213), 'second_color': (68, 68, 68), 'third_color': (73, 54, 21)},
 {'name': 'Flint and Steel', 'id': 259, 'data': 0, 'id_in_image': 395, 'main_color': (26, 26, 26), 'second_color': (82, 82, 82), 'third_color': (173, 173, 173)},
 {'name': 'Apple', 'id': 260, 'data': 0, 'id_in_image': 449, 'main_color': (255, 28, 43), 'second_color': (96, 16, 14), 'third_color': (180, 19, 30)},
 {'name': 'Bow', 'id': 261, 'data': 0, 'id_in_image': 459, 'main_color': (73, 54, 21), 'second_color': (82, 82, 82), 'third_color': (40, 30, 11)},
 {'name': 'Arrow', 'id': 262, 'data': 0, 'id_in_image': 460, 'main_color': (48, 42, 29), 'second_color': (219, 219, 219), 'third_color': (137, 103, 39)},
 {'name': 'Coal', 'id': 263, 'data': 0, 'id_in_image': 461, 'main_color': (23, 23, 23), 'second_color': (5, 5, 5), 'third_color': (41, 41, 41)},
 {'name': 'Charcoal', 'id': 263, 'data': 1, 'id_in_image': 462, 'main_color': (24, 21, 17), 'second_color': (78, 69, 55), 'third_color': (66, 59, 47)},
 {'name': 'Diamond', 'id': 264, 'data': 0, 'id_in_image': 463, 'main_color': (12, 55, 48), 'second_color': (239, 253, 251), 'third_color': (148, 244, 228)},
 {'name': 'Iron Ingot', 'id': 265, 'data': 0, 'id_in_image': 464, 'main_color': (93, 93, 93), 'second_color': (151, 151, 151), 'third_color': (225, 225, 225)},
 {'name': 'Gold Ingot', 'id': 266, 'data': 0, 'id_in_image': 465, 'main_color': (231, 231, 3), 'second_color': (255, 255, 139), 'third_color': (80, 80, 0)},
 {'name': 'Iron Sword', 'id': 267, 'data': 0, 'id_in_image': 466, 'main_color': (40, 39, 37), 'second_color': (240, 240, 240), 'third_color': (73, 73, 73)},
 {'name': 'Wooden Sword', 'id': 268, 'data': 0, 'id_in_image': 467, 'main_color': (47, 35, 13), 'second_color': (134, 101, 38), 'third_color': (106, 80, 30)},
 {'name': 'Wooden Shovel', 'id': 269, 'data': 0, 'id_in_image': 468, 'main_color': (48, 36, 13), 'second_color': (135, 101, 38), 'third_color': (110, 83, 31)},
 {'name': 'Wooden Pickaxe', 'id': 270, 'data': 0, 'id_in_image': 470, 'main_color': (50, 37, 14), 'second_color': (108, 81, 31), 'third_color': (73, 54, 21)},
 {'name': 'Wooden Axe', 'id': 271, 'data': 0, 'id_in_image': 471, 'main_color': (49, 36, 14), 'second_color': (105, 79, 30), 'third_color': (73, 54, 21)},
 {'name': 'Stone Sword', 'id': 272, 'data': 0, 'id_in_image': 472, 'main_color': (81, 81, 81), 'second_color': (58, 57, 56), 'third_color': (147, 147, 147)},
 {'name': 'Stone Shovel', 'id': 273, 'data': 0, 'id_in_image': 473, 'main_color': (86, 86, 86), 'second_color': (148, 148, 148), 'third_color': (73, 54, 21)},
 {'name': 'Stone Pickaxe', 'id': 274, 'data': 0, 'id_in_image': 474, 'main_color': (87, 87, 87), 'second_color': (73, 54, 21), 'third_color': (40, 30, 11)},
 {'name': 'Stone Axe', 'id': 275, 'data': 0, 'id_in_image': 475, 'main_color': (96, 96, 96), 'second_color': (73, 54, 21), 'third_color': (40, 30, 11)},
 {'name': 'Diamond Sword', 'id': 276, 'data': 0, 'id_in_image': 476, 'main_color': (11, 47, 40), 'second_color': (51, 235, 203), 'third_color': (43, 199, 172)},
 {'name': 'Diamond Shovel', 'id': 277, 'data': 0, 'id_in_image': 18, 'main_color': (25, 48, 35), 'second_color': (73, 54, 21), 'third_color': (51, 235, 203)},
 {'name': 'Diamond Pickaxe', 'id': 278, 'data': 0, 'id_in_image': 45, 'main_color': (22, 52, 40), 'second_color': (73, 54, 21), 'third_color': (39, 178, 154)},
 {'name': 'Diamond Axe', 'id': 279, 'data': 0, 'id_in_image': 72, 'main_color': (24, 50, 37), 'second_color': (39, 178, 154), 'third_color': (73, 54, 21)},
 {'name': 'Stick', 'id': 280, 'data': 0, 'id_in_image': 126, 'main_color': (40, 30, 11), 'second_color': (73, 54, 21), 'third_color': (137, 103, 39)},
 {'name': 'Bowl', 'id': 281, 'data': 0, 'id_in_image': 153, 'main_color': (31, 21, 2), 'second_color': (113, 79, 15), 'third_color': (83, 57, 9)},
 {'name': 'Mushroom Stew', 'id': 282, 'data': 0, 'id_in_image': 180, 'main_color': (40, 27, 3), 'second_color': (204, 145, 114), 'third_color': (145, 109, 85)},
 {'name': 'Golden Sword', 'id': 283, 'data': 0, 'id_in_image': 207, 'main_color': (59, 59, 37), 'second_color': (223, 227, 84), 'third_color': (156, 158, 69)},
 {'name': 'Golden Shovel', 'id': 284, 'data': 0, 'id_in_image': 234, 'main_color': (52, 47, 25), 'second_color': (224, 228, 84), 'third_color': (73, 54, 21)},
 {'name': 'Golden Pickaxe', 'id': 285, 'data': 0, 'id_in_image': 261, 'main_color': (54, 51, 28), 'second_color': (73, 54, 21), 'third_color': (188, 191, 77)},
 {'name': 'Golden Axe', 'id': 286, 'data': 0, 'id_in_image': 288, 'main_color': (52, 48, 26), 'second_color': (182, 185, 75), 'third_color': (73, 54, 21)},
 {'name': 'String', 'id': 287, 'data': 0, 'id_in_image': 315, 'main_color': (68, 68, 68), 'second_color': (247, 247, 247), 'third_color': (219, 219, 219)},
 {'name': 'Feather', 'id': 288, 'data': 0, 'id_in_image': 342, 'main_color': (235, 235, 235), 'second_color': (104, 104, 104), 'third_color': (137, 137, 137)},
 {'name': 'Gunpowder', 'id': 289, 'data': 0, 'id_in_image': 369, 'main_color': (74, 74, 74), 'second_color': (45, 45, 45), 'third_color': (114, 114, 114)},
 {'name': 'Wooden Hoe', 'id': 290, 'data': 0, 'id_in_image': 423, 'main_color': (47, 35, 13), 'second_color': (108, 81, 31), 'third_color': (73, 54, 21)},
 {'name': 'Stone Hoe', 'id': 291, 'data': 0, 'id_in_image': 450, 'main_color': (87, 87, 87), 'second_color': (73, 54, 21), 'third_color': (40, 30, 11)},
 {'name': 'Iron Hoe', 'id': 292, 'data': 0, 'id_in_image': 477, 'main_color': (68, 68, 68), 'second_color': (73, 54, 21), 'third_color': (40, 30, 11)},
 {'name': 'Diamond Hoe', 'id': 293, 'data': 0, 'id_in_image': 486, 'main_color': (26, 47, 33), 'second_color': (73, 54, 21), 'third_color': (104, 78, 30)},
 {'name': 'Golden Hoe', 'id': 294, 'data': 0, 'id_in_image': 487, 'main_color': (51, 46, 24), 'second_color': (73, 54, 21), 'third_color': (104, 78, 30)},
 {'name': 'Wheat Seeds', 'id': 295, 'data': 0, 'id_in_image': 488, 'main_color': (46, 67, 12), 'second_color': (105, 176, 56), 'third_color': (0, 226, 16)},
 {'name': 'Wheat', 'id': 296, 'data': 0, 'id_in_image': 489, 'main_color': (106, 100, 30), 'second_color': (163, 167, 46), 'third_color': (36, 51, 8)},
 {'name': 'Bread', 'id': 297, 'data': 0, 'id_in_image': 490, 'main_color': (147, 109, 34), 'second_color': (105, 77, 23), 'third_color': (55, 41, 13)},
 {'name': 'Leather Helmet', 'id': 298, 'data': 0, 'id_in_image': 491, 'main_color': (47, 21, 12), 'second_color': (198, 92, 53), 'third_color': (84, 39, 22)},
 {'name': 'Leather Tunic', 'id': 299, 'data': 0, 'id_in_image': 492, 'main_color': (198, 92, 53), 'second_color': (158, 73, 42), 'third_color': (61, 28, 16)},
 {'name': 'Leather Pants', 'id': 300, 'data': 0, 'id_in_image': 497, 'main_color': (198, 92, 53), 'second_color': (84, 39, 22), 'third_color': (158, 73, 42)},
 {'name': 'Leather Boots', 'id': 301, 'data': 0, 'id_in_image': 498, 'main_color': (84, 39, 22), 'second_color': (61, 28, 16), 'third_color': (158, 73, 42)},
 {'name': 'Chainmail Helmet', 'id': 302, 'data': 0, 'id_in_image': 499, 'main_color': (33, 31, 31), 'second_color': (100, 100, 100), 'third_color': (203, 203, 203)},
 {'name': 'Chainmail Chestplate', 'id': 303, 'data': 0, 'id_in_image': 500, 'main_color': (100, 100, 100), 'second_color': (35, 35, 35), 'third_color': (199, 199, 199)},
 {'name': 'Chainmail Leggings', 'id': 304, 'data': 0, 'id_in_image': 501, 'main_color': (37, 37, 37), 'second_color': (97, 97, 97), 'third_color': (205, 205, 205)},
 {'name': 'Chainmail Boots', 'id': 305, 'data': 0, 'id_in_image': 502, 'main_color': (36, 36, 36), 'second_color': (95, 95, 95), 'third_color': (203, 203, 203)},
 {'name': 'Iron Helmet', 'id': 306, 'data': 0, 'id_in_image': 503, 'main_color': (27, 20, 17), 'second_color': (206, 206, 206), 'third_color': (45, 45, 45)},
 {'name': 'Iron Chestplate', 'id': 307, 'data': 0, 'id_in_image': 504, 'main_color': (198, 198, 198), 'second_color': (33, 33, 33), 'third_color': (150, 150, 150)},
 {'name': 'Iron Leggings', 'id': 308, 'data': 0, 'id_in_image': 19, 'main_color': (35, 35, 35), 'second_color': (198, 198, 198), 'third_color': (150, 150, 150)},
 {'name': 'Iron Boots', 'id': 309, 'data': 0, 'id_in_image': 46, 'main_color': (45, 45, 45), 'second_color': (25, 25, 25), 'third_color': (150, 150, 150)},
 {'name': 'Diamond Helmet', 'id': 310, 'data': 0, 'id_in_image': 154, 'main_color': (34, 30, 28), 'second_color': (51, 235, 203), 'third_color': (30, 138, 119)},
 {'name': 'Diamond Chestplate', 'id': 311, 'data': 0, 'id_in_image': 181, 'main_color': (51, 235, 203), 'second_color': (33, 33, 33), 'third_color': (30, 138, 119)},
 {'name': 'Diamond Leggings', 'id': 312, 'data': 0, 'id_in_image': 208, 'main_color': (35, 35, 35), 'second_color': (51, 235, 203), 'third_color': (30, 138, 119)},
 {'name': 'Diamond Boots', 'id': 313, 'data': 0, 'id_in_image': 235, 'main_color': (35, 35, 35), 'second_color': (30, 138, 119), 'third_color': (51, 235, 203)},
 {'name': 'Golden Helmet', 'id': 314, 'data': 0, 'id_in_image': 262, 'main_color': (34, 30, 28), 'second_color': (234, 238, 87), 'third_color': (219, 162, 19)},
 {'name': 'Golden Chestplate', 'id': 315, 'data': 0, 'id_in_image': 289, 'main_color': (234, 238, 87), 'second_color': (33, 33, 33), 'third_color': (219, 162, 19)},
 {'name': 'Golden Leggings', 'id': 316, 'data': 0, 'id_in_image': 316, 'main_color': (35, 35, 35), 'second_color': (234, 238, 87), 'third_color': (219, 162, 19)},
 {'name': 'Golden Boots', 'id': 317, 'data': 0, 'id_in_image': 343, 'main_color': (35, 35, 35), 'second_color': (219, 162, 19), 'third_color': (234, 238, 87)},
 {'name': 'Flint', 'id': 318, 'data': 0, 'id_in_image': 370, 'main_color': (28, 28, 28), 'second_color': (40, 40, 40), 'third_color': (114, 114, 114)},
 {'name': 'Raw Porkchop', 'id': 319, 'data': 0, 'id_in_image': 397, 'main_color': (246, 115, 115), 'second_color': (250, 161, 161), 'third_color': (81, 38, 38)},
 {'name': 'Cooked Porkchop', 'id': 320, 'data': 0, 'id_in_image': 451, 'main_color': (30, 25, 12), 'second_color': (177, 153, 105), 'third_color': (220, 202, 162)},
 {'name': 'Painting', 'id': 321, 'data': 0, 'id_in_image': 478, 'main_color': (165, 160, 152), 'second_color': (76, 56, 17), 'third_color': (41, 35, 23)},
 {'name': 'Golden Apple', 'id': 322, 'data': 0, 'id_in_image': 505, 'main_color': (234, 238, 87), 'second_color': (27, 24, 23), 'third_color': (219, 162, 19)},
 {'name': 'Enchanted Golden Apple', 'id': 322, 'data': 1, 'id_in_image': 513, 'main_color': (234, 238, 87), 'second_color': (27, 24, 23), 'third_color': (219, 162, 19)},
 {'name': 'Sign', 'id': 323, 'data': 0, 'id_in_image': 514, 'main_color': (159, 132, 77), 'second_color': (105, 84, 50), 'third_color': (46, 33, 12)},
 {'name': 'Oak Door', 'id': 324, 'data': 0, 'kind': 'Block', 'double': True, 'id_in_image': 515, 'main_color': (159, 132, 77), 'second_color': (105, 84, 51), 'third_color': (65, 52, 33)},
 {'name': 'Bucket', 'id': 325, 'data': 0, 'id_in_image': 516, 'main_color': (102, 102, 102), 'second_color': (53, 53, 53), 'third_color': (155, 155, 155)},
 {'name': 'Water Bucket', 'id': 326, 'data': 0, 'id_in_image': 517, 'main_color': (53, 53, 53), 'second_color': (222, 222, 222), 'third_color': (53, 96, 219)},
 {'name': 'Lava Bucket', 'id': 327, 'data': 0, 'id_in_image': 518, 'main_color': (53, 53, 53), 'second_color': (222, 222, 222), 'third_color': (89, 89, 89)},
 {'name': 'Minecart', 'id': 328, 'data': 0, 'id_in_image': 519, 'main_color': (39, 39, 41), 'second_color': (22, 23, 23), 'third_color': (81, 83, 86)},
 {'name': 'Saddle', 'id': 329, 'data': 0, 'id_in_image': 520, 'main_color': (45, 19, 8), 'second_color': (218, 102, 44), 'third_color': (239, 126, 74)},
 {'name': 'Iron Door', 'id': 330, 'data': 0, 'kind': 'Block', 'double': True, 'id_in_image': 522, 'main_color': (205, 205, 205), 'second_color': (149, 149, 149), 'third_color': (109, 109, 109)},
 {'name': 'Redstone', 'id': 331, 'data': 0, 'id_in_image': 523, 'main_color': (45, 0, 0), 'second_color': (74, 0, 0), 'third_color': (114, 0, 0)},
 {'name': 'Snowball', 'id': 332, 'data': 0, 'id_in_image': 524, 'main_color': (242, 252, 252), 'second_color': (108, 116, 116), 'third_color': (204, 214, 214)},
 {'name': 'Boat', 'id': 333, 'data': 0, 'id_in_image': 525, 'main_color': (71, 58, 36), 'second_color': (107, 85, 48), 'third_color': (40, 30, 10)},
 {'name': 'Leather', 'id': 334, 'data': 0, 'id_in_image': 526, 'main_color': (198, 92, 53), 'second_color': (158, 73, 42), 'third_color': (84, 39, 22)},
 {'name': 'Milk Bucket', 'id': 335, 'data': 0, 'id_in_image': 527, 'main_color': (232, 232, 232), 'second_color': (53, 53, 53), 'third_color': (90, 90, 90)},
 {'name': 'Brick', 'id': 336, 'kind': 'Block', 'data': 0, 'stair': 108, 'id_in_image': 528, 'main_color': (114, 56, 39), 'second_color': (52, 25, 18), 'third_color': (183, 90, 64)},
 {'name': 'Clay', 'id': 337, 'data': 0, 'id_in_image': 529, 'main_color': (97, 102, 122), 'second_color': (55, 57, 68), 'third_color': (165, 169, 185)},
 {'name': 'Sugar Canes', 'id': 338, 'data': 0, 'id_in_image': 530, 'main_color': (43, 56, 29), 'second_color': (163, 210, 111), 'third_color': (130, 168, 89)},
 {'name': 'Paper', 'id': 339, 'data': 0, 'id_in_image': 531, 'main_color': (214, 214, 214), 'second_color': (234, 234, 234), 'third_color': (81, 81, 81)},
 {'name': 'Book', 'id': 340, 'data': 0, 'id_in_image': 20, 'main_color': (41, 29, 8), 'second_color': (101, 75, 23), 'third_color': (170, 170, 170)},
 {'name': 'Slimeball', 'id': 341, 'data': 0, 'id_in_image': 47, 'main_color': (101, 161, 92), 'second_color': (54, 88, 50), 'third_color': (131, 200, 115)},
 {'name': 'Minecart with Chest', 'id': 342, 'data': 0, 'id_in_image': 74, 'main_color': (32, 28, 21), 'second_color': (137, 103, 39), 'third_color': (136, 139, 145)},
 {'name': 'Minecart with Furnace', 'id': 343, 'data': 0, 'id_in_image': 101, 'main_color': (23, 24, 24), 'second_color': (58, 58, 58), 'third_color': (136, 139, 145)},
 {'name': 'Egg', 'id': 344, 'data': 0, 'id_in_image': 128, 'main_color': (223, 206, 155), 'second_color': (178, 164, 124), 'third_color': (85, 78, 59)},
 {'name': 'Compass', 'id': 345, 'data': 0, 'id_in_image': 155, 'main_color': (42, 40, 36), 'second_color': (115, 115, 115), 'third_color': (255, 20, 20)},
 {'name': 'Fishing Rod', 'id': 346, 'data': 0, 'id_in_image': 182, 'main_color': (68, 68, 68), 'second_color': (43, 35, 20), 'third_color': (73, 54, 21)},
 {'name': 'Clock', 'id': 347, 'data': 0, 'id_in_image': 209, 'main_color': (222, 222, 144), 'second_color': (87, 87, 18), 'third_color': (45, 45, 13)},
 {'name': 'Glowstone Dust', 'id': 348, 'data': 0, 'id_in_image': 236, 'main_color': (84, 84, 0), 'second_color': (136, 136, 0), 'third_color': (210, 210, 0)},
 {'name': 'Raw Fish', 'id': 349, 'data': 0, 'id_in_image': 263, 'main_color': (107, 159, 147), 'second_color': (90, 134, 124), 'third_color': (70, 99, 95)},
 {'name': 'Raw Salmon', 'id': 349, 'data': 1, 'id_in_image': 290, 'main_color': (167, 54, 52), 'second_color': (111, 52, 48), 'third_color': (153, 108, 103)},
 {'name': 'Clownfish', 'id': 349, 'data': 2, 'id_in_image': 317, 'main_color': (225, 105, 33), 'second_color': (28, 38, 37), 'third_color': (241, 202, 178)},
 {'name': 'Pufferfish', 'id': 349, 'data': 3, 'id_in_image': 344, 'main_color': (234, 212, 37), 'second_color': (169, 146, 8), 'third_color': (99, 90, 18)},
 {'name': 'Cooked Fish', 'id': 350, 'data': 0, 'id_in_image': 549, 'main_color': (164, 151, 156), 'second_color': (89, 91, 93), 'third_color': (196, 177, 180)},
 {'name': 'Cooked Salmon', 'id': 350, 'data': 1, 'id_in_image': 550, 'main_color': (159, 75, 35), 'second_color': (42, 38, 24), 'third_color': (188, 125, 73)},
 {'name': 'Ink Sack', 'id': 351, 'data': 0, 'id_in_image': 551, 'main_color': (10, 10, 12), 'second_color': (101, 92, 105), 'third_color': (58, 58, 68)},
 {'name': 'Rose Red', 'id': 351, 'data': 1, 'id_in_image': 552, 'main_color': (122, 7, 7), 'second_color': (217, 74, 74), 'third_color': (190, 48, 48)},
 {'name': 'Cactus Green', 'id': 351, 'data': 2, 'id_in_image': 559, 'main_color': (34, 53, 5), 'second_color': (99, 134, 46), 'third_color': (77, 110, 26)},
 {'name': 'Coco Beans', 'id': 351, 'data': 3, 'id_in_image': 560, 'main_color': (73, 39, 17), 'second_color': (151, 103, 70), 'third_color': (137, 88, 54)},
 {'name': 'Lapis Lazuli', 'id': 351, 'data': 4, 'id_in_image': 21, 'main_color': (10, 43, 122), 'second_color': (32, 76, 173), 'third_color': (52, 94, 195)},
 {'name': 'Purple Dye', 'id': 351, 'data': 5, 'id_in_image': 48, 'main_color': (81, 26, 113), 'second_color': (176, 100, 216), 'third_color': (136, 53, 184)},
 {'name': 'Cyan Dye', 'id': 351, 'data': 6, 'id_in_image': 75, 'main_color': (16, 75, 99), 'second_color': (34, 110, 142), 'third_color': (60, 142, 176)},
 {'name': 'Light Gray Dye', 'id': 351, 'data': 7, 'id_in_image': 102, 'main_color': (61, 61, 76), 'second_color': (204, 204, 204), 'third_color': (165, 165, 183)},
 {'name': 'Gray Dye', 'id': 351, 'data': 8, 'id_in_image': 129, 'main_color': (65, 65, 65), 'second_color': (109, 109, 109), 'third_color': (151, 151, 151)},
 {'name': 'Pink Dye', 'id': 351, 'data': 9, 'id_in_image': 156, 'main_color': (243, 175, 209), 'second_color': (128, 54, 92), 'third_color': (219, 139, 180)},
 {'name': 'Lime Dye', 'id': 351, 'data': 10, 'id_in_image': 553, 'main_color': (61, 109, 0), 'second_color': (97, 166, 8), 'third_color': (131, 212, 28)},
 {'name': 'Dandelion Yellow', 'id': 351, 'data': 11, 'id_in_image': 554, 'main_color': (142, 107, 19), 'second_color': (222, 213, 38), 'third_color': (185, 151, 27)},
 {'name': 'Light Blue Dye', 'id': 351, 'data': 12, 'id_in_image': 555, 'main_color': (110, 152, 212), 'second_color': (47, 84, 136), 'third_color': (139, 181, 240)},
 {'name': 'Magenta Dye', 'id': 351, 'data': 13, 'id_in_image': 556, 'main_color': (107, 33, 102), 'second_color': (182, 85, 176), 'third_color': (219, 122, 213)},
 {'name': 'Orange Dye', 'id': 351, 'data': 14, 'id_in_image': 557, 'main_color': (237, 168, 57), 'second_color': (146, 70, 12), 'third_color': (197, 120, 30)},
 {'name': 'Bone Meal', 'id': 351, 'data': 15, 'id_in_image': 558, 'main_color': (230, 230, 235), 'second_color': (84, 84, 104), 'third_color': (115, 115, 132)},
 {'name': 'Bone', 'id': 352, 'data': 0, 'id_in_image': 183, 'main_color': (120, 120, 112), 'second_color': (234, 232, 204), 'third_color': (253, 253, 233)},
 {'name': 'Sugar', 'id': 353, 'data': 0, 'id_in_image': 210, 'main_color': (247, 247, 247), 'second_color': (84, 84, 104), 'third_color': (213, 213, 223)},
 {'name': 'Cake', 'id': 354, 'data': 0, 'id_in_image': 237, 'main_color': (216, 215, 216), 'second_color': (162, 80, 30), 'third_color': (73, 73, 73)},
 {'name': 'Bed', 'id': 355, 'data': 0, 'id_in_image': 264, 'main_color': (96, 18, 11), 'second_color': (142, 23, 23), 'third_color': (114, 114, 114)},
 {'name': 'Redstone Repeater', 'id': 356, 'data': 0, 'id_in_image': 291, 'main_color': (164, 167, 161), 'second_color': (81, 16, 10), 'third_color': (44, 11, 6)},
 {'name': 'Cookie', 'id': 357, 'data': 0, 'id_in_image': 318, 'main_color': (217, 131, 62), 'second_color': (231, 144, 66), 'third_color': (75, 42, 21)},
 {'name': 'Map', 'id': 358, 'data': 0, 'id_in_image': 345, 'main_color': (214, 214, 150), 'second_color': (75, 75, 23), 'third_color': (234, 234, 199)},
 {'name': 'Shears', 'id': 359, 'data': 0, 'id_in_image': 372, 'main_color': (77, 54, 46), 'second_color': (97, 97, 97), 'third_color': (168, 168, 168)},
 {'name': 'Melon', 'id': 360, 'data': 0, 'id_in_image': 399, 'main_color': (188, 32, 20), 'second_color': (75, 87, 18), 'third_color': (132, 137, 32)},
 {'name': 'Pumpkin Seeds', 'id': 361, 'data': 0, 'id_in_image': 426, 'main_color': (203, 198, 141), 'second_color': (200, 212, 170), 'third_color': (202, 177, 110)},
 {'name': 'Melon Seeds', 'id': 362, 'data': 0, 'id_in_image': 453, 'main_color': (42, 34, 11), 'second_color': (97, 85, 53), 'third_color': (29, 23, 5)},
 {'name': 'Raw Beef', 'id': 363, 'data': 0, 'id_in_image': 480, 'main_color': (18, 2, 1), 'second_color': (225, 89, 81), 'third_color': (221, 57, 49)},
 {'name': 'Steak', 'id': 364, 'data': 0, 'id_in_image': 507, 'main_color': (21, 10, 7), 'second_color': (139, 82, 60), 'third_color': (107, 57, 41)},
 {'name': 'Raw Chicken', 'id': 365, 'data': 0, 'id_in_image': 534, 'main_color': (255, 229, 217), 'second_color': (49, 0, 0), 'third_color': (184, 132, 115)},
 {'name': 'Cooked Chicken', 'id': 366, 'data': 0, 'id_in_image': 561, 'main_color': (144, 77, 37), 'second_color': (7, 4, 1), 'third_color': (213, 148, 107)},
 {'name': 'Rotten Flesh', 'id': 367, 'data': 0, 'id_in_image': 567, 'main_color': (168, 80, 42), 'second_color': (96, 43, 18), 'third_color': (39, 19, 15)},
 {'name': 'Ender Pearl', 'id': 368, 'data': 0, 'id_in_image': 568, 'main_color': (9, 52, 45), 'second_color': (15, 90, 78), 'third_color': (52, 153, 136)},
 {'name': 'Blaze Rod', 'id': 369, 'data': 0, 'id_in_image': 569, 'main_color': (178, 100, 16), 'second_color': (185, 147, 28), 'third_color': (255, 230, 33)},
 {'name': 'Ghast Tear', 'id': 370, 'data': 0, 'id_in_image': 571, 'main_color': (55, 74, 74), 'second_color': (221, 228, 228), 'third_color': (169, 190, 190)},
 {'name': 'Gold Nugget', 'id': 371, 'data': 0, 'id_in_image': 572, 'main_color': (101, 101, 8), 'second_color': (238, 238, 1), 'third_color': (255, 255, 139)},
 {'name': 'Nether Wart', 'id': 372, 'data': 0, 'id_in_image': 573, 'main_color': (86, 19, 24), 'second_color': (166, 37, 48), 'third_color': (190, 63, 74)},
 {'name': 'Potion', 'id': 373, 'data': 0, 'id_in_image': 574, 'main_color': (186, 186, 186), 'second_color': (44, 74, 157), 'third_color': (218, 218, 218)},
 {'name': 'Glass Bottle', 'id': 374, 'data': 0, 'id_in_image': 575, 'main_color': (186, 186, 186), 'second_color': (218, 218, 218), 'third_color': (204, 175, 165)},
 {'name': 'Spider Eye', 'id': 375, 'data': 0, 'id_in_image': 576, 'main_color': (42, 0, 16), 'second_color': (111, 9, 39), 'third_color': (196, 95, 107)},
 {'name': 'Fermented Spider Eye', 'id': 376, 'data': 0, 'id_in_image': 577, 'main_color': (42, 0, 16), 'second_color': (196, 108, 106), 'third_color': (162, 74, 76)},
 {'name': 'Blaze Powder', 'id': 377, 'data': 0, 'id_in_image': 578, 'main_color': (150, 51, 0), 'second_color': (236, 152, 5), 'third_color': (255, 221, 10)},
 {'name': 'Magma Cream', 'id': 378, 'data': 0, 'id_in_image': 579, 'main_color': (142, 33, 37), 'second_color': (216, 225, 102), 'third_color': (85, 105, 39)},
 {'name': 'Brewing Stand', 'id': 379, 'data': 0, 'id_in_image': 580, 'main_color': (100, 100, 100), 'second_color': (143, 143, 143), 'third_color': (49, 49, 49)},
 {'name': 'Cauldron', 'id': 380, 'data': 0, 'id_in_image': 49, 'main_color': (29, 29, 29), 'second_color': (82, 82, 82), 'third_color': (68, 68, 68)},
 {'name': 'Eye of Ender', 'id': 381, 'data': 0, 'id_in_image': 76, 'main_color': (99, 153, 95), 'second_color': (22, 48, 55), 'third_color': (48, 96, 100)},
 {'name': 'Glistering Melon', 'id': 382, 'data': 0, 'id_in_image': 103, 'main_color': (101, 91, 13), 'second_color': (188, 34, 21), 'third_color': (199, 54, 39)},
 {'name': 'Spawn Elder Guardian', 'id': 383, 'data': 4, 'id_in_image': 508, 'main_color': (167, 172, 152), 'second_color': (89, 85, 93), 'third_color': (60, 53, 71)},
 {'name': 'Spawn Wither Skeleton', 'id': 383, 'data': 5, 'id_in_image': 535, 'main_color': (22, 22, 22), 'second_color': (43, 46, 46), 'third_color': (60, 65, 65)},
 {'name': 'Spawn Stray', 'id': 383, 'data': 6, 'id_in_image': 601, 'main_color': (90, 104, 105), 'second_color': (45, 55, 55), 'third_color': (154, 164, 164)},
 {'name': 'Spawn Husk', 'id': 383, 'data': 23, 'id_in_image': 265, 'main_color': (103, 101, 79), 'second_color': (55, 53, 46), 'third_color': (156, 152, 102)},
 {'name': 'Spawn Zombie Villager', 'id': 383, 'data': 27, 'id_in_image': 292, 'main_color': (73, 50, 43), 'second_color': (37, 26, 22), 'third_color': (85, 110, 71)},
 {'name': 'Spawn Skeleton Horse', 'id': 383, 'data': 28, 'id_in_image': 319, 'main_color': (98, 104, 85), 'second_color': (47, 52, 38), 'third_color': (78, 86, 62)},
 {'name': 'Spawn Zombie Horse', 'id': 383, 'data': 29, 'id_in_image': 346, 'main_color': (38, 78, 48), 'second_color': (96, 151, 93), 'third_color': (23, 43, 28)},
 {'name': 'Spawn Donkey', 'id': 383, 'data': 31, 'id_in_image': 373, 'main_color': (67, 60, 49), 'second_color': (74, 66, 54), 'third_color': (44, 40, 34)},
 {'name': 'Spawn Mule', 'id': 383, 'data': 32, 'id_in_image': 400, 'main_color': (26, 7, 0), 'second_color': (49, 36, 22), 'third_color': (37, 23, 14)},
 {'name': 'Spawn Evoker', 'id': 383, 'data': 34, 'id_in_image': 427, 'main_color': (21, 20, 19), 'second_color': (133, 139, 139), 'third_color': (105, 110, 110)},
 {'name': 'Spawn Vex', 'id': 383, 'data': 35, 'id_in_image': 454, 'main_color': (100, 118, 134), 'second_color': (113, 116, 119), 'third_color': (112, 132, 151)},
 {'name': 'Spawn Vindicator', 'id': 383, 'data': 36, 'id_in_image': 481, 'main_color': (24, 50, 51), 'second_color': (133, 139, 139), 'third_color': (105, 110, 110)},
 {'name': 'Spawn Creeper', 'id': 383, 'data': 50, 'id_in_image': 562, 'main_color': (10, 142, 9), 'second_color': (5, 74, 4), 'third_color': (5, 62, 4)},
 {'name': 'Spawn Skeleton', 'id': 383, 'data': 51, 'id_in_image': 589, 'main_color': (164, 164, 164), 'second_color': (37, 37, 37), 'third_color': (83, 83, 83)},
 {'name': 'Spawn Spider', 'id': 383, 'data': 52, 'id_in_image': 594, 'main_color': (32, 27, 24), 'second_color': (91, 7, 7), 'third_color': (46, 40, 35)},
 {'name': 'Spawn Zombie', 'id': 383, 'data': 54, 'id_in_image': 595, 'main_color': (0, 149, 149), 'second_color': (0, 77, 77), 'third_color': (85, 110, 71)},
 {'name': 'Spawn Slime', 'id': 383, 'data': 55, 'id_in_image': 596, 'main_color': (49, 83, 40), 'second_color': (72, 143, 55), 'third_color': (64, 117, 52)},
 {'name': 'Spawn Ghast', 'id': 383, 'data': 56, 'id_in_image': 597, 'main_color': (212, 212, 212), 'second_color': (105, 105, 105), 'third_color': (101, 101, 101)},
 {'name': 'Spawn Pigman', 'id': 383, 'data': 57, 'id_in_image': 598, 'main_color': (37, 55, 20), 'second_color': (213, 134, 134), 'third_color': (183, 115, 115)},
 {'name': 'Spawn Enderman', 'id': 383, 'data': 58, 'id_in_image': 599, 'main_color': (2, 2, 2), 'second_color': (18, 18, 18), 'third_color': (0, 0, 0)},
 {'name': 'Spawn Cave Spider', 'id': 383, 'data': 59, 'id_in_image': 600, 'main_color': (7, 40, 48), 'second_color': (91, 7, 7), 'third_color': (10, 59, 69)},
 {'name': 'Spawn Silverfish', 'id': 383, 'data': 60, 'id_in_image': 602, 'main_color': (25, 25, 25), 'second_color': (44, 44, 44), 'third_color': (89, 89, 89)},
 {'name': 'Spawn Blaze', 'id': 383, 'data': 61, 'id_in_image': 603, 'main_color': (210, 152, 1), 'second_color': (113, 93, 22), 'third_color': (153, 149, 76)},
 {'name': 'Spawn Magma Cube', 'id': 383, 'data': 62, 'id_in_image': 604, 'main_color': (38, 0, 0), 'second_color': (151, 151, 0), 'third_color': (120, 120, 0)},
 {'name': 'Spawn Bat', 'id': 383, 'data': 65, 'id_in_image': 605, 'main_color': (8, 8, 8), 'second_color': (68, 55, 43), 'third_color': (59, 48, 37)},
 {'name': 'Spawn Witch', 'id': 383, 'data': 66, 'id_in_image': 606, 'main_color': (38, 0, 0), 'second_color': (44, 88, 33), 'third_color': (68, 134, 52)},
 {'name': 'Spawn Endermite', 'id': 383, 'data': 67, 'id_in_image': 607, 'main_color': (18, 18, 18), 'second_color': (55, 55, 55), 'third_color': (13, 13, 13)},
 {'name': 'Spawn Guardian', 'id': 383, 'data': 68, 'id_in_image': 608, 'main_color': (76, 110, 97), 'second_color': (114, 59, 22), 'third_color': (162, 84, 32)},
 {'name': 'Spawn Shulker', 'id': 383, 'data': 69, 'id_in_image': 609, 'main_color': (46, 33, 49), 'second_color': (119, 82, 119), 'third_color': (134, 93, 134)},
 {'name': 'Spawn Pig', 'id': 383, 'data': 90, 'id_in_image': 610, 'main_color': (215, 148, 145), 'second_color': (107, 49, 47), 'third_color': (189, 130, 128)},
 {'name': 'Spawn Sheep', 'id': 383, 'data': 91, 'id_in_image': 611, 'main_color': (109, 95, 95), 'second_color': (207, 207, 207), 'third_color': (182, 177, 177)},
 {'name': 'Spawn Cow', 'id': 383, 'data': 92, 'id_in_image': 612, 'main_color': (48, 38, 27), 'second_color': (90, 90, 90), 'third_color': (133, 133, 133)},
 {'name': 'Spawn Chicken', 'id': 383, 'data': 93, 'id_in_image': 613, 'main_color': (101, 101, 101), 'second_color': (143, 143, 143), 'third_color': (149, 0, 0)},
 {'name': 'Spawn Squid', 'id': 383, 'data': 94, 'id_in_image': 614, 'main_color': (21, 36, 47), 'second_color': (33, 54, 68), 'third_color': (57, 69, 78)},
 {'name': 'Spawn Wolf', 'id': 383, 'data': 95, 'id_in_image': 615, 'main_color': (99, 89, 82), 'second_color': (176, 172, 171), 'third_color': (201, 197, 197)},
 {'name': 'Spawn Mooshroom', 'id': 383, 'data': 96, 'id_in_image': 616, 'main_color': (103, 9, 10), 'second_color': (98, 98, 98), 'third_color': (143, 13, 14)},
 {'name': 'Spawn Ocelot', 'id': 383, 'data': 98, 'id_in_image': 23, 'main_color': (46, 36, 28), 'second_color': (217, 201, 113), 'third_color': (187, 174, 98)},
 {'name': 'Spawn Horse', 'id': 383, 'data': 100, 'id_in_image': 130, 'main_color': (106, 97, 22), 'second_color': (172, 141, 112), 'third_color': (150, 124, 98)},
 {'name': 'Spawn Rabbit', 'id': 383, 'data': 101, 'id_in_image': 157, 'main_color': (76, 47, 32), 'second_color': (137, 85, 57), 'third_color': (57, 35, 24)},
 {'name': 'Spawn Polar Bear', 'id': 383, 'data': 102, 'id_in_image': 184, 'main_color': (92, 93, 91), 'second_color': (215, 215, 215), 'third_color': (188, 188, 188)},
 {'name': 'Spawn Llama', 'id': 383, 'data': 103, 'id_in_image': 211, 'main_color': (80, 51, 35), 'second_color': (172, 141, 112), 'third_color': (99, 72, 54)},
 {'name': 'Spawn Villager', 'id': 383, 'data': 120, 'id_in_image': 211, 'main_color': (80, 51, 35), 'second_color': (172, 141, 112), 'third_color': (99, 72, 54)},
 {'name': "Bottle o' Enchanting", 'id': 384, 'data': 0, 'id_in_image': 50, 'main_color': (232, 255, 143), 'second_color': (214, 228, 90), 'third_color': (81, 60, 3)},
 {'name': 'Fire Charge', 'id': 385, 'data': 0, 'id_in_image': 77, 'main_color': (16, 13, 10), 'second_color': (83, 44, 6), 'third_color': (161, 49, 0)},
 {'name': 'Book and Quill', 'id': 386, 'data': 0, 'id_in_image': 104, 'main_color': (100, 48, 25), 'second_color': (225, 225, 225), 'third_color': (31, 20, 6)},
 {'name': 'Written Book', 'id': 387, 'data': 0, 'id_in_image': 131, 'main_color': (101, 39, 20), 'second_color': (20, 10, 0), 'third_color': (167, 167, 167)},
 {'name': 'Emerald', 'id': 388, 'data': 0, 'id_in_image': 158, 'main_color': (0, 159, 45), 'second_color': (0, 94, 6), 'third_color': (80, 242, 141)},
 {'name': 'Item Frame', 'id': 389, 'data': 0, 'id_in_image': 185, 'main_color': (85, 57, 31), 'second_color': (100, 70, 48), 'third_color': (136, 99, 43)},
 {'name': 'Flower Pot', 'id': 390, 'data': 0, 'id_in_image': 239, 'main_color': (89, 39, 28), 'second_color': (150, 96, 79), 'third_color': (55, 22, 16)},
 {'name': 'Carrot', 'id': 391, 'data': 0, 'id_in_image': 266, 'main_color': (255, 151, 33), 'second_color': (4, 104, 3), 'third_color': (172, 57, 0)},
 {'name': 'Potato', 'id': 392, 'data': 0, 'id_in_image': 293, 'main_color': (171, 106, 14), 'second_color': (232, 185, 97), 'third_color': (249, 222, 167)},
 {'name': 'Baked Potato', 'id': 393, 'data': 0, 'id_in_image': 320, 'main_color': (172, 92, 10), 'second_color': (237, 170, 91), 'third_color': (251, 216, 152)},
 {'name': 'Poisonous Potato', 'id': 394, 'data': 0, 'id_in_image': 347, 'main_color': (221, 203, 90), 'second_color': (240, 233, 168), 'third_color': (160, 149, 23)},
 {'name': 'Empty Map', 'id': 395, 'data': 0, 'id_in_image': 374, 'main_color': (214, 214, 150), 'second_color': (234, 234, 199), 'third_color': (81, 81, 0)},
 {'name': 'Golden Carrot', 'id': 396, 'data': 0, 'id_in_image': 401, 'main_color': (100, 70, 6), 'second_color': (231, 163, 35), 'third_color': (254, 246, 12)},
 {'name': 'Mob Head (Skeleton)', 'id': 397, 'data': 0, 'id_in_image': 428, 'main_color': (89, 89, 89), 'second_color': (149, 149, 149), 'third_color': (86, 86, 86)},
 {'name': 'Mob Head (Wither Skeleton)', 'id': 397, 'data': 1, 'id_in_image': 455, 'main_color': (21, 22, 22), 'second_color': (36, 37, 37), 'third_color': (7, 7, 7)},
 {'name': 'Mob Head (Zombie)', 'id': 397, 'data': 2, 'id_in_image': 482, 'main_color': (31, 48, 24), 'second_color': (46, 77, 35), 'third_color': (69, 107, 52)},
 {'name': 'Mob Head (Human)', 'id': 397, 'data': 3, 'id_in_image': 509, 'main_color': (35, 23, 12), 'second_color': (80, 54, 40), 'third_color': (110, 110, 110)},
 {'name': 'Mob Head (Creeper)', 'id': 397, 'data': 4, 'id_in_image': 536, 'main_color': (42, 93, 37), 'second_color': (93, 145, 87), 'third_color': (13, 29, 12)},
 {'name': 'Mob Head (Dragon)', 'id': 397, 'data': 5, 'id_in_image': 563, 'main_color': (16, 16, 16), 'second_color': (21, 21, 21), 'third_color': (89, 89, 89)},
 {'name': 'Carrot on a Stick', 'id': 398, 'data': 0, 'id_in_image': 590, 'main_color': (68, 68, 68), 'second_color': (43, 35, 20), 'third_color': (157, 90, 18)},
 {'name': 'Nether Star', 'id': 399, 'data': 0, 'id_in_image': 617, 'main_color': (210, 219, 219), 'second_color': (85, 107, 107), 'third_color': (136, 164, 164)},
 {'name': 'Pumpkin Pie', 'id': 400, 'data': 0, 'id_in_image': 623, 'main_color': (231, 159, 94), 'second_color': (208, 98, 44), 'third_color': (217, 119, 70)},
 {'name': 'Firework Rocket', 'id': 401, 'data': 0, 'id_in_image': 624, 'main_color': (164, 44, 32), 'second_color': (227, 227, 227), 'third_color': (45, 20, 9)},
 {'name': 'Firework Star', 'id': 402, 'data': 0, 'id_in_image': 625, 'main_color': (76, 76, 76), 'second_color': (114, 114, 114), 'third_color': (45, 45, 45)},
 {'name': 'Enchanted Book', 'id': 403, 'data': 0, 'id_in_image': 626, 'main_color': (47, 35, 9), 'second_color': (100, 74, 22), 'third_color': (74, 55, 16)},
 {'name': 'Redstone Comparator', 'id': 404, 'data': 0, 'id_in_image': 627, 'main_color': (79, 20, 13), 'second_color': (164, 167, 161), 'third_color': (45, 15, 8)},
 {'name': 'Nether Brick', 'id': 405, 'data': 0, 'id_in_image': 628, 'main_color': (48, 24, 28), 'second_color': (62, 30, 36), 'third_color': (70, 38, 44)},
 {'name': 'Nether Quartz', 'id': 406, 'data': 0, 'id_in_image': 629, 'main_color': (230, 225, 218), 'second_color': (208, 195, 182), 'third_color': (178, 163, 152)},
 {'name': 'Minecart with TNT', 'id': 407, 'data': 0, 'id_in_image': 630, 'main_color': (29, 25, 19), 'second_color': (136, 139, 145), 'third_color': (219, 68, 26)},
 {'name': 'Minecart with Hopper', 'id': 408, 'data': 0, 'id_in_image': 631, 'main_color': (18, 18, 18), 'second_color': (50, 50, 50), 'third_color': (136, 139, 145)},
 {'name': 'Prismarine Shard', 'id': 409, 'data': 0, 'id_in_image': 632, 'main_color': (104, 167, 149), 'second_color': (151, 198, 181), 'third_color': (52, 105, 91)},
 {'name': 'Prismarine Crystals', 'id': 410, 'data': 0, 'id_in_image': 634, 'main_color': (139, 187, 175), 'second_color': (73, 101, 93), 'third_color': (218, 232, 219)},
 {'name': 'Raw Rabbit', 'id': 411, 'data': 0, 'id_in_image': 635, 'main_color': (255, 229, 216), 'second_color': (227, 172, 154), 'third_color': (184, 132, 115)},
 {'name': 'Cooked Rabbit', 'id': 412, 'data': 0, 'id_in_image': 636, 'main_color': (150, 81, 40), 'second_color': (102, 51, 23), 'third_color': (214, 152, 112)},
 {'name': 'Rabbit Stew', 'id': 413, 'data': 0, 'id_in_image': 637, 'main_color': (38, 25, 3), 'second_color': (211, 145, 101), 'third_color': (91, 53, 14)},
 {'name': "Rabbit's Foot", 'id': 414, 'data': 0, 'id_in_image': 638, 'main_color': (172, 132, 86), 'second_color': (201, 161, 108), 'third_color': (141, 104, 67)},
 {'name': 'Rabbit Hide', 'id': 415, 'data': 0, 'id_in_image': 639, 'main_color': (199, 158, 103), 'second_color': (175, 134, 88), 'third_color': (114, 87, 63)},
 {'name': 'Armor Stand', 'id': 416, 'data': 0, 'id_in_image': 640, 'main_color': (61, 48, 30), 'second_color': (72, 58, 37), 'third_color': (171, 137, 85)},
 {'name': 'Iron Horse Armor', 'id': 417, 'data': 0, 'id_in_image': 641, 'main_color': (33, 33, 33), 'second_color': (90, 90, 90), 'third_color': (125, 125, 125)},
 {'name': 'Golden Horse Armor', 'id': 418, 'data': 0, 'id_in_image': 642, 'main_color': (85, 30, 14), 'second_color': (124, 89, 1), 'third_color': (173, 123, 1)},
 {'name': 'Diamond Horse Armor', 'id': 419, 'data': 0, 'id_in_image': 643, 'main_color': (39, 49, 92), 'second_color': (75, 94, 103), 'third_color': (107, 129, 139)},
 {'name': 'Lead', 'id': 420, 'data': 0, 'id_in_image': 24, 'main_color': (118, 70, 35), 'second_color': (131, 101, 80), 'third_color': (175, 149, 131)},
 {'name': 'Name Tag', 'id': 421, 'data': 0, 'id_in_image': 51, 'main_color': (55, 41, 16), 'second_color': (96, 91, 83), 'third_color': (238, 238, 238)},
 {'name': 'Minecart with Command Block', 'id': 422, 'data': 0, 'id_in_image': 78, 'main_color': (32, 28, 21), 'second_color': (147, 147, 150), 'third_color': (183, 141, 113)},
 {'name': 'Raw Mutton', 'id': 423, 'data': 0, 'id_in_image': 105, 'main_color': (226, 96, 87), 'second_color': (90, 13, 9), 'third_color': (155, 42, 37)},
 {'name': 'Cooked Mutton', 'id': 424, 'data': 0, 'id_in_image': 132, 'main_color': (158, 104, 82), 'second_color': (51, 26, 17), 'third_color': (100, 55, 39)},
 {'name': 'Banner', 'id': 425, 'data': 0, 'id_in_image': 159, 'main_color': (151, 151, 151), 'second_color': (86, 68, 41), 'third_color': (235, 235, 235)},
 {'name': 'Spruce Door', 'id': 427, 'data': 0, 'id_in_image': 186, 'main_color': (116, 86, 51), 'second_color': (81, 81, 81), 'third_color': (73, 54, 33)},
 {'name': 'Birch Door', 'id': 428, 'data': 0, 'id_in_image': 213, 'main_color': (213, 202, 140), 'second_color': (248, 244, 225), 'third_color': (153, 144, 100)},
 {'name': 'Jungle Door', 'id': 429, 'data': 0, 'id_in_image': 240, 'main_color': (178, 130, 94), 'second_color': (160, 116, 85), 'third_color': (145, 105, 77)},
 {'name': 'Acacia Door', 'id': 430, 'data': 0, 'id_in_image': 483, 'main_color': (177, 102, 64), 'second_color': (130, 75, 48), 'third_color': (86, 50, 32)},
 {'name': 'Dark Oak Door', 'id': 431, 'data': 0, 'id_in_image': 510, 'main_color': (71, 46, 22), 'second_color': (38, 24, 11), 'third_color': (17, 11, 5)},
 {'name': 'Chorus Fruit', 'id': 432, 'data': 0, 'id_in_image': 537, 'main_color': (89, 51, 89), 'second_color': (120, 89, 120), 'third_color': (129, 100, 129)},
 {'name': 'Popped Chorus Fruit', 'id': 433, 'data': 0, 'id_in_image': 564, 'main_color': (150, 108, 150), 'second_color': (90, 51, 90), 'third_color': (182, 144, 182)},
 {'name': 'Beetroot', 'id': 434, 'data': 0, 'id_in_image': 591, 'main_color': (141, 49, 48), 'second_color': (95, 30, 24), 'third_color': (166, 76, 83)},
 {'name': 'Beetroot Seeds', 'id': 435, 'data': 0, 'id_in_image': 618, 'main_color': (133, 111, 74), 'second_color': (222, 176, 117), 'third_color': (0, 0, 0)},
 {'name': 'Beetroot Soup', 'id': 436, 'data': 0, 'id_in_image': 645, 'main_color': (40, 27, 3), 'second_color': (162, 33, 33), 'third_color': (83, 57, 9)},
 {'name': "Dragon's Breath", 'id': 437, 'data': 0, 'id_in_image': 648, 'main_color': (231, 220, 227), 'second_color': (186, 186, 186), 'third_color': (210, 159, 175)},
 {'name': 'Splash Potion', 'id': 438, 'data': 0, 'id_in_image': 649, 'main_color': (91, 74, 67), 'second_color': (44, 74, 157), 'third_color': (93, 50, 40)},
 {'name': 'Spectral Arrow', 'id': 439, 'data': 0, 'id_in_image': 650, 'main_color': (8, 7, 5), 'second_color': (98, 86, 14), 'third_color': (150, 150, 150)},
 {'name': 'Tipped Arrow', 'id': 440, 'data': 0, 'id_in_image': 659, 'main_color': (35, 34, 33), 'second_color': (42, 75, 141), 'third_color': (137, 103, 39)},
 {'name': 'Lingering Potion', 'id': 441, 'data': 0, 'id_in_image': 660, 'main_color': (90, 74, 67), 'second_color': (44, 74, 157), 'third_color': (55, 92, 195)},
 {'name': 'Shield', 'id': 442, 'data': 0, 'id_in_image': 661, 'main_color': (76, 68, 42), 'second_color': (70, 61, 37), 'third_color': (107, 105, 112)},
 {'name': 'Elytra', 'id': 443, 'data': 0, 'id_in_image': 662, 'main_color': (53, 53, 53), 'second_color': (136, 136, 153), 'third_color': (120, 120, 120)},
 {'name': 'Spruce Boat', 'id': 444, 'data': 0, 'id_in_image': 663, 'main_color': (46, 35, 19), 'second_color': (94, 72, 42), 'third_color': (132, 98, 45)},
 {'name': 'Birch Boat', 'id': 445, 'data': 0, 'id_in_image': 664, 'main_color': (94, 80, 51), 'second_color': (40, 30, 10), 'third_color': (183, 167, 112)},
 {'name': 'Jungle Boat', 'id': 446, 'data': 0, 'id_in_image': 665, 'main_color': (72, 48, 31), 'second_color': (106, 73, 40), 'third_color': (40, 30, 10)},
 {'name': 'Acacia Boat', 'id': 447, 'data': 0, 'id_in_image': 666, 'main_color': (148, 85, 44), 'second_color': (90, 48, 28), 'third_color': (40, 30, 10)},
 {'name': 'Dark Oak Boat', 'id': 448, 'data': 0, 'id_in_image': 667, 'main_color': (42, 28, 12), 'second_color': (78, 50, 23), 'third_color': (137, 102, 36)},
 {'name': 'Totem of Undying', 'id': 449, 'data': 0, 'id_in_image': 668, 'main_color': (238, 225, 142), 'second_color': (105, 78, 39), 'third_color': (178, 117, 67)},
 {'name': 'Shulker Shell', 'id': 450, 'data': 0, 'id_in_image': 670, 'main_color': (144, 100, 144), 'second_color': (136, 94, 136), 'third_color': (119, 80, 119)},
 {'name': 'Iron Nugget', 'id': 452, 'data': 0, 'id_in_image': 671, 'main_color': (88, 95, 104), 'second_color': (226, 230, 235), 'third_color': (57, 60, 64)},
 {'name': '13 Disc', 'id': 2256, 'data': 0, 'id_in_image': 15, 'main_color': (67, 67, 67), 'second_color': (30, 30, 30), 'third_color': (255, 255, 255)},
 {'name': 'Cat Disc', 'id': 2257, 'data': 0, 'id_in_image': 42, 'main_color': (67, 67, 67), 'second_color': (30, 30, 30), 'third_color': (76, 255, 0)},
 {'name': 'Blocks Disc', 'id': 2258, 'data': 0, 'id_in_image': 69, 'main_color': (30, 30, 30), 'second_color': (64, 64, 64), 'third_color': (81, 81, 81)},
 {'name': 'Chirp Disc', 'id': 2259, 'data': 0, 'id_in_image': 96, 'main_color': (67, 67, 67), 'second_color': (30, 30, 30), 'third_color': (127, 0, 2)},
 {'name': 'Far Disc', 'id': 2260, 'data': 0, 'id_in_image': 150, 'main_color': (67, 67, 67), 'second_color': (30, 30, 30), 'third_color': (182, 255, 0)},
 {'name': 'Mall Disc', 'id': 2261, 'data': 0, 'id_in_image': 177, 'main_color': (67, 67, 67), 'second_color': (30, 30, 30), 'third_color': (154, 117, 255)},
 {'name': 'Mellohi Disc', 'id': 2262, 'data': 0, 'id_in_image': 204, 'main_color': (67, 67, 67), 'second_color': (30, 30, 30), 'third_color': (178, 0, 255)},
 {'name': 'Stal Disc', 'id': 2263, 'data': 0, 'id_in_image': 231, 'main_color': (64, 64, 64), 'second_color': (35, 35, 35), 'third_color': (9, 9, 9)},
 {'name': 'Strad Disc', 'id': 2264, 'data': 0, 'id_in_image': 258, 'main_color': (30, 30, 30), 'second_color': (64, 64, 64), 'third_color': (81, 81, 81)},
 {'name': 'Ward Disc', 'id': 2265, 'data': 0, 'id_in_image': 285, 'main_color': (67, 67, 67), 'second_color': (30, 30, 30), 'third_color': (142, 198, 0)},
 {'name': '11 Disc', 'id': 2266, 'data': 0, 'id_in_image': 312, 'main_color': (36, 36, 36), 'second_color': (64, 64, 64), 'third_color': (9, 9, 9)},
 {'name': 'Wait Disc', 'id': 2267, 'data': 0, 'id_in_image': 339, 'main_color': (67, 67, 67), 'second_color': (29, 29, 30), 'third_color': (129, 169, 226)}]


# Turn all Blocks into shortcuts, so Blocks.STONE = (1,0)
for b in block_library:
    name = b["name"].replace(" ", "")
    setattr(this, name.upper(),  (b["id"], b["data"]))
