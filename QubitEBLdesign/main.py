
import gdspy
import numpy as np 

pi = np.pi
'''
general update needed to remove most if not all numbers
replace with variables with informative names 
'''
def basePlate():
  circle = gdspy.Round([0,0], 1, tolerance=1e-6)
  return gdspy.slice(circle, -0.9, 0)[1]

def markerL():
  return gdspy.FlexPath([(0,-1), (0,0), (1,0)], 0.1)

def markerV():
  return gdspy.Polygon([(0,0), (2,0.5), (2,-0.5)])
 
def resonator():
  pt1 = np.array([1,50])
  return gdspy.Rectangle(pt1, -pt1)

def join(a,b): return gdspy.boolean(a, b, 'or', precision=1e-6, max_points=1e6)
def cut(a,b): return gdspy.boolean(a, b, 'not', precision=1e-6, max_points=1e6)

def qubitC(
  lengths=[1, 4e-1, 8e-2, 1e-2], widths=[1, 1e-1, 1e-2, 0.5e-2],
  jumpRadius = 1, jumpWidth = 1e-2, useJump = True,
  borderWidth = 1e-3,
):
  """
  separate layers through cutting
  separate into two elements, thin lead near JJ and coarse features, 
  need to be able to define overlap between the two as well.  
  """
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
  # jump
  jump = gdspy.Path(jw, [0,jr]).arc(jr, pi*0.5, pi*1.5, tolerance=1e-6)
  p6 = join(p4, jump) if useJump else p4
  # border
  p7 = gdspy.offset(p6, borderWidth, precision=1e-6, max_points=1e6)
  p7 = cut(p7, gdspy.Rectangle([-ws[-2], -ls[-1]], [ws[-2], ls[-1] ]))
  p8 = cut(p7, p6)
  p6.layers = [2,2]
  return [p6, p8]

def qubitL(length = 1e-2):
  """
  layers
  absolute sizes
  change name to bridge_free_JJ 
  each individual feature needs to have its own layer
  check old file for details 
  """
  w1, x1, x2, x3, y1 = np.array([0.2, 0.2, 0.5, 1.5, 0.7]) 
  p1 = gdspy.FlexPath(
    [(x2,-y1), (-x1,-y1), (-x1,y1), (x2,y1)], w1,
    precision=1e-6, max_points=1e6,
  ).translate(0,y1+w1)
  rect1 = gdspy.Rectangle((x2, -y1-w1/2), (-x2, y1+w1/2)).translate(0,y1+w1)
  p2 = cut(rect1, p1)
  p2.layers = [1, 2]
  p1b = gdspy.copy(p1).rotate(pi)
  p2b = gdspy.copy(p2).rotate(pi)
  rect2 = gdspy.Rectangle((-x3, -w1/2), (x3, w1/2))
  scale = length / ( y1*2+w1 + w1/2 )
  return [x.scale(scale) for x in [p1, p2, p1b, p2b, rect2]]

'''
break from here and put the rest in a separate file, something 
like test_pattern_1 
'''
def group1():
  '''
  all translations need to be automatically calcuated 
  based on feature sizes and critical relevant dims
  '''
  p1 = qubitC()
  p2 = qubitL()
  p3 = resonator().scale(0.2).translate(0, 13)
  p4a = markerV().rotate(0 ).translate(-6, 50)
  p4b = markerV().rotate(pi).translate( 6, 50)
  p5a = markerL().rotate(0    ).translate(-6, 60)
  p5b = markerL().rotate(-pi/2).translate( 6, 60)
  return p1 + p2 + [p3, p4a, p4b, p5a, p5b]

def group2():
  def p1():
    return qubitC(useJump=False) + qubitL()
  p1a = [x.translate(-3, -6) for x in p1()]
  p1b = [x.translate(-1, -6) for x in p1()]
  p1c = [x.translate( 1, -6) for x in p1()]
  p1d = [x.translate( 3, -6) for x in p1()]
  p2a = markerL().rotate(0    ).translate(-6, -3)
  p2b = markerL().rotate(-pi/2).translate( 6, -3)
  p2c = markerL().rotate(pi/2 ).translate(-6, -9)
  p2d = markerL().rotate(pi   ).translate( 6, -9)
  x = 10
  '''
  label needs to be moved to inside of the corner markers
  '''
  t1 = gdspy.Text('label %d nm' % (x), 0.5, [0,-3])
  return group1() + p1a+p1b+p1c+p1d + [p2a,p2b,p2c,p2d, t1]

if __name__ == '__main__':
  lib = gdspy.GdsLibrary()
  c1 = lib.new_cell('c1')
  c1.add(group2()) 
  c1.add(gdspy.Label('o', [0,0]))
  lib.write_gds('main.gds')
  gdspy.LayoutViewer()