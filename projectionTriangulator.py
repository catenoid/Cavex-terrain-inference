import numpy as np
import polygon_triangulate as pt

sampleX = [(0, 0, 0), (0, 0, -3), (0, 1, -2), (0, 2, -2), (0, 2, -1), (0, 1, -1), (0, 1, 0)]
sampleY = [(-2, 2, -1), (0, 2, -1), (0, 2, -2), (-2, 2, -2)]
sampleZ = [(0, 1, -1), (0, 2, -1), (-2, 2, -1), (-2, 1, -1)]

def triangulate2D(verts2D):
  xs = []
  ys = []
  for x,y in verts2D:
    xs.append(x)
    ys.append(y)
  indices = pt.polygon_triangulate(len(verts2D), np.array(xs), np.array(ys))
  polygon = []
  for triangle in np.transpose(indices):
    v1,v2,v3 = triangle
    polygon.append((verts2D[v1], verts2D[v2], verts2D[v3]))
  return polygon

removeX = lambda (x,y,z) : (y,z)
removeY = lambda (x,y,z) : (x,z)
removeZ = lambda (x,y,z) : (x,y)

def triangulate(verts3D):
  # Find the axis plane in which the polygon lies
  inXplane = True
  inYplane = True
  inZplane = True
  
  (x1,y1,z1) = verts3D[0]
  for (x2,y2,z2) in verts3D[1:]:
    if (x1 != x2):
      inXplane = False
    if (y1 != y2):
      inYplane = False
    if (z1 != z2):
      inZplane = False
    (x1,y1,z1) = (x2,y2,z2)
  
  x,y,z = verts3D[0]
  distributeX = lambda ((y1,z1), (y2,z2), (y3,z3)) : ((x,y1,z1), (x,y2,z2), (x,y3,z3))
  distributeY = lambda ((x1,z1), (x2,z2), (x3,z3)) : ((x1,y,z1), (x2,y,z2), (x3,y,z3))
  distributeZ = lambda ((x1,y1), (x2,y2), (x3,y3)) : ((x1,y1,z), (x2,y2,z), (x3,y3,z))
  
  if inXplane:
    verts2D = map(removeX, verts3D)
    triangles = map(lambda (v1,v2,v3) : (v1,v3,v2), map(distributeX, triangulate2D(verts2D)))
  elif inYplane:
    verts2D = map(removeY, verts3D)
    verts2D.reverse()
    triangles = map(distributeY, triangulate2D(verts2D))
  elif inZplane:
    verts2D = map(removeZ, verts3D)
    triangles = map(lambda (v1,v2,v3) : (v1,v3,v2), map(distributeZ, triangulate2D(verts2D)))
  
  return triangles

if (__name__ == "__main__"):
  print "Triangulating sample plots in orthogonal axis planes"
  print triangulate(sampleX)
  print triangulate(sampleY)
  print triangulate(sampleZ)
