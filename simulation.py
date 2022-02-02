from road import Road
from car import Car
from network import Network

import matplotlib.pyplot as plt
import sys
import pygame
from random import random, randint, uniform
import numpy as np
from numpy.random import choice

pygame.init()

# Some colors to use.
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)

# Size and width of the pygame screen.
SIZE = WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode(SIZE)

# Width of the road and length of the cars.
R_WIDTH = 10
C_LENGTH = 16
MIN_DIST = 40


class PollutionMap:
    """
    Used to create a map of pollution. Visualize the pollution in the simulation
    and keep track of the pollution.
    """

    def __init__(self, pol_type="co2") -> None:
        """Sets the pollution to plot."""
        self.pol_map = np.zeros(SIZE)
        self.total_pol = 0
        self.pol_type = pol_type

    def __try_add(self, x, y, level):
        """
        Check if the position is within the map.
        If it is, it add the pollution to the map and to the total pollution.
        """
        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            return
        self.pol_map[x, y] = self.pol_map[x, y] + level
        self.total_pol = self.total_pol + level

    def add_pollution(self, x, y, level, spread=15):
        """
        Add pollution to the map. Spread the pollution over a certain area.
        The spread is a number of pixels. The pollution is added to the map
        and to the total pollution. A spread of 0 means that the pollution
        is added to the total only.
        """
        if spread == 0:
            self.total_pol = self.total_pol + level
            return

        for i in range(-spread + 1, spread):
            for j in range(-spread + 1, spread):
                self.__try_add(
                    round(x + i), round(y + j), level / (abs(i) + abs(j) + 1)
                )

    def draw_map(self, ax):
        """ Draws a subplot in matplotlib."""
        ax.imshow(self.pol_map.T, interpolation="none", cmap="hot", vmin=0)
        ax.set_title(f"{self.pol_type} pollution")
        ax.legend()
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.axis("off")


