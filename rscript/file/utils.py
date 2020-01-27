__all__ = [
    "Point", "Rect", "MinMax",
    "str_to_bool", "str_to_heredoc",
    "bytes_xor", "bytes_to_int", "bytes_to_uint",
    "int_to_bytes", "uint_to_bytes", "rgb_to_dword",
    "random_point", "near_point",
]

from random import randint


def sin(x):
    sign = 1
    if x > 180:
        x -= 180
        sign = -1
    return sign * 4 * x * (180 - x) / (40500 - x * (180 - x))


def cos(x):
    sign = 1
    if x > 90:
        x -= 180
        sign = -1
    elif x > 270:
        x -= 360
    return sign * (4 * (8100 - x * x)) / (32400 + x * x)


class Point:
    __slots__ = "x", "y"

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __str__(self):
        return f"{self.x},{self.y}"


class Rect:
    __slots__ = "top", "left", "width", "height"

    def __init__(self, top, left, width, height):
        self.top = top
        self.left = left
        self.width = width
        self.height = height

    @property
    def bottom(self):
        return self.top + self.height

    @property
    def right(self):
        return self.left + self.width

    def __repr__(self):
        return f"Rect({self.top}, {self.left}, {self.width}, {self.height})"

    def __str__(self):
        return f"{self.top},{self.left},{self.bottom},{self.right}"


class MinMax:
    __slots__ = "min", "max"

    def __init__(self, min, max):
        """
        :type min: int | float | str
        :type max: int | float | str
        """
        self.min = min
        """:type : T"""
        self.max = max
        """:type : T"""

    def __repr__(self):
        return f"MinMax({self.min}, {self.max})"

    def __str__(self):
        return f"{self.min}..{self.max}"

    @classmethod
    def from_str(cls, s, f=str):
        """
        :type s: str
        :type f: type
        :rtype: MinMax
        """
        min, max = s.split('..', 1)
        return cls(f(min), f(max))


def str_to_bool(s):
    """
    :type s: str
    :rtype: bool
    """
    return s.lower() in ("true", "yes")


def bytes_xor(a, b):
    """
    :type a: bytes
    :type b: bytes
    :rtype : bytes
    """
    return bytes(_a ^ _b for (_a, _b) in zip(a, b))


def bytes_to_int(a):
    return int.from_bytes(a, 'little', signed=True)


def bytes_to_uint(a):
    return int.from_bytes(a, 'little', signed=False)


def int_to_bytes(a):
    return a.to_bytes(4, 'little', signed=True)


def uint_to_bytes(a):
    return a.to_bytes(4, 'little', signed=False)


def str_to_heredoc(s):
    result = ['<<<', s, '>>>']
    return '\x0d\x0a'.join(result)


def rgb_to_dword(r, g, b):
    return (b << 16) | (g << 8) | r


def random_point(rect=Rect(80, 0, 800, 1000)):
    return Point(randint(rect.left, rect.right),
                 randint(rect.top, rect.bottom))


def near_point(pos=random_point(), radius=60):
    angle = randint(0, 360)
    sh_x = cos(angle) * radius
    sh_y = sin(angle) * radius
    return Point(int(pos.x + sh_x), int(pos.y + sh_y))
