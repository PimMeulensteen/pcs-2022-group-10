""" This file contains a class for a car. The car class has a
    method to move the car on a Raod, to change Roads at the end of the road and to update the
    speed based on other veichles. """


from road import *
from math import dist
from random import choice
import numpy as np


class Car:
    def __init__(self, max_speed, path, color):
        """
        Sets the start parameters:
        speed, color, position and direction
        """
        self.max = max_speed
        self.speed = max_speed
        self.color = color

        self.reaction = 0
        self.delta = 4
        self.a = 0
        self.max_a = 70
        self.max_brake = 100

        self.path = path
        self.index = 0
        self.road = self.path[0]

        # otherwise pass by reference
        # maybe one of you knows a fix
        self.pos = [self.road.start[0], self.road.start[1]]

        self.progress = 0
        self.dir = self.road.angle

    def move(self, dt):
        """
        Moves the car according to the timestep and its speed
        """
        movx = np.cos(self.dir) * self.speed * dt
        # in pygame, y is going down, so we have to invert it
        movy = -np.sin(self.dir) * self.speed * dt

        self.pos[0] += movx
        self.pos[1] += movy

        # how far the car is along the road
        self.progress = dist(self.pos, self.road.start) / self.road.length

        # change road if necessary
        done = self.change_road()
        return done

    def change_road(self):
        """
        Makes the cars change roads if there is a road to change to and
        the current road has ended.
        """
        if self.progress > 1:
            self.index += 1
            if self.index >= len(self.path):
                return 1

            self.road = self.path[self.index]
            self.pos = [self.road.start[0], self.road.start[1]]
            self.progress = 0
            self.dir = self.road.angle
        return 0

    def change_speed(self, cars, dt):
        """
        Makes the car change its speed if the car in front is slower
        """

        def is_behind_other_car(other):
            """Return True if the current car is behind the other car"""
            return (
                other_car.progress > self.progress
                and other_car.road == self.road
                and other_car.progress <= n_p
            )

        nearest = None
        for other_car in cars:
            if other_car == self:
                continue

            n_p = nearest.progress if nearest else 1

            if is_behind_other_car(other_car):
                nearest = other_car

                speed_div = np.abs(self.speed - other_car.speed)
                distance = np.abs(
                    self.progress * self.road.length
                    - other_car.progress * other_car.road.length
                )

                # get the desired distance to the car in front
                min_des_dist = 30
                react_dist = self.speed * self.reaction
                des_dist = (
                    min_des_dist
                    + react_dist
                    + (self.speed * speed_div)
                    / (2 * np.sqrt(self.max_a * self.max_brake))
                )

                # get the acceleration
                self.a = self.max_a * (
                    1
                    - (self.speed / self.max) ** self.delta
                    - (des_dist / distance) ** 2
                )

        # if there is no car in front, accelerate to the max
        if not nearest:
            self.a = self.max_a * (1 - (self.speed / self.max) ** self.delta)

        # Eulers method
        self.speed += self.a * dt

        # Cap speed at the max
        self.speed = min(self.speed, self.max)

    def on_screen(self, width, height) -> bool:
        """
        Finds out if a car is of screen and deletes it if it is.
        """
        return not (
            self.pos[0] < 0
            or self.pos[0] > width
            or self.pos[1] < 0
            or self.pos[1] > height
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Car):
            return (
                self.road == other.road
                and self.speed == other.speed
                and self.color == other.color
                and self.pos == other.pos
            )
        return False
