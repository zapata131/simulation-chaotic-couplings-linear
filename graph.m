close all;
clc;

%% Plot 1: System States Overview
% Plots the first and second states of the Rossler system or representative signals.
if exist('ScopeData', 'var')
    data = ScopeData.signals(1,1).values;
    dataS = ScopeData.signals(1,2).values;
    time = ScopeData.time; % Assuming time is available in structure or workspace 'tout'

    figure('Name', 'System States Overview');
    
    subplot(2,1,1);
    plot(tout, data);
    title('First state of the systems');
    xlabel('Time');
    grid on;

    subplot(2,1,2);
    plot(tout, dataS);
    title('Second state of the systems');
    xlabel('Time');
    grid on;
else
    warning('ScopeData not found. Run the simulation first.');
end

%% Plot 2: Coupling Strengths / Rossler States
% Plots the 5 states of the Generalized Rossler System involved in coupling.
if exist('ScopeData1', 'var')
    data2 = ScopeData1.signals.values;
    
    figure('Name', 'Rossler States / Coupling Strengths');

    for i = 1:5
        subplot(5,1,i);
        plot(tout, data2(:,i));
        
        % Set Y-limits for better visibility (adjust as needed based on data range)
        % ylim([0 1.5]); 
        
        title(['State ', num_str(i)]);
        grid on;
    end
    xlabel('Time');
else
    warning('ScopeData1 not found. Run the simulation first.');
end