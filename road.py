import numpy as np
from car import Car
from random import randint
from typing import Tuple


class Road:
    """
    Defines a road by its start and end points.
    """

    def __init__(self, start, end):
        """
        Sets the start parameters:
        start, end, id, length and angle
        """
        self.start = start
        self.end = end

        deltaX = end[0] - start[0]
        deltaY = end[1] - start[1]
        self.length = np.sqrt(deltaX ** 2 + deltaY ** 2)
        # in pygame, y is going down, so we have to invert it
        self.angle = -np.arctan2(deltaY, deltaX)

    def intersects(self, other):
        """
        Check if the road intersects with the other road.
        Returns the intersection point if it does, None otherwise.
        """
        if self == other:
            return None

        if (self.angle % np.pi) == (other.angle % np.pi):
            return None

        xs1, ys1, xe1, ye1 = self.start + self.end
        xs2, ys2, xe2, ye2 = other.start + other.end

        # determine at what fraction of the (extended) line segments the
        # intersection lies, fractions lie in the unit interval if it exists
        selffrac = ((xs1 - xs2) * (ys2 - ye2) - (ys1 - ys2) * (xs2 - xe2)) / (
            (xs1 - xe1) * (ys2 - ye2) - (ys1 - ye1) * (xs2 - xe2)
        )

        otherfrac = ((xs1 - xs2) * (ys1 - ye1) - (ys1 - ys2) * (xs1 - xe1)) / (
            (xs1 - xe1) * (ys2 - ye2) - (ys1 - ye1) * (xs2 - xe2)
        )

        # check if the intersection lies on the line segments
        if 0 < selffrac < 1 and 0 < otherfrac < 1:
            return [xs1 + selffrac * (xe1 - xs1), ys1 + selffrac * (ye1 - ys1)]
        else:
            return None

    def split_road(self, point):
        """
        Splits the road in two at the given point.
        """
        old_end = self.end
        self.end = point
        return Road(point, old_end)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Road):
            return self.start == other.start and self.end == other.end

        return False
