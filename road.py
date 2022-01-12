import numpy as np

"""
    Defines a road by its start and end points.
"""
class Road:
    """
        Sets the start parameters:
        start, end, id, length and angle
    """
    def __init__(self, start, end, id):
        self.start = start
        self.end = end
        self.id = id

        deltaX = end[0] - start[0]
        deltaY = end[1] - start[1]
        self.length = np.sqrt(deltaX ** 2 + deltaY ** 2)
        #in pygame, y is going down, so we have to invert it
        self.angle = -np.arctan2(deltaY, deltaX)
