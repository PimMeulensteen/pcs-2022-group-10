# pcs-2022-group-10

Run the simulation with
```bash
python3 simulation.py
```

Note: the simulation can be stopped when desired by closing the simulation window. A pollution map is automatically created in the figure pollution.png

For the experiment resulting in a figure similar to exp_light_120s_20r_orig.png run
```bash
python3 experiment.py light
```
to run an experiment that determines the CO2 emission per car for varying traffic light durations (time lights are green before turning red). The results appear in figure exp_light_120s_20r.png.

For the experiment resulting in a figure similar to exp_traffic_120s_20r_orig.png run
```bash
python3 experiment.py traffic
```
to run an experiment that determines the CO2 emission per car for varying levels of business at the intersection (thus the expected number of cars per second). The results appear in figure exp_traffic_120s_20r.png.

Both experiments take approximately 5 minutes.

Some non-standard libaries that are required to run: numpy, matplotlib, pygame
