from collections import deque
import segment
import inferTerrain
import projectionTriangulator
import createUnityObject

# Representing a drawing on isometric paper:
# Orient the paper with one set of graticules vertically upright
# Terminology: azimuth = degrees clockwise from "north,"
#   in this case, towards the top of the page

# Representing 2D coordinates:
# +Primary axis: azimuth = 60
# +Secondary axis: azimuth = 0

# Representing Attached Edges:
# Connect points on isometric paper with a vertex pair
# (as indexed into verts2D list)

# Representing Unattached Edges:
# Hidden floor: CCW from above
# Hidden ceiling: CW from above
# Paired colour represents the plane of movement to traverse that edge

# Once converted to 3D vector displacements, the absolute offset vertex must:
#   - be met in foreground traversal (i.e., not 'undef' in verts3D)
#   - not alias multiple 3d vertices (i.e., a tip on the rose tree)

# Import the isometric graph:
from archway import verts2D, attachedEdges, coplanarPaths

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
# This occurs:
#   (1) When a coplanar path meets an attached edge,
#       and the intersecting 3D coordinate is calculated twice
#   (2) At the starting vertex of a coplanar path,
#       when the contour wraps upon itself
  duplicates = {} # { (x,y,z) : [ vertices that refer to that coordinate] }
  for oldIndex in range(len(verts3D)):
    v = verts3D[oldIndex]
    if (v != 'undef'):
      if v in duplicates:
        duplicates[v].append(oldIndex)
      else:
        duplicates[v] = [oldIndex]
  return duplicates

def createOldToNewIndexMapping(uniqueVerts3D, duplicates, oldVertexCount):
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

# Visible polygons orient clockwise
# The one "polygon" which orients CCW is the hole in the ground plane
#   formed by the unused attached edges which meet the ground plane
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

def anchorRelativePath(offset, deltas):
  anchoredPath = []
  lastVertex = offset
  for delta in deltas:
    anchoredPath.append(lastVertex)
    lastVertex = add3(lastVertex, delta)
  return anchoredPath

def triangulateIsometricGraph(verts2D, attachedEdges, coplanarPaths):
  verts3D = ['undef' for v in verts2D]
  offset = (0,0,0)
  verts3D[0] = offset

  adjacentVertexGraph = createAdjacencyGraph(verts2D, attachedEdges)

  seen = []
  def foregroundTraversal(startingVertex):
    def DFS(v1):
      seen.append(v1)
      for v2 in adjacentVertexGraph[v1]:
        if (v2 not in seen):
          displacement = orthogonalVector3(subtract2(verts2D[v2], verts2D[v1]))
          verts3D[v2] = add3(verts3D[v1], displacement) 
          DFS(v2)
    DFS(startingVertex)

  def backgroundTraversal(path):
    unaliasedVertices = []
    pathOffsetOf = {}
    deltas = deque([])
    lastEdge, _ = path[-1]
    offsetIntoPath = 0
    for (v1,v2), colour in path:
      deltas.append(coplanarVector3(subtract2(verts2D[v2],verts2D[v1]), colour))
      if lastEdge == (v2,v1):
        unaliasedVertices.append(v1)
        pathOffsetOf[v1] = offsetIntoPath
      lastEdge = (v1,v2)
      offsetIntoPath += 1
    return (unaliasedVertices, pathOffsetOf, deltas)

  def addCyclicEdges(vertsToAdd, firstVertex):
    #firstVertex = len(verts3D)
    lastVertex = firstVertex + len(vertsToAdd)
    pathVertices = range(firstVertex, lastVertex)
    edgesToAdd = [(i,i+1) for i in pathVertices[:-1]]
    edgesToAdd.append((lastVertex-1, firstVertex))
    return edgesToAdd

  contourQueue = deque([backgroundTraversal(path) for path in coplanarPaths])
  invisibleMeshContours = []
  unattachedEdges = []
  foregroundTraversal(0)
  while(len(contourQueue) > 0):
    contour = contourQueue.popleft()
    unaliasedVertices, pathOffsetOf, deltas = contour
    potentialAnchors = [ v for v in unaliasedVertices if v in seen ]
    if (potentialAnchors != []):
      anchor = potentialAnchors.pop()
      unaliasedVertices.remove(anchor)
      deltas.rotate(pathOffsetOf[anchor])
      vertsToAdd = anchorRelativePath(verts3D[anchor], deltas)
      invisibleMeshContours.append(vertsToAdd)
      for v in unaliasedVertices:
        verts3D[v] = vertsToAdd[pathOffsetOf[v]-pathOffsetOf[anchor]]
        foregroundTraversal(v)
    else:
      contourQueue.append(contour)

  for c in invisibleMeshContours:
    newEdges = addCyclicEdges(c, len(verts3D))
    verts3D.extend(c)
    unattachedEdges.extend(newEdges)

  duplicates = createDuplicateDictionary(verts3D)
  uniqueVerts3D = duplicates.keys()

  toNewIndex = createOldToNewIndexMapping(uniqueVerts3D, duplicates, len(verts3D))
  renumberedAttachedEdges = renumberEdges(toNewIndex, attachedEdges)
  renumberedUnattachedEdges = renumberEdges(toNewIndex, unattachedEdges)

  directedEdges = renumberedAttachedEdges + reverseEdges(renumberedAttachedEdges) + renumberedUnattachedEdges

  print "uniqueVerts3D",uniqueVerts3D
  print "directedEdges",directedEdges

  simplePolygons = segment.separateIntoPolygons(uniqueVerts3D, directedEdges)

