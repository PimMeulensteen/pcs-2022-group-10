import numpy as np
from math import dist


class Road:
    """Define a road for the car to drive on."""

    def __init__(self, start, end):
        """Defines a road by its start and end points."""
        self.start = start
        self.end = end

        self.green = True

        self.children = []
        self.parents = []

        # The cars which are on the road.
        self.cars = []

        self.length = dist(start, end)
        deltaX = end[0] - start[0]
        deltaY = end[1] - start[1]
        # in pygame, y is going down, so invert the angle
        self.angle = -np.arctan2(deltaY, deltaX)

    def intersects(self, other):
        """
        Check if the road intersects with the other road.
        Return the intersection point if it does, None otherwise.
        """
        if self == other:
            return None

        if (self.angle % np.pi) == (other.angle % np.pi):
            return None

        xs1, ys1, xe1, ye1 = self.start + self.end
        xs2, ys2, xe2, ye2 = other.start + other.end

        # Determine at what fraction of the (extended) line segments the
        # intersection lies. Fractions lie in the unit interval if it exists.
        selffrac = ((xs1 - xs2) * (ys2 - ye2) - (ys1 - ys2) * (xs2 - xe2)) / (
            (xs1 - xe1) * (ys2 - ye2) - (ys1 - ye1) * (xs2 - xe2)
        )

        otherfrac = ((xs1 - xs2) * (ys1 - ye1) - (ys1 - ys2) * (xs1 - xe1)) / (
            (xs1 - xe1) * (ys2 - ye2) - (ys1 - ye1) * (xs2 - xe2)
        )

        # Check if the intersection lies on the line segments.
        if 0 <= selffrac <= 1 and 0 <= otherfrac <= 1:
            return [xs1 + selffrac * (xe1 - xs1), ys1 + selffrac * (ye1 - ys1)]
        else:
            return None

    def split_road(self, point):
        """
        Split the road into two roads at the given point. Set the endpoint of
        the road to point and return the new road from point to end.
        """

        # If the split point is at the start or end, the road is not split.
        if self.start == point or self.end == point:
            return None

        old_end = self.end
        self.end = point
        self.length = dist(self.start, self.end)
        return Road(point, old_end)

    def full(self):
        """Check if a car can come to the road."""

        for car in self.cars:
            # If there is a car at the start and it is slower than speed,
            # the road is full.
            if dist(car.pos, self.start) <= 40:
                return True
        else:
            return False

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Road):
            return self.start == other.start and self.end == other.end
        return False
