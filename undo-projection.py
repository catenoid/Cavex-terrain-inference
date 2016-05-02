verts2D = [
  (0,0),
  (3,0),
  (2,1),
  (0,1),
  (-1,2),
  (1,2),
  (1,3),
  (-1,3),
  (-2,4),
  (0,4),
  (-2,3),
  (-3,3),
  (0,-1),
  (6,-1),
  (0,5),
  (-6,5)
] # list of (a,b)

AE = {
  (0,1) : 0,
  (2,3) : 2,
  (0,3) : 3,
  (3,4) : 4,
  (4,5) : 5,
  (6,7) : 8,
  (4,7) : 9,
  (7,8) : 12,
  (0,11) : 15,
}
#  (12,13) : 16,
#  (13,14) : 17,
#  (14,15) : 18,
#  (12,15) : 19,
#  (0,12) : 20 # Cut in ground plane
#} # the smaller vertex must be listed first

adjacentVertices = [[] for v in verts2D]
for (v1,v2) in AE.keys():
  adjacentVertices[v1].append(v2)
  adjacentVertices[v2].append(v1)

def add3(v1,v2):
  v1_x, v1_y, v1_z = v1
  v2_x, v2_y, v2_z = v2
  return (v1_x + v2_x, v1_y + v2_y, v1_z + v2_z) 

def subtract2(v1,v2):
  v1_x, v1_y = v1
  v2_x, v2_y = v2
  return (v1_x - v2_x, v1_y - v2_y) 

def normalise(x):
  if (x == 0):
    return 0
  else:
    return x/abs(x)

isoCoordNormToAzimuth = {
  (0,1) : 0,
  (1,0) : 60,
  (1,-1) : 120,
  (0,-1) : 180,
  (-1,0) : 240,
  (-1,1) : 300
}

def length(vector2):
  x,y = vector2
  if (x == 0):
    return abs(y)
  else:
    return abs(x)

def scale(vector3, c):
  x,y,z = vector3
  return (c*x,c*y,c*z)

def azimuth(vector2):
  x,y = vector2
  return isoCoordNormToAzimuth[(normalise(x), normalise(y))]

attachedEdgeToVector3 = {
  0   : (0,1,0),
  60  : (-1,0,0),
  120 : (0,0,1),
  180 : (0,-1,0),
  240 : (1,0,0),
  300 : (0,0,-1)
}

coplanarXToVector3 = {
  0   : (0,1,0),
  60  : (0,1,1),
  120 : (0,0,1),
  180 : (0,-1,0),
  240 : (0,-1,-1),
  300 : (0,0,-1)
}

coplanarYToVector3 = {
  0   : (-1,0,-1),
  60  : (-1,0,0),
  120 : (0,0,1),
  180 : (1,0,1),
  240 : (1,0,0),
  300 : (0,0,-1)
}

coplanarZToVector3 = {
  0   : (0,1,0),
  60  : (-1,0,0),
  120 : (-1,-1,0),
  180 : (0,-1,0),
  240 : (1,0,0),
  300 : (1,1,0)
}

colourToDisplacements = {
  'w' : coplanarYToVector3,
  'g' : coplanarXToVector3,
  'b' : coplanarZToVector3
}

def unattachedEdgeToVector3(axisAngle, colour):
  return colourToDisplacements[colour][axisAngle]

def getEdge(v1,v2):
  return edges[(min(v1,v2), max(v1,v2))]

def attachedDisplacement(delta):
  scaleFactor = length(delta)
  axisAngle = azimuth(delta)
  unit = attachedEdgeToVector3[axisAngle]
  return scale(unit, scaleFactor)

def coplanarDisplacement(delta, colour):
  scaleFactor = length(delta)
  axisAngle = azimuth(delta)
  unit = unattachedEdgeToVector3(axisAngle, colour)
  return scale(unit, scaleFactor)

verts3D = [0 for v in verts2D]
offset = (0,0,0)
verts3D[0] = offset
seen = []

# we only need to traverse edges that are noton the bounds of the zero area shape...
def foregroundTraversal(v1):
  seen.append(v1)
  for v2 in adjacentVertices[v1]:
    if (v2 not in seen):
      delta = subtract2(verts2D[v2], verts2D[v1])
      verts3D[v2] = add3(verts3D[v1], attachedDisplacement(delta))
      foregroundTraversal(v2)

print "Performing foreground traversal"
foregroundTraversal(0)
for vector in verts3D:
  print vector

# The unattached form a closed face with no area
# When walking this face, use coplanar calculations with the outside colour
print "performing background traversal"

UEColours = [ # directed CW
  ((11,10), 'w'),
  ((10,8), 'w'),
  ((8,9), 'w'),
  ((9,6), 'w'),
  ((6,5), 'w'),
  ((5,2), 'w'),
  ((2,1), 'w'),
  ((1,2), 'b'),
  ((2,5), 'w'),
  ((5,6), 'b'),
  ((6,9), 'w'),
  ((9,8), 'w'),
  ((8,10), 'g'),
  ((10,11), 'g')
]

def backgroundTraversal():
  pathDeltas = []
  for ((v1,v2), colour) in UEColours:
    delta = subtract2(verts2D[v2], verts2D[v1])
    pathDeltas.append(coplanarDisplacement(delta, colour))
  aliasedVerts3D = []
  v = verts3D[11] # start on an edge with only one unattached
  for dv in pathDeltas:
    nextVertex = add3(v,dv)
    aliasedVerts3D.append(nextVertex)
    v = nextVertex
  for v in aliasedVerts3D:
    print v

backgroundTraversal()
  #vertsToAdd = aliased[1:-1]
  #firstNewVertex = len(verts3D)
  #lastNewVertex = firstNewVertex + len(vertsToAdd) - 1
  #pathVertices = range(firstNewVertex, lastNewVertex)
  #connect = lambda i : (i,i+1)
  #pathEdges = map(connect, pathVertices)
  #edgesToAdd = (v1, firstNewVertex) + pathEdges + (lastNewVertex, path[-1])
  # faces to change: replace the edge list segment for the background face with edgesToAdd

