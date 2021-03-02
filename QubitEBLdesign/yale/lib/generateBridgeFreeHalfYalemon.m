function plgs = generateBridgeFreeHalfYalemon(junctionWidth, bridgeDataType)

p = inputParser;

needleLength = 0.900;    
junctionLength = 0.100;
narrowWidth = 1.000;  %describes skinny part connecting the junction pattern and the big antenna.  
narrowLength = 20.0;
transitionWidth = 10.0;
extensionLength = 40.0;
extraLength = 300.0;
fat_lead_len = 2000;
farLength = 1200.0-extraLength-50.0+1000.0;
fco = 0.0;

[junction, JJedge] = generateBridgeFreeJunction2('junctionLength',junctionLength,'junctionWidth',junctionWidth,...
        'needleLength',needleLength,'narrowWidth',narrowWidth,'narrowLength',narrowLength,'leadWidth',transitionWidth, 'extensionLength',extensionLength, 'fco',fco, 'bridgeDataType',bridgeDataType); 

probefunnel = shFunnel(trTranslate(extraLength,0)*trRotate(-90),'startWidth', transitionWidth, 'endWidth', 200.0, 'funnelLength', 50.0, 'layer', LYR_QUBIT_COARSE);
proberect = shSquare(trTranslate(farLength/2+50.0+extraLength, 0.0)*trScale(farLength, 200.0), 'layer', LYR_QUBIT_COARSE);
bottom_fat_lead = gpcMultiClip(probefunnel,proberect,GPC_UNION);
coarse_lead = shSquare(trScale(extraLength, transitionWidth));
coarse_lead = applyTransform(coarse_lead, trTranslate(JJedge + 0.5*extraLength, 0));

bottom = gpcMultiClip(bottom_fat_lead,coarse_lead,GPC_UNION);
bottom_pad = shCircle(trTranslate(farLength+extraLength+50.0,0)*trScale(1400.0, 1400.0));
far_structure = gpcMultiClip(bottom,bottom_pad,GPC_UNION);

thin_fork = shSquare(trScale(300, 16),'layer', LYR_QUBIT_COARSE);
thin_fork = applyTransform(thin_fork,  trTranslate(-JJedge-300*0.5, 0));
funnel_to_fat_lead = shFunnel(trTranslate(-JJedge-300, 0)*trRotate(90),'startWidth', 16, 'endWidth', 200.0, 'funnelLength', 50.0, 'layer', LYR_QUBIT_COARSE);
fat_lead = shSquare(trTranslate(-JJedge-300-50-0.5*fat_lead_len,0)*trScale(fat_lead_len, 200.0), 'layer', LYR_QUBIT_COARSE);
top_branch = gpcMultiClip(thin_fork, funnel_to_fat_lead, GPC_UNION);
top_branch = gpcMultiClip(top_branch, fat_lead, GPC_UNION);
bigPad = shCircle(trTranslate(-JJedge-300-50-fat_lead_len+100,0)*trScale(700.0*2,700.0*2), 'layer', LYR_QUBIT_COARSE);
top_branch = gpcMultiClip(top_branch, bigPad, GPC_UNION);
fork1 = applyTransform(top_branch, trRotate(60));
fork1 = applyTransform(fork1, trTranslate(-34,65));
fork2 = applyTransform(fork1, trYFlip());
%y_shape = gpcMultiClip(fork1, fork2, GPC_UNION);

arcShort = shArc('midRadius', 250.0, 'arcWidth', 4.0, 'fromAngle', 1.4, 'openingAngle', 90.0, 'layer', LYR_QUBIT_COARSE);
arcShort2 = shArc('midRadius', 250.0, 'arcWidth', 4.0, 'fromAngle', 90.0, 'openingAngle', 30.0, 'layer', LYR_QUBIT_COARSE);
arcShort2 = applyTransform(arcShort2, trScale(1.5, 1.0));
groundShort = gpcMultiClip(arcShort, arcShort2, GPC_UNION);

plgs = [junction far_structure fork2 groundShort];
liftOffUnderCut = 0.4;
if liftOffUnderCut ~= 0
    liftOffUnderCuts = plgUndercutify(plgsFilter(plgs,LYR_QUBIT_COARSE),liftOffUnderCut, 1);
    liftOffUnderCuts = gpcMultiClip(liftOffUnderCuts,plgsFilter(plgs,LYR_QUBIT_FINE),GPC_DIFF); %remove undercuts overlapping with fine dose
    plgs = [plgs, liftOffUnderCuts];
end

