%% Rossler System and Network Connection Parameters
% This script defines the parameters for the Simulink simulation 'red6Rossler.mdl'.

%% Parameters for the Generalized Rossler System in R^5
% Reference: Meyer et al., "Hyperchaos in the generalized Rössler system", 1997.
a = 0.1;
b = 4;
d = 2;
e = 0.1;

% Additional parameters (potentially for other variants or unused)
a1 = 0.1;
a2 = 0.1;

% Frequency parameters for Linear Oscillators (implied usage)
w1 = 1;
w2 = 1;

%% Parameters for the Network Couplings
% These parameters control the interaction between the Rossler system and the Linear Oscillators.

% Coupling Constant (Global scaling for coupling strength)
K = 1;

% Offset for the Chaotic Signals (Shifts the Rossler states)
ofs = 1;

% Signal Multiplier (Scales the amplitude of the Rossler System states input to the network)
amp = 0.2;