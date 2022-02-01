from road import *
from car import *
from network import *
from simulation import *

import matplotlib.pyplot as plt


def experiment(ref_data, change, secs, reps):
    """
    Experiment to find average CO2 emission per second, each simulation
    is run for a specified number of seconds, average is taken over
    a specified number of iterations.
    """
    data = [[] for _ in ref_data]
    for i in range(len(ref_data)):
        for j in range(reps):
            sim = Simulation()

            change(sim, ref_data[i])

            for _ in range(FPS * secs):
                sim.simulate()
                # Close the window
                # for event in pygame.event.get():
                #     if event.type == pygame.QUIT:
                #         sys.exit()
            data[i].append(sim.pol_maps[0].total_pol / (sim.num_cars * secs))
            print(j)
        print("DONE", ref_data[i])

    return np.asarray(data)


def change_lightdur(sim, dur):
    """
    Change the traffic lights in the simulation according
    to the specified duration (the time before switching a
    different light green).
    """
    sim.light_duration = dur


def experiment_lights(secs, reps):
    """
    Experiment to find CO2 emission based on the duration of time
    each light is green, before switching to another light.
    Returns average CO2 emission per second.
    """
    trafficlight_duration = [5 * i for i in range(1, 7)]

    return (
        trafficlight_duration,
        experiment(trafficlight_duration, change_lightdur, secs, reps),
        "the length of the time between switching traffic lights",
        "traffic light duration (seconds)",
    )


def change_traffic(sim, prob):
    """
    Change the traffic lights in the simulation according to the specified
    probability indicating how often a new car enters traffic (the higher
    the probability, the more traffic).
    """
    sim.car_gen_prob = prob


def experiment_traffic(secs, reps):
    """
    Experiment to find CO2 emission based on the probability of cars
    entering traffic per second, thus on how busy the intersection is.
    Returns average CO2 emission per second.
    """
    prob_car_per_step = [4 * i for i in range(1, 10)]
    prob_car_per_sec = [FPS * p // 100 for p in prob_car_per_step]

    return (
        prob_car_per_sec,
        experiment(prob_car_per_step, change_traffic, secs, reps),
        "how busy traffic is at the intersection.",
        "expected number of cars per second (cars)",
    )


def main():
    pygame.quit()
    seconds = 60
    repetitions = 10

    ref_data, data, caption, ref_data_label = experiment_traffic(
        seconds, repetitions
    )

    # create image
    plt.figure(figsize=(10, 7))

    # plot the data
    plt.bar(
        range(len(ref_data)),
        np.mean(data, 1),
        yerr=np.std(data, 1),
        capsize=10,
    )
    plt.xticks(range(len(ref_data)), ref_data)

    plt.title(
        "The average CO2 emission based on " + caption,
    )
    plt.xlabel(ref_data_label)
    plt.ylabel("CO2 emission per car (mg/second)")

    plt.show()


if __name__ == "__main__":
    main()
