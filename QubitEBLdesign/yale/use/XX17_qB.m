
function plgs = XX17_qB(junctionTestFileName)

jjWidths = [1.52, 1.56, 1.60, 1.64, 1.54, 1.58, 1.62, 1.66,];
ro_lengths = [9150, 9150, 9150, 9150, 9150, 9150, 9150, 9150];
direction = 1;
bridgeInnerDataTypes = [0];
rotation=0;
qB_start = (780+150)+600;
ro_gap = 2510+800;
extentLabelFontParams = { ...
    'fontName', '5x7 pixels', 'shearAngle', 0.0, 'letterHeight', 150, ...
    'hAlign', 'left', 'vAlign', 'bottom', 'layer', LYR_EBEAM_FIELDS, 'dataType', 0};
testLabelFontParams = { ...
    'fontName', '5x7 pixels', 'shearAngle', 0.0, 'letterHeight', 40, ...
    'hAlign', 'left', 'vAlign', 'top', 'layer', LYR_QUBIT_COARSE, 'dataType', 0};

fx = 300;   %how wide are the qubit field instances
fy = 290;   %how tall are the qubit field instances
dx1 = 25330+(27750-21385);
dx2 = 2250;
dx = dx1+dx2;  % spacing between the devices
dy = 3600+300;   % spacing between the devices
%Assume dicing loss is 300
mountmarkx = dx1 -(27750-21385);

polx = polyfit((length(bridgeInnerDataTypes)+1)/2+[0 1], [0 dx], 1);
poly = polyfit((length(jjWidths)+1)/2-[0 1], [0 dy], 1);
nx = length(bridgeInnerDataTypes);
ny = length(jjWidths);

extentX = fx*ceil(nx*dx/fx)/2; 
extentY = fy*ceil(ny*dy/fy)/2; 
fprintf('(%d, %d)', extentX, extentY);

gdsFile = gds_create_library(junctionTestFileName);
gds_start_structure(gdsFile, [junctionTestFileName 'Field']);
gds_write_boundaries(gdsFile, ...
    shSquare(trScale(fx, fy)*trTranslate(0.5, -0.5), 'layer', LYR_EBEAM_FIELDS));
gds_close_structure(gdsFile);

gds_start_structure(gdsFile, [junctionTestFileName]);
plgs = shWafer(WAFER_SAPPHIRE_TWO_INCH);
gds_write_boundaries(gdsFile, plgs);

gds_write_aref(gdsFile, [junctionTestFileName 'Field'], ...
    'refPoint', [-extentX; extentY], ...
    'columns', extentX*2/fx, 'columnOffset', fx, ...
    'rows', extentY*2/fy, 'rowOffset', -fy);
extent = applyTransform( str2boundaries(sprintf('Extent := (%c%d,%c%d)\nField size := (%d,%d)', 206, extentY, 206, extentX, fy, fx), ...
         extentLabelFontParams{:}), trTranslate(-extentX-100, -extentY)*trRotate(90));
plgs = [plgs extent];
gds_write_boundaries(gdsFile, extent); 

