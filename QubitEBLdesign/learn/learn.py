
import gdspy
import numpy as np 

pi = np.pi 
lib1 = gdspy.GdsLibrary()
cell1 = lib1.new_cell('FIRST') 

layer0 = {"layer": 0, "datatype": 7}
layer1 = {"layer": 1, "datatype": 3}
layer2 = {"layer": 2, "datatype": 3}
layer3 = {"layer": 3, "datatype": 3}

rect1 = gdspy.Rectangle([0,0], [2,1])

points1 = [(0, 0), (2, 2), (2, 6), (-6, 6), (-6, -6), (-4, -4), (-4, 4), (0, 4)]
poly1 = gdspy.Polygon(points1)

circle1 = gdspy.Round([0,0], 2, tolerance=0.1) 

ellipse1 = gdspy.Round([4,0], [1,2], tolerance=1e-4)

arc1 = gdspy.Round(
  [2,4], 2, tolerance=0.01,
  inner_radius=1, 
  initial_angle=-0.2*pi, final_angle=1.2*pi
)

c1 = gdspy.Curve(0,0).L(1,0, 2,1, 2,2, 0,2)
p1 = gdspy.Polygon(c1.get_points())

c2 = gdspy.Curve(3,1).l(1,0, 2,1, 2,2, 0,2)
p2 = gdspy.Polygon(c2.get_points())

c3 = gdspy.Curve(0,2).l(4 * np.exp(1j*pi/6))
c3.arc([4, 2], 0.5*pi, -0.5*pi)
p3 = gdspy.Polygon(c3.get_points())

c4 = gdspy.Curve(0,0).c(1,0, 1,1, 2,1)
c4.s(1,1, 0,1).S(np.exp(1j*pi/6), 0,0)
p4 = gdspy.Polygon(c4.get_points(), **layer1)

c5 = gdspy.Curve(5,3).Q(3,2, 3,0, 5,0, 4.5,1).T(5,3)
p5 = gdspy.Polygon(c5.get_points(), **layer2)

c6 = gdspy.Curve(0,3).i([(1,0), (2,0), (1,-1)], cycle=True)
p6 = gdspy.Polygon(c6.get_points(), **layer3)
p6.rotate(pi/2, center=[0,3])
p6.scale(1, 0.5)

# skip References https://gdspy.readthedocs.io/en/stable/gettingstarted.html#references

path1 = gdspy.Path(1, [0,0])
path1.segment(4, pi/2)
path1.turn(2, -pi/2)
path1.segment(1)
path1.turn(3, -pi)

path2 = gdspy.Path(0.5, [0,0])
path2.bezier([(0,5), (5,5), (5,10)])
def spiral(t):
  r = 4 - 3*t
  theta = 5*t*pi
  x = r*np.cos(theta) - 4
  y = r*np.sin(theta)
  return (x,y)
path2.parametric(spiral)

path3 = gdspy.Path(0.1, [-5.5,3], 
  number_of_paths=3, distance=1.5)
path3.segment(2, 3*pi/2, final_width=0.5)
path3.bezier([(0,-2), (1,-3), (3,-3)], final_distance=0.75)
path3.parametric(
  lambda u: (5*u, 0),
  lambda u: (1, 0),
  final_width = lambda u: 0.4+0.1*np.cos(10*pi*u),
  number_of_evaluations=256
)
path3.turn(3, pi/2)
path3.segment(2, final_width=1, final_distance=1.5)

fp1 = gdspy.FlexPath(
  [(0, 0), (3, 0), (3, 2), (5, 3), (3, 4), (0, 4)], 
  1, gdsii_path=True
)
fp1.smooth([(0,2), (2,2), (4,3), (5,1)], relative=True)

fp2 = gdspy.FlexPath(
  [(12,0), (8,0), (8,3), (10,2)],
  width=[0.2, 0.3, 0.4],
  offset=0.5,
  ends=['extended', 'flush', 'round'],
  corners=['bevel', 'miter', 'round']
)
fp2.arc(2, -pi/2, pi/2)

# skip broken and pointy

points2 = [(0, 0), (0, 10), (20, 0), (18, 15), (8, 15)]
fp4 = gdspy.FlexPath(
  points2, 0.5, gdsii_path=True, 
  corners='circular bend', bend_radius=5, **layer1
)
fp4b = gdspy.FlexPath(points2, 0.5, gdsii_path=True, **layer2)

rp1 = gdspy.RobustPath(
  [50,0], 
  width=[2,0.5,1,1], 
  offset=[0,0,-1,1],
  ends=['extended', 'round', 'flush', 'flush'],
  layer=[0,2,1,1]
)
rp1.segment([45,0])
rp1.segment(
  [5,0], 
  width=[lambda u: 2+16*u*(1-u), 0.5, 1, 1],
  offset=[
    0,
    lambda u: 8*u*(1-u)*np.cos(12*pi*u),
    lambda u: -1 - 8*u*(1-u),
    lambda u:  1 + 8*u*(1-u),
  ]
)
rp1.segment([0,0])
rp1.smooth(
  [(5,10)],
  angles=[pi, 0],
  width=0.5,
  offset=[-1/4, 1/4, -3/4, 3/4]
)
rp1.parametric(
  lambda u: np.array( [45*u, 4*np.sin(6*pi*u)] ),
  offset=[
    lambda u: -0.25 * np.cos(24*pi*u),
    lambda u:  0.25 * np.cos(24*pi*u),
    -0.75,
    0.75
  ]
)

t1 = gdspy.Text('fuck', 4, [0,0])
bb1 = np.array(t1.get_bounding_box())
rect2 = gdspy.Rectangle(bb1[0] - 1, bb1[1] + 1)
rect2 = gdspy.boolean(rect2, t1, 'not')

ring1 = gdspy.Round((-6, 0), 6, inner_radius=4)
ring2 = gdspy.Round((0, 0), 6, inner_radius=4)
ring3 = gdspy.Round((6, 0), 6, inner_radius=4)
slices1 = gdspy.slice(ring1, -3, axis=0)
slices2 = gdspy.slice(ring2, [-3, 3], axis=0)
slices3 = gdspy.slice(ring3, 3, axis=0)

rect1 = gdspy.Rectangle((-4, -4), (1, 1))
rect2 = gdspy.Rectangle((-1, -1), (4, 4))
outer = gdspy.offset([rect1, rect2], -0.5, join_first=True, layer=1)

p7 = gdspy.Path(2, [-3,-2])
p7.segment(4, 0)
p7.turn(2, pi/2).turn(2, -pi/2)
p7.segment(4)
p7join = gdspy.boolean(p7, None, 'or', max_points=0)
p7join.translate(0,-5)
p7.fillet(0.5)
p7join.fillet(0.5)

def add(li = []): [cell1.add(i) for i in li]
def pointLabel(xy): return gdspy.Label(str(xy), xy)
def addGrid(size=10):
  a = np.arange(-size, size)
  add([pointLabel([x,y]) for x in a for y in a])

add([p7,p7join])
lib1.write_gds('learn.gds')
gdspy.LayoutViewer()
