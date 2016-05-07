import segment
import triangulator

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
#  (0,-1),  # Bounding vertices of the ground plane
#  (6,-1),  # Requires some thought
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

def orthogonalDisplacement(delta):
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
      verts3D[v2] = add3(verts3D[v1], orthogonalDisplacement(delta((v1,v2))))
      foregroundTraversal(v2)

foregroundTraversal(0)

# Dealiasing vertices along unattached edge paths
# To do: Ground plane. Colours are interiors, whereas those along the unattached path are exterior

unattachedPaths = [ # directed CW, colour on outside
# Update: When segmenting into polygons, I assume hidden edges are directed CCW
#         Reworking required
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
  return [coplanarDisplacement(delta(vertexPair), colour) for (vertexPair, colour) in path]

def dealias(path):
  dealiasedVerts = []
  v = verts3D[path[0][0][0]] # AAAAHHH
  for dv in aliasedDeltaPath(path):
    nextVertex = add3(v,dv)
    dealiasedVerts.append(nextVertex)
    v = nextVertex
  return dealiasedVerts

edges = attachedEdges
vertexLoops = []

for path in unattachedPaths:
  vertsToAdd = dealias(path)
  firstNewVertex = len(verts3D) - 1
  lastNewVertex = firstNewVertex + len(vertsToAdd)
  pathVertices = range(firstNewVertex, lastNewVertex)
  edgesToAdd = [ (i,i+1) for i in pathVertices ]
  verts3D += vertsToAdd
  edges += edgesToAdd
  vertexLoops.append(pathVertices)

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

uniqueVerts3D = duplicates.keys()

# Renumber the edges to according to uniqueVerts3D
oldToNewIndex = ['undef' for v in verts3D]
for newIndex in range(len(uniqueVerts3D)):
  v = uniqueVerts3D[newIndex]
  oldIndices = duplicates[v]
  for i in oldIndices:
    oldToNewIndex[i] = newIndex

newEdges = [ (oldToNewIndex[v1], oldToNewIndex[v2]) for (v1,v2) in edges ]
hiddenTerrainContours = map(lambda loop : map(lambda v : oldToNewIndex[v], loop), vertexLoops)

print "Vertices:"
for i in range(len(uniqueVerts3D)):
  print i,":",uniqueVerts3D[i]
print "Edges:"
for e in newEdges:
  print e

# TRIANGULATE THE VISIBLE MESH
# Convert to directed edges: attached edges bidirectional, hidden paths directed counterclockwise
# Separate into simple polygons
#   "Factor-out" the constant co-ordinate and pass the list of 2D coordinates to triangulate
#   "Re-distribute" the constant co-ordinate

directedEdges = ## double count attached edges, add hidden paths w/o colour
simplePolygons = segment.separateIntoPolygons(verts3D, directedEdges)
for polygon in simplePolygons:
  constantAxisCoordinate = ###
  vertexTriples2D = triangulator.triangulate_v1(removeConstantAxis(polygon))
  my_triangles = redistribute(constantAxisCoordinate, vertexTriples2D)