class Simulation:
    """Define a simulation of the traffic at the intersection."""

    def __init__(self, pol_type="", save_pol_map=True) -> None:
        # The number of simulation frames per second.
        self.FPS = 30
        # The length of one simulation step.
        self.dt = 1 / self.FPS
        self.cars = []
        self.roads = []
        self.network = Network()
        self.timer = 0
        self.light_duration = 20
        self.car_gen_prob = 1
        self.num_cars = 0

        # Create the roads.
        self.create_roads()

        # Add them to the network.
        self.network.add_roads(self.roads)
        self.network.calibrate()

        # Start the traffic lights.
        self.set_trafficlights()

        # Prepare parameters for the polution.
        self.pol_type = pol_type
        if len(pol_type) > 0:
            self.pol_maps = [PollutionMap(pol_type)]
        else:
            self.pol_maps = [
                PollutionMap("co2"),
                PollutionMap("no"),
                PollutionMap("hc"),
                PollutionMap("co"),
            ]

        self.pol_spread = 15 if save_pol_map else 0

    def create_roads(self) -> None:
        """Generate roads for the simulation."""
        self.create_road([500, 215], [0, 215])
        self.create_road([0, 285], [500, 285])
        self.create_road([215, 0], [215, 500])
        self.create_road([285, 500], [285, 0])

    def create_road(self, start=[0, 0], end=[0, 0], r=None) -> None:
        """
        Create a road object. Ensure that if the road intersects with another
        road, it will split the current road and the intersecting road both into
        two new roads so that the intersection no longer occurs.
        """
        if r:
            new_road = r
        else:
            new_road = Road(start, end)
        self.roads.append(new_road)

        # Check if the road intersects with another road.
        # If so, split the roads (the new and the intersected road) into two.
        for road in self.roads:
            intersection = road.intersects(new_road)
            if intersection:
                r1 = road.split_road(intersection)
                r2 = new_road.split_road(intersection)

                # Only create a road if the road truly intersects,
                # i.e, it does not only touch the intersection point.
                # Else, a road with length zero would be created.
                if r1:
                    self.create_road(r=r1)
                if r2:
                    self.create_road(r=r2)

    def set_trafficlights(self):
        """Set the traffic light to red, for each incoming road."""
        for road in self.network.in_roads:
            road.green = False

    def step(self) -> None:
        """Simulate one step and draw it."""
        self.simulate()
        self.draw()

    def create_car(self, path=None, random=False, speed=13, color=YELLOW):
        """
        Create a car object. If random is True, it will have a
        random speed and be on a random start_road.
        """

        if random:
            speed = uniform(50, 61)
            # Index 0 for right, 1 for straight, 2 for left, 3 for U-turn.
            # Also defines the likelyhood. In this case, 10% U-turn,
            # 30% for the rest.
            index = choice([0, 1, 2, 3], p=[0.3, 0.3, 0.3, 0.1])

            # Choose a path according to the type.
            # Since the paths are ordened by length, we can use 0 for right,
            # which is the shortest path, etc.
            path = self.network.paths[randint(0, 3) + 4 * index]

        # Only spawn the car if there is space to do so.
        if path[0].full():
            return 1

        self.cars.append(Car(speed, path, color))
        self.num_cars += 1
        return 0

    def simulate(self) -> None:
        """Simulate a small step of traffic flow."""

        self.switch_trafficlights()

        self.timer += 1

        # Update every car.
        for car in self.cars:
            car.change_speed(self.dt, self.network.in_roads)

            # Move the car and check if the path is complete.
            done = car.move(self.dt)

            # Update the pollution.
            if len(self.pol_type) > 1:
                self.pol_maps[0].add_pollution(
                    *car.gen_pollution(self.dt, self.pol_type), self.pol_spread
                )
            else:
                for i in range(4):
                    pol_type = ["co2", "no", "hc", "co"][i]
                    self.pol_maps[i].add_pollution(
                        *car.gen_pollution(self.dt, pol_type), self.pol_spread
                    )

            # Delete cars if their path is complete.
            if done:
                self.cars.remove(car)
                del car

        # Spawn new random cars.
        if random() < self.car_gen_prob / 100:
            self.create_car(random=True)

    def switch_trafficlights(self):
        """Switch traffic lights every self.light_duration steps."""
        if (self.timer % (self.FPS * self.light_duration)) == 0:
            next = 2 * ((self.timer // (self.FPS * self.light_duration)) % 2)

            self.network.in_roads[next].green = True
            self.network.in_roads[next + 1].green = True
        elif ((self.timer + (4 * self.FPS)) % (self.FPS * self.light_duration)) == 0:
            next = 2 * (
                ((self.timer + (4 * self.FPS)) //
                 (self.FPS * self.light_duration)) % 2
            )

            self.network.in_roads[(next - 2) % 4].green = False
            self.network.in_roads[(next - 1) % 4].green = False

    def draw(self):
        """Draw the cars and the roads to the screen."""
        # First make the screen black.
        screen.fill(0)

        self.draw_roads()
        self.draw_cars()
        pygame.display.update()

    def draw_roads(self):
        """Draw the roads to the screen."""
        # Loop through the roads and get the corners and plot them.
        for road in self.roads:

            # Get the perpendicular angle for the width of the road.
            perp = np.pi / 2 + road.angle

            # Width of the road.
            w = R_WIDTH
            offset = [w * np.cos(perp), -w * np.sin(perp)]

            # Corners of the road.
            p1 = [x + y for x, y in zip(road.start, offset)]
            p2 = [x - y for x, y in zip(road.start, offset)]
            p3 = [x - y for x, y in zip(road.end, offset)]
            p4 = [x + y for x, y in zip(road.end, offset)]

            # Draw the road polygon.
            pygame.draw.polygon(screen, GRAY, [p1, p2, p3, p4])

            # Draw arrows that denote the direction.
            d = [w * np.cos(road.angle), w * -np.sin(road.angle)]
            shift = [32 * (y - x) / 64 for x, y in zip(road.start, road.end)]
            center = [x + y + (z / 2) for x, y, z in zip(road.start, shift, d)]
            p1s = [x + y - (z / 2) for x, y, z in zip(p1, shift, d)]
            p2s = [x + y - (z / 2) for x, y, z in zip(p2, shift, d)]

            # Draw the traffic light color onto the road.
            # The arrow points in the direction of the road.
            trafficlight_color = GREEN if road.green else RED
            pygame.draw.line(screen, trafficlight_color, p1s, center, width=5)
            pygame.draw.line(screen, trafficlight_color, p2s, center, width=5)

    def draw_cars(self):
        """Draw the cars to the screen."""
        for car in self.cars:

            # Get the perpendicular angle for the width of the car.
            perp = (car.dir + np.pi / 2) % (np.pi * 2)

            # The width and length of the car in its proper orientation.
            w = R_WIDTH - 2
            l = C_LENGTH
            offsetw = [w * np.cos(perp), -w * np.sin(perp)]
            offsetl = [l * np.cos(car.dir), -l * np.sin(car.dir)]

            # The corners of the car.
            p1 = [x + y + z for x, y, z in zip(car.pos, offsetw, offsetl)]
            p2 = [x + y - z for x, y, z in zip(car.pos, offsetw, offsetl)]
            p3 = [x - y - z for x, y, z in zip(car.pos, offsetw, offsetl)]
            p4 = [x - y + z for x, y, z in zip(car.pos, offsetw, offsetl)]

            # Draw the car.
            pygame.draw.polygon(screen, car.color, [p1, p2, p3, p4])

    def draw_pol_map(self):
        """Draws the map of the different types of pollution."""

        _, axs = plt.subplots(2, 2, figsize=(8, 8))
        plt.suptitle("Pollution heatmap for differnet pollution types")
        plt.subplots_adjust(wspace=0.02, hspace=0.1)
        for pol_map, ax in zip(self.pol_maps, axs.flatten()):
            # ax.set_aspect('equal')
            pol_map.draw_map(ax)
        plt.savefig("pollution.png")


def main():
    sim = Simulation()
    # Otherwise the window is immediately closed.
    while True:
        sim.step()
        # Close the window and draw the pollution map.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sim.draw_pol_map()
                pygame.quit()
                sys.exit()


if __name__ == "__main__":
    main()