### ISSUE:
### The ccw identifier failed: select manually as index 1
  #del simplePolygons[identifyCCWpolygon(simplePolygons)]
  del simplePolygons[1]

  visibleTriangles = []
  for polygon in simplePolygons:
    polygonVerts3D = [ uniqueVerts3D[v1] for (v1,v2) in polygon ]
    visibleTriangles += projectionTriangulator.triangulate(polygonVerts3D)
  
  convexOnlyTriangles = []
  concaveOnlyTriangles = []

### ISSUE:
### Need to manually identify floor vs. ceiling 
#  for convexContour in invisibleMeshContours:
#    print "invisibleMeshContours",convexContour
#    convexOnlyTriangles += inferTerrain.addHiddenFloor(convexContour)
#    reflectedContour = map(lambda (x,y,z) : (x,-y,z), convexContour)
#    concaveOnlyTriangles += inferTerrain.addHiddenFloor(reflectedContour)
  invisibleMeshContours[0].reverse()
  convexOnlyTriangles += inferTerrain.addHiddenFloor(invisibleMeshContours[0])
  reflectedContour = map(lambda (x,y,z) : (x,-y,z), invisibleMeshContours[0])
  concaveOnlyTriangles += inferTerrain.addHiddenFloor(reflectedContour)

  convexOnlyTriangles += inferTerrain.addHiddenCeiling(invisibleMeshContours[1])
  reflectedContour = map(lambda (x,y,z) : (x,-y,z), invisibleMeshContours[1])
  concaveOnlyTriangles += inferTerrain.addHiddenCeiling(reflectedContour)

  name = "Archway"
  visibleMesh = open(name+"_visible.cs", 'w')
  visibleMesh.write(createUnityObject.generateVisibleMesh(name+"_visible", visibleTriangles))
  
  convexMesh = open(name+"_convex.cs", 'w')
  convexMesh.write(createUnityObject.generateConvexMesh(name+"_convex", convexOnlyTriangles))
  
  concaveMesh = open(name+"_concave.cs", 'w')
  concaveMesh.write(createUnityObject.generateConcaveMesh(name+"_concave", concaveOnlyTriangles))

if __name__ == "__main__":
  triangulateIsometricGraph(verts2D, attachedEdges, coplanarPaths)
