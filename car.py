""" This file contains a class for a car. The car class has a
    method to move the car on a Raod, to change Roads at the end of the road and to update the
    speed based on other veichles. """

from road import *
from math import dist
from random import choice
import numpy as np


class Car:
    def __init__(self, max_speed, path, color, roads):
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

        # If there are cars on the road, the most recent one is the closest
        if len(roads[roads.index(self.road)].cars) > 0:
            self.in_front = roads[roads.index(self.road)].cars[-1]
        else:
            self.in_front = None

        roads[roads.index(self.road)].cars.append(self)


        # otherwise pass by reference
        # maybe one of you knows a fix
        self.pos = [self.road.start[0], self.road.start[1]]

        self.progress = 0
        self.dir = self.road.angle

    def cur_polution(self):
        # These valeus are for CO emissions. The values are in mg/sec, and based on the pape
        # "On Road Measurements of Vehicle Tailpipe Emissions" by Frey et al.
        # TODO make this more general
        if self.speed < 10:
            # We consider speeds less than 10 km/h as idle
            return 1.5

        if self.a > 0:
            return 23

        if self.a < 0:
            return 5.5

        return 11

    def gen_polution(self, dt):
        """
        Adds pollution to the road the car is on.
        """
        return self.pos[0], self.pos[1], self.cur_polution()

    def move(self, dt, roads):
        """
        Moves the car according to the timestep and its speed
        """
        # In pygame, y is going down, so we have to invert it
        self.pos[0] += np.cos(self.dir) * self.speed * dt
        self.pos[1] += -np.sin(self.dir) * self.speed * dt

        # How far the car is along the road
        self.progress = dist(self.pos, self.road.start) / self.road.length

        # If the car is at the end of the path, we want to remove it
        if self.progress > 1 and self.index >= len(self.path) - 1:
            roads[roads.index(self.road)].cars.remove(self)
            return True

        # If the car is at the end of the road, change the road
        if self.progress > 1:
            self.index += 1
            self.change_road(roads)

        # If the car in front has moved to a different road, remove it
        if self.in_front:
            if self.in_front.road != self.road:
                self.in_front = None
            # If the car in front has ended, remove it
            elif self.in_front.index == len(self.path) - 1:
                if self.in_front not in roads[roads.index(self.road)].cars:
                    self.in_front = None


        return False

    def change_road(self, roads):
        """
        Makes the cars change roads if there is a road to change to and
        the current road has ended.
        """
        if self.progress > 1:
            # Remove the car from the current road
            roads[roads.index(self.road)].cars.remove(self)

            self.road = self.path[self.index]
            self.pos = [self.road.start[0], self.road.start[1]]
            self.progress = 0
            self.dir = self.road.angle

            # If there are cars on the road, the most recent one is the closest
            if len(roads[roads.index(self.road)].cars) > 0:
                self.in_front = roads[roads.index(self.road)].cars[-1]
            else:
                self.in_front = None

            # Add the car to the new road
            roads[roads.index(self.road)].cars.append(self)

    def change_speed(self, dt):
        """
        Makes the car change its speed if the car in front is slower
        """
        #if there is a car in front, match its speed
        if self.in_front:
            self.decelerate(self.in_front.speed, self.in_front.progress,
                            self.in_front.road.length)
        # if there is no car in front and green, accelerate to the max
        elif not self.in_front and self.road.green == True:
            self.a = self.max_a * (1 - (self.speed / self.max)**self.delta)
        # if at a red light, decelerate to a stop
        else:
            if 0.65 < self.progress < 0.85:
                self.decelerate(0, 0.85, self.road.length, min_des_dist=0)
            elif 0.85 < self.progress < 0.9:
                self.a = 0
                self.speed = 0

        # Eulers method
        self.speed += self.a * dt

        # Cap speed at the max
        self.speed = min(self.speed, self.max)

    def decelerate(self, aim_speed, aim_progr, aim_roadlen, min_des_dist=40):
        """
        Decelerate according to a desired speed and where on the road this
        should be reached. For example: can be used to decelerate according
        to a car in front, or to decelerate when approaching a red light.
        """
        speed_div = np.abs(self.speed - aim_speed)
        distance = np.abs(self.progress * self.road.length -
                          aim_progr * aim_roadlen)

        # get the desired distance to the car in front
        react_dist = self.speed * self.reaction
        des_dist = (min_des_dist + react_dist + (self.speed * speed_div) /
                    (2 * np.sqrt(self.max_a * self.max_brake)))

        # get the acceleration
        self.a = self.max_a * (1 - (self.speed / self.max)**self.delta -
                               (des_dist / distance)**2)

        # if too close to car in front or desired point is reached, brake
        if distance < des_dist:
            self.a = 0
            self.speed = 0

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Car):
            return (self.road == other.road and self.speed == other.speed
                    and self.color == other.color and self.pos == other.pos)
        return False
