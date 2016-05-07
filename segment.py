# The visible faces of a set of two steps
sampleVerts3D = [
  ( 0, 0,  0),
  ( 0, 0, -2),
  ( 0, 2, -2),
  ( 0, 2, -1),
  ( 0, 1, -1),
  ( 0, 1,  0),
  (-2, 2, -2),
  (-2, 2, -1),
  (-2, 1, -1),
  (-2, 1,  0),
  (-2, 0,  0),
]

# Faces are directed clockwise
sampleDirectedEdges = [
# "L-shape"
  (0, 1),
  (1, 2),
  (2, 3),
  (3, 4),
  (4, 5),
  (5, 0),
# Top of upper step
  (2, 6),
  (6, 7),
  (7, 3),
  (3, 2),
# Side of upper step	
  (7, 8),
  (8, 4),
  (4, 3),
  (3, 7),
# Top of lower step
  (8, 9),
  (9, 5),
  (5, 4),
  (4, 8),
# Side of lower step
  (5, 9),
  (9, 10),
  (10, 0),
  (0, 5),
]

def subtract3(v1,v2):
  x1,y1,z1 = v1
  x2,y2,z2 = v2
  return (x1-x2, y1-y2, z1-z2)

def signedUnit(n):
  return n/abs(n) if (n != 0) else 0

def normalisedCrossProduct(delta1, delta2):
  d1_x, d1_y, d1_z = delta1
  d2_x, d2_y, d2_z = delta2
  x = d1_y * d2_z - d1_z * d2_y
  y = d1_z * d2_x - d1_x * d2_z
  z = d1_x * d2_y - d1_y * d2_x
  return (signedUnit(x), signedUnit(y), signedUnit(z))

def separateIntoPolygons(verts3D, directedEdges):
  edgeIndices = range(len(directedEdges))
  def doesEdgeFollow(i):
    v_start, v_end = directedEdges[i]
    return (lambda j : directedEdges[j][0] == v_end)
  edgesFollowing = [ filter(doesEdgeFollow(i), edgeIndices) for i in edgeIndices ]
  print "edgesFollowing",edgesFollowing

  def normalTo(e1,e2):
    v1,v2 = directedEdges[e1]
    v3 = directedEdges[e2][1]
    d1 = subtract3(verts3D[v2], verts3D[v1]) 
    d2 = subtract3(verts3D[v3], verts3D[v2]) 
    return normalisedCrossProduct(d2,d1)

  def completeFace(e1,e2):
    print "complete face e1",e1,"e2",e2
    face = [e1,e2]
    faceNormal = normalTo(e1,e2)
    print "face normal", faceNormal
    def addNextCoplanarEdge(edge):
      faceContinues = False
      for e in edgesFollowing[edge]:
        if (not faceContinues):
          if (normalTo(e,edge) == faceNormal and e not in face):
            faceContinues = True
      if (faceContinues):
        print "next edge is",e
        face.append(e)
        addNextCoplanarEdge(e)

    addNextCoplanarEdge(e2)
    return face

  polygons = []

  def clipFace(es):
    if (len(es) >= 3):
      print "clipface with list",es
      e1 = es[0]
      e2 = edgesFollowing[e1][0]
      polygon = completeFace(e1, e2)
      print "polygon is",polygon
      polygons.append(polygon)
      clipFace(filter(lambda edge : edge not in polygon, es))

  clipFace(edgeIndices)
  return polygons

print "Result:"
print separateIntoPolygons(sampleVerts3D, sampleDirectedEdges)
