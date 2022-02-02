
import numpy as np
import matplotlib.pyplot as plt
from simulation import Simulation, pygame
FPS = 30


def experiment(ref_data, change, secs, reps, filename):
    """
    Experiment to find average CO2 emission per second, each simulation
    is run for a specified number of seconds, average is taken over
    a specified number of iterations.
    """
    data = [[] for _ in ref_data]
    for i in range(len(ref_data)):
        for j in range(reps):
            sim = Simulation("co", save_pol_map=False)

            change(sim, ref_data[i])

            for _ in range(sim.FPS * secs):
                sim.simulate()

            data[i].append(sim.pol_maps[0].total_pol / (sim.num_cars * secs))
            print(j)
        print("DONE", ref_data[i])

        with open(filename + ".txt", "a") as file:
            file.write(" ".join(str(d) for d in data[i]) + "\n")

    return np.asarray(data)


def save_image(ref_data, data, caption, ref_data_label, filename):
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

    # plt.show()
    plt.savefig(filename + ".png")


def change_lightdur(sim, dur):
    """
    Change the traffic lights in the simulation according
    to the specified duration (the time before switching a
    different light green).
    """
    sim.light_duration = dur


def experiment_lights(secs, reps, filename):
    """
    Experiment to find CO2 emission based on the duration of time
    each light is green, before switching to another light.
    Returns average CO2 emission per second.
    """
    trafficlight_duration = [5 * i for i in range(1, 7)]

    with open(filename + ".txt", "w") as file:
        file.write(" ".join(str(d) for d in trafficlight_duration) + "\n")

    save_image(
        trafficlight_duration,
        experiment(
            trafficlight_duration, change_lightdur, secs, reps, filename
        ),
        "the length of the time between switching traffic lights",
        "traffic light duration (seconds)",
        filename,
    )


def change_traffic(sim, prob):
    """
    Change the traffic lights in the simulation according to the specified
    probability indicating how often a new car enters traffic (the higher
    the probability, the more traffic).
    """
    sim.car_gen_prob = prob


def experiment_traffic(secs, reps, filename):
    """
    Experiment to find CO2 emission based on the probability of cars
    entering traffic per second, thus on how busy the intersection is.
    Returns average CO2 emission per second.
    """
    prob_car_per_step = [4 * i for i in range(1, 8)]
    prob_car_per_sec = [FPS * p // 100 for p in prob_car_per_step]

    with open(filename + ".txt", "w") as file:
        file.write(" ".join(str(d) for d in prob_car_per_sec) + "\n")

    save_image(
        prob_car_per_sec,
        experiment(prob_car_per_step, change_traffic, secs, reps, filename),
        "how busy traffic is at the intersection.",
        "expected number of cars per second (cars)",
        filename,
    )


def main():
    pygame.quit()
    repetitions = 10

    # Run experiment based on time between light switches
    # seconds = 60
    # experiment_lights(seconds, repetitions, "exp_light_60s_10r")

    # Run experiment based on business of the road
    seconds = 30
    experiment_traffic(seconds, repetitions, "exp_traffic_30s_10r")


if __name__ == "__main__":
    main()
