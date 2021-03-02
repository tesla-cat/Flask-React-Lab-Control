function plgs = generateJunctionPattern(varargin)

p = inputParser;
p.addParamValue('junctionWidth',     1.4);
p.addParamValue('trap_size',         1.0);
p.addParamValue('coarseDataType',    1);
p.addParamValue('contactExtention',    -5.0);
p.addParamValue('bridgeDataType1',   100);

p.KeepUnmatched = true;

p.parse(varargin{:});
expandStructure(p.Results);

fineLength = 45.0;
leadWidth = 12;%10.0;       %describes part after funnel from pad (aka squid line width) 
extentionLength = 20;%50.0;
padWidth = 80.0;%300.0
padLength = 60.0;%;500.0
funnelLength = 10.0;%50.0

% JJedge = bridgeLength/2.0 + fingerLength + narrowLeadWidth*2 + narrowLength + leadWidth*2 + extentionLength;
JJedge = fineLength / 2.0;
junction = generateBridgeFreeJunction_rotated('extensionLength', JJedge + extentionLength/2 - 9.0 , 'bridgeDataType1', bridgeDataType1);

probefunnel = shFunnel('startWidth', leadWidth, 'endWidth', padWidth, 'funnelLength', funnelLength, 'layer', LYR_QUBIT_COARSE, 'dataType', coarseDataType);
probeRect = shSquare(trTranslate(0, padLength/2+funnelLength)*trScale(padWidth, padLength), 'layer', LYR_QUBIT_COARSE, 'dataType', coarseDataType);
probingPad = gpcMultiClip(probeRect,probefunnel,GPC_UNION);
probingPad_right = applyTransform(probingPad, trTranslate(JJedge+extentionLength+20.0, 0)*trRotate(-90));
probingPad_left = applyTransform(probingPad_right, trScale(-1));
plgs = [junction  probingPad_left probingPad_right];

% adding a square to the edge of the pads, two parameters are size of the
% squares and the offset from the edge of the pad
qpt_overlap = shSquare(trScale(trap_size,130.0),'layer',LYR_TRAP,'dataType',0);
qpt_overlap = applyTransform(qpt_overlap, trTranslate(JJedge + extentionLength+padLength,0));
qpt_probe1 = applyTransform(shSquare(trScale(100,100),'layer',LYR_TRAP,'dataType',0), ...
    trTranslate(JJedge + extentionLength+padLength,padLength+ 50.0));
qpt_probe2 = applyTransform(qpt_probe1, trScale(1,-1));
qpt = gpcMultiClip(qpt_overlap, qpt_probe1, GPC_UNION);
qpt_through = gpcMultiClip(qpt, qpt_probe2, GPC_UNION);
qpt_probe3 = applyTransform(qpt_probe1,trXFlip());
qpt_probe4 = applyTransform(qpt_probe2,trXFlip());
contact1 = shSquare(trScale(trap_size,130/2-padWidth/2 -5 + 2*contactExtention),'layer',LYR_TRAP,'dataType',0);
contact1 = applyTransform(contact1, trTranslate(-JJedge - extentionLength - padLength, padWidth/2+10.0));
contact2 = applyTransform(contact1, trYFlip());
qpt_corner1 = gpcMultiClip(qpt_probe3, contact1, GPC_UNION); 
qpt_corner2 = gpcMultiClip(qpt_probe4, contact2, GPC_UNION); 

plgs = [plgs qpt_through qpt_probe4, qpt_corner1 qpt_corner2];

liftOffUnderCut = 0.2;
if liftOffUnderCut ~= 0
    liftOffUnderCuts = plgUndercutify(plgsFilter(plgs,LYR_QUBIT_COARSE),liftOffUnderCut);
    liftOffUnderCuts = gpcMultiClip(liftOffUnderCuts,plgsFilter(plgs,LYR_QUBIT_FINE),GPC_DIFF); %remove undercuts overlapping with fine dose
    plgs = [plgs, liftOffUnderCuts];

end

