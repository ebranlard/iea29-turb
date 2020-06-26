%% Documentation   
% Contact: E. Branlard 

%% Initialization
clear all; close all; clc; % addpath()

%% Parameters
box_file='A1_161.bts';

[velocity, ~, y, z, ~, nz, ny, dz, dy, dt, ~, ~, ~] = readfile_BTS(box_file);

%% Plot at a probe 
zProbe=57;
yProbe=0;
[~,iy] = min(abs(y-yProbe));
[~,iz] = min(abs(z-zProbe));
time=0:dt:dt*(size(velocity,1)-1);

figure()
subplot(3,1,1)
plot(time, velocity(:,1,iy,iz))
ylabel('u [m/s]')
subplot(3,1,2)
plot(time, velocity(:,2,iy,iz))
ylabel('v [m/s]')
subplot(3,1,3)
plot(time, velocity(:,3,iy,iz))
ylabel('w [m/s]')
xlabel('Time [s]')

