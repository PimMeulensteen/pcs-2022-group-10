from road import *
from car import *
from network import *

import matplotlib.pyplot as plt
import sys
import pygame
from random import randint
from numpy.random import choice

# Sets the number of simulation frames per second
FPS = 60
clock = pygame.time.Clock()

pygame.init()

# Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)

# Size and width of the pygame screen
SIZE = WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode(SIZE)

# width of the road and lenght of the cars
R_WIDTH = 10
C_LENGTH = 16
MIN_DIST = 40


class PollutionMap:
    def __init__(self) -> None:
        self.pol_map = np.zeros(SIZE)
        self.total_pol = 0

    def __try_add(self, x, y, level):
        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            return
        # print(f"added {level} at {x}, {y}")
        self.pol_map[x, y] = self.pol_map[x, y] + level
        self.total_pol = self.total_pol + level

    def add_pollution(self, x, y, level, spread=15):
        for i in range(-spread + 1, spread):
            for j in range(-spread + 1, spread):
                self.__try_add(
                    round(x + i), round(y + j), level / (abs(i) + abs(j) + 1)
                )

    def draw_map(self):
        plt.imshow(self.pol_map, interpolation="none")
        plt.title("Pollution Map")
        plt.legend()
        plt.savefig("pollution.png")


class Simulation:
    def __init__(self) -> None:
        self.avg_FPS = 0
        self.frames = 0
        self.cars = []
        self.roads = []
        self.network = Network()
        self.startroads = []
        self.timer = 0
        self.light_duration = 10
        self.gen_random_data()
        self.pol_map = PollutionMap()

    def step(self):
        clock.tick(FPS)
        self.simulate()
        self.draw()

    def gen_random_data(self) -> None:
        # Test roads
        self.create_road([500, 215], [0, 215])
        self.create_road([0, 285], [500, 285])
        self.create_road([215, 0], [215, 500])
        self.create_road([285, 500], [285, 0])
        self.network.add_roads(self.roads)
        self.network.calibrate()
        self.set_trafficlights()

    def create_road(self, start=[0, 0], end=[0, 0], r=None):
        """This method create a road object. It ensures that if the road
        intersects with another road, it will split the current road and
        the intersecting roads both into two new roads."""
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
                if r1:
                    self.create_road(r=r1)
                if r2:
                    self.create_road(r=r2)

    def set_trafficlights(self):
        """
        Set the traffic light to red, for each incoming road.
        """
        for road in self.network.in_roads:
            road.green = False

    def create_car(self, path=None, random=False, speed=200, color=YELLOW):
        """
        This method create a car object. if random is True, it will have a
        random speed and be on a random road.
        """

        if random == True:
            speed = randint(100, 150)
            # index 0 for right, 1 for straight, 2 for left, 3 for U-turn
            index = choice([0, 1, 2, 3], p=[0.3, 0.3, 0.3, 0.1])
            path = self.network.paths[randint(0, 3) + 4 * index]

        start_road = self.roads[self.roads.index(path[0])]

        if start_road.full() == True:
            return 1

        self.cars.append(Car(speed, path, color, self.roads))
        return 0

    def simulate(self):
        """
        Simulate a small step of traffic flow.
        """
        self.switch_trafficlights()

        self.frames += 1
        self.timer += 1
        dt = clock.get_time() / 1000
        self.avg_FPS = (self.avg_FPS * (self.frames - 1) + dt) / self.frames
        # print(len(self.cars), self.avg_FPS, self.timer / 1000)

        for car in self.cars:
            car.change_speed(dt, self.network.in_roads)
            done = car.move(dt)
            self.pol_map.add_pollution(*car.gen_pollution(dt))

            # Delete cars if they are at the end of their path
            if done == True:
                self.cars.remove(car)
                del car

        # Spawns random cars
        if randint(0, 50) == 0:
            self.create_car(random=True)

    def switch_trafficlights(self):
        """
        Switch traffic lights every n steps.
        """
        if (self.timer % (FPS * self.light_duration)) == 0:
            next = 2 * ((self.timer // (FPS * self.light_duration)) % 2)

            self.network.in_roads[(next - 2) % 4].green = False
            self.network.in_roads[(next - 1) % 4].green = False
            self.network.in_roads[next].green = True
            self.network.in_roads[next + 1].green = True

    def draw(self):
        screen.fill(0)
        self.draw_roads()
        self.draw_cars()
        pygame.display.update()

    def draw_roads(self):
        """
        Draws the roads correctly to the screen.
        """
        # loop through the roads and get the dimensions
        for road in self.roads:

            # get the perpendicular angle for the width of the road
            perp = np.pi / 2 + road.angle

            # width of the road
            w = R_WIDTH
            offset = [w * np.cos(perp), -w * np.sin(perp)]

            # points to draw the rectangle
            p1 = [x + y for x, y in zip(road.start, offset)]
            p2 = [x - y for x, y in zip(road.start, offset)]
            p3 = [x - y for x, y in zip(road.end, offset)]
            p4 = [x + y for x, y in zip(road.end, offset)]

            # draw the road
            pygame.draw.polygon(screen, GRAY, [p1, p2, p3, p4])

            # draw arrows that denote the direction
            d = [w * np.cos(road.angle), w * -np.sin(road.angle)]
            shift = [32 * (y - x) / 64 for x, y in zip(road.start, road.end)]
            center = [x + y + (z / 2) for x, y, z in zip(road.start, shift, d)]
            p1s = [x + y - (z / 2) for x, y, z in zip(p1, shift, d)]
            p2s = [x + y - (z / 2) for x, y, z in zip(p2, shift, d)]

            trafficlight_color = GREEN if road.green else RED
            pygame.draw.line(screen, trafficlight_color, p1s, center, width=5)
            pygame.draw.line(screen, trafficlight_color, p2s, center, width=5)

    def draw_cars(self):
        """
        Draws the cars correctly to the screen.
        """
        for car in self.cars:

            # get the perpendicular angle for the width of the car
            perp = (car.dir + np.pi / 2) % (np.pi * 2)

            # the width and length of the car in its proper orientation
            w = R_WIDTH - 2
            l = C_LENGTH
            offsetw = [w * np.cos(perp), -w * np.sin(perp)]
            offsetl = [l * np.cos(car.dir), -l * np.sin(car.dir)]

            # the corners of the car
            p1 = [x + y + z for x, y, z in zip(car.pos, offsetw, offsetl)]
            p2 = [x + y - z for x, y, z in zip(car.pos, offsetw, offsetl)]
            p3 = [x - y - z for x, y, z in zip(car.pos, offsetw, offsetl)]
            p4 = [x - y + z for x, y, z in zip(car.pos, offsetw, offsetl)]

            # draw the car
            pygame.draw.polygon(screen, car.color, [p1, p2, p3, p4])


sim = Simulation()


def main():
    # Otherwise the window is immediately closed
    while True:
        sim.step()
        # Close the window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sim.pol_map.draw_map()
                pygame.quit()
                sys.exit()


if __name__ == "__main__":
    main()
