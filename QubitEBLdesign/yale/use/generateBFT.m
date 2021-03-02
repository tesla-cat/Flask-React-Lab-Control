function plgs = generateBFT(fingerWidth)

JJsize = 0.6;
fingerLength = 5.0;     
narrowLeadWidth = 1.0;  %describes skinny part before hammer and finger.  
narrowLength = 6.0;
leadWidth = 12.0; %describes part after funnel from pad (aka squid line width) 
funnelextention = 20.0;

%[junction, JJedge] = generateBridgeFreeJunction('junctionWidth',fingerWidth);
JJedge = bridgeLength/2.0 + fingerLength + narrowLeadWidth*2 + narrowLength + leadWidth*2 + extensionLength;
junction = generateSingleJunction2('fingerWidth',fingerWidth,'mushroomExtraWidth',mushroomExtraWidth,'bridgeExtraWidth',bridgeExtraWidth,'bridgeLength',bridgeLength,...
    'needlesLength',fingerLength,'narrowWidth',narrowLeadWidth,'narrowLength',narrowLength,'squidLineWidth',leadWidth,'extensionLength',extensionLength,...
    'fineCoarseOverlap',1.0,'dataType',dataType,'coarseDataType',coarseDataType);

funnel = shFunnel('startWidth', 1.0, 'endWidth', 10.0, 'funnelLength', 20.0, 'layer', LYR_QUBIT_COARSE, 'dataType', 0);
funnela = applyTransform(funnel, trTranslate(JJedge, 0)*trRotate(-90));
% funnelb = applyTransform(funnela, trXFlip());
lead = shSquare(trTranslate(JJedge + 20.0 + 40, 0)*trScale(80.0, 10.0), 'layer', LYR_QUBIT_COARSE, 'dataType', 0);
funnel2 = shFunnel('startWidth', 10.0, 'endWidth', 300.0, 'funnelLength', 50.0, 'layer', LYR_QUBIT_COARSE, 'dataType', 0);
funnel2 = applyTransform(funnel2, trTranslate(JJedge + 20.0 + 80, 0)*trRotate(-90));
rect = shSquare(trTranslate(JJedge + 20.0 + 80+ 250 + 50.0, 0)*trScale(500.0, 300.0), 'layer', LYR_QUBIT_COARSE, 'dataType', 0);
left = gpcMultiClip(funnela, lead, GPC_UNION);
right = applyTransform(left, trXFlip());
pad_left = gpcMultiClip(funnel2, rect, GPC_UNION);
pad_right = applyTransform(pad_left, trXFlip());
plgs = [junction left right pad_right pad_left];
% plgs = [plgs outer_rect];

% liftOffUnderCut = 0.2;
% if liftOffUnderCut ~= 0
%     liftOffUnderCuts = plgUndercutify(plgsFilter(plgs,LYR_QUBIT_COARSE),liftOffUnderCut);
%     liftOffUnderCuts = gpcMultiClip(liftOffUnderCuts,plgsFilter(plgs,LYR_QUBIT_FINE),GPC_DIFF); %remove undercuts overlapping with fine dose
%     plgs = [plgs, liftOffUnderCuts];
% end

%gds_write_boundaries('test', plgs);


                



    

