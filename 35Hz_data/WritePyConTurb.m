%% Documentation   
% Contact: E. Branlard 

%% Initialization
clear all; close all; clc; % addpath()

%% Parameters
dt_box = 0.1;


Files={
'A1_Tjaereborg_20090721_1120_000035.tim',
'A2_Tjaereborg_20090721_1130_000035.tim',
'B1_Tjaereborg_20090721_1310_000035.tim'
};
ShortFiles={'A1','A2','B1'};

for i = 1:length(Files)
    file = Files{i}
    dat  = ReadData(file,174);

    vH  = [17,57,93];   % Heights
    sWD = [110,102,94]; % Wind direction
    su  = [105,97,89]; % "u"
    sv  = [106,98,90]; % "v"
    sw  = [107,99,91]; % "w"
    suh = [109,101,93]; % "w"

    dt=1/35;
    time=[0:dt:600];
    time=time(1:size(dat,1));

    M_abs = [time(:)]; % absolute coordinates, x towards East, y towards North
    M_box = [time(:)]; % box coordinates, rotated by 13deg compared to absolute coordinates
    lbl_abs='#time_[s]';
    lbl_box='#time_[s]';
    for ih = 1:length(vH)
        h = vH(ih);
        sh = num2str(h);
        WD = dat(:, sWD(ih));
        u  = dat(:, su(ih));
        v  = dat(:, sv(ih));
        w  = dat(:, sw(ih));
        uh = sqrt(u.^2+v.^2); % NOTE: I don't trust u and v, but I trust their norm
        uh2= dat(:,suh(ih));
        theta =-WD*pi/180-pi/2 ; % From wind direction to anticlockwise radian starting from x axis
        % Absolute coordinate system
        ux= uh.*cos(theta);
        uy= uh.*sin(theta);
        uz= w;
        M_abs=[M_abs, ux(:), uy(:), uz(:), uh(:), uh2(:), WD(:)]; 
        lbl_abs=[lbl_abs sprintf(',u%s_[m/s],v%s_[m/s],w%s_[m/s],WS%s_[m/s],WS%s_[m/s],WD%s_[deg]',sh,sh,sh,sh,sh,sh)];
        % Box coordinate system
        phi=13; % -257-90
        ux_box = ux * cosd(phi) + uy*sind(phi);
        uy_box = uy * cosd(phi) - ux*sind(phi);
        uz_box = uz;
        M_box=[M_box, ux_box(:), uy_box(:), uz_box(:), uh(:), WD(:)];
        lbl_box=[lbl_box sprintf(',ubox%s_[m/s],vbox%s_[m/s],wbox%s_[m/s],WS%s_[m/s],WD%s_[deg]',sh,sh,sh,sh,sh)];
    end


    % --- Writting absolute data to csv
    fileOut= [ShortFiles{i}, '_absolute.csv'];
    fid=fopen(fileOut,'w'); fwrite(fid,[lbl_abs char(10)]); fclose(fid);
    dlmwrite(fileOut,M_abs,'-append','delimiter',',','precision',8);
    % --- Writting box data to csv
    fileOut= [ShortFiles{i}, '_box.csv'];
    fid=fopen(fileOut,'w'); fwrite(fid,[lbl_box char(10)]); fclose(fid);
    dlmwrite(fileOut,M_box,'-append','delimiter',',','precision',8);
    % --- Writting resampled box data to csv
    time_box=time(1):dt_box:time(end);
    M_box_interp=zeros(length(time_box),size(M_box,2));
    for ic = 1:size(M_box_interp,2)
        M_box_interp(:,ic) = interp1(time, M_box(:,ic), time_box);
    end
    fileOut= [ShortFiles{i}, '_box_interp.csv'];
    fid=fopen(fileOut,'w'); fwrite(fid,[lbl_box char(10)]); fclose(fid);
    dlmwrite(fileOut,M_box_interp,'-append','delimiter',',','precision',8);

    %--- Writting file for pyConTurb
    iu = [2:5:size(M_box_interp,2)];
    iv = [3:5:size(M_box_interp,2)];
    iw = [4:5:size(M_box_interp,2)];
    %xMM = 293.9; % TODO might need to be 0
    xMM = 0.0; % TODO might need to be 0
    yMM =-107.1;
    fileOut= [ShortFiles{i}, '_pyConTurb_tc.csv'];
    fid=fopen(fileOut,'w');
    % header
    sLine='index,';
    for sc = {'u','v','w'}; for ih = 1:length(vH)
        sLine=strcat(sLine,sprintf('%s_p%d,',sc{1},ih-1));
    end; end
    fprintf(fid,'%s\n',sLine(1:end-1));
    % components
    sLine='k,';
    for sc = [0,1,2]; for ih = 1:length(vH)
        sLine=strcat(sLine,sprintf('%d,',sc));
    end; end
    fprintf(fid,'%s\n',sLine(1:end-1));
    % x
    sLine='x,';
    for sc = [0,1,2]; for ih = 1:length(vH)
       sLine=strcat(sLine,sprintf('%f,',xMM));
    end; end
    fprintf(fid,'%s\n',sLine(1:end-1));
    % y
    sLine='y,';
    for sc = [0,1,2]; for ih = 1:length(vH)
       sLine=strcat(sLine,sprintf('%f,',yMM));
    end; end
    fprintf(fid,'%s\n',sLine(1:end-1));
    % z
    sLine='z,';
    for sc = [0,1,2]; for ih = 1:length(vH)
       sLine=strcat(sLine,sprintf('%f,',vH(ih)));
    end; end
    fprintf(fid,'%s\n',sLine(1:end-1));
    % Time
    for it=1:length(time_box)
        sLine=sprintf('%9.2f,',time_box(it));
        for ih = 1:length(vH); sLine=strcat(sLine,sprintf('%10.4f,',M_box_interp(it,iu(ih)))); end; 
        for ih = 1:length(vH); sLine=strcat(sLine,sprintf('%10.4f,',M_box_interp(it,iv(ih)))); end; 
        for ih = 1:length(vH); sLine=strcat(sLine,sprintf('%10.4f,',M_box_interp(it,iw(ih)))); end; 
        fprintf(fid,'%s\n',sLine(1:end-1));
    end
    fclose(fid);


    % --- Writting original data to csv
