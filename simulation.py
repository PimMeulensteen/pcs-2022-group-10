from road import *
from car import *

import sys
import pygame

#Sets the number of simulation frames per second
FPS = 60
clock = pygame.time.Clock()

pygame.init()

#Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

#Size and with of the pygame screen
size = width, height = 500, 500
screen = pygame.display.set_mode(size)


class Simulation:
    def __init__(self) -> None:
        self.cars = []
        self.roads = []

    def gen_random_data(self) -> None:
        #Test roads
        self.roads = [
            Road([500, 230], [0, 230], 0),
            Road([0, 270], [500, 270], 1),
            Road([230, 0], [230, 500], 2),
            Road([270, 500], [270, 0], 3)
        ]

        #Test cars
        self.cars = [
            Car(150, self.roads[0], RED),
            Car(200, self.roads[1], GREEN),
            Car(100, self.roads[2], BLUE),
            Car(300, self.roads[3], WHITE)
        ]

    def step(self):
        clock.tick(FPS)
        self.simulate()
        self.draw()

        #Close the window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def simulate(self):
        dt = clock.get_time() / 1000
        for car in self.cars:
            car.move(dt)

        if randint(0, 40) == 0:
            self.cars.append(self.roads[0].get_random_car_at_start())

    def draw_roads(self):
        """
            Draws the roads correctly to the screen.
        """
        #loop through the roads and get the dimensions
        for road in self.roads:

            #get the perpendicular angle for the width of the road
            perp = np.pi / 2 + road.angle

            #width of the road
            w = 10
            offset = [w * np.cos(perp), -w * np.sin(perp)]

            #points to draw the rectangle
            p1 = [x + y for x, y in zip(road.start, offset)]
            p2 = [x - y for x, y in zip(road.start, offset)]
            p3 = [x - y for x, y in zip(road.end, offset)]
            p4 = [x + y for x, y in zip(road.end, offset)]

            #draw the road
            pygame.draw.polygon(screen, GRAY, [p1, p2, p3, p4])

            #draw arrows that denote the direction
            d = [w * np.cos(road.angle), w * -np.sin(road.angle)]
            center = [x + y for x, y in zip(road.start, d)]
            pygame.draw.line(screen, WHITE, p1, center, width=5)
            pygame.draw.line(screen, WHITE, p2, center, width=5)

    def draw_cars():
        """
            Draws the cars correctly to the screen.
        """
        for car in self.cars:

            #get the perpendicular angle for the width of the car
            perp = (car.dir + np.pi / 2) % (np.pi * 2)

            #the width and length of the car in its proper orientation
            w = 8
            l = 16
            offsetw = [w * np.cos(perp), -w * np.sin(perp)]
            offsetl = [l * np.cos(car.dir), -l * np.sin(car.dir)]

            #the corners of the car
            p1 = [x + y + z for x, y, z in zip(car.pos, offsetw, offsetl)]
            p2 = [x + y - z for x, y, z in zip(car.pos, offsetw, offsetl)]
            p3 = [x - y - z for x, y, z in zip(car.pos, offsetw, offsetl)]
            p4 = [x - y + z for x, y, z in zip(car.pos, offsetw, offsetl)]

            #draw the car
            pygame.draw.polygon(screen, car.color, [p1, p2, p3, p4])

    def draw(self):
        screen.fill(0)
        self.draw_roads()
        self.draw_cars()
        pygame.display.update()


sim = Simulation()


def main():
    #Otherwise the window is immediatly closed
    while True:
        sim.step()


if __name__ == "__main__":
    main()