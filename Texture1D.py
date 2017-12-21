from numpy import cumsum, random as rnd
from Map import Map
from Blocks import closest_by_color, color_as_rgb, block_by_id, DEBUG_MODE
import math


# Example test steps:
# import Texture1D;
# t = Texture1D.Texture1D(Map(gradient = True, gradient_type = "linear_bezier",
#     colors = Texture1D.COMMON_TEXTURES.RainbowGlass, only_blocks=True, name_contains="Glass"))
# steps = 30
# for i in range(steps):print(t.block(Map(step=i, steps=steps)), i, steps)


class Texture1D(object):
    def __init__(self, options=Map()):
        self.gradient_calculated_steps = {}
        self.options = None
        self.axis = None
        self.gradient_type = None
        self.colors_names = None
        self.colors = None
        self.material = None
        self.steps = None
        self.blocks = None
        self.chances = None

        self.set_options(options)

    def set_options(self, options=Map()):
        self.options = options
        if options.gradient:
            self.axis = options.gradient_axis or "y"
            # TODO: Implement so xyz can be passed in
            self.gradient_type = options.gradient_type or "linear"
            self.colors_names = options.colors or rand_hex_color(2)
            self.colors = [color_as_rgb(color_name) for color_name in self.colors_names]
        elif options.blocks:
            self.blocks = options.blocks
            if options.chances:
                self.chances = options.chances
        else:
            self.material = options.color or options.material or rand_hex_color(1)

    def color(self, options=Map()):
        options = self.options + options
        if self.options.gradient:
            hex_colors = self.get_calculated_steps(options)
            if options.step:
                step = options.step
            elif options.point and options.bounds:

                if self.axis == "y":
                    bounds_lowest = options.bounds.lowest
                    # bounds_highest = options.bounds.highest
                    step = options.point.y - bounds_lowest
                elif self.axis == "x":
                    bounds_lowest = options.bounds.x_low
                    # bounds_highest = options.bounds.x_high
                    step = options.point.x - bounds_lowest
                else:
                    # if self.axis == "z":
                    bounds_lowest = options.bounds.z_low
                    # bounds_highest = options.bounds.z_high
                    step = options.point.z - bounds_lowest

                step = int(step)

                # step_range = bounds_highest - bounds_lowest + 1
                # step = dist_from_low
            else:
                step = 0

            if "hex" in hex_colors:
                hex_colors = hex_colors["hex"]

            if step > len(hex_colors) - 1:
                step = len(hex_colors) - 1
            elif step < 0:
                step = 0
            return hex_colors[step]

        else:
            if self.blocks and self.chances:
                block = weighted_choice(self.chances, self.blocks)
            elif self.blocks:
                block = rnd.choice(self.blocks)
            else:
                block = self.material

            block_obj = block_by_id(block)
            return block_obj["main_color"]

    def block(self, options=Map()):
        if self.options.gradient:
            color = self.color(options)
            if (type(color) == tuple and len(color) == 3) or (type(color) == str):
                block_obj = closest_by_color(color, self.options + options)
            else:
                error_string = "Error - Texture1D block color (\"" + str(color) + "\") not recognized"
                if DEBUG_MODE == 1:
                    raise ValueError(error_string)
                else:
                    print(error_string)

                block_obj = block_by_id(0)
        else:
            if self.blocks and self.chances:
                block = weighted_choice(self.chances, self.blocks)
            elif self.blocks:
                block = rnd.choice(self.blocks)
            else:
                block = self.material
            block_obj = block_by_id(block)

        return block_obj

    def get_calculated_steps(self, options=Map()):
        options = self.options + options
        steps = options.steps or self.steps

        if not steps:
            if not options.bounds:
                raise ValueError("Material does not have associated bounds")
            else:
                b = options.bounds
                if self.axis == "y":
                    steps = b.highest - b.lowest + 1
                elif self.axis == "x":
                    steps = b.x_high - b.x_low + 1
                elif self.axis == "z":
                    steps = b.z_high - b.z_low + 1
                self.steps = steps

        if steps:
            if self.gradient_calculated_steps and steps in self.gradient_calculated_steps:
                return self.gradient_calculated_steps[steps]
            else:
                if self.gradient_type == "linear":
                    self.gradient_calculated_steps[steps] = polylinear_gradient(self.colors, steps)
                elif self.gradient_type == "linear_bezier":
                    bez = bezier_gradient(self.colors, steps)
                    self.gradient_calculated_steps[steps] = bez["gradient"]
                else:
                    raise ValueError("unrecognized gradient_type: " + str(self.gradient_type))

                return self.gradient_calculated_steps[steps]

        raise ValueError('options.steps or colors not entered')

    def info(self, steps=10):
        for i in range(steps):
            block = self.block(Map(step=i, steps=steps))
            color = rgb_to_hex(block["main_color"])
            print(i, "of", steps, color, block)


# ==========================================================
# Many functions from https://bsou.io/posts/color-gradients-with-python


def hex_to_rgb(color):
    """ "#FFFFFF" -> [255,255,255] '''
    Note: Pass 16 to the integer function for change of base"""

    try:
        # out = [int(hex[i:i+2], 16) for i in range(1,6,2)]
        out_rgb = color_as_rgb(color)
        out = [out_rgb[0], out_rgb[1], out_rgb[2]]

    except ValueError:
        print("Hex invalid", color)
        out = color

    return out


