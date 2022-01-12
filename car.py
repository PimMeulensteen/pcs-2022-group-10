from road import *

class Car:

    """
        Sets the start parameters:
        speed, color, position and direction
    """
    def __init__(self, speed, road, color):
        self.speed = speed
        self.color = color

        #otherwise pass by reference
        #maybe one of you knows a fix
        self.pos = [road.start[0], road.start[1]]

        self.dir = road.angle

    """
        Moves the car according to the timestep and its speed
    """
    def move(self, dt):

        movx = np.cos(self.dir) * self.speed * dt
        #in pygame, y is going down, so we have to invert it
        movy = -np.sin(self.dir) * self.speed * dt

        self.pos[0] += movx
        self.pos[1] += movy
