# Simulation of Chaotic Couplings in Linear Systems

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Matlab](https://img.shields.io/badge/Matlab-Simulink-orange)](https://www.mathworks.com/products/simulink.html)

This project simulates a complex network of linear systems connected via chaotic couplings derived from a Generalized Rossler System in $R^5$.

![Network Structure](https://user-images.githubusercontent.com/366479/32516730-f4bc212a-c3c9-11e7-849f-08a269c32dd2.PNG)

## Overview

The simulation consists of:
1.  **Generalized Rossler System**: A hyperchaotic system in 5 dimensions.
2.  **Linear Oscillators**: 6 harmonic oscillators with different initial conditions.
3.  **Chaotic Coupling**: The linear systems are coupled using signals from the Rossler system, creating complex dynamics.

## Python Simulation (New)

A Python implementation is now available, replicating the Simulink model using `scipy.integrate`.

### Prerequisites
Install the required packages:
```bash
pip install -r requirements.txt
```

### Running the Simulation
Execute the simulation script:
```bash
python3 python_simulation.py
```
This will solve the differential equations and generate two plots:
-   `rossler_states.png`: The chaotic states of the Rossler system.
-   `linear_systems_states.png`: The states of the 6 linear oscillators.

## MATLAB / Simulink Simulation

### Preparation
Modify parameters in the `param_Ross.m` file.
-   **Rossler Parameters**: Control the chaotic system dynamics.
-   **Network Parameters**:
    -   `K`: Coupling Constant.
    -   `ofs`: Offset for chaotic signals.
    -   `amp`: Amplitude of the chaotic signals.
    -   Default: $K=1, ext{ofs}=1, ext{amp}=0.2$.

### Running
1.  Run `param_Ross.m` to load parameters into the workspace.
2.  Open and run `red6Rossler.mdl` in Simulink.
3.  Run `graph.m` to plot the results.

### Notable Components in Simulink
-   **Connection Timer**: A step block enabling coupling after a set time.
-   **Linear# Subsystems**: Harmonic oscillators.
-   **RosslerR5**: The generalized Rossler system.
-   **Fcn Blocks**: Define the coupling logic based on the network structure.

## Reference
The Generalized Rossler System is based on:
_Meyer et al., "Hyperchaos in the generalized Rössler system", 1997._
