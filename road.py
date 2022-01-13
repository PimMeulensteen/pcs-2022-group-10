import numpy as np
from car import Car
from random import randint


class Road:
    """
    Defines a road by its start and end points.
    """
    def __init__(self, start, end, id):
        """
        Sets the start parameters:
        start, end, id, length and angle
        """
        self.start = start
        self.end = end
        self.id = id

        deltaX = end[0] - start[0]
        deltaY = end[1] - start[1]
        self.length = np.sqrt(deltaX**2 + deltaY**2)
        #in pygame, y is going down, so we have to invert it
        self.angle = -np.arctan2(deltaY, deltaX)

    def get_random_car_at_start(self) -> Car:
        """
            Returns a random car at the start of the road
        """
        return Car(randint(200, 300), self, (255, 255, 0))
