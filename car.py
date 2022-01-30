"""
This file contains a class for a car. The car class has a
method to move the car on a Road, to change Roads at the end of the road and
to update the speed based on other veichles. """

from road import *
from math import dist
import numpy as np

class Car:
    def __init__(self, max_speed, path, color, roads):
        """Set the start parameters"""
        self.max = max_speed
        self.v = max_speed
        self.a = 0
        self.color = color

        self.reaction = 0
        self.delta = 3
        self.max_a = 30
        self.max_brake = 30

        self.path = path
        self.index = 0
        self.road = self.path[0]

        self.pos = [self.road.start[0], self.road.start[1]]
        self.progress = 0
        self.dir = self.road.angle

        # If there are cars on the road, the most recent one is the closest.
        if len(self.road.cars) > 0:
            self.in_front = self.road.cars[-1]
        else:
            self.in_front = None

        self.road.cars.append(self)

    def cur_polution(self):
        # These valeus are for CO emissions. The values are in mg/sec, and based on the pape
        # "On Road Measurements of Vehicle Tailpipe Emissions" by Frey et al.
        # TODO make this more general
        if self.v < 10:
            # We consider speeds less than 10 km/h as idle
            return 1.5

        if self.a > 0:
            return 23

        if self.a < 0:
            return 5.5

        return 11

    def gen_polution(self, dt):
        """Add pollution to the road the car is on."""
        return self.pos[0], self.pos[1], self.cur_polution()

    def move(self, dt):
        """Move the car according to the timestep and its speed."""
        # In pygame, y is going down, so we have to invert it.
        self.pos[0] += np.cos(self.dir) * self.v * dt
        self.pos[1] += -np.sin(self.dir) * self.v * dt

        # How far the car is along the road.
        self.progress = dist(self.pos, self.road.start) / self.road.length

        # If the car is at the end of the road, change the road.
        if self.progress > 1:
            return self.change_road()

        # If the car in front has moved to a different road, remove it
        if self.in_front:
            if self.in_front not in self.road.cars:
                self.in_front = None

        return False

    def change_road(self):
        """
        Make the cars change roads if there is a road to change to and
        the current road has ended. Return True if this can be done, otherwise
        return False.
        """
        # Remove the car from the current road
        self.road.cars.remove(self)

        self.index += 1
        if self.index >= len(self.path):
            return True

        self.road = self.path[self.index]
        self.pos = [self.road.start[0], self.road.start[1]]
        self.progress = 0
        self.dir = self.road.angle

        # If there are cars on the road, the most recent one is the closest.
        if len(self.road.cars) > 0:
            self.in_front = self.road.cars[-1]
        else:
            self.in_front = None

        # Add the car to the new road
        self.road.cars.append(self)

        return False

    def change_speed(self, dt, in_roads):
        """
        Makes the car change its speed if the car in front is slower
        """
        # If there is a car in front, match its speed,
        if self.in_front:
            self.decelerate(self.in_front.v, self.in_front.progress,
                            self.in_front.road.length)
        # Wait if necessary.
        elif self.wait(in_roads) == True:
            self.decelerate(0, 1, self.road.length)
        # If there is no car in front and no wait, accelerate to the max.
        elif self.road.green == True:
            self.a = self.max_a * (1 - (self.v / self.max)**self.delta)

        # Eulers method
        self.v += self.a * dt

        # Cap speed at the max
        self.v = min(self.v, self.max)
        self.v = max(self.v, 0)

    def decelerate(self, aim_speed, aim_progr, aim_roadlen, min_des_dist=40):
        """
        Decelerate according to a desired speed and where on the road this
        should be reached. For example: can be used to decelerate according
        to a car in front, or to decelerate when approaching a red light.
        """
        speed_div = self.v - aim_speed
        distance = aim_progr * aim_roadlen - self.progress * self.road.length

        # Get the desired distance to the car in front.
        react_dist = self.v * self.reaction
        des_dist = (min_des_dist + react_dist + (self.v * speed_div) /
                    (2 * np.sqrt(self.max_a * self.max_brake)))
        # Get the acceleration.
        self.a = self.max_a * (1 - (self.v / self.max)**self.delta -
                               (des_dist / distance)**2)

        if distance < min_des_dist:
            self.v = 0
            self.a = 0

    def wait(self, in_roads):
        """Decide if a car should wait."""
        if self.road.green == False:
            return True
        if self.index < len(self.path) - 1:
            # Wait if the next road is occupied.
            if self.path[self.index + 1].full(self.v) == True and self.progress > 0.8:
                return True

            # Wait if a car is coming that has the right of way.
            for road in self.path[self.index + 1].parents:
                if road == self.road:
                    continue
                if road.green == True and road in in_roads:
                    for car in road.cars:
                        if car.progress > 0.5:
                            return True
        return False


    def __eq__(self, other: object) -> bool:
        if isinstance(other, Car):
            return (self.road == other.road and self.v == other.v
                    and self.color == other.color and self.pos == other.pos)
        return False
