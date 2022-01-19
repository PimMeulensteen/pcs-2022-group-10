from road import *
from car import *

import sys
import pygame

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
size = width, height = 500, 500
screen = pygame.display.set_mode(size)


class Simulation:
    def step(self):
        clock.tick(FPS)
        self.simulate()
        self.draw()

    def __init__(self) -> None:
        self.cars = []
        self.roads = []
        self.startroads = []
        self.timer = 0
        self.gen_random_data()

    def gen_random_data(self) -> None:
        # Test roads
        self.create_road([500, 230], [0, 230], gen=True)
        self.create_road([0, 270], [500, 270], gen=True)
        self.create_road([230, 0], [230, 500], gen=True)
        self.create_road([270, 500], [270, 0], gen=True)
        self.create_tree()

        # Test cars
        self.create_car(self.roads[0], False, 150, RED)
        self.create_car(self.roads[1], False, 100, GREEN)
        self.create_car(self.roads[2], False, 140, BLUE)
        self.create_car(self.roads[3], False, 120, WHITE)

    def create_road(self, start=[0, 0], end=[0, 0], r=None, gen=False):
        """This method create a road object. It ensures that if the road
        intersects with another road, it will split the current road and
        the intersecting roads both into two new roads."""
        if r:
            new_road = r
        else:
            new_road = Road(start, end)
        self.roads.append(new_road)

        # Mark roads where cars can generate (at the start coordinates)
        if gen:
            self.startroads.append(new_road)

        # Check if the road intersects with another road.
        # If so, split the roads (the new and the intersected road) into two.
        for road in self.roads:
            intersection = road.intersects(new_road)
            if intersection:
                self.create_road(r=road.split_road(intersection))
                self.create_road(r=new_road.split_road(intersection))

    def create_tree(self):
        """
        This gives every road their children and parents,
        so where the cars could come from and where they can go
        """
        #At first we get the roads with no parents
        to_check = self.startroads.copy()
        visited = []
        while len(to_check) > 0:
            for end_road in self.roads:

                #If a end_road is a child of to_check[0], we add it to its
                #children and add to_check[0] to end_road's parents.
                if to_check[0].end == end_road.start:
                    to_check[0].children.append(end_road)
                    end_road.parents.append(to_check[0])
                    #If we have not checked end_road, add it to the roads we
                    #need to check
                    if end_road not in visited:
                        to_check.append(end_road)

            visited.append(to_check.pop(0))


    def create_car(self, road=None, random=False, speed=200, color=YELLOW):
        """
        This method create a car object. if random is True, it will have a
        random speed and be on a random road.
        """
        if random == True:
            speed = randint(100, 150)
            road = self.startroads[randint(0, len(self.startroads)) - 1]
            self.cars.append(Car(speed, road, color))
        else:
            self.cars.append(Car(speed, road, color))

    def simulate(self):
        self.timer += 1
        dt = clock.get_time() / 1000
        for car in self.cars:
            car.change_speed(self.cars, dt)
            car.move(dt)

            # delete cars if they go of the screen
            if car.on_screen(width, height) == False:
                self.cars.remove(car)
                del car

        # Spawns random cars
        last_car = 0
        if randint(0, 40) == 0 and self.timer - last_car > 30:
            self.create_car(random=True)
            last_car = self.timer

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
            w = 10
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
            pygame.draw.line(screen, WHITE, p1s, center, width=5)
            pygame.draw.line(screen, WHITE, p2s, center, width=5)

    def draw_cars(self):
        """
        Draws the cars correctly to the screen.
        """
        for car in self.cars:

            # get the perpendicular angle for the width of the car
            perp = (car.dir + np.pi / 2) % (np.pi * 2)

            # the width and length of the car in its proper orientation
            w = 8
            l = 16
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
                pygame.quit()
                sys.exit()


if __name__ == "__main__":
    main()
