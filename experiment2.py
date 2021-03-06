import sys
import numpy as np
import matplotlib.pyplot as plt
from simulation import Simulation, pygame
from sys import stdout as out

# Set the number of frames per second
FPS = 30


def experiment(ref_data, change, secs, reps, filename):
    """
    Experiment to find average CO2 emission per second. Each simulation
    is run for a specified number of seconds, average is taken over
    a specified number of repetitions.
    """
    data = [[] for _ in ref_data]
    for i in range(len(ref_data)):
        for j in range(reps):
            sim = Simulation("CO2", save_pol_map=False)
            change(sim, ref_data[i])

            for _ in range(sim.FPS * secs):
                sim.simulate()

            data[i].append(sim.pol_maps[0].total_pol / sim.num_cars)
            out.write(f"\rInput={ref_data[i]}: {(j + 1) / reps * 100:.0f}%")
            out.flush()
        print()
        # Write the data to a file
        with open(filename + ".txt", "a") as file:
            file.write(" ".join(str(d) for d in data[i]) + "\n")

    return np.asarray(data)


def save_image(ref_data, data, caption, ref_data_label, filename):
    # Create image
    plt.figure(figsize=(10, 7))

    # Plot the given data
    plt.bar(
        range(len(ref_data)),
        np.mean(data, 1),
        yerr=np.std(data, 1),
        capsize=5,
    )
    plt.xticks(range(len(ref_data)), ref_data)

    plt.title(
        "The average CO2 emission based on " + caption,
    )
    plt.xlabel(ref_data_label)
    plt.ylabel("CO2 emission per car (mg)")

    # plt.show()
    plt.savefig(filename + ".png")


def change_lightdur(sim, dur):
    """
    Change the traffic lights in the simulation according
    to the specified duration (the time before switching a
    different light green).
    """
    sim.light_duration = dur

    # Additional settings for consistency and reproducibility
    sim.car_gen_prob = 10/9
    sim.FPS = FPS


def experiment_lights(secs, reps, filename):
    """
    Experiment to find CO2 emission based on the duration of time
    each light is green, before switching to another light.
    Returns average CO2 emission per second.
    """
    trafficlight_duration = [5 + (1 * i) for i in range(21)]

    # Write the data to a file
    with open(filename + ".txt", "w") as file:
        file.write(" ".join(str(d) for d in trafficlight_duration) + "\n")

    save_image(
        [x - 4 for x in trafficlight_duration],
        experiment(
            trafficlight_duration, change_lightdur, secs, reps, filename
        ),
        "the length of the time between switching traffic lights",
        "Traffic light duration (seconds)",
        filename,
    )


def change_traffic(sim, prob):
    """
    Change the traffic lights in the simulation according to the specified
    probability indicating how often a new car enters traffic (the higher
    the probability, the more traffic).
    """
    sim.car_gen_prob = prob

    # Additional settings for consistency and reproducibility
    sim.light_duration = 8
    sim.FPS = FPS


def experiment_traffic(secs, reps, filename):
    """
    Experiment to find CO2 emission based on the probability of cars
    entering traffic per second, thus on how busy the intersection is.
    Returns average CO2 emission per second.
    """
    prob_car_per_step = [5/18 + 1/24 * i for i in range(21)]
    cars_per_min = [round(FPS * p * 60 / 100,2) for p in prob_car_per_step]

    with open(filename + ".txt", "w") as file:
        file.write(" ".join(str(d) for d in cars_per_min) + "\n")

    save_image(
        cars_per_min,
        experiment(prob_car_per_step, change_traffic, secs, reps, filename),
        "how busy traffic is at the intersection.",
        "Expected number of cars per minute (cars)",
        filename,
    )

def main():
    # Switches the simulation visibility off
    pygame.quit()

    # Specifies the number of repetitions and simulation duration
    reps = int(sys.argv[3])
    secs = int(sys.argv[2])

    # Run experiment based on time between light switches
    # or run experiment based on business of the road
    if len(sys.argv) > 1 and sys.argv[1] == "light":
        experiment_lights(secs, reps, f"exp_light_{secs}s_{reps}r")
    elif len(sys.argv) > 1 and sys.argv[1] == "traffic":
        experiment_traffic(secs, reps, f"exp_traffic_{secs}s_{reps}r")


if __name__ == "__main__":
    main()
