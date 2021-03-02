function [plgs, halfTotalWidth] = generateBridgeFreeJunction2(varargin)

p = inputParser;

%Default Junction parameters (these can be changed by function arguments)
p.addParamValue('junctionLength',       0.100);
p.addParamValue('junctionWidth',        1.500);
p.addParamValue('needleLength',         0.9);
p.addParamValue('needleOffset',         0.25);
p.addParamValue('needleWidth',          0.08);
p.addParamValue('underCutWidth',        0.1);

%Default narrow lead parameters
p.addParamValue('narrowWidth',          1.0);
p.addParamValue('narrowLength',         20.0);
p.addParamValue('narrowRadius',         0.2); 
p.addParamValue('liftOffUnderCut',      0.15);

%Default coarse lead and funnel structures
p.addParamValue('leadWidth',            10.0);
p.addParamValue('funnelRelativeLength', 1.0);
p.addParamValue('extensionLength',      100.0);
p.addParamValue('fco',                  2.0); %fine-coarse overlap

p.addParamValue('bridgeInnerDataType',  0); %to vary bridge inner dose
p.addParamValue('ushape_datatype',  0); %to vary bridge inner dose
p.addParamValue('fine_undercut',0.4);

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
       'layer', LYR_QUBIT_FINE_BRIDGE, 'dataType', ushape_datatype), leftUndercutInside, GPC_DIFF);
   
jj_left = [leftNeedle leftUndercutInside leftUndercutBorder];
jj_right = applyTransform(jj_left, trScale(-1));
junction = [overlap jj_left jj_right];

lead = shRoundedRectangle('width', narrowLength, 'height', narrowWidth,'radius', narrowRadius,'layer', LYR_QUBIT_FINE, 'dataType', 0);   
leftNarrowLead = applyTransform(lead, trTranslate(-junctionLength/2-needleLength-narrowLength/2, 0));

% The long narrow lead and the funnel connecting to coarse structures.
% Its position was misplaced a little with the small junction width and
% needle length neglected, but I've left it as is.
leftNarrowFunnel = shFunnel ( trTranslate(-narrowLength,0)*trRotate(90), ...
    'startWidth', narrowWidth, 'endWidth', leadWidth, 'funnelLength', leadWidth*funnelRelativeLength, ...
    'layer', LYR_QUBIT_FINE, 'dataType', 0);
leftStructures = gpcMultiClip(leftNarrowLead,leftNarrowFunnel,GPC_UNION);

if extensionLength ~= 0
    % Extension structure on the coarse layer going to the probe pad
    leftExtension = shSquare(trTranslate(narrowLength+leadWidth*funnelRelativeLength-fco,0)*trScale(extensionLength+fco, leadWidth)*trTranslate(0.5,0),'layer', LYR_QUBIT_COARSE,'dataType', 0);
    leftStructures = [leftStructures leftExtension];
else
    leftExtension = shSquare(trTranslate(narrowLength+leadWidth*funnelRelativeLength,0)*trScale(10.0, leadWidth)*trTranslate(0.5,0),'layer', LYR_QUBIT_COARSE,'dataType', 0);
end

rightStructures = applyTransform(leftStructures, trScale(-1));
plgs = [leftStructures rightStructures junction];

liftOffUnderCut = fine_undercut;
if liftOffUnderCut > 0
    liftOffUnderCut_fine = plgUndercutify(plgsFilter(plgs,LYR_QUBIT_FINE),liftOffUnderCut, liftOffUnderCut);
    liftOffUnderCut_fine = gpcMultiClip(liftOffUnderCut_fine, leftExtension, GPC_DIFF); %remove undercuts overlapping with coarse dose
    liftOffUnderCut_fine = gpcMultiClip(liftOffUnderCut_fine, applyTransform(leftExtension,trXFlip()), GPC_DIFF); 
    
    funnyblock = shSquare(trScale(junctionLength+needleLength*2,1.0),'layer', LYR_QUBIT_FINE);
    liftOffUnderCut_fine = gpcMultiClip(liftOffUnderCut_fine, funnyblock,GPC_DIFF); %remove undercuts overlapping with fine dose
%    liftOffUnderCut_fine = gpcMultiClip(liftOffUnderCut_fine, applyTransform(funnyblock,trYFlip()),GPC_DIFF); %remove undercuts overlapping with fine dose
    
    plgs = [plgs, liftOffUnderCut_fine];
end

halfTotalWidth = narrowLength+leadWidth*funnelRelativeLength+extensionLength; % This is the correct length due to the funnel placement.

