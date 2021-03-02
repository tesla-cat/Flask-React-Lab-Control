function [ panel panelSize ] = generateHolyPanel(holeRadius, holeDensity)

hr= holeRadius;
stot = 0.707107;
hole = struct('points', ...
     hr*[[stot 0 -stot -1 -stot 0 stot 1 stot]; [stot 1 stot 0 -stot -1 -stot 0 stot]], ...
     'layer', LYR_QUBIT_COARSE, 'dataType', 0);
 
hs = hr*(sqrt(2*3.14159/holeDensity)-2);
 
displacement = hs/2+hr;

rightUpperCorner = applyTransform(hole, trTranslate(displacement, displacement));
leftUpperCorner = applyTransform(hole, trTranslate(-displacement, displacement));
rightLowerCorner = applyTransform(hole, trTranslate(displacement, -displacement));
leftLowerCorner = applyTransform(hole, trTranslate(-displacement, -displacement));

panelSize = 2*hr+hs;

fullPanel = [ hole rightUpperCorner leftUpperCorner rightLowerCorner leftLowerCorner];


boundingBox = shSquare(trScale(panelSize/2, panelSize)*trTranslate(0.5,0), 'layer', LYR_QUBIT_COARSE);
panel = [ gpcMultiClip(boundingBox, plgsFilter(fullPanel, LYR_QUBIT_COARSE), GPC_DIFF) ];
panel = [panel applyTransform(panel, trXFlip)];


