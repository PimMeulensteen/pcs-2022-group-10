from road import *
from car import *
from network import *
from simulation import *

import matplotlib.pyplot as plt


def main():
    seconds = 60
    repetitions = 10
    trafficlight_duration = [5 * i for i in range(1, 7)]

    avg_pol_per_sec = [[] for _ in trafficlight_duration]
    for i in range(len(trafficlight_duration)):
        for _ in range(repetitions):
            sim = Simulation()
            sim.light_duration = trafficlight_duration[i]

            for _ in range(FPS * seconds):
                sim.step()
                # Close the window
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sim.pol_map.draw_map()

                        sys.exit()
            avg_pol_per_sec[i].append(sim.pol_map.total_pol / seconds)
        print("DONE", trafficlight_duration[i])
    pygame.quit()

    # create image
    plt.figure(figsize=(10, 7))

    # plot the data
    avg_pol_per_sec = np.asarray(avg_pol_per_sec)
    plt.bar(
        range(len(trafficlight_duration)),
        np.mean(avg_pol_per_sec, 1),
        yerr=np.std(avg_pol_per_sec, 1),
        capsize=10,
    )
    plt.xticks(range(len(trafficlight_duration)), trafficlight_duration)

    plt.title(
        "The average CO emission based on"
        + "the length of the time between switching traffic lights",
    )
    plt.xlabel("traffic light duration (seconds)")
    plt.ylabel("emission (CO per second)")

    plt.show()


if __name__ == "__main__":
    main()
