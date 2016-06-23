import segment
import inferTerrain
import triangulator
import projectionTriangulator
import createUnityObject

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
  (0,-1),  # Bounding vertices of the ground plane
  (-6,5),
  (0,5),
  (6,-1),
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

coplanarPaths = [ 
# A contour aliased to an acyclic graph goes counter-clockwise from above
# So the colour paired with a directed edge is the colour on the outside of the contour
# First vertex must be found in foreground traversal, until I check for 'undef's
[ # Back of steps
  ((11,10), 'g'),
  ((10,8), 'g'),
  ((8,9), 'w'),
  ((9,6), 'w'),
  ((6,5), 'b'),
  ((5,2), 'w'),
  ((2,1), 'b'),
  ((1,2), 'w'),
  ((2,5), 'w'),
  ((5,6), 'w'),
  ((6,9), 'w'),
  ((9,8), 'w'),
  ((8,10), 'w'),
  ((10,11), 'w'),
],
]

# THIS GROUND PLANE IS NOTHING BUT TROUBLE
# ??? Make a cut in the ground plane from (0,0) to (0,-1) to make it a polygon oriented clockwise, without holes
#[ # Ground: Left half
## Avoiding duplicates with the above path implies there will be 5 edges
#  ((11,0), 'w'),
#  ((0,12), 'w'),
#  ((12,15), 'w'),
#  ((15,14), 'w'),
#  ((14,9), 'w'), 
##  ((9,8), 'w'),
##  ((8,10), 'w'),
##  ((10,11), 'w'),
#],
#[ # Ground: Right half
##  ((1,2), 'w'),
##  ((2,5), 'w'),
##  ((5,6), 'w'),
##  ((6,9), 'w'),
#  ((9,14), 'w'),
#  ((14,13), 'w'),
#  ((13,12), 'w'),
#  ((12,0), 'w'),
#  ((0,1), 'w'),
#]
## The addition of two ground halves has caused lots of edge to be repeated
#
##[ # Ground
##  ((0,12), 'w'),
##  ((12,13), 'w'),
##  ((13,14), 'w'),
##  ((14,15), 'w'),
##  ((15,12), 'w'),
##  ((12,0), 'w'),
##]
#]
# DEATH TO GROUND PLANES -- do a birds eye view of all white triangles, combine, mask, triangulate

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
# All edge traversals are coplanar, but two edges are aliases with two different colours
def coplanarDisplacements3D(path):
  return [coplanarDisplacement(delta(vertexPair), colour) for (vertexPair, colour) in path]

def dealias(path):
  dealiasedVerts = []
  v = verts3D[path[0][0][0]] # The first vertex in the path must have been met in fg traversal, so the delta path can be anchored
  # Do this properly path[i][0][0,1]
  # check 0 and 1 (vertex pair in edge), increment i until verts3D doesn't return undef
  # then start indexed i into coplanarDisplacements3D
  for dv in coplanarDisplacements3D(path):
    nextVertex = add3(v,dv)
    dealiasedVerts.append(nextVertex)
    v = nextVertex
  return dealiasedVerts

unattachedEdges = []
invisibleMeshContours = []

# Trace the contours which alias to an acyclic graph of vertices, and add edges going counter-clockwise around the contour
for path in coplanarPaths:
  vertsToAdd = dealias(path)
  firstNewVertex = len(verts3D)
  lastNewVertex = firstNewVertex + len(vertsToAdd)
  pathVertices = range(firstNewVertex, lastNewVertex)
  edgesToAdd = [ (i,i+1) for i in pathVertices[:-1] ] + [(lastNewVertex-1, firstNewVertex)]
  verts3D += vertsToAdd
  unattachedEdges += edgesToAdd
  invisibleMeshContours.append(pathVertices)

