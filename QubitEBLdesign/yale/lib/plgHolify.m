function plgsOut = plgHolify(plgsIn, varargin)

p = inputParser;

p.addRequired('plgsIn');

p.addParamValue('frameWidth', 5.0);
p.addParamValue('brkFunction', @brkHexagon);

p.addParamValue('latticeConstant', 10);
p.addParamValue('fillingRatio', 0.5);

p.parse(plgsIn, varargin{:});
expandStructure(p.Results);

plgsOut = [];

for plgIndex = 1:length(plgsIn)
   
    plg = fixOrientation(plgsIn(plgIndex));
    plgInteria = offsetPath(plg, frameWidth, true);
    
    plgFrame = gpcMultiClip(plg, plgInteria, GPC_DIFF);

    plgBBox = boundingBox(plg);
    
    holeGrid = brkFunction( ...
        'latticeConstant', latticeConstant, ...
        'frameWidth', 0, ...
        'fillingRatio', fillingRatio, ...
        'height', plgBBox(4)-plgBBox(2), ...
        'width', plgBBox(3)-plgBBox(1));
    
    holeGrid = applyTransform(holeGrid, trTranslate( ...
        (plgBBox(1)+plgBBox(3))/2, (plgBBox(2)+plgBBox(4))/2));
    
    for gridPlgIndex = 1:length(holeGrid)
       
        plgsOut = [ plgsOut gpcMultiClip(plgInteria, holeGrid(gridPlgIndex), GPC_INT) ];
    end
    
    plgsOut = [plgsOut plgFrame];
end

