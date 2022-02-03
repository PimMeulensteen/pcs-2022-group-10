"""
This file contains a class for a car. The car class has a
method to move the car on a Road, to change Roads at the end of the road and
to update the speed based on other veichles.
"""

from math import dist
import numpy as np
from dataclasses import dataclass


@dataclass
class EmmissionType:
    idle: float
    accel: float
    decel: float
    cruise: float


CAR_NO = EmmissionType(0.06, 1.4, 0.52, 1.1)
CAR_HC = EmmissionType(0.25, 1, 0.36, 0.6)
CAR_CO = EmmissionType(1.5, 23, 5.5, 11)
CAR_CO2 = EmmissionType(1.7, 6.4, 2.6, 4.1)
EM_TYPES = {"NO": CAR_NO, "HC": CAR_HC, "CO": CAR_CO, "CO2": CAR_CO2}


class Car:
    def __init__(self, max_speed, path, color):
        """Set the start parameters"""
        self.max = max_speed
        self.v = max_speed
        self.a = 0
        self.color = color

        self.reaction = 1.6
        self.delta = 4

        # A meter is 4 pixels, so times 4.
        self.max_a = 0.73 * 4
        self.max_brake = 1.67 * 4

        # Variables for the path of the car.
        self.path = path
        self.index = 0
        self.road = self.path[0]

        # Variables for the position and orientation.
        self.pos = [self.road.start[0], self.road.start[1]]
        self.dir = self.road.angle

        # How far the car is on the current road.
        self.progress = 0

        # Which car is in front
        self.in_front = self.check_in_front()

        # Add the car to the list of cars on that road.
        self.road.cars.append(self)

    def cur_pollution(self, pol_type="CO2"):
        """
        These valeus are for CO emissions. The values are in mg/sec, and based
        on the paper "On Road Measurements of Vehicle Tailpipe Emissions" by
        Frey et al.
        """
        if self.v < 10:
            # We consider speeds less than 10 units/second as idle
            return EM_TYPES[pol_type].idle

        if self.a > 0.1:
            return EM_TYPES[pol_type].accel

        if self.a < 0.1:
            return EM_TYPES[pol_type].decel
        return EM_TYPES[pol_type].cruise

    def gen_pollution(self, dt, pol_type="CO2"):
        """Add pollution to the road the car is on."""
        return self.pos[0], self.pos[1], self.cur_pollution(pol_type) * dt

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

        # Add the car to the new road
        self.road.cars.append(self)

        return False

    def change_speed(self, dt, in_roads):
        """
        Makes the car change its speed if the car in front is slower
        """

        # Check if there is a car in front of you.
        self.in_front, distance = self.check_in_front()
        if self.in_front:
            # If there is a car on the same road in front, match its speed.
            if self.in_front.road == self.road:
                self.decelerate(self.in_front.v, distance)
            # Wait if necessary.
            elif self.wait(in_roads):
                distance = self.road.length - self.progress * self.road.length
                self.decelerate(0, distance)
            # If there is a car in front on another road, match its speed,
            else:
                self.decelerate(self.in_front.v, distance)

        # Wait if necessary.
        if self.wait(in_roads):
            distance = self.road.length - self.progress * self.road.length
            self.decelerate(0, distance)
        # If there is no car in front and no wait, accelerate to the max.
        elif self.road.green:
            self.a = self.max_a * (1 - (self.v / self.max) ** self.delta)

        # Eulers method
        self.v += self.a * dt

        # Cap speed at the max
        self.v = min(self.v, self.max)
        self.v = max(self.v, 0)

    def decelerate(self, aim_speed, distance, min_des_dist=45):
        """
        Decelerate according to a desired speed and where on the road this
        should be reached. For example: can be used to decelerate according
        to a car in front, or to decelerate when approaching a red light.
        """
        speed_div = self.v - aim_speed

        # Get the desired distance to the car in front.
        react_dist = self.v * self.reaction
        des_dist = (
            min_des_dist
            + react_dist
            + (self.v * speed_div) / (2 * np.sqrt(self.max_a * self.max_brake))
        )
        # Get the acceleration.
        self.a = self.max_a * (
            1 - (self.v / self.max) ** self.delta - (des_dist / distance) ** 2
        )

        if distance < min_des_dist:
            self.v = 0
            self.a = 0

    def wait(self, in_roads):
        """Decide if a car should wait."""
        if not self.road.green:
            return True
        if self.index < len(self.path) - 1:
            # Wait if a car is coming that has the right of way.
            for road in self.path[self.index + 1].parents:
                if road == self.road:
                    continue

                if road.green and road in in_roads:
                    for car in road.cars:
                        if dist(car.pos, car.road.end) < 80:
                            return True
        return False

    def check_in_front(self):
        """
        Check if there is a car in front of self, and returns it
        and the distance between the cars.
        """
        nearest = None
        nearest_progress = 1

        # Check the cars on the current road first.
        for car in self.road.cars:
            if (
                car.progress > self.progress
                and car.progress < nearest_progress
            ):
                nearest_progress = car.progress
                nearest = car

        # Return if there is.
        if nearest:
            return (
                nearest,
                nearest_progress * car.road.length
                - self.progress * self.road.length,
            )

        # Check the other roads in the path.
        for road in self.path[self.index + 1 :]:
            road_index = self.path.index(road)
            for car in road.cars:
                if car.progress < nearest_progress:
                    nearest_progress = car.progress
                    nearest = car

            if nearest:
                # Calculate the distance between. This is the sum of the road
                # lengths minus the progress the cars have made.
                distance = sum(
                    [r.length for r in self.path[self.index : road_index]]
                )
                distance += nearest.progress * nearest.road.length
                distance -= self.progress * self.road.length
                return nearest, distance

        return None, 0

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Car):
            return (
                self.road == other.road
                and self.v == other.v
                and self.color == other.color
                and self.pos == other.pos
            )
        return False