def rgb_to_hex(rgb):
    """ [255,255,255] -> "#FFFFFF"
    # Components need to be integers for hex to make sense """

    rgb = [int(x) for x in rgb]
    return "#" + "".join(["0{0:x}".format(v) if v < 16 else
                          "{0:x}".format(v) for v in rgb])


def rand_hex_color(num=1):
    """ Generate random hex colors, default is one,
        returning a string. If num is greater than
        1, an array of strings is returned. """
    colors = []
    for i in range(num):
        color = rgb_to_hex([x * 255 for x in rnd.rand(3)])
        colors.append(color)

    if num == 1:
        colors = colors[0]

    return colors


def color_dict(gradient):
    """ Takes in a list of RGB sub-lists and returns dictionary of
      colors in RGB and hex form for use in a graphing function
      defined later on """
    return {"hex": [rgb_to_hex(RGB) for RGB in gradient],
            "r": [RGB[0] for RGB in gradient],
            "g": [RGB[1] for RGB in gradient],
            "b": [RGB[2] for RGB in gradient]}


def linear_gradient(start_hex, finish_hex="#FFFFFF", n=10):
    """ returns a gradient list of (n) colors between
      two hex colors. start_hex and finish_hex
      should be the full six-digit color string,
      including the number sign ("#FFFFFF")

    Note: Starting and ending colors in RGB form """

    s = hex_to_rgb(start_hex)
    f = hex_to_rgb(finish_hex)

    # Initialize a list of the output colors with the starting color
    rgb_list = [s]
    # Calculate a color at each evenly spaced value of t from 1 to n
    for t in range(1, n):
        # Interpolate RGB vector for color at the current value of t
        curr_vector = [
            int(s[j] + (float(t) / (n - 1)) * (f[j] - s[j]))
            for j in range(3)
        ]
        # Add it to our list of output colors
        rgb_list.append(curr_vector)

    return color_dict(rgb_list)


def polylinear_gradient(colors, n):
    """ returns a list of colors forming linear gradients between
        all sequential pairs of colors. "n" specifies the total
        number of desired output colors """

    color_count = len(colors)

    if n < 1:
        out = []
    elif color_count == 1:
        out = colors * n
    elif n == 1:
        out = [colors[0]]
    elif n == 2:
        out = [colors[0], colors[-1]]
    elif n < color_count:
        out = [colors[0]]
        colors_per_grad = float(len(colors) - 1) / float(n - 1)

        for i in range(1, n):
            out.append(colors[round(i * colors_per_grad)])

    elif n == color_count:
        out = colors
    else:
        # elif n > color_count > 1:
        # TODO: There must be a better way to band by these colors, not apparent right now
        extended = [colors[0]]
        colors_per_grad = float(n) / float(len(colors))

        for i in range(color_count - 1):
            span = linear_gradient(colors[i], colors[i + 1], int(math.ceil(colors_per_grad)) + 1)
            extended.extend(span['hex'][1:])

        out = polylinear_gradient(extended, n)

    return out


fact_cache = {}


def fact(n):
    """ Factorial function """

    try:
        return fact_cache[n]
    except KeyError:
        if n == 1 or n == 0:
            result = 1
        else:
            result = n * fact(n - 1)
        fact_cache[n] = result
        return result


def bernstein(t, n, i):
    """ Bernstein coefficient """
    binomial = fact(n) / float(fact(i) * fact(n - i))
    return binomial * ((1 - t) ** (n - i)) * (t ** i)


def bezier_gradient(colors, n_out=100):
    """ Returns a "bezier gradient" dictionary
        using a given list of colors as control
        points. Dictionary also contains control
        colors/points.

    Use RGB vectors for each color, use as control points """

    rgb_list = [hex_to_rgb(color) for color in colors]
    n = len(rgb_list) - 1

    def bezier_interp(t):
        """ Define an interpolation function
            for this specific curve
        # List of all stop_points """

        stop_points = [
            list(map(lambda x: int(bernstein(t, n, i) * x), c))
            for i, c in enumerate(rgb_list)
        ]
        # Output color
        out = [0, 0, 0]
        # Add components of each stop_points together

        for vector in stop_points:
            for c in range(3):
                out[c] += vector[c]

        return out

    gradient = [
        bezier_interp(float(t) / (n_out - 1))
        for t in range(n_out)
    ]
    # Return all points requested for gradient
    return {
        "gradient": color_dict(gradient),
        "control": color_dict(rgb_list)
    }


def weighted_choice(weights, objects):
    """Return a random item from objects, with the weighting defined by weights
    (which must sum to 1)."""
    cs = cumsum(weights)  # An array of the weights, cumulatively summed.
    idx = sum(cs < rnd.rand())  # Find the index of the first weight over a random value.
    return objects[idx]


COLOR_MAPS = Map()
COMMON_TEXTURES = Map()


def init():
    COLOR_MAPS.RainbowPrime = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082", "#9400D3"]
    COLOR_MAPS.Rainbow = [(53, 0, 0), (175, 0, 54), (255, 120, 7), (92, 92, 0), (29, 43, 0), (0, 50, 73),
                          (0, 15, 73), (58, 0, 103)]

    COMMON_TEXTURES.RainbowGlass = Texture1D(
        Map(gradient=True, gradient_type="linear", onlyBlock="Block", name_contains="Glass",
            colors=COLOR_MAPS.Rainbow, axis="y"))
    COMMON_TEXTURES.OldStoneWall = Texture1D(Map(blocks=[4, 48, (97, 1)], chances=[.90, .08, .02], random=True))


init()
