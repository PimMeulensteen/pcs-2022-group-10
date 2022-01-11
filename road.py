import numpy as np

"""
    Defines a road by its start and end points.
"""
class Road:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.length = np.sqrt((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2)

        deltaX = end[0] - start[0]
        deltaY = end[1] - start[1]
        self.slope = "undefined" if deltaX == 0 else deltaY/deltaX
        self.angle = -np.arctan2(deltaY, deltaX) * 180 / np.pi
