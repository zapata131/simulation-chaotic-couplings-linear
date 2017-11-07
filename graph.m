close all
data=ScopeData.signals(1,1).values;
figure
subplot(2,1,1)
plot(tout,data)
title('First state of the systems')
xlabel('Time')

subplot(2,1,2)
dataS=ScopeData.signals(1,2).values;
plot(tout,dataS)
title('Second state of the systems')
xlabel('Time')







data2=ScopeData1.signals.values;
figure


subplot(5,1,1)
plot(tout,data2(:,1))
ylim([0 1.5])
title('Coupling strengths')


subplot(5,1,2)
plot(tout,data2(:,2))
ylim([0 1.5])

subplot(5,1,3)
plot(tout,data2(:,3))
ylim([0 1.5])

subplot(5,1,4)
plot(tout,data2(:,4))

subplot(5,1,5)
plot(tout,data2(:,5))
ylim([0 1.5])

xlabel('Time')
% 
% figure
% 
% 
% 
% subplot(6,1,1)
% plot(tout,data(:,1))
% 
% title('Estados del sistema (separados)')
% 
% subplot(6,1,2)
% plot(tout,data(:,2))
% 
% subplot(6,1,3)
% plot(tout,data(:,3))
% 
% subplot(6,1,4)
% plot(tout,data(:,4))
% 
% subplot(6,1,5)
% plot(tout,data(:,5))
% 
% subplot(6,1,6)
% plot(tout,data(:,6))
% 
% xlabel('Tiempo')