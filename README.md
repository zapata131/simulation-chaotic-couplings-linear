# simulation-chaotic-couplings-linear
This is a Simulink Simulation for a Complex Network of linear Systems connected vía Chaotic Couplings.


## Preparation
In order to get the simulation going you have to modify the parameters in the _param_Ross.m_ file. 

The file is divided in two sets of parameters; the first one lets you vary the parameters in the generalized Rossler System present in the Simulink File inside the subsystem "RosslerR5".

The second set of parameters lets you set a Coupling Constant for the network (_K_), an offset for the Rössler System's states (_ofs_) and lets you change the amplitude of the states signal for this system (_amp_). The proposed parameters are _K=1_, _ofs=1_ and _amp=0.2_.

This generalized Rossler Sysyem is proposed by Meyer et al in the paper _Hyperchaos in the generalized Rössler system_, published in 1997.

## Simulink Simulation

Once the _param_Ross.m_ file is modified and run, you can then run the Simulink Simulation.

*Notable things you'll find:*

*Connection Timer*: A step block that lets you modify the connection time for the whole network.
*Subsystems named Linear#*: This are simple harmonic oscillators with different initial conditions.
*RosslerR5*: The Generalized Rossler System in R^5.
*function blocks*: This have the connection information for the network. The network is connected as shown in this figure


