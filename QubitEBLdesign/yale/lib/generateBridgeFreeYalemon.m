function plgs = generateBridgeFreeYalemon(junctionWidth, bridgeDataType)

p = inputParser;

needleLength = 0.600;    
junctionLength = 0.100;
narrowWidth = 1.000;  %describes skinny part connecting the junction pattern and the big antenna.  
narrowLength = 20.0;
transitionWidth = 10.0;
extensionLength = 20.0;
extraLength = 300.0;
farLength = 1200.0-extraLength-50.0;
forkLength = 2600.0-extraLength-50.0;
fco = 0.0;

[junction, JJedge] = generateBridgeFreeJunction2('junctionLength',junctionLength,'junctionWidth',junctionWidth,...
        'needleLength',needleLength,'narrowWidth',narrowWidth,'narrowLength',narrowLength,'leadWidth',transitionWidth, 'extensionLength',extensionLength, 'fco',fco, 'bridgeDataType',bridgeDataType); 

extraExtension = shSquare(trScale(extraLength, transitionWidth)*trTranslate(0.5,0));
probefunnel = shFunnel(trTranslate(extraLength,0)*trRotate(-90),'startWidth', transitionWidth, 'endWidth', 120.0, 'funnelLength', 50.0, 'layer', LYR_QUBIT_COARSE);
proberect = shSquare(trTranslate(farLength/2+50.0+extraLength, 0.0)*trScale(farLength, 120.0), 'layer', LYR_QUBIT_COARSE);
blah = gpcMultiClip(probefunnel,proberect,GPC_UNION);
blah = gpcMultiClip(blah,extraExtension,GPC_UNION);
bigPad = shCircle(trTranslate(farLength+extraLength+50.0,0)*trScale(700.0,700.0));
blah = gpcMultiClip(blah,bigPad,GPC_UNION);
far_structure = applyTransform(blah, trTranslate(JJedge, 0));

extraExtension = shSquare(trScale(extraLength, 8.0)*trTranslate(0.5,0));
probefunnel = shFunnel(trTranslate(extraLength,0)*trRotate(-90),'startWidth', 8.0, 'endWidth', 120.0, 'funnelLength', 50.0, 'layer', LYR_QUBIT_COARSE);
proberect = shSquare(trTranslate(forkLength/2+50.0+extraLength, 0.0)*trScale(forkLength, 120.0), 'layer', LYR_QUBIT_COARSE);
blah = gpcMultiClip(probefunnel,proberect,GPC_UNION);
blah = gpcMultiClip(blah,extraExtension,GPC_UNION);
bigPad = shCircle(trTranslate(forkLength+extraLength+50.0,0)*trScale(700.0,700.0));
blah = gpcMultiClip(blah,bigPad,GPC_UNION);
fork1 = applyTransform(blah, trTranslate(-JJedge, 0)*trRotate(125));
fork2 = applyTransform(blah, trTranslate(-JJedge, 0)*trRotate(360-125));

%groundShort = shSquare(trTranslate(0.0, 200.0)*trScale(400.0, 4.0), 'layer', LYR_QUBIT_COARSE);
%blah = shSquare(trTranslate(200.0, 105.0)*trScale(4.0, 200.0-5.0+4.0), 'layer', LYR_QUBIT_COARSE);
%groundShort = gpcMultiClip(groundShort, blah, GPC_UNION);
%blah = shSquare(trTranslate(32.0, 13.0)*trScale(2.0, 16.0), 'layer', LYR_QUBIT_COARSE);
%groundShort = gpcMultiClip(groundShort, blah, GPC_UNION);

arcShort = shArc('midRadius', 200.0, 'arcWidth', 4.0, 'fromAngle', 1.4, 'openingAngle', 90.0, 'layer', LYR_QUBIT_COARSE);
arcShort2 = shArc('midRadius', 200.0, 'arcWidth', 4.0, 'fromAngle', 90.0, 'openingAngle', 33.0, 'layer', LYR_QUBIT_COARSE);
arcShort2 = applyTransform(arcShort2, trScale(1.5, 1.0));
groundShort = gpcMultiClip(arcShort, arcShort2, GPC_UNION);

plgs = [junction far_structure fork1 fork2 groundShort];

liftOffUnderCut = 0.2;
if liftOffUnderCut ~= 0
    liftOffUnderCuts = plgUndercutify(plgsFilter(plgs,LYR_QUBIT_COARSE),liftOffUnderCut, 1);
    liftOffUnderCuts = gpcMultiClip(liftOffUnderCuts,plgsFilter(plgs,LYR_QUBIT_FINE),GPC_DIFF); %remove undercuts overlapping with fine dose
    plgs = [plgs, liftOffUnderCuts];

end

