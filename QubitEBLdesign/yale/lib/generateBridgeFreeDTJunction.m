function plgs = generateBridgeFreeDTJunction(junctionWidth, bridgeDataType, fineDataType, coarseDataType, padLength)

needleLength = 0.600;    
junctionLength = 0.080;
narrowLeadWidth = 1.000;  %describes skinny part connecting the junction pattern and the big antenna.  
narrowLength = 60.0;
transitionWidth = 20.0;
hea = 15.0;
fco = 0.2;

[junction, JJedge] = generateBridgeFreeJunction('junctionLength',junctionLength,'junctionWidth',junctionWidth,...
        'needleLength',needleLength,'narrowWidth',narrowLeadWidth,'narrowLength',narrowLength,'bridgeDataType',bridgeDataType,'fineDataType',fineDataType); 

transitionFunnel = shFunnel(trTranslate(JJedge,0.0)*trRotate(-90),'startWidth', narrowLeadWidth, 'endWidth', transitionWidth, 'funnelLength',narrowLeadWidth*5, 'layer', LYR_QUBIT_FINE, 'dataType', fineDataType);
fco_compensation = shSquare(trTranslate(JJedge+narrowLeadWidth*5,0)*trScale(fco,transitionWidth)*trTranslate(0.5,0), 'layer', LYR_QUBIT_FINE, 'dataType', fineDataType);
funnel_right = gpcMultiClip(transitionFunnel, fco_compensation, GPC_UNION);
funnel_left = applyTransform(funnel_right,trScale(-1));

%transitionLead = shSquare(trTranslate(narrowLeadWidth*2,0)*trScale(extensionLength,leadWidth)*trTranslate(0.5,0), 'layer', LYR_QUBIT_COARSE, 'dataType', coarseDataType);
probefunnel = shFunnel(trTranslate(narrowLeadWidth*5,0.0)*trRotate(-90),'startWidth', transitionWidth, 'endWidth', 250.0, 'funnelLength', 50.0, 'layer', LYR_QUBIT_COARSE, 'dataType', coarseDataType);
proberect = shSquare(trTranslate(narrowLeadWidth*5+50.0+padLength/2, 0.0)*trScale(padLength, 250.0), 'layer', LYR_QUBIT_COARSE, 'dataType', coarseDataType);
probingPad = gpcMultiClip(probefunnel,proberect,GPC_UNION);
probingPad = applyTransform(probingPad, trTranslate(JJedge, 0));

probingPad_right = probingPad;
probingPad_left = applyTransform(probingPad_right, trScale(-1));
plgs = [junction funnel_right funnel_left probingPad_right probingPad_left];

liftOffUnderCut = 0.2;
if liftOffUnderCut ~= 0
    liftOffUnderCuts = plgUndercutify(plgsFilter(plgs,LYR_QUBIT_COARSE),liftOffUnderCut);
    liftOffUnderCuts = gpcMultiClip(liftOffUnderCuts,plgsFilter(plgs,LYR_QUBIT_FINE),GPC_DIFF); %remove undercuts overlapping with fine dose
    plgs = [plgs, liftOffUnderCuts];

end

