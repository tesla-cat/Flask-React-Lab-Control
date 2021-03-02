function plgs = generateBridgeJunctionPattern(varargin)

p = inputParser;
p.addParamValue('junctionWidth',     1.4);
p.addParamValue('trap_size',         2.5);
p.addParamValue('coarseDataType',    0);
p.addParamValue('contactExtension',  10.0);
p.addParamValue('dataType',   0);
% p.addParamValue('overlap',  5.0);
p.addParamValue('lead_length',  60.0);
p.addParamValue('Rotation',  1);
p.addParamValue('narrowLength',  5.0);
p.addParamValue('fingerWidth',  0.2);
p.addParamValue('extensionLength', 50);
p.addParamValue('needlesLength', 4.0); 
p.addParamValue('funnelRelativeLength',   2.0);
p.addParamValue('nextNarrowWidth',       12.0);
p.addParamValue('bridgeLength',     0.46);

p.KeepUnmatched = true;

p.parse(varargin{:});
expandStructure(p.Results);

padWidth = 80.0;%300.0
padLength = 80.0;%;500.0
funnelLength = 10.0;%50.0

JJedge = bridgeLength/2.0 + extensionLength + needlesLength + funnelRelativeLength + narrowLength + funnelRelativeLength * nextNarrowWidth;
junction = generateSingleJunction2('fingerWidth',fingerWidth, 'dataType', dataType, 'bridgeLength', bridgeLength);

probefunnel = shFunnel('startWidth', nextNarrowWidth, 'endWidth', padWidth, 'funnelLength', funnelLength, 'layer', LYR_QUBIT_COARSE, 'dataType', 0);
probeRect = shSquare(trScale(padWidth, padLength), 'layer', LYR_QUBIT_COARSE, 'dataType', 0);
% probeRect = applyTransform(probeRect, trTranslate(0, 0.5*padWidth+funnelLength));
probeRect = applyTransform(probeRect, trTranslate(0, 0.5*JJedge + 0.5*funnelLength));
probingPad = gpcMultiClip(probeRect,probefunnel,GPC_UNION);
probingPad_right = applyTransform(probingPad, trTranslate(JJedge, 0)*trRotate(-90));
probingPad_left = applyTransform(probingPad_right, trScale(-1));
plgs = [junction  probingPad_left probingPad_right];

% adding a square to the edge of the pads, two parameters are size of the
% squares and the offset from the edge of the pad
qpt_overlap = shSquare(trScale(trap_size,200.0),'layer',LYR_TRAP,'dataType',0);
qpt_overlap = applyTransform(qpt_overlap, trTranslate(JJedge + 0.5*padLength+funnelLength,0));
qpt_probe1 = applyTransform(shSquare(trScale(80,80),'layer',LYR_TRAP,'dataType',0), ...
    trTranslate(JJedge + 0.5*padLength+funnelLength,padLength+60.0));
qpt_probe = shSquare(trScale(80,80),'layer',LYR_TRAP,'dataType',0);
qpt_probe = applyTransform(qpt_probe, trTranslate(0, lead_length/2 + 40.0));

qpt_probe2 = applyTransform(qpt_probe1, trScale(1,-1));
qpt = gpcMultiClip(qpt_overlap, qpt_probe1, GPC_UNION);
qpt_through = gpcMultiClip(qpt, qpt_probe2, GPC_UNION);
contact1 = shSquare(trScale(trap_size, contactExtension),'layer',LYR_TRAP,'dataType',0);
contact1 = applyTransform(contact1, trTranslate(0,-contactExtension/2));
lead1 = shSquare(trScale(trap_size, lead_length),'layer',LYR_TRAP,'dataType',0);
qpt_right = gpcMultiClip(qpt_probe, lead1, GPC_UNION);
qpt_right = applyTransform(qpt_right, trTranslate(0, lead_length/2));
qpt_right1 = applyTransform(qpt_right, trRotate(45));
qpt_right2 = applyTransform(qpt_right1, trXFlip());
qpt_right_blah = gpcMultiClip(qpt_right1, qpt_right2, GPC_UNION);
qpt_right = gpcMultiClip(qpt_right_blah, contact1, GPC_UNION);
qpt_right = applyTransform(qpt_right, trTranslate(-(JJedge+ 0.5*padLength+funnelLength),padWidth/2));
qpt_left = applyTransform(qpt_right, trYFlip());


plgs = [plgs qpt_through qpt_right qpt_left];

liftOffUnderCut = 0.2;
if liftOffUnderCut ~= 0
    liftOffUnderCuts = plgUndercutify(plgsFilter(plgs,LYR_QUBIT_COARSE),liftOffUnderCut);
    liftOffUnderCuts = gpcMultiClip(liftOffUnderCuts,plgsFilter(plgs,LYR_QUBIT_FINE),GPC_DIFF); %remove undercuts overlapping with fine dose
    plgs = [plgs, liftOffUnderCuts];

end

