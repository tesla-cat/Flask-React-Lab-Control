function [plgs, halfTotalWidth] = generateBridgeFreeJunction(varargin)

p = inputParser;

p.addParamValue('narrowWidth',          1.0);
p.addParamValue('narrowLength',         5.0);

p.addParamValue('needleLength',          0.6); 

p.addParamValue('bridgeDataType',       0);
p.addParamValue('fineDataType',         0);

p.addParamValue('junctionLength',       0.080);
p.addParamValue('junctionWidth',        1.500);

p.KeepUnmatched = true;

p.parse(varargin{:});
expandStructure(p.Results);

%bridgeDataType0 = 0;
bridgeDataType1 = 1;

%fineDataType0 = 0;
fineDataType1 = 1;
fineDataType2 = 2;

junction = shSquare( trScale(junctionLength, junctionWidth), 'layer', LYR_QUBIT_FINE, 'dataType', fineDataType2);

leftNeedle = shSquare( trTranslate(-junctionLength/2, -0.250)*trScale(needleLength, 0.080)*trTranslate(-0.5,0), ...   
       'layer', LYR_QUBIT_FINE, 'dataType', fineDataType1);
   
leftUndercutInside = shSquare( trTranslate(-junctionLength/2-0.100, +0.090)*trScale(needleLength-2*0.100, 0.400)*trTranslate(-0.5,0), ...   
       'layer', LYR_QUBIT_FINE_BRIDGE, 'dataType', bridgeDataType);

leftUndercutBorder = gpcMultiClip(shSquare( trTranslate(-junctionLength/2, +0.040)*trScale(needleLength, 0.500)*trTranslate(-0.5,0), ...   
       'layer', LYR_QUBIT_FINE_BRIDGE, 'dataType', bridgeDataType1), leftUndercutInside, GPC_DIFF);

leftNarrowLead = shSquare( trTranslate(-junctionLength/2-needleLength, 0)*trScale(narrowLength, narrowWidth)*trTranslate(-0.5,0), ...   
       'layer', LYR_QUBIT_FINE, 'dataType', fineDataType);
   
leftStructures = [leftNeedle leftUndercutInside leftUndercutBorder leftNarrowLead];

rightStructures = applyTransform(leftStructures, trScale(-1));

plgs = [junction leftStructures rightStructures];
        
halfTotalWidth = junctionLength/2+needleLength+narrowLength;

