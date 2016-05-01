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
  False # The coplanar cut must be unattached or else the algorithm infers (1,0,1) incorrectly as (0,-1,0)
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

adjacentVertices = []
for v in verts2D:
  adjacentVertices.append([])

for (v1,v2) in edges.keys():
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

# There can be two face colours for an unattached edge if there is a plane behind it.
# This only finds the first. I need the facility to find the foreground face and the background face.
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

def getEdge(v1,v2):
  return edges[(min(v1,v2), max(v1,v2))]

def displacement(v1, v2):
  delta = subtract2(verts2D[v2], verts2D[v1])
  scaleFactor = length(delta)
  axisAngle = azimuth(delta)
  edge = getEdge(v1,v2) 
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
seen = []

def foregroundTraversal(v1):
  seen.append(v1)
  unattachedEdgeCount = 0
  for v2 in adjacentVertices[v1]:
    edge = getEdge(v1,v2) 
    if (!isEdgeAttached[edge]):
      unattachedEdgeCount += 1
    if (v2 not in seenVerts):
      verts3D[v2] = add3(verts3D[v1], foregroundDisplacement(v1, v2))
      foregroundTraversal(v2)
  if (unattachedEdgeCount == 1):
    backgroundTraversal(v1)

# Required for vertices 2,5,6,9,8,10
# I swear this is going to drive me fucking insane. Ultimatum: For now, ONLY TRY AND SUPPORT LINEAR UNATTACHED GRAPHS
# split branching paths into lines. A connecting triple with begin with the aliasedVert3D for its v1
# because of the way the projection works, the upper face is the background face
# lower face is foreground
# how about when doing the foreground traversal, build up the unattached edge graph
# then break it up into paths/segments/lines whatever these things are called
# Walk them, starting with the backgorund vertex (ie the new one) if at a join...
def backgroundTraversal(v1):
  path = []
  aliasedVerts3D = [verts3D[v1]]
  traceProjectedEdges(v1)
  vertsToAdd = aliasedVerts3D[1:-1]
  firstNewVertex = len(verts3D) # is it possible to have no new vertices? if so this needs fixing
  lastNewVertex = firstNewVertex + len(vertsToAdd) - 1
  pathVertices = range(firstNewVertex, lastNewVertex)
  connect = lambda i : (i,i+1)
  pathEdges = map(connect, pathVertices))
  edgesToAdd = (v1, firstNewVertex) + pathEdges + (lastNewVertex, path[-1])
  # faces to change
  # replace the edge list segment for the background face with edgesToAdd
  verts3D.append(vertsToAdd)
  # edges is a dictionary, not a list (why... why... god why)

  def traceProjectedEdges(v1):
    path.append(v1)
    for v2 in adjacentVertices[v1]:
      if (!isEdgeAttached[getEdge(v1,v2)] and v2 not in path):
        aliasedVerts3D.append(add3(aliasedVerts3D[-1], backgroundDisplacement(v1, v2)))
        traceProjectedEdges(v2)
        break

foregroundTraversal(0)

for vector in verts3D:
  print vector
