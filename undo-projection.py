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
stairVerts2D = [
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
stairAttachedEdges = [
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

stairCoplanarPaths = [
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

def createAdjacencyGraph(verts2D, attachedEdges):
  adjacentVertices = [[] for v in verts2D]
  for (v1,v2) in attachedEdges:
    adjacentVertices[v1].append(v2)
    adjacentVertices[v2].append(v1)
  return adjacentVertices

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
# White 'w', +y normal | Grey 'g', +x normal | Black 'b', +z normal
# Legacy notation from drafting on paper and shading in, to replace
coplanarDisplacements = {
  'w' : coplanarYToVector3,
  'g' : coplanarXToVector3,
  'b' : coplanarZToVector3
}

def coplanarVector3(delta, colour):
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

def orthogonalVector3(delta):
  scaleFactor = length(delta)
  axisAngle = azimuth(delta)
  unit = attachedEdgeToVector3[axisAngle]
  return scale(unit, scaleFactor)

def foregroundTraversal(verts2D, attachedEdges):
# The 2D coordinate (0,0) will be anchored to 3D coordinate 'offset'
  adjacentVertexGraph = createAdjacencyGraph(verts2D, attachedEdges)
  verts3D = ['undef' for v in verts2D]
  offset = (0,0,0)
  verts3D[0] = offset
  seen = []
  def DFS(v1):
    seen.append(v1)
    for v2 in adjacentVertexGraph[v1]:
      if (v2 not in seen):
        isometricDisplacement = subtract2(verts2D[v2], verts2D[v1])
        verts3D[v2] = add3(verts3D[v1], orthogonalVector3(isometricDisplacement))
        DFS(v2)
  DFS(0)
  return verts3D

def getAliasedVertices(coplanarDisplacements, startingVert3D):
  dealiasedVerts = []
  v = startingVert3D
  for dv in coplanarDisplacements:
    nextVertex = add3(v,dv)
    dealiasedVerts.append(nextVertex)
    v = nextVertex
  return dealiasedVerts

def createDuplicateDictionary(verts3D):
# Alias vertices that refer to the same 3D coordinate
#   (1) When a coplanar path meets an attached edge, and the intersecting 3D coordinate is calculated twice
#   (2) At the starting vertex of a coplanar path, when the contour wraps upon itself
  duplicates = {} # { (x,y,z) : [ vertices that refer to that coordinate] }
  for oldIndex in range(len(verts3D)):
    v = verts3D[oldIndex]
    if (v != 'undef'):
      if v in duplicates:
        duplicates[v].append(oldIndex)
      else:
        duplicates[v] = [oldIndex]
  return duplicates

def createOldToNewIndexMapping(duplicates, oldVertexCount):
  uniqueVerts3D = duplicates.keys()
  toNewIndex = ['undef' for i in range(oldVertexCount)]
  for newIndex in range(len(uniqueVerts3D)):
    v = uniqueVerts3D[newIndex]
    oldIndices = duplicates[v]
    for i in oldIndices:
      toNewIndex[i] = newIndex
  return toNewIndex

def renumberEdges(toNewIndex, edges):
  return [ (toNewIndex[v1], toNewIndex[v2]) for (v1,v2) in edges ]

def reverseEdges(edges):
  return map(lambda (v1,v2) : (v2,v1), edges)

# Make edges directional, such that visible polygons orient clockwise
# The one "polygon" which orients CCW is the hole in the ground plane
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

def triangulateIsometricGraph(verts2D, attachedEdges, coplanarPaths):
  foregroundVerts3D = foregroundTraversal(verts2D, attachedEdges)

  unattachedEdges = []
  invisibleMeshContours = []
  verts3D = foregroundVerts3D

  for path in coplanarPaths:
    startingVert3D = verts3D[path[0][0][0]]
    coplanarDisplacements = [ coplanarVector3(subtract2(verts2D[v2], verts2D[v1]), colour) for ((v1,v2), colour) in path ]
    vertsToAdd = getAliasedVertices(coplanarDisplacements, startingVert3D)
    firstNewVertex = len(verts3D)
    lastNewVertex = firstNewVertex + len(vertsToAdd)
    pathVertices = range(firstNewVertex, lastNewVertex)
    edgesToAdd = [ (i,i+1) for i in pathVertices[:-1] ] + [(lastNewVertex-1, firstNewVertex)]
    verts3D += vertsToAdd
    unattachedEdges += edgesToAdd
    invisibleMeshContours.append(pathVertices)

  duplicates = createDuplicateDictionary(verts3D)
  uniqueVerts3D = duplicates.keys()
  toNewIndex = createOldToNewIndexMapping(duplicates, len(verts3D))
  renumberedAttachedEdges = renumberEdges(toNewIndex, attachedEdges)
  renumberedUnattachedEdges = renumberEdges(toNewIndex, unattachedEdges)
  renumberedInvisibleMeshContours = [ map(lambda v : uniqueVerts3D[toNewIndex[v]], contour) for contour in invisibleMeshContours ]

  directedEdges = renumberedAttachedEdges + reverseEdges(renumberedAttachedEdges) + renumberedUnattachedEdges
  simplePolygons = segment.separateIntoPolygons(uniqueVerts3D, directedEdges)
  del simplePolygons[identifyCCWpolygon(simplePolygons)]
  
  visibleTriangles = []
  for polygon in simplePolygons:
    polygonVerts3D = [ uniqueVerts3D[v1] for (v1,v2) in polygon ]
    visibleTriangles += projectionTriangulator.triangulate(polygonVerts3D)
  
  convexOnlyTriangles = []
  concaveOnlyTriangles = []
  for convexContour in renumberedInvisibleMeshContours:
    convexOnlyTriangles += inferTerrain.addHiddenFloor(convexContour)
    reflectedContour = map(lambda (x,y,z) : (x,-y,z), convexContour)
    concaveOnlyTriangles += inferTerrain.addHiddenFloor(reflectedContour)

  nameOfVisibleMesh = "Testing_visible-mod"
  visibleMesh = open(nameOfVisibleMesh+".cs", 'w')
  visibleMesh.write(createUnityObject.generateVisibleMesh(nameOfVisibleMesh, visibleTriangles))
  
  nameOfConvexMesh = "Testing_convex-mod"
  convexMesh = open(nameOfConvexMesh+".cs", 'w')
  convexMesh.write(createUnityObject.generateConvexMesh(nameOfConvexMesh, convexOnlyTriangles))
  
  nameOfConcaveMesh = "Testing_concave-mod"
  concaveMesh = open(nameOfConcaveMesh+".cs", 'w')
  concaveMesh.write(createUnityObject.generateConcaveMesh(nameOfConcaveMesh, concaveOnlyTriangles))

if __name__ == "__main__":
  triangulateIsometricGraph(stairVerts2D, stairAttachedEdges, stairCoplanarPaths)
