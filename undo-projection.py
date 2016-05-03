# Representing a drawing on isometric paper:
# Orient the paper with one set of graticules vertically upright
# (Terminology: azimuth = degrees clockwise from "north," in this case, towards the top of the page)

# Representing 2D coordinates:
# +Primary axis: azimuth = 60
# +Secondary axis: azimuth = 0
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
#  (0,-1),
#  (6,-1),
#  (0,5),
#  (-6,5),
]

# Representing connections between points on isometric paper with a vertex pair (as indexed into verts2D)
attachedEdges = [
  (0,1),
  (2,3),
  (0,3),
  (3,4),
  (4,5),
  (6,7),
  (4,7),
  (7,8),
  (0,11),
]

adjacentVertices = [[] for v in verts2D]
for (v1,v2) in attachedEdges:
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

# Converting a unit change in the isometric coordinate system (as used in verts2D), to an angle direction in degrees
deltaToAzimuth = {
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
  return deltaToAzimuth[(normalise(x), normalise(y))]

# Moving coplanar in 3D space:
# Conversion from the azimuth (from the isometric paper diagram), to the equivalent (x,y,z) displacement
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

# Colours
# White 'w': +y normal
# Grey 'g': +x normal
# Black 'b': +z normal
# (Legacy notation from drafting on paper and shading in, to replace)
coplanarDisplacements = {
  'w' : coplanarYToVector3,
  'g' : coplanarXToVector3,
  'b' : coplanarZToVector3
}

def coplanarDisplacement(delta, colour):
  scaleFactor = length(delta)
  axisAngle = azimuth(delta)
  unit = coplanarDisplacements[colour][axisAngle]
  return scale(unit, scaleFactor)

# Moving along concave/cavex edges in 3D space
# Conversion from the azimuth (from the isometric paper diagram), to the equivalent (x,y,z) displacement
attachedEdgeToVector3 = {
  0   : (0,1,0),
  60  : (-1,0,0),
  120 : (0,0,1),
  180 : (0,-1,0),
  240 : (1,0,0),
  300 : (0,0,-1)
}

def attachedDisplacement(delta):
  scaleFactor = length(delta)
  axisAngle = azimuth(delta)
  unit = attachedEdgeToVector3[axisAngle]
  return scale(unit, scaleFactor)

def delta(vertexPair):
  v1,v2 = vertexPair
  return subtract2(verts2D[v2], verts2D[v1])

# The 2D coordinate (0,0) will be anchored to 3D coordinate 'offset'
offset = (0,0,0)
verts3D = ['undef' for v in verts2D]
verts3D[0] = offset

seen = []
def foregroundTraversal(v1):
  seen.append(v1)
  for v2 in adjacentVertices[v1]:
    if (v2 not in seen):
      verts3D[v2] = add3(verts3D[v1], attachedDisplacement(delta((v1,v2))))
      foregroundTraversal(v2)

foregroundTraversal(0)

# Dealiasing vertices along unattached edge paths
# To do: Ground plane. Colours are interiors, whereas those along the unattached path are exterior

unattachedPaths = [ # directed CW, colour on outside
[ # Back of steps
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
]

def aliasedDeltaPath(path):
  deltas3D = []
  for (vertexPair, colour) in path:
    deltas3D.append(coplanarDisplacement(delta(vertexPair), colour))
  return deltas3D

def dealias(path):
  dealiasedVerts = []
  v = verts3D[path[0][0][0]] # AAAAHHH
  for dv in aliasedDeltaPath(path):
    nextVertex = add3(v,dv)
    dealiasedVerts.append(nextVertex)
    v = nextVertex
  return dealiasedVerts

edges = attachedEdges

for path in unattachedPaths:
  vertsToAdd = dealias(path)
  firstNewVertex = len(verts3D) - 1
  lastNewVertex = firstNewVertex + len(vertsToAdd)
  pathVertices = range(firstNewVertex, lastNewVertex)
  connect = lambda i : (i,i+1)
  edgesToAdd = map(connect, pathVertices)
  verts3D += vertsToAdd
  edges += edgesToAdd

# Alias vertices that refer to the same 3D coordinate
# This happens when an unattached edge path meets an attached edge, and the vertex is calculated twice
duplicates = {} # { (x,y,z) : [ vertices that refer to that coordinate] }

for oldIndex in range(len(verts3D)):
  v = verts3D[oldIndex]
  if (v != 'undef'):
    if (duplicates.__contains__(v)):
      duplicates[v].append(oldIndex)
    else:
      duplicates[v] = [oldIndex]

nonDuplicatedVerts3D = duplicates.keys()

# Renumber the edges to according to nonDuplicatedVerts3D
oldToNewIndex = ['undef' for v in verts3D]
for newIndex in range(len(nonDuplicatedVerts3D)):
  v = nonDuplicatedVerts3D[newIndex]
  oldIndices = duplicates[v]
  for i in oldIndices:
    oldToNewIndex[i] = newIndex

newEdges = []
for (v1,v2) in edges:
  newEdges.append((oldToNewIndex[v1], oldToNewIndex[v2]))

print "Vertices:"
for v in nonDuplicatedVerts3D:
  print v
print "Edges:"
for e in newEdges:
  print e
