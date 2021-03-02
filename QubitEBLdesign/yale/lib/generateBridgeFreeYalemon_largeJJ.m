function plgs = generateBridgeFreeYalemon_largeJJ(junctionWidth, bridgeDataType)

p = inputParser;


needleLength = 0.900;    
junctionLength = 0.100;
narrowWidth = 1.000;  %describes skinny part connecting the junction pattern and the big antenna.  
narrowLength = 20.0;
transitionWidth = 10.0;
extensionLength = 100.0;
extraLength = 100.0;
fat_lead_len = 2000;
farLength = 1200.0-extraLength-50.0+1000.0;
fco = 0.0;
pad_rad = 360;
lead_w = 80;
% params for fat ymons at low frequencies 
% needleLength = 0.900;    
% junctionLength = 0.100;
% narrowWidth = 1.000;  %describes skinny part connecting the junction pattern and the big antenna.  
% narrowLength = 20.0;
% transitionWidth = 10.0;
% extensionLength = 100.0;
% extraLength = 100.0;
% fat_lead_len = 2000;
% farLength = 1200.0-extraLength-50.0+1000.0;
% fco = 0.0;
% pad_rad = 540;

[junction, JJedge] = generateBridgeFreeJunction2('junctionLength',junctionLength,'junctionWidth',junctionWidth,...
        'needleLength',needleLength,'narrowWidth',narrowWidth,'narrowLength',narrowLength,'leadWidth',transitionWidth, 'extensionLength',extensionLength, 'fco',fco, 'bridgeDataType',bridgeDataType); 

probefunnel = shFunnel(trTranslate(extraLength+extensionLength,0)*trRotate(-90),'startWidth', transitionWidth, 'endWidth', 200.0, 'funnelLength', 50.0, 'layer', LYR_QUBIT_COARSE);
proberect = shSquare(trTranslate(farLength/2+50.0+extraLength+extensionLength, 0.0)*trScale(farLength, 200.0), 'layer', LYR_QUBIT_COARSE);
bottom_fat_lead = gpcMultiClip(probefunnel,proberect,GPC_UNION);
coarse_lead = shSquare(trScale(extraLength, transitionWidth));
coarse_lead = applyTransform(coarse_lead, trTranslate(JJedge + 0.5*extraLength, 0));

bottom = gpcMultiClip(bottom_fat_lead,coarse_lead,GPC_UNION);
bottom_pad = shCircle(trTranslate(farLength+extraLength+50.0,0)*trScale(pad_rad*1.4*2, pad_rad*1.4*2));
far_structure = gpcMultiClip(bottom,bottom_pad,GPC_UNION);

thin_fork = shSquare(trScale(lead_w, 16),'layer', LYR_QUBIT_COARSE);
thin_fork = applyTransform(thin_fork,  trTranslate(-JJedge-lead_w*0.5, 0));
funnel_to_fat_lead = shFunnel(trTranslate(-JJedge-300, 0)*trRotate(90),'startWidth', 16, 'endWidth', 200.0, 'funnelLength', 50.0, 'layer', LYR_QUBIT_COARSE);
fat_lead = shSquare(trTranslate(-JJedge-300-50-0.5*fat_lead_len,0)*trScale(fat_lead_len, 200.0), 'layer', LYR_QUBIT_COARSE);
top_branch = gpcMultiClip(thin_fork, funnel_to_fat_lead, GPC_UNION);
top_branch = gpcMultiClip(top_branch, fat_lead, GPC_UNION);
bigPad = shCircle(trTranslate(-JJedge-300-50-fat_lead_len+200,0)*trScale(pad_rad*1.4*2,pad_rad*1.4*2), 'layer', LYR_QUBIT_COARSE);
top_branch = gpcMultiClip(top_branch, bigPad, GPC_UNION);
fork1 = applyTransform(top_branch, trRotate(60));
fork1 = applyTransform(fork1, trTranslate(-60,120));
fork2 = applyTransform(fork1, trYFlip());
y_shape = gpcMultiClip(fork1, fork2, GPC_UNION);

arcShort = shArc('midRadius', 400.0, 'arcWidth', 10.0, 'fromAngle', 10, 'openingAngle', 90.0, 'layer', LYR_QUBIT_COARSE);
arcShort2 = shArc('midRadius', 400.0, 'arcWidth', 10.0, 'fromAngle', 90.0, 'openingAngle',25.0, 'layer', LYR_QUBIT_COARSE);
arcShort2 = applyTransform(arcShort2, trScale(1.5, 1.0));
groundShort = gpcMultiClip(arcShort, arcShort2, GPC_UNION);

plgs = [junction far_structure y_shape groundShort];
liftOffUnderCut = 0.4;
if liftOffUnderCut ~= 0
    liftOffUnderCuts = plgUndercutify(plgsFilter(plgs,LYR_QUBIT_COARSE),liftOffUnderCut, liftOffUnderCut);
    liftOffUnderCuts = gpcMultiClip(liftOffUnderCuts,plgsFilter(plgs,LYR_QUBIT_FINE),GPC_DIFF); %remove undercuts overlapping with fine dose
    plgs = [plgs, liftOffUnderCuts];
end

