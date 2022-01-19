from road import *
from math import dist
from random import choice
import numpy as np


class Car:
    def __init__(self, max, road, color):
        """
        Sets the start parameters:
        speed, color, position and direction
        """
        self.max = max
        self.speed = max
        self.color = color


        self.reaction = 0
        self.delta = 4
        self.a = 0
        self.max_a = 70
        self.max_brake = 100

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

    def change_speed(self, cars, dt):
        """
        Makes the car change its speed if the car in front is slower
        """
        nearest = None
        for car in cars:

            n_p = nearest.progress if nearest else 1

            #check if car is behind another car
            if car.progress > self.progress and car.road == self.road and car.progress <= n_p:
                nearest = car

                speed_div = np.abs(self.speed - car.speed)
                distance= np.abs(self.progress * self.road.length - car.progress * car.road.length)

                #get the desired distance to the car in front
                min_des_dist = 30
                react_dist = self.speed * self.reaction
                des_dist = min_des_dist + react_dist +\
                           (self.speed * speed_div) /\
                           (2 * np.sqrt(self.max_a * self.max_brake))

                #get the acceleration
                self.a = self.max_a * (1-(self.speed/self.max) ** self.delta\
                    -(des_dist/distance) ** 2)

        #if there is no car in front, accelerate to the max
        if not nearest:
            self.a = self.max_a * (1-(self.speed/self.max) ** self.delta)

        #Eulers method
        self.speed += self.a * dt

        #Cap speed at the max
        self.speed = min(self.speed, self.max)


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