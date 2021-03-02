function plgs = generateDolan3DTransmon(fingerWidth, bridgeDataType, fineDataType, coarseDataType)

bridgeLength = 0.460;
mushroomExtraWidth = 0.200;
bridgeExtraWidth = 0.200;
fingerLength = 4.4;     
narrowWidth = 1.000;  %describes skinny part before hammer and finger.  
narrowLength = 65.0;
transitionWidth = 20.0;       %describes part after funnel from pad (aka squid line width) 
fco = 0.15;
hea = 15.0;

[junction, JJedge] = generateSingleJunction('fingerWidth',fingerWidth,'mushroomExtraWidth',mushroomExtraWidth,'bridgeExtraWidth',bridgeExtraWidth,'bridgeLength',bridgeLength,...
    'needlesLength',fingerLength,'narrowWidth',narrowWidth,'narrowLength',narrowLength,'funnelRelativeLength',1, ...
    'bridgeDataType',bridgeDataType,'fineDataType',fineDataType,'coarseDataType',coarseDataType);

transitionFunnel = shFunnel(trTranslate(JJedge,0.0)*trRotate(-90),'startWidth', narrowWidth, 'endWidth', transitionWidth, 'funnelLength',narrowWidth*5, 'layer', LYR_QUBIT_FINE, 'dataType', fineDataType);
fco_compensation = shSquare(trTranslate(JJedge+narrowWidth*5,0)*trScale(fco,transitionWidth)*trTranslate(0.5,0), 'layer', LYR_QUBIT_FINE, 'dataType', fineDataType);
funnel_right = gpcMultiClip(transitionFunnel, fco_compensation, GPC_UNION);
funnel_left = applyTransform(funnel_right,trScale(-1));

%transitionLead = shSquare(trTranslate(narrowWidth*2,0)*trScale(extensionLength,leadWidth)*trTranslate(0.5,0), 'layer', LYR_QUBIT_COARSE, 'dataType', coarseDataType);
probefunnel = shFunnel(trTranslate(narrowWidth*5,0.0)*trRotate(-90),'startWidth', transitionWidth, 'endWidth', 300.0, 'funnelLength', 50.0, 'layer', LYR_QUBIT_COARSE, 'dataType', coarseDataType);
proberect = shSquare(trTranslate(narrowWidth*5+300.0, 0.0)*trScale(500.0, 300.0), 'layer', LYR_QUBIT_COARSE, 'dataType', coarseDataType);
probingPad = gpcMultiClip(probefunnel,proberect,GPC_UNION);
probingPad = applyTransform(plgHolify(probingPad, 'frameWidth', hea, 'latticeConstant', 30), trTranslate(JJedge, 0));

bugHoleFixing = shSquare(trTranslate(JJedge+narrowWidth*4+8.0, 0)*trScale(9.0,20.0)*trTranslate(0.5,0), 'layer', LYR_QUBIT_COARSE, 'dataType', coarseDataType);
%probingPad_right = gpcMultiClip(probingPad,bugHoleFixing, GPC_UNION);
vortex_trap = shCircle(trTranslate(JJedge+435.0,0)*trScale(60), 'layer', LYR_QUBIT_COARSE, 'dataType', coarseDataType);
probingPad_right = [probingPad, vortex_trap, bugHoleFixing];
probingPad_left = applyTransform(probingPad_right, trScale(-1));
plgs = [junction funnel_right funnel_left probingPad_right probingPad_left];


liftOffUnderCut = 0.2;
if liftOffUnderCut ~= 0
    liftOffUnderCuts = plgUndercutify(plgsFilter(plgs,LYR_QUBIT_COARSE),liftOffUnderCut);
    liftOffUnderCuts = gpcMultiClip(liftOffUnderCuts,plgsFilter(plgs,LYR_QUBIT_FINE),GPC_DIFF); %remove undercuts overlapping with fine dose
    plgs = [plgs, liftOffUnderCuts];

end

