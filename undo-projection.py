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

edges = {
  (0,1) : 0,
  (1,2) : 1,
  (2,3) : 2,
  (0,3) : 3,
  (3,4) : 4,
  (4,5) : 5,
  (2,5) : 6,
  (5,6) : 7,
  (6,7) : 8,
  (4,7) : 9,
  (6,9) : 10,
  (8,9) : 11,
  (7,8) : 12,
  (8,10) : 13,
  (10,11) : 14,
  (0,11) : 15,
  (12,13) : 16,
  (13,14) : 17,
  (14,15) : 18,
  (12,15) : 19,
  (0,12) : 20 # Cut in ground plane
} # the smaller vertex must be listed first

isEdgeAttached = [
  True,
  False, 
  True,
  True,
  True,
  True,
  False,
  False,
  True,
  True,
  False,
  False,
  True,
  False,
  False,
  True,
  False,
  False,
  False,
  False,
  False # This requires some thinking
]

# Say all edges were unattached (floating terrain piece), then face data required
# This bit needs work, because once one face is known, the others can be inferred depending on the edge crossed
faces = [
  ([0,3,2,1], 'B'),
  ([2,4,5,6], 'W'),
  ([5,9,8,7], 'B'),
  ([8,12,11,10], 'W'),
  ([3,15,14,13,12,9,4], 'G'),
  ([19,18,17,16,20,0,1,6,7,10,11,13,14,15,20], 'W')  # has a hole in
]

contiguousVertices = []
for v in verts2D:
  contiguousVertices.append([])

for (v1,v2) in edges.keys():
  contiguousVertices[v1].append(v2)
  contiguousVertices[v2].append(v1)

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

def faceColour(searchedEdge):
  for (edgeList, colour) in faces:
    for edge in edgeList:
      if (searchedEdge == edge):
        return colour

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
  'W' : coplanarYToVector3,
  'G'  : coplanarXToVector3,
  'B' : coplanarZToVector3
}

def unattachedEdgeToVector3(axisAngle, colour):
  return colourToDisplacements[colour][axisAngle]

def displacement(v1, v2):
  delta = subtract2(verts2D[v2], verts2D[v1])
  scaleFactor = length(delta)
  axisAngle = azimuth(delta)
  edge = edges[(min(v1,v2), max(v1,v2))] 
  if (isEdgeAttached[edge]):
    unit = attachedEdgeToVector3[axisAngle]
  else:
    unit = unattachedEdgeToVector3(axisAngle, faceColour(edge))
  return scale(unit, scaleFactor)

# verts3D[0] = offset
offset = (0,0,0)

verts3D = []
for v in verts2D: 
  verts3D.append(0)

verts3D[0] = offset
seenVerts = []
def DFS(v1):
  seenVerts.append(v1)
  for v2 in contiguousVertices[v1]:
    if (v2 not in seenVerts):
      verts3D[v2] = add3(verts3D[v1], displacement(v1, v2))
      DFS(v2)

DFS(0)

for vector in verts3D:
  print vector

