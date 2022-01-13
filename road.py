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

        if self.angle == other.angle:
            return None

        # if self.start[0] <
        raise NotImplementedError


    def split_road(self, point) -> "Road":
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
