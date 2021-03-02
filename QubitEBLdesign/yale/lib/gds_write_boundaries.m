function gds_write_boundaries (gdsFile, boundaries, oldWay)

global writeTimes;

if isempty(writeTimes)
    writeTimes = [];
end

localTic;

libCreated = false;

if ischar(gdsFile)
    
    gdsFileName = gdsFile;
    gdsFile = gds_create_library(gdsFileName);
    gds_start_structure(gdsFile, gdsFileName);
    
    libCreated = true;
end
    
if nargin == 2
    
    boundariesBuffer = gdsEncodeBoundaries(boundaries);
    fwrite(gdsFile, boundariesBuffer, 'uint8');
else

    for boundary = boundaries
        
        if boundary.points(1,1) ~= boundary.points(1,end) || boundary.points(2,1) ~= boundary.points(2,end)
            gds_write_path(gdsFile, boundary, 0);
        else
            gds_write_boundary(gdsFile, boundary);
        end
    end
end
if libCreated
    
    gds_close_structure(gdsFile);
    gds_close_library(gdsFile);
end

writeTimes = [ writeTimes ; length(boundaries) localToc ];