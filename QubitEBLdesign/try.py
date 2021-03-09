
import gdspy
import numpy as np 

pi = np.pi

def part1(pos = -0.9):
  circle = gdspy.Round([0,0], 1, tolerance=1e-3)
  circleCut = gdspy.slice(circle, pos, 0)
  return circleCut[1]

def part23a(width = 0.1):
  p = gdspy.FlexPath([(0,-1), (0,0), (1,0)], width)
  return p

def part23b():
  p = gdspy.Polygon([(0,0), (2,0.5), (2,-0.5)])
  return p
  
def part23c(width = 1e-2):
  pt1 = np.array([width/2,0.5])
  p = gdspy.Rectangle(pt1, -pt1)
  return p

def part23d(
  lengths = [1, 4e-1, 8e-2], widths = [1, 1e-1, 1e-2],
  gapFrac = 0.1, pathWidth = 1e-3, offset = 5e-3,
):
  size = np.sum(lengths) * (1+2*gapFrac) + offset
  p = gdspy.Path(pathWidth, [0, -size])
  widths.append(0)
  ws = [widths[i]-widths[i+1] for i in range(len(widths)-1)]
  p.segment(widths[0]/2, '-x')
  for i, l in enumerate(lengths):
    p.segment(l, '+y')
    dy = l * gapFrac
    dx = ws[i] * 0.5
    p.bezier([(0, dy), (dx, dy), (dx, dy*2)], tolerance=1E-6)
  p2 = gdspy.copy(p)
  p2.mirror([0,1])
  p3 = gdspy.boolean(p, p2, 'or', precision=1e-6, max_points=1e6)
  p4 = gdspy.copy(p3)
  p4.rotate(pi)
  p5 = gdspy.boolean(p3, p4, 'or', precision=1e-6, max_points=1e6)
  return [p5]

def part23d2(
  lengths = [1, 4e-1, 8e-2], widths = [1, 1e-1, 1e-2, 0.5e-2],
  gapFrac = 0.1, pathWidth = 1e-3, offset = 5e-3,
):
  ws = [widths[i]-widths[i+1] for i in range(len(widths)-1)]
  size = np.sum(lengths[:-1]) * (1+2*gapFrac) + lengths[-1] \
    + ws[-1]/2 + offset
  c = gdspy.Curve(0, -size, tolerance=1e-6).h(-widths[0]/2)
  for i, l in enumerate(lengths):
    dy = l * gapFrac
    dx = ws[i] * 0.5
    if i < len(lengths)-1:
      c.v(l).c(0,dy, dx,dy, dx,dy*2)
    else:
      c.v(l).arc(dx, pi, pi/2).H(0)
  p = gdspy.Polygon(c.get_points())
  p2 = gdspy.copy(p).mirror([0,1])
  p3 = gdspy.boolean(p, p2, 'or', precision=1e-6, max_points=1e6)
  p4 = gdspy.copy(p3).rotate(pi)
  p5 = gdspy.boolean(p3, p4, 'or', precision=1e-6, max_points=1e6)
  return [p3, p4]

def join(a,b): return gdspy.boolean(a, b, 'or', precision=1e-6, max_points=1e6)
def cut(a,b): return gdspy.boolean(a, b, 'not', precision=1e-6, max_points=1e6)

def part23d3(
  lengths=[1, 4e-1, 8e-2, 1e-2], 
  widths=[1, 1e-1, 1e-2, 0.5e-2],
  jumpRadius = 1, jumpWidth = 1e-2,
  borderWidth = 1e-3,
):
  ls, ws, jr, jw = lengths, widths, jumpRadius, jumpWidth
  bw = borderWidth
  c = gdspy.Curve(0, -np.sum(ls), tolerance=1e-6).H(-ws[0]/2)
  for i, l in enumerate(ls[:-1]):
    if i < len(ls)-2: 
      dx = (ws[i] - ws[i+1]) / 2
      c.v(l*0.9).c(0, l*0.05, dx, l*0.05, dx, l*0.1)
    else:
      w = ws[i] / 2
      c.v(l - w).c(0, w, 0, w, w, w)  
  p = gdspy.Polygon(c.get_points())
  p2 = gdspy.copy(p).mirror([0,1])
  p3 = join(p, p2)
  p4 = gdspy.copy(p3).rotate(pi)
  p5 = join(p3, p4)
  # jump
  jump = gdspy.Path(jw, [0,jr]).arc(jr, pi*0.5, pi*1.5, tolerance=1e-6)
  p6 = join(p5, jump)
  # border
  p7 = gdspy.offset(p6, bw, precision=1e-6, max_points=1e6)
  p7 = cut(p7, gdspy.Rectangle([-ws[-2], -ls[-1]], [ws[-2], ls[-1] ]))
  p8 = cut(p7, p6)
  p6.layers = [2]
  return [p6, p8]

def part4567(length = 1e-2):
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

def combine1():
  return part23d3() + part4567(1e-2)

if __name__ == '__main__':
  parts = [combine1]
  lib = gdspy.GdsLibrary()
  for i, part in enumerate(reversed(parts)):
    c1 = lib.new_cell('c%d' % i)
    c1.add(part()) 
    c1.add(gdspy.Label('o', [0,0]))
    c1.write_svg('./try/part %d.svg' % i)
  lib.write_gds('try.gds')
  gdspy.LayoutViewer()