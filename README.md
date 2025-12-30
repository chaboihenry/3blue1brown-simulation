# 3Blue1Brown Physics Simulation

A Python physics simulation that demonstrates elastic collisions between two objects to approximate the value of π

## How It Works

The simulation features:
- **Left blob (red)**: Fixed mass of 1kg, starts stationary
- **Right blob (blue)**: Variable mass (100^n kg), starts with velocity of 1 m/s
- **Wall collision**: Left wall that reflects the red blob
- **Elastic collisions**: Between the two blobs following conservation of momentum and energy

The total number of collisions approximates π × √(mass_ratio), demonstrating a beautiful connection between physics and mathematics.

## Running the Simulation

```bash
python main.py
```

Enter a power of 100 for the right blob's mass (1-9) when prompted. Higher powers result in more collisions and better π approximations.

## Features

- Real-time collision counting
- π approximation display
- Adaptive simulation speed for large mass ratios
- Burst mode for handling thousands of collisions efficiently
- Visual representation with pygame

Inspired by [3Blue1Brown's "Colliding blocks compute π"](https://www.youtube.com/watch?v=HEfHFsfGXjs)
