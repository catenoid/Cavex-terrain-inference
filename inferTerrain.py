# INFER HIDDEN TERRAIN
# Follow unattached edge paths which alias foreground and background vertices
# Transform paths to contours
# Add hidden floor/ceiling (to triangulate)
# Triangulate the wall connecting the unattached edge contour to the hidden floor/ceiling

def birdsEyeView((x,y,z)):
  return (x,z)

def isXZaliased(v1,v2):
  return birdsEyeView(v1) == birdsEyeView(v2)

def groupXZAliased(path):
  aliased = []
  chord = [path[0]]
  barrelShifted = path[1:] + [path[0]]
  for v in barrelShifted:
    if (isXZaliased(v, chord[-1])):
      chord.append(v)
    else:
      aliased.append(chord)
      chord = [v]
  return aliased

def zeroArea(triangle):
  v1,v2,v3 = triangle
  return v1 == v2 or v2 == v3 or v1 == v3

def floorHeight(contour):
  return min(map(lambda (x,y,z) : y, contour))

def ceilingHeight(contour):
  return max(map(lambda (x,y,z) : y, contour))

# A "wall" of rectangles joins the hidden floor/ceiling to the visible mesh
# A rectangular wall segment is composed of two identical right triangles
# j = (i+1) % len(aliasedVerts3D), but (+) can't go in a variable name
def wallSegmentBounds(contour, y):
  aliasedInXZPlane = groupXZAliased(contour)
  flatContour = map(lambda vs : (vs[0][0], y, vs[0][2]), aliasedInXZPlane)
  jaggedContour = map(lambda vs : (vs[0], vs[-1]), aliasedInXZPlane)
  return zip(flatContour, jaggedContour)

def connectToFloor(left_side, right_side):
  flat_L, (jagged_first_L, jagged_last_L) = left_side
  flat_R, (jagged_first_R, jagged_last_R) = right_side
  triangle1 = (jagged_last_L, flat_R,         flat_L)
  triangle2 = (jagged_last_L, jagged_first_R, flat_R)
  return filter(lambda t : not zeroArea(t), [triangle1, triangle2])

def connectToCeiling(left_side, right_side):
  flat_L, (jagged_first_L, jagged_last_L) = left_side
  flat_R, (jagged_first_R, jagged_last_R) = right_side
  triangle1 = (flat_L, jagged_first_R, jagged_last_L)
  triangle2 = (flat_L, flat_R,         jagged_first_R)
  return filter(lambda t : not zeroArea(t), [triangle1, triangle2])

def triangulateWall(contour, y, triangulate):
  wallTriangles = []
  a = wallSegmentBounds(contour, y)
  cyclicPairs = [ (i,(i+1)%len(a)) for i in range(len(a)) ]
  for (i,j) in cyclicPairs:
    wallTriangles += triangulate(a[i], a[j])
  return wallTriangles

def addHiddenFloor(contour):
  return triangulateWall(contour, floorHeight(contour), lambda t1, t2 : connectToFloor(t1,t2))

def addHiddenCeiling(contour):
  return triangulateWall(contour, ceilingHeight(contour), lambda t1, t2 : connectToCeiling(t1,t2))

# need verts3D and hiddenTerrainContours (directed path of 3d vertices)
# for contour in hiddenTerrainContours:
#   contourVerts3D = map(lambda v : verts3D[v], contour)
#   tri = addHiddenFloor(contourVerts3D)
#   for t in tri:
#     print t 
  # Triangulate floorContour (That becomes part of the hidden mesh)
# Whether or not we add a floor or ceiling depends on which side is in the foreground
