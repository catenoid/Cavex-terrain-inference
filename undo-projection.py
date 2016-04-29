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
  (-3,3)
] # list of (a,b)

isEdgeAttached = {
  (0,1) : True,
  (1,2) : False, 
  (2,3) : True,
  (0,3) : True,
  (3,4) : True,
  (4,5) : True,
  (2,5) : False,
  (5,6) : False,
  (6,7) : True,
  (4,7) : True,
  (6,9) : False,
  (8,9) : False,
  (7,8) : True,
  (8,10) : False,
  (10,11) : False,
  (0,11) : True
} # list of (v1,v2), attached boolean

# Say all edges were unattached (floating terrain piece), then face data required
# This bit needs work
faces = [
  ([0,1,2,3], 'B'),
  ([2,6,5,4], 'W'),
  ([5,7,8,9], 'B'),
  ([8,10,11,12], 'W'),
  ([3,4,9,12,13,14,15], 'G')
]

print "Building vertex dictionary:"

contiguousVertices = []
for v in verts2D:
  contiguousVertices.append([])

for (v1,v2) in isEdgeAttached.keys():
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
  240 : (1,0,0),
  300 : (0,-1,-1)
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
  120 : (-1,0,-1),
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

def displacement(vertex1, vertex2):
  delta = subtract2(verts2D[vertex1], verts2D[vertex2])
  axisAngle = azimuth(delta)
  attached = isEdgeAttached[(vertex1, vertex2)]
  if (attached):
    return attachedEdgeToVector3[axisAngle]
  else:
    edge = f(vertex1, vertex2) # but dictionaries are unordered. we need an array of edge
    return unattachedEdgeToVector3(axisAngle, faceColour(edge))

# verts3D[0] = offset
offset = (0,0,0)

print "Building 3d Verts array:"
verts3D = []
for v in verts2D: 
  verts3D.append(0)

print verts3D

verts3D[0] = offset
seenVerts = []
def DFS(v1):
  print "DFS meets ", v1
  seenVerts.append(v1)
  for v2 in contiguousVertices[v1]:
    print "Crossed edge to", v2
    if (v2 not in seenVerts):
      verts3D[v2] = add3(verts3D[v1], displacement(v1, v2))
      print "Inserted ", v2, "into 3d verts"
      DFS(v2)
    else:
      print "Already seen ", v2, " no recurse"

DFS(0)

for vector in verts3D:
  print vector

