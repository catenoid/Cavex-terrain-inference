import triangulator

sampleX = [(0, 0, 0), (0, 0, -3), (0, 1, -2), (0, 2, -2), (0, 2, -1), (0, 1, -1), (0, 1, 0)]
sampleY = [(-2, 2, -1), (0, 2, -1), (0, 2, -2), (-2, 2, -2)]
sampleZ = [(0, 1, -1), (0, 2, -1), (-2, 2, -1), (-2, 1, -1)]

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
  
  def getTriangles(to2D, to3D):
    verts2D = map(to2D, verts3D)
    verts2D.reverse()
    return map(to3D, triangulator.triangulate(verts2D))

  if inXplane:
    verts2D = map(removeX, verts3D)
    verts2D.reverse()
    triangles = map(distributeX, triangulator.triangulate(verts2D))
  elif inYplane:
    verts2D = map(removeY, verts3D)
    triangles = map(distributeY, triangulator.triangulate(verts2D))
  elif inZplane:
    verts2D = map(removeZ, verts3D)
    verts2D.reverse()
    triangles = map(distributeZ, triangulator.triangulate(verts2D))
  
  return triangles
