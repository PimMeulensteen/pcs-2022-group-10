from road import *
from car import *
from network import *
from simulation import *


def main():
    seconds = 20
    trafficlight_duration = [5 * i for i in range(1, 5)]

    for dur in trafficlight_duration:
        sim = Simulation()
        sim.light_duration = dur

        for _ in range(FPS * seconds):
            sim.step()
            # Close the window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sim.pol_map.draw_map()

                    sys.exit()
        print("DONE", dur)
    pygame.quit()


if __name__ == "__main__":
    main()