# Alias vertices that refer to the same 3D coordinate
# This happens:
#   (1) When an unattached edge path meets an attached edge, and the intersecting vertex 3D coordinate is calculated twice
#   (2) At the starting vertex of an unattached path, when the contour wraps upon itself
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
# For an entry in oldToNewIndex to be 'undef', the vertex was not encountered in the foreground traversal
oldToNewIndex = ['undef' for v in verts3D]
for newIndex in range(len(uniqueVerts3D)):
  v = uniqueVerts3D[newIndex]
  oldIndices = duplicates[v]
  for i in oldIndices:
    oldToNewIndex[i] = newIndex

renumberedAttachedEdges = [ (oldToNewIndex[v1], oldToNewIndex[v2]) for (v1,v2) in attachedEdges ]
renumberedUnattachedEdges = [ (oldToNewIndex[v1], oldToNewIndex[v2]) for (v1,v2) in unattachedEdges ]
convexMeshContours = [ map(lambda v : uniqueVerts3D[oldToNewIndex[v]], contour) for contour in invisibleMeshContours ]

print "Visible mesh:"
print "Vertices:"
for i in range(len(uniqueVerts3D)):
  print i,":",uniqueVerts3D[i]
print "\nAttached edges:"
for e in renumberedAttachedEdges:
  print e
print "\nUnattached edges"
for e in renumberedUnattachedEdges:
  print e

def reverseEdges(edges):
  return map(lambda (v1,v2) : (v2,v1), edges)

# TRIANGULATE THE VISIBLE MESH
# Make edges directional, such that visible polygons orient clockwise
directedEdges = renumberedAttachedEdges + reverseEdges(renumberedAttachedEdges) + renumberedUnattachedEdges
simplePolygons = segment.separateIntoPolygons(uniqueVerts3D, directedEdges)

# The one "polygon" which orients CCW is the hole in the ground plane
# Selectively reverse the edges of one of the simple polygons,
# then check for consistancy in the edges of this reversed polygon and all the other simple polygons
def identifyCCWpolygon(polygons):
  for i in range(len(polygons)):
    edges = reverseEdges(polygons[i])
    for j in range(0,i) + range((i+1),len(polygons)):
      edges += polygons[j]

    sortedEdges = sorted(edges + reverseEdges(edges))
    if (len(sortedEdges) > 1):
      duplicateSeen = False
      previousEdge = sortedEdges[0]
      for edge in sortedEdges[1:]:
        if (edge == previousEdge):
          duplicateSeen = True
        previousEdge = edge
      if (duplicateSeen == True):
        return i

del simplePolygons[identifyCCWpolygon(simplePolygons)]

visibleTriangles = []
for polygon in simplePolygons:
  verts3D = [ uniqueVerts3D[v1] for (v1,v2) in polygon ]
  visibleTriangles += projectionTriangulator.triangulate(verts3D)

# TRIANGULATE THE INVISIBLE MESH
convexOnlyTriangles = []
concaveOnlyTriangles = []
for convexContour in convexMeshContours:
  convexOnlyTriangles += inferTerrain.addHiddenFloor(convexContour)
  reflectedContour = map(lambda (x,y,z) : (x,-y,z), convexContour)
  concaveOnlyTriangles += inferTerrain.addHiddenFloor(reflectedContour)

# For the mesh names, implement conformation to C sharp naming rules
# i.e. no spaces, begin with a capital letter

nameOfVisibleMesh = "Testing_visible"
visibleMesh = open(nameOfVisibleMesh+".cs", 'w')
visibleMesh.write(createUnityObject.generateVisibleMesh(nameOfVisibleMesh, visibleTriangles))

nameOfConvexMesh = "Testing_convex"
convexMesh = open(nameOfConvexMesh+".cs", 'w')
convexMesh.write(createUnityObject.generateConvexMesh(nameOfConvexMesh, convexOnlyTriangles))

nameOfConcaveMesh = "Testing_concave"
concaveMesh = open(nameOfConcaveMesh+".cs", 'w')
concaveMesh.write(createUnityObject.generateConcaveMesh(nameOfConcaveMesh, concaveOnlyTriangles))
