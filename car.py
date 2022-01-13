from road import *


class Car:
    def __init__(self, speed, road, color):
        """
        Sets the start parameters:
        speed, color, position and direction
        """
        self.speed = speed
        self.color = color

        # otherwise pass by reference
        # maybe one of you knows a fix
        self.pos = [road.start[0], road.start[1]]

        self.dir = road.angle

    def move(self, dt):
        """
        Moves the car according to the timestep and its speed
        """
        movx = np.cos(self.dir) * self.speed * dt
        # in pygame, y is going down, so we have to invert it
        movy = -np.sin(self.dir) * self.speed * dt

        self.pos[0] += movx
        self.pos[1] += movy
