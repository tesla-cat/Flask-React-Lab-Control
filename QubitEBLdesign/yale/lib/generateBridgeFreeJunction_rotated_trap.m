function [plgs, halfTotalWidth] = generateBridgeFreeJunction_rotated_trap(varargin)

p = inputParser;
%Default Junction parameters (these can be changed by function arguments)
p.addParamValue('leadWidth',            12.0);
p.addParamValue('narrowWidth',          1.0);
p.addParamValue('narrowLength',         5.0);
p.addParamValue('narrowRadius',         0.2);

p.addParamValue('needleLength',         0.6);
p.addParamValue('needleOffset',         0.25);
p.addParamValue('needleWidth',          0.08);

p.addParamValue('bridgeDataType1',      0);
p.addParamValue('fineDataType0',        0);

p.addParamValue('junctionLength',       0.100);
p.addParamValue('junctionWidth',        1.500);

p.addParamValue('underCutWidth',        0.1);
p.addParamValue('funnelRelativeLength', 2.0);
p.addParamValue('extensionLength',      120.0);
p.addParamValue('fineCourseOverlap',    1.5);
p.addParamValue('qpt_size',    2.0);

p.KeepUnmatched = true;

p.parse(varargin{:});
expandStructure(p.Results);

bridgeDataType0 = 0;
bridgeDataType1 = 0;

fineDataType0 = 0;
fineDataType1 = 1;
fineDataType2 = 1;

%create the junction and rotate it such that the junction is along the
%direction of the leads 
% junction = shSquare( trScale(junctionLength, junctionWidth), 'layer', LYR_QUBIT_FINE_NEEDLE, 'dataType', 0);
% junction = applyTransform(junction, trRotate(90));
overlap = shSquare( trScale(junctionLength, junctionWidth), 'layer', LYR_QUBIT_JUNCTION, 'dataType', 0);
% junction = applyTransform(overlap, trRotate(90));

leftNeedle = shSquare( trTranslate(-junctionLength/2, -needleOffset)*trScale(needleLength, needleWidth)*trTranslate(-0.5,0 ), ...   
       'layer', LYR_QUBIT_FINE_NEEDLE, 'dataType', 0);
   
leftUndercutInside = shSquare( trTranslate(-junctionLength/2-underCutWidth, -needleOffset+needleWidth/2+underCutWidth) ...
    *trScale(needleLength-2*underCutWidth, 2*needleOffset-underCutWidth)*trTranslate(-0.5,0.5), ...   
       'layer', LYR_QUBIT_FINE_BRIDGE_INNER, 'dataType', bridgeDataType1);

leftUndercutBorder = gpcMultiClip(shSquare( trTranslate(-junctionLength/2, -needleOffset + needleWidth/2)*trScale(needleLength, 2*needleOffset)*trTranslate(-0.5,0.5), ...   
       'layer', LYR_QUBIT_FINE_BRIDGE, 'dataType', bridgeDataType0), leftUndercutInside, GPC_DIFF);
jj_left = [leftNeedle leftUndercutInside leftUndercutBorder];
jj_right = applyTransform(jj_left, trScale(-1));
junction = [overlap jj_left jj_right];
rotated_JJ = applyTransform(junction, trRotate(90));

%Rectangular NarrowLead   
% leftRectLead = shSquare( trTranslate(-junctionLength/2-needleLength, 0)*trScale(narrowLength, narrowWidth)*trTranslate(-0.5,0), ...   
%        'layer', LYR_QUBIT_FINE, 'dataType', fineDataType0);

% Rounded Rectangluar NarrowLead   
lead = shRoundedRectangle('width', narrowWidth, 'height', narrowLength+narrowRadius,'radius', narrowRadius,'layer', LYR_QUBIT_FINE, 'dataType', fineDataType0);   

lead1 = shRoundedRectangle('width', narrowLength+narrowRadius, 'height', narrowWidth,'radius', narrowRadius,'layer', LYR_QUBIT_FINE, 'dataType', fineDataType0);   
lead1 = applyTransform(lead1, trTranslate(2.5, -5.35));


leftNarrowLead = applyTransform(lead, trRotate(90)*trTranslate(-junctionLength/2-needleLength, 0)*trTranslate(-narrowLength/2-narrowRadius/2,0)*trRotate(90));

lead2 = shRoundedRectangle('width', narrowWidth, 'height', narrowLength+narrowRadius + narrowWidth*1.15 ,'radius', narrowRadius,'layer', LYR_QUBIT_FINE, 'dataType', fineDataType0);   
% lead2 = applyTransform(lead2, trRotate(90));
lead2 = applyTransform(lead2, trTranslate(5, -2.675));

%Make slanted corners on NarrowLead
% Slant = shTriangle( trTranslate(-junctionLength/2 - needleLength, narrowWidth/2)*trScale(narrowWidth/2 - (needleOffset + needleWidth/2))*trRotate(-45)*trScale(sqrt(2), sqrt(2))*trScale(1,0.5)*trTranslate(0,-0.5), ...
%     'layer', LYR_QUBIT_FINE, 'dataType', fineDataType0);
% lowerSlant = applyTransform(Slant, trScale(1,-1));
% leftNarrowLead = gpcMultiClip(leftLead, upperSlant, GPC_DIFF);
% leftNarrowLead = gpcMultiClip(leftLead, lowerSlant, GPC_DIFF);
% leftNarrowLead = gpcMultiClip(leftNarrowLead, upperSlant, GPC_DIFF);
% leftNarrowLead = gpcMultiClip(leftNarrowLead, lowerSlant, GPC_DIFF);

leftNarrowFunnel = shFunnel ( trTranslate(-junctionLength/2-needleLength-6.0*narrowLength,0)*trRotate(90), ...
    'startWidth', narrowWidth, 'endWidth', leadWidth, 'funnelLength', leadWidth, ...
    'layer', LYR_QUBIT_FINE, 'dataType', 0);

lead3 = shRoundedRectangle('width', 6.0*narrowLength+narrowRadius -3.5, 'height', narrowWidth,'radius', narrowRadius,'layer', LYR_QUBIT_FINE, 'dataType', fineDataType0);
lead3 = applyTransform(lead3, trTranslate(18.0, 0));
% leftStructures = gpcMultiClip(lead3,leftNarrowFunnel,GPC_UNION);
leftStructure = gpcMultiClip(lead1,leftNarrowLead,GPC_UNION);
leftStructure = gpcMultiClip(lead2,leftStructure,GPC_UNION);
leftStructure = gpcMultiClip(lead3,leftStructure,GPC_UNION);
leftStructure = gpcMultiClip(leftNarrowFunnel,leftStructure,GPC_UNION);
leftExtension = shSquare( trTranslate(-12.0-junctionLength/2-needleLength-narrowLength-2*leadWidth,0)* ...
    trScale(extensionLength, leadWidth)*trTranslate(-0.5,0), ...
    'layer', LYR_QUBIT_COARSE,'dataType', 0);

leftStructures = [leftStructure leftExtension];

% if extensionLength ~=0
%     leftExtension = shSquare( trTranslate(-12.0-junctionLength/2-needleLength-narrowLength-2*leadWidth,0)* ...
%         trScale(extensionLength, leadWidth)*trTranslate(-0.5,0), ...
%         'layer', LYR_QUBIT_COARSE,'dataType', 0);
% end
    
rightStructures = applyTransform(leftStructures, trScale(-1));

plgs = [leftStructures rightStructures rotated_JJ];

halfTotalWidth = junctionLength/2+needleLength+narrowLength+2*leadWidth+extensionLength;