for jjWidthsIndex = 1:length(jjWidths)
    jjWidth = jjWidths(jjWidthsIndex);
    ro_len = ro_lengths(jjWidthsIndex);
    for bridgeIndex = 1:length(bridgeInnerDataTypes)
        bridgeInnerDataType = bridgeInnerDataTypes(bridgeIndex);
        if direction == 1
            cp = [ polyval(polx, bridgeIndex) ; polyval(poly, jjWidthsIndex) ];
        else
            cp = [ polyval(polx, bridgeIndex) ; polyval(poly, (length(jjWidths)+1-jjWidthsIndex)) ];
        end
        gds_write_boundaries(gdsFile, shSquare(trTranslate(cp)*trScale(dx-10, dy-10), 'layer', LYR_BACK_MARKS));
        chipmark = [shSquare(trTranslate(-(dx/2-200)+10, -(dy/2-200)+100)*trScale(20, 200), 'layer', LYR_QUBIT_COARSE, 'datatype', 2) ...
            shSquare(trTranslate(-(dx/2-200)+20+90, -(dy/2-200)+10)*trScale(180, 20), 'layer', LYR_QUBIT_COARSE, 'datatype', 2) ...
            shSquare(trTranslate((dx/2-200)-10, (dy/2-200)-100)*trScale(20, 200), 'layer', LYR_QUBIT_COARSE, 'datatype', 2) ...
            shSquare(trTranslate((dx/2-200)-20-90, (dy/2-200)-10)*trScale(180, 20), 'layer', LYR_QUBIT_COARSE, 'datatype', 2)...
            shSquare(trTranslate(-(dx/2-200)+10, (dy/2-200)-100)*trScale(20, 200), 'layer', LYR_QUBIT_COARSE, 'datatype', 2) ...
            shSquare(trTranslate(-(dx/2-200)+20+90, (dy/2-200)-10)*trScale(180, 20), 'layer', LYR_QUBIT_COARSE, 'datatype', 2) ...
            shSquare(trTranslate((dx/2-200)-10, -(dy/2-200)+100)*trScale(20, 200), 'layer', LYR_QUBIT_COARSE, 'datatype', 2) ...
            shSquare(trTranslate((dx/2-200)-20-90, -(dy/2-200)+10)*trScale(180, 20), 'layer', LYR_QUBIT_COARSE, 'datatype', 2)];
        chipmark = applyTransform(chipmark, trTranslate(cp)*trRotate(rotation*180.0));
        
        chipmark2 = [shSquare(trTranslate(-(dx/2-200)+dx1+10, -(dy/2-200)+100)*trScale(20, 200), 'layer', LYR_QUBIT_COARSE, 'datatype', 2) ...
            shSquare(trTranslate(-(dx/2-200)+dx1+20+90, -(dy/2-200)+10)*trScale(180, 20), 'layer', LYR_QUBIT_COARSE, 'datatype', 2) ...
            shSquare(trTranslate(-(dx/2-200)+dx1+10, (dy/2-200)-100)*trScale(20, 200), 'layer', LYR_QUBIT_COARSE, 'datatype', 2) ...
            shSquare(trTranslate(-(dx/2-200)+dx1+20+90, (dy/2-200)-10)*trScale(180, 20), 'layer', LYR_QUBIT_COARSE, 'datatype', 2)];
        chipmark2 = applyTransform(chipmark2, trTranslate(cp)*trRotate(rotation*180.0));
        
        mountmark = [shTriangle(trTranslate(dx/2-dx2-mountmarkx, dy/2-200-200)*trScale(200, 400), 'layer', LYR_QUBIT_COARSE, 'datatype', 2) ...
            shTriangle(trTranslate(dx/2-dx2-mountmarkx, -dy/2+200+200)*trScale(200, -400), 'layer', LYR_QUBIT_COARSE, 'datatype', 2)];
        mountmark = applyTransform(mountmark, trTranslate(cp)*trRotate(rotation*180.0));
        
        chipmarks = [plgUndercutify([chipmark, chipmark2, mountmark], 0.20, 1), chipmark, chipmark2, mountmark]; %liftoffUndercut=0.20
        testLabelPlgs1a = applyTransform(str2boundaries(sprintf('F%d', jjWidth*1000), testLabelFontParams{:}), ...
            trTranslate(-dx/2+240, dy/2-250));
        testLabelPlgs1b = applyTransform(str2boundaries(sprintf('Row%d', jjWidthsIndex+1), testLabelFontParams{:}), ...
            trTranslate(-dx/2+240, -dy/2+300));
        newJunction = applyTransform(generate_qB_pattern(jjWidth, bridgeInnerDataType), trTranslate(dx1/2-dx2/2-qB_start, 0)*trScale(-1));
        roRes = shSquare(trTranslate(dx1/2-dx2/2-ro_len*0.5-ro_gap, 0)*trScale(ro_len,150.0), 'layer', LYR_QUBIT_COARSE, 'datatype', 1);
        roResonator = [plgUndercutify(roRes,0.20,1), roRes];
        device = applyTransform([newJunction roResonator testLabelPlgs1a testLabelPlgs1b], trTranslate(cp)*trRotate(rotation*180.0));
        testLabelPlgs2a = applyTransform(str2boundaries(sprintf('F%d', jjWidth*1000), testLabelFontParams{:}), ...
            trTranslate(dx1/2-dx2/2+240, dy/2-250));
        testLabelPlgs2b = applyTransform(str2boundaries(sprintf('Row%d', jjWidthsIndex+1), testLabelFontParams{:}), ...
            trTranslate(dx1/2-dx2/2+240, -dy/2+300));
        
        testJunction1 = applyTransform(generateBFJunctionPattern('junctionWidth', jjWidth,'contactExtension', 5, 'bridgeInnerDataType', bridgeInnerDataType, 'fco', 1, 'Rotation', 0), trTranslate(dx1/2,dy/3));
        testJunction2 = applyTransform(generateBFJunctionPattern('junctionWidth', jjWidth,'contactExtension', 10,'bridgeInnerDataType', bridgeInnerDataType, 'fco', 1, 'Rotation', 0), trTranslate(dx1/2,dy/9));
        testJunction3 = applyTransform(generateBFJunctionPattern('junctionWidth', jjWidth,'contactExtension', 18,'bridgeInnerDataType', bridgeInnerDataType, 'fco', 1, 'Rotation', 0), trTranslate(dx1/2,-dy/9));
        testJunction4 = applyTransform(generateBFJunctionPattern('junctionWidth', jjWidth,'contactExtension', 25,'bridgeInnerDataType', bridgeInnerDataType, 'fco', 1, 'Rotation', 0), trTranslate(dx1/2,-dy/3));
        testJunctions = applyTransform([testJunction1 testJunction2 testJunction3 testJunction4 testLabelPlgs2a testLabelPlgs2b], trTranslate(cp)*trRotate(rotation*180.0));
                       
        gds_write_boundaries(gdsFile, device);
        gds_write_boundaries(gdsFile, testJunctions);
        gds_write_boundaries(gdsFile, chipmarks);
  %      gds_write_boundaries(gdsFile, chipmark2);
        
        plgs = [plgs device testJunctions chipmarks];
        
    end
    fprintf('.');
end


gds_close_structure(gdsFile);
gds_start_structure(gdsFile, [junctionTestFileName '_rotated']);
gds_write_aref(gdsFile, [junctionTestFileName], 'angle', 270); 
gds_close_structure(gdsFile);
gds_start_structure(gdsFile, [junctionTestFileName '_rotateflipped']);
gds_write_aref(gdsFile, [junctionTestFileName], 'angle', 90); 
gds_close_structure(gdsFile);

gds_close_library(gdsFile);

return



