function [plgs, halfTotalWidth] = generateBridgeFreeJunction_rotated(varargin)

p = inputParser;

%Default Junction parameters (these can be changed by function arguments)
p.addParamValue('junctionLength',       0.100);
p.addParamValue('junctionWidth',        1.500);
p.addParamValue('needleLength',         0.6);
p.addParamValue('needleOffset',         0.25);
p.addParamValue('needleWidth',          0.08);
p.addParamValue('underCutWidth',        0.1);

%Default narrow lead parameters
p.addParamValue('narrowWidth',          1.0);
p.addParamValue('narrowLength',         5.0); % length of the S-segments
p.addParamValue('narrowLength2',        25.0);% length of the long narrow lead
p.addParamValue('narrowRadius',         0.2);
p.addParamValue('liftOffUnderCut',      0.15);

%Default coarse lead and funnel structures
p.addParamValue('leadWidth',            12.0);
p.addParamValue('funnelRelativeLength', 1.0);
p.addParamValue('extensionLength',      100.0);

p.addParamValue('bridgeInnerDataType',  0); %to vary bridge inner dose

p.KeepUnmatched = true;
p.parse(varargin{:});
expandStructure(p.Results);

%create the junction and rotate it such that the junction is along the
%direction of the leads 
overlap = shSquare(trScale(junctionLength, junctionWidth), 'layer', LYR_QUBIT_JUNCTION, 'dataType', 0);

leftNeedle = shSquare( trTranslate(-junctionLength/2, -needleOffset)*trScale(needleLength, needleWidth)*trTranslate(-0.5,0 ), ...   
       'layer', LYR_QUBIT_FINE_NEEDLE, 'dataType', 0);   

leftUndercutInside = shSquare( trTranslate(-junctionLength/2-underCutWidth, -needleOffset+needleWidth/2+underCutWidth) ...
    *trScale(needleLength-2*underCutWidth, 2*needleOffset-underCutWidth)*trTranslate(-0.5,0.5), ...   
       'layer', LYR_QUBIT_FINE_BRIDGE_INNER, 'dataType', bridgeInnerDataType);
leftUndercutBorder = gpcMultiClip(shSquare( trTranslate(-junctionLength/2, -needleOffset + needleWidth/2)*trScale(needleLength, 2*needleOffset)*trTranslate(-0.5,0.5), ...   
       'layer', LYR_QUBIT_FINE_BRIDGE, 'dataType', 0), leftUndercutInside, GPC_DIFF);
   
jj_left = [leftNeedle leftUndercutInside leftUndercutBorder];
jj_right = applyTransform(jj_left, trScale(-1));
junction = [overlap jj_left jj_right];
rotated_JJ = applyTransform(junction, trRotate(90));

% The S-shaped Rounded Rectangluar leads going out of the junction  
lead = shRoundedRectangle('width', narrowWidth, 'height', narrowLength+narrowRadius,'radius', narrowRadius,'layer', LYR_QUBIT_FINE, 'dataType', 0);   
leftNarrowLead = applyTransform(lead, trRotate(90)*trTranslate(-junctionLength/2-needleLength, 0)*trTranslate(-narrowLength/2-narrowRadius/2,0)*trRotate(90));

lead1 = shRoundedRectangle(trTranslate(2.5, -5.35), 'width', narrowLength+narrowRadius, ...
    'height', narrowWidth,'radius', narrowRadius,'layer', LYR_QUBIT_FINE, 'dataType', 0);   
lead2 = shRoundedRectangle(trTranslate(5, -2.675), 'width', narrowWidth, 'height', narrowLength+narrowRadius + narrowWidth*1.15, ...
    'radius', narrowRadius,'layer', LYR_QUBIT_FINE, 'dataType', 0);   

leftStructures = gpcMultiClip(lead1,leftNarrowLead,GPC_UNION);
leftStructures = gpcMultiClip(lead2,leftStructures,GPC_UNION);

% The long narrow lead and the funnel connecting to coarse structures
lead3 = shSquare(trTranslate(narrowLength,0)*trScale(narrowLength2, narrowWidth)*trTranslate(0.5,0),'layer', LYR_QUBIT_FINE, 'dataType', 0);
leftNarrowFunnel = shFunnel ( trTranslate(-narrowLength-narrowLength2,0)*trRotate(90), ...
    'startWidth', narrowWidth, 'endWidth', leadWidth, 'funnelLength', leadWidth*funnelRelativeLength, ...
    'layer', LYR_QUBIT_FINE, 'dataType', 0);
blah = gpcMultiClip(lead3,leftNarrowFunnel,GPC_UNION);
leftStructures = gpcMultiClip(blah,leftStructures,GPC_UNION);

if extensionLength ~= 0
    % Extension structure on the coarse layer going to the probe pad
    leftExtension = shSquare(trTranslate(narrowLength+narrowLength2+leadWidth*funnelRelativeLength,0)*trScale(extensionLength, leadWidth)*trTranslate(0.5,0),'layer', LYR_QUBIT_COARSE,'dataType', 0);
    leftStructures = [leftStructures leftExtension];
else
    leftExtension = shSquare(trTranslate(narrowLength+narrowLength2+leadWidth*funnelRelativeLength,0)*trScale(10.0, leadWidth)*trTranslate(0.5,0),'layer', LYR_QUBIT_COARSE,'dataType', 0);
end

rightStructures = applyTransform(leftStructures, trScale(-1));
plgs = [leftStructures rightStructures rotated_JJ];

if liftOffUnderCut ~= 0
    liftOffUnderCut_fine = plgUndercutify(plgsFilter(plgs,LYR_QUBIT_FINE),liftOffUnderCut);
    liftOffUnderCut_fine = gpcMultiClip(liftOffUnderCut_fine, leftExtension, GPC_DIFF); %remove undercuts overlapping with coarse dose
    liftOffUnderCut_fine = gpcMultiClip(liftOffUnderCut_fine, applyTransform(leftExtension,trXFlip()), GPC_DIFF); 
    
    funnyblock = shSquare(trTranslate(0,-junctionLength/2-needleLength-0.2 + 0.2)*trScale(narrowWidth+0.2*2 ,0.4),'layer', LYR_QUBIT_FINE);
    liftOffUnderCut_fine = gpcMultiClip(liftOffUnderCut_fine, funnyblock,GPC_DIFF); %remove undercuts overlapping with fine dose
    liftOffUnderCut_fine = gpcMultiClip(liftOffUnderCut_fine, applyTransform(funnyblock,trYFlip()),GPC_DIFF); %remove undercuts overlapping with fine dose
    
    plgs = [plgs, liftOffUnderCut_fine];
end

halfTotalWidth = narrowLength+narrowLength2+leadWidth*funnelRelativeLength+extensionLength;

