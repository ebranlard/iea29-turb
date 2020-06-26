function [velocity, twrVelocity, y, z, zTwr, nz, ny, dz, dy, dt, zHub, z1,mffws] = readfile_BTS(FileName,fileFmt)
%[velocity, twrVelocity, y, z, zTwr, nz, ny, dz, dy, dt, zHub, z1,mffws] = readfile_BTS(FileName,fileFmt)
% Author: Bonnie Jonkman, National Renewable Energy Laboratory
%
% Input:
%  FileName      - string: contains file name (.bts extension) to open
%  fileFmt       - string: optional, contains format of grid points.
%
% Output:
%  velocity      - 4-D array: time, velocity component (1=U, 2=V, 3=W), iy, iz 
%  twrVelocity   - 3-D array: time, velocity component, iz
%  y             - 1-D array: horizontal locations y(iy)
%  z             - 1-D array: vertical locations z(iz)
%  zTwr          - 1-D array: vertical locations of tower points zTwr(iz)
%  nz, ny        - scalars: number of points in the vertical and horizontal
%                  directions of the grid
%  dz, dy, dt    - scalars: distance between two points in the vertical
%                  [m], horizontal [m], and time [s] dimensions
% zHub           - scalar: hub height [m]
% z1             - scalar: vertical location of bottom of grid [m above ground level]
% mffws          - scalar: mean hub-height wind speed

if ( nargin < 2 )
    fileFmt = 'int16';
end
nffc = 3;

fid  = fopen( FileName );

if fid > 0
    %----------------------------        
    % get the header information
    %----------------------------
    
    tmp   = fread( fid, 1, 'int16');        % TurbSim format identifier (should = 7 or 8 if periodic), INT(2)

    nz    = fread( fid, 1, 'int32');        % the number of grid points vertically, INT(4)
    ny    = fread( fid, 1, 'int32');        % the number of grid points laterally, INT(4)
    ntwr  = fread( fid, 1, 'int32');        % the number of tower points, INT(4)
    nt    = fread( fid, 1, 'int32');        % the number of time steps, INT(4)

    dz    = fread( fid, 1, 'float32');      % grid spacing in vertical direction, REAL(4), in m
    dy    = fread( fid, 1, 'float32');      % grid spacing in lateral direction, REAL(4), in m
    dt    = fread( fid, 1, 'float32');      % grid spacing in delta time, REAL(4), in m/s
    mffws = fread( fid, 1, 'float32');      % the mean wind speed at hub height, REAL(4), in m/s
    zHub  = fread( fid, 1, 'float32');      % height of the hub, REAL(4), in m
    z1    = fread( fid, 1, 'float32');      % height of the bottom of the grid, REAL(4), in m

    Vslope(1)  = fread( fid, 1, 'float32'); % the U-component slope for scaling, REAL(4)
    Voffset(1) = fread( fid, 1, 'float32'); % the U-component offset for scaling, REAL(4)
    Vslope(2)  = fread( fid, 1, 'float32'); % the V-component slope for scaling, REAL(4)
    Voffset(2) = fread( fid, 1, 'float32'); % the V-component offset for scaling, REAL(4)
    Vslope(3)  = fread( fid, 1, 'float32'); % the W-component slope for scaling, REAL(4)
    Voffset(3) = fread( fid, 1, 'float32'); % the W-component offset for scaling, REAL(4)

        % Read the description string: "Generated by TurbSim (vx.xx, dd-mmm-yyyy) on dd-mmm-yyyy at hh:mm:ss."

    nchar    = fread( fid, 1, 'int32');     % the number of characters in the description string, max 200, INT(4)
    asciiINT = fread( fid, nchar, 'int8' ); % the ASCII integer representation of the character string
    asciiSTR = char( asciiINT' );

    disp( ['Reading from the file ' FileName ' with heading: ' ] );
    disp( ['   "' asciiSTR '".' ] ) ;

    %-------------------------        
    % get the grid information
    %-------------------------

    nPts        = ny*nz;
    nv          = nffc*nPts;               % the size of one time step
    nvTwr       = nffc*ntwr;
%   velocity    = zeros(nt,nffc,nPts);
    velocity    = zeros(nt,nffc,ny,nz);
    twrVelocity = zeros(nt,nffc,ntwr);        
    
    if strcmpi(fileFmt,'float32')
        Voffset = 0.0*Voffset;
        Vslope  = ones(size(Vslope));
    end
    
   
    for it = 1:nt
        %--------------------
        %get the grid points
        %--------------------

        
       [v, cnt] = fread( fid, nv, fileFmt ); % read the velocity components for one time step
       if ( cnt < nv ) 
           disp([ it nt ny nz nffc nv cnt])
           fclose(fid);
           error(['Could not read entire file: at grid record ' num2str( (it-1)*(nv+nvTwr)+cnt ) ' of ' num2str(nt*(nv+nvTwr))]);
       end

        ip = 1;
        for iz = 1:nz
            for iy = 1:ny
                for k=1:nffc
                    velocity(it,k,iy,iz) = ( v(ip) - Voffset(k))/Vslope(k) ;
                    ip = ip + 1;
                end %k
            end %iy
        end % iz

        %---------------------
        %get the tower points
        %---------------------
        if nvTwr > 0
        
            [v, cnt] = fread( fid, nvTwr, fileFmt ); % read the velocity components for the tower
            if ( cnt < nvTwr ) 
                error(['Could not read entire file: at tower record ' num2str( (it-1)*(nv+nvTwr)+nv+cnt ) ' of ' num2str(nt*(nv+nvTwr))]);
            end

            for k=1:nffc      % scale the data
                twrVelocity(it,k,:) = (v(k:3:nvTwr) - Voffset(k))/Vslope(k); 
            end    
            
        end

    end %it

    fclose(fid);
else
    error(['Could not open the wind file: ' FileName]) ;
end


y = [0:ny-1]*dy - dy*(ny-1)/2;
z = [0:nz-1]*dz + z1;
zTwr = z1 - [0:ntwr-1]*dz;

% squeeze(velocity(1  ,1,:,:))
% squeeze(velocity(end,1,:,:))

return;
