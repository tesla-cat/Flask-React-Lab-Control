function plgs = generateBFJunctionPattern(varargin)

p = inputParser;
p.addParamValue('junctionWidth',     1.4);
p.addParamValue('coarseDataType',    0);
p.addParamValue('contactExtension',  10.0);
p.addParamValue('dataType',   0);
p.addParamValue('Rotation',  1);
p.addParamValue('bridgeInnerDataType',  0);
p.addParamValue('ushape_datatype',  0);
p.addParamValue('extensionLength', 100.0);
p.addParamValue('fco', 1.5);
p.addParamValue('fine_undercut', 0.4);
p.KeepUnmatched = true;

p.parse(varargin{:});
expandStructure(p.Results);

leadWidth = 10;%10.0;       %describes part after funnel from pad (aka squid line width) 
padWidth = 450.0;%300.0
padLength = 80.0;%;500.0
funnelLength = 20.0;%50.0


if (Rotation == 1)
    [junction, JJedge] = generateBridgeFreeJunction_rotated('extensionLength', extensionLength, 'junctionWidth', junctionWidth, 'leadWidth', leadWidth, 'bridgeInnerDataType', bridgeInnerDataType);
else
    [junction, JJedge] = generateBridgeFreeJunction2('extensionLength', extensionLength, 'junctionWidth', junctionWidth, ...
        'leadWidth', leadWidth, 'dataType', dataType, 'fco',fco, ...
        'bridgeInnerDataType', bridgeInnerDataType, 'ushape_datatype', ushape_datatype, 'fine_undercut', fine_undercut);
end
probefunnel = shFunnel('startWidth', leadWidth, 'endWidth', padWidth, 'funnelLength', funnelLength, 'layer', LYR_QUBIT_COARSE, 'dataType', 0);
probeRect = shSquare(trTranslate(0, padLength/2+funnelLength)*trScale(padWidth, padLength), 'layer', LYR_QUBIT_COARSE, 'dataType', 0);
probingPad = gpcMultiClip(probeRect,probefunnel,GPC_UNION);
probingPad_right = applyTransform(probingPad, trTranslate(JJedge, 0)*trRotate(-90));
probingPad_left = applyTransform(probingPad_right, trScale(-1));
plgs = [junction  probingPad_left probingPad_right];

liftOffUnderCut = 0.4;
if liftOffUnderCut ~= 0
    liftOffUnderCuts = plgUndercutify(plgsFilter(plgs,LYR_QUBIT_COARSE),liftOffUnderCut, 0.4);
    %liftOffUnderCutFine = plgUndercutify(plgsFilter(plgs,LYR_QUBIT_FINE),liftOffUnderCut, 0.4);
    liftOffUnderCuts = gpcMultiClip(liftOffUnderCuts,plgsFilter(plgs,LYR_QUBIT_FINE),GPC_DIFF); %remove undercuts overlapping with fine dose
    plgs = [plgs, liftOffUnderCuts];%, liftOffUnderCutFine];
end

