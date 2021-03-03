
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

def part23e():
  # jump
  pass

def part4567():
  w1 = 0.2
  p1 = gdspy.FlexPath([(0.5,-1), (-0.4,-1), (-0.4,1), (0.5,1)], w1)
  rect1 = gdspy.Rectangle((0.5, -1-w1/2), (-0.4-0.3, 1+w1/2))
  p2 = gdspy.boolean(rect1, p1, 'not')
  p2.layers = [1, 2]
  return [p1, p2]

if __name__ == '__main__':
  parts = [part1, part23a, part23b, part23c, part23d, part4567]
  lib = gdspy.GdsLibrary()
  for i, part in enumerate(reversed(parts)):
    c1 = lib.new_cell('c%d' % i)
    c1.add(part()) 
    c1.write_svg('./try/part %d.svg' % i)
  lib.write_gds('try.gds')
  gdspy.LayoutViewer()