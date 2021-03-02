
import numpy as np 
import gdspy

pi = np.pi
# https://gdspy.readthedocs.io/en/stable/gettingstarted.html#integrated-photonics

def grating(
  period, numTeeth, fillFrac, width, pos, 
  direction, lda=1, sin_theta = 0, focusDist=-1,
  focusWidth=-1, tol=1e-3, layer=0, dataType=0,  
):
  width1 = period * fillFrac  
  print('focusDist', focusDist)
  print('focusWidth', focusWidth)
  if focusDist < 0:
    p = gdspy.L1Path(
      initial_point=[
        pos[0] - width / 2,
        pos[1] + period * (numTeeth-1) + width1
      ],
      direction='+x',
      width=width1,
      length=[width],
      turn=[],
      number_of_paths=numTeeth,
      distance=period,
      layer=layer,
      datatype=dataType,
    )
  else:
    neff = lda / period + sin_theta
    qmin = int(focusDist / period + 0.5)
    p = gdspy.Path(
      width=width1, 
      initial_point=pos,
    )
    c3 = neff**2 - sin_theta**2
    w = width/2
    for q in range(qmin, qmin+numTeeth):
      c1 = q * lda * sin_theta
      c2 = (q*lda)**2
      p.parametric(
        curve_function=lambda t:(
          width * t - w,
          (c1+neff*np.sqrt(c2-c3*(width*t-w)**2))/c3
        ),
        tolerance=tol,
        max_points=0,
        layer=layer,
        datatype=dataType
      )
      p.x = pos[0]
      p.y = pos[1]
    sz = p.polygons[0].shape[0] // 2
    if focusWidth == 0:
      p.polygons[0] = np.vstack([ 
        p.polygons[0][:sz, :], 
        [pos] 
      ])
    elif focusWidth > 0:
      p.polygons[0] = np.vstack([
        p.polygons[0][:sz, :],
        [
          (pos[0] + focusWidth/2, pos[1]),
          (pos[0] - focusWidth/2, pos[1]),
        ]
      ])
    p.fracture()
  if direction == "-x":
    return p.rotate(angle=pi/2, center=pos)
  elif direction == "+x":
    return p.rotate(-pi/2, pos)
  elif direction == "-y":
    return p.rotate(pi, pos)
  else:
    return p

if __name__=='__main__':
  lib = gdspy.GdsLibrary()

  focusWidth = 0.45
  Rbend = 50
  Rring = 20
  taperLen = 50
  inputGap = 150
  ioGap = 500
  wgGap = 20
  ringGaps = [0.06 + 0.02 * i for i in range(8)]

  ring = lib.new_cell('Nring')
  ring.add(gdspy.Round(
    [Rring,0], Rring, Rring-focusWidth, tolerance=1e-3
  ))

  grat = lib.new_cell('Ngrat')
  grat.add(grating(
    0.626, 28, 0.5, 19, [0,0], "+y", 1.55, 
    np.sin(8 /180*pi), 21.5, focusWidth, tol=1e-3
  ))

  taper = lib.new_cell('Ntaper')
  taper.add(gdspy.Path(0.12, [0,0]).segment(
    taperLen,'+y',final_width=focusWidth
  ))
  
  neg = lib.new_cell('Negative')
  for i, gap in enumerate(ringGaps):
    path = gdspy.FlexPath(
      [(inputGap*i, taperLen)],
      width=focusWidth,
      corners='circular bend',
      bend_radius=Rbend,
      gdsii_path=True
    )
    path.segment([0, 600-wgGap*i], relative=True)
    path.segment([ioGap, 0], relative=True)
    path.segment([0, 300+wgGap*i], relative=True)
    neg.add(path)
    neg.add(gdspy.CellReference(
      ring, [inputGap*i+focusWidth/2+gap, 300]
    ))
  neg.add(gdspy.CellArray(
    taper, len(ringGaps), 1, [inputGap,0], [0,0]
  ))
  neg.add(gdspy.CellArray(
    grat, len(ringGaps), 1, [inputGap,0], [ioGap, 900+taperLen]
  ))

  lib.write_gds('photon.gds')
  gdspy.LayoutViewer(lib)