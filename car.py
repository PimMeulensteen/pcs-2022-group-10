from road import *
from math import dist
from random import choice


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

        self.road = road
        self.progress = 0
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

        #how far the car is along the road
        self.progress = dist(self.pos, self.road.start) / self.road.length

        #change road if necessary
        self.change_road()

    def change_road(self):
        """
        Makes the cars change roads if there is a road to change to and
        the current road has ended.
        """
        if self.progress > 1:
            if len(self.road.children) == 0:
                return 0
            self.road = choice(self.road.children)
            self.pos = [self.road.start[0], self.road.start[1]]
            self.progress = 0
            self.dir = self.road.angle
        return 0

    def change_speed(self, cars):
        """
        Makes the car change its speed if the car in front is slower
        """

        #Werkt erg slecht, moeten we nog doen
        """
        for car in cars:
            if car.progress > self.progress and car.road == self.road:
                if dist(car.pos, self.pos) <= 50:
                    self.speed -= 50/dist(car.pos, self.pos)
                    self.speed = max(self.speed, 10)
        """

        pass


    def on_screen(self, width, height) -> bool:
        """
        Finds out if a car is of screen and deletes it if it is.
        """
        if self.pos[0] < 0 or self.pos[0] > width:
            return False
        elif self.pos[1] < 0 or self.pos[1] > height:
            return False
        return True


    def __eq__(self, other: object) -> bool:
        if isinstance(other, Car):
            return self.road == other.road and self.speed == other.speed and\
                   self.color == other.color and self.pos == other.pos
        return False