%     dat=[time(:) dat];
%     fileOut2= [ShortFiles{i}, '_ori.csv'];
%     dlmwrite(fileOut2,dat,'delimiter',',','precision',4)
end


% WS_nac      = 81; % Wind speed nacelle
% WD_nac      = 82; % Wind directions nacelle
% Power       = 83; % elect. Power [kW]
% RotSpd      = 84; % rotor speed [rpm]
% Yaw         = 85; % yaw [deg]
% Pitch       = 86; % Pitch blade 1 [deg]
% %===Mast
% Stat_S90    = 88; % Status sonic90
% WS_S90      = 93; % Wind speed (magnitude) sonic90 (h=93m) [m/s]
% WD_S90      = 94; % Wind direction (yaw) sonic90 (h=93m) [deg]
% WD_tilt_S90 = 95; % Wind direction (tilt) sonic90 (h=93m) [deg]
% Stat_S57    = 96; % Status sonic90
% WSxyz_S57   =[97,98,99]; % Wind speed (x,y,z) sonic57 (h=57m)  [m/s]
% WS_S57      = 101; % Wind speed (magnitude) sonic57 (h=57m) [m/s]
% WD_S57      = 102; % Wind direction (yaw) sonic57 (h=57m) [deg]
% WD_tilt_S57 = 103; % Wind direction (tilt) sonic57 (h=57m) [deg]
% Stat_S17    = 104; % Status sonic90
% WSxyz_S17   =[105,106,107]; % Wind speed (x,y,z) sonic17 [m/s]
% WS_S17      = 109; % Wind speed (magnitude) sonic17 [m/s]
% WD_S17      = 110; % Wind direction (yaw) sonic17 [deg]
% WD_tilt_S17 = 111; % Wind direction (tilt) sonic17 (h=17m) [deg]
% WS_C77      = 114; % Wind speed cup77  [m/s]
% WS_C41      = 116; % Wind speed cup41  [m/s]
% WS_C28      = 117; % Wind speed cup28 (h=28.5m)  [m/s]
% 
% P_ATMO      = 123; % atmospheric pressure [hPa]
% 
% T17         = 108; % Temp at sonic, h=17m [C]
% T57         = 100; % Temp at sonic, h=57m [C]
% T90         = 92;  % Temp at sonic, h=93m [C]
% Tdiff90     = 120; % Temp diff 90m-5m       [C]
% 
% Ft13        = 138; % Tangential load at r=13m  [N/m]
% Ft19        = 139; % Tangential load at r=19m  [N/m]
% Ft30        = 140; % Tangential load at r=30m  [N/m]
% Ft37        = 141; % Tangential load at r=37m  [N/m]
% Fn13        = 142; % Normal load at r=13m  [N/m]
% Fn19        = 143; % Normal load at r=19m  [N/m]
% Fn30        = 144; % Normal load at r=30m  [N/m]
% Fn37        = 145; % Normal load at r=37m  [N/m]
% Fm13        = 146; % Moment at r=13m  [N/m]
% Fm19        = 147; % Moment at r=19m  [N/m]
% Fm30        = 148; % Moment at r=30m  [N/m]
% Fm37        = 149; % Moment at r=37m  [N/m]
%  



