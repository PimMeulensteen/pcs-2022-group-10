from road import *

import sys
import pygame

pygame.init()


#Test roads
roads = [Road([500,230],[0,230]),
         Road([0,270],[500,270]),
         Road([230,0],[230,500]),
         Road([270,500],[270,0])]


#Size and with of the pygame screen
size = width, height = 500, 500
screen = pygame.display.set_mode(size)


#Colors
WHITE = (255,255,255)
GRAY = (128,128,128)



def main():

    #Otherwise the window is immediatly closed
    while True:

        #Function that draws the objects one screen, right now only roads
        draw(roads)

        #Close the window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


"""
    Draws the elements to the screen
"""
def draw(roads):
    draw_roads(roads)
    pygame.display.update()


"""
    Draws the roads correctly to the screen
"""
def draw_roads(roads):

    #loop through the roads and get the dimensions
    for road in roads:

        #Get the perpendicular angle for the width of the road
        if road.slope == 0:
            perp = np.pi/2
        elif road.slope == "undefined":
            perp = 0
        else:
            perp = np.arctan(-1/road.slope)

        #width of the road
        w = 10
        offset = [w * np.cos(perp),w * np.sin(perp)]

        #points to draw the rectangle
        p1 = [x + y for x,y in zip(road.start, offset)]
        p2 = [x - y for x,y in zip(road.start, offset)]
        p3 = [x - y for x,y in zip(road.end, offset)]
        p4 = [x + y for x,y in zip(road.end, offset)]

        pygame.draw.polygon(screen, GRAY, [p1,p2,p3,p4])

        #TO ADD
        #Arrow to denote the direction of the road



if __name__ == "__main__":
    main()