
import gdspy
import numpy as np 

pi = np.pi

def join(a,b): return gdspy.boolean(a, b, 'or', precision=1e-6, max_points=1e6, layer=a.layers[0])
def cut(a,b): return gdspy.boolean(a, b, 'not', precision=1e-6, max_points=1e6, layer=a.layers[0])

def basePlate(center=[0,0], radius=1, slicePosition=-0.9, layer=0):
  circle = gdspy.Round(center, radius, tolerance=1e-6, layer=layer)
  return gdspy.slice(circle, slicePosition, 0)[1]

def markerL(size=1, width=0.1, label = 'label', layer=12):
  t = gdspy.Text(label, 0.2, [0.1,-0.4], layer=layer)
  p = gdspy.FlexPath([(0,-1), (0,0), (1,0)], width, layer=layer)
  return join(p, t).scale(size)

def markerV(size=1, layer=12):
  return gdspy.Polygon([(0,0), (2,0.5), (2,-0.5)], layer=layer).scale(size)
 
def resonator(length=20, width=0.4, layer=12):
  pt1 = np.array([width/2, length/2])
  return gdspy.Rectangle(pt1, -pt1, layer=layer)

def qubitC(
  lengths=[1, 4e-1, 8e-2, 1e-2], widths=[1, 1e-1, 1e-2, 0.5e-2],
  jumpRadius = 1, jumpWidth = 1e-2, useJump = True,
  borderWidth = 1e-3,
  overlap = 1e-2,
  layers = [6, 11, 12],
):
  ls, ws, jr, jw = lengths, widths, jumpRadius, jumpWidth
  c = gdspy.Curve(0, -np.sum(ls), tolerance=1e-6).H(-ws[0]/2)
  for i, l in enumerate(ls[:-1]):
    if i < len(ls)-2: 
      dx = (ws[i] - ws[i+1]) / 2
      c.v(l*0.8).c(0, l*0.1, dx, l*0.1, dx, l*0.2)
    else:
      w = ws[i] / 2
      c.v(l - w).c(0, w, 0, w, w, w)  
  p = gdspy.Polygon(c.get_points())
  p2 = join(p,  gdspy.copy(p).mirror([0,1]))
  p4 = join(p2, gdspy.copy(p2).rotate(pi))
  # slice
  pt1 = ls[-3]*0.2 + ls[-2] + ls[-1]
  p4a = gdspy.slice(gdspy.copy(p4), [pt1, -pt1], 1, precision=1e-6)
  p4a = join(p4a[0], p4a[2])
  p4b = gdspy.slice(gdspy.copy(p4), [pt1+overlap, -pt1-overlap], 1, precision=1e-6)
  p4b = p4b[1]
  # jump
  jump = gdspy.Path(jw, [0,jr]).arc(jr, pi*0.5, pi*1.5, tolerance=1e-6)
  p6 = join(p4, jump) if useJump else p4
  p6a = join(p4a, jump) if useJump else p4a
  # border
  p7 = gdspy.offset(p6, borderWidth, precision=1e-6, max_points=1e6)
  p7 = cut(p7, gdspy.Rectangle([-ws[-2], -ls[-1]], [ws[-2], ls[-1] ]))
  p8 = cut(p7, p6)
  # layers
  p4b.layers = [layers[1]] * 2 # small feature
  p6a.layers = [layers[2]] * 2 # big feature
  p8.layers  = [layers[0]] * 2 # border
  return [p4b, p6a, p8] # p6, p8

def qubitJJ(
  length = 1e-2, sizes = [0.2, 0.2, 0.5, 1.5, 0.7],
  layers = [7, 8, 9, 10],
):
  w1, x1, x2, x3, y1 = np.array(sizes) 
  p1 = gdspy.FlexPath(
    [(x2,-y1), (-x1,-y1), (-x1,y1), (x2,y1)], w1,
    precision=1e-6, max_points=1e6,
  ).translate(0,y1+w1)
  rect1 = gdspy.Rectangle((x2, -y1-w1/2), (-x2, y1+w1/2)).translate(0,y1+w1)
  p2 = cut(rect1, p1)
  p1b = gdspy.copy(p1).rotate(pi)
  p2b = gdspy.copy(p2).rotate(pi)
  rect2 = gdspy.Rectangle((-x3, -w1/2), (x3, w1/2))
  scale = length / ( y1*2+w1 + w1/2 )
  # layers
  rect2.layers = [layers[0]]  # center rect
  p1.layers = p1b.layers = [layers[3]]  # C shape
  p2.layers = p2b.layers = layers[1:3]
  return [x.scale(scale) for x in [p1, p2, p1b, p2b, rect2]]

def generate(part):
  lib = gdspy.GdsLibrary()
  c1 = lib.new_cell('c1')
  c1.add(part()) 
  c1.add(gdspy.Label('origin', [0,0]))
  lib.write_gds('output.gds')
  gdspy.LayoutViewer()