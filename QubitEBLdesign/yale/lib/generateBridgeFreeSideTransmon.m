function plgs = generateBridgeFreeSideTransmon(junctionWidth, bridgeDataType)% pad_w, pad_len)

p = inputParser;
needleLength = 0.900;    
junctionLength = 0.100;
narrowWidth = 1.000;  %describes skinny part connecting the junction pattern and the big antenna.  
narrowLength = 20.0;
transitionWidth = 10.0;
extensionLength = 100.0;
pad_w = 450; 
pad_len = 900*1.25;%1000*1.25;
fco = 1.5;

[junction, JJedge] = generateBridgeFreeJunction2('junctionLength',junctionLength,'junctionWidth',junctionWidth,...
        'needleLength',needleLength,'narrowWidth',narrowWidth,'narrowLength',narrowLength,'leadWidth',transitionWidth, 'extensionLength',extensionLength, 'fco',fco, 'bridgeDataType',bridgeDataType); 

probefunnel = shFunnel(trTranslate(JJedge,0)*trRotate(-90),'startWidth', transitionWidth, 'endWidth', pad_w, 'funnelLength', 50.0, 'layer', LYR_QUBIT_COARSE);
pad = shSquare(trScale(pad_len, pad_w),'layer', LYR_QUBIT_COARSE);
pad = applyTransform(pad, trTranslate(JJedge+50+pad_len*0.5, 0));


bottom_structure = gpcMultiClip(probefunnel,pad,GPC_UNION);

top_structure = applyTransform(bottom_structure,trXFlip());



arcShort = shArc('midRadius', pad_w, 'arcWidth', 4.0, 'fromAngle', 30, 'openingAngle', 120.0, 'layer', LYR_QUBIT_COARSE);
%arcShort2 = shArc('midRadius', 500.0, 'arcWidth', 4.0, 'fromAngle', 90.0, 'openingAngle', 30.0, 'layer', LYR_QUBIT_COARSE);
%arcShort2 = applyTransform(arcShort2, trScale(1.5, 1.0));
%groundShort = gpcMultiClip(arcShort, arcShort2, GPC_UNION);

plgs = [junction bottom_structure top_structure arcShort];
liftOffUnderCut = 0.4;
if liftOffUnderCut > 0
    liftOffUnderCuts = plgUndercutify(plgsFilter(plgs,LYR_QUBIT_COARSE),liftOffUnderCut, liftOffUnderCut);
    liftOffUnderCuts = gpcMultiClip(liftOffUnderCuts,plgsFilter(plgs,LYR_QUBIT_FINE),GPC_DIFF); %remove undercuts overlapping with fine dose
    plgs = [plgs, liftOffUnderCuts];
end

