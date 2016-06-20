# INFER HIDDEN TERRAIN
# Follow unattached edge paths which alias foreground and background vertices
# Transform paths to contours
# Add hidden floor/ceiling (to triangulate)
# Triangulate the wall connecting the unattached edge contour to the hidden floor/ceiling

def birdsEyeView((x,y,z)):
  return (x,z)

def isXZaliased(v1,v2):
  return birdsEyeView(v1) == birdsEyeView(v2)

# Input a list of 3d coordinates for a hidden contour.
# Group these coordinates into "chords," those which are consecutive and vertically colinear
# Returns a list of "chords"
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

def hasZeroArea(triangle):
  v1,v2,v3 = triangle
  return v1 == v2 or v2 == v3 or v1 == v3
# (What about if all three vertices are colinear?)

def floorHeight(contour):
  return min(map(lambda (x,y,z) : y, contour))

def ceilingHeight(contour):
  return max(map(lambda (x,y,z) : y, contour))

# A "wall" of rectangles joins the hidden floor/ceiling to the visible mesh
# The wall is bound in the y-axis by two contours
# The "flat" contour traces the coplanar face that is hidden from the camera (the "floor"/"ceiling")
# The "tooth" contour runs along the top/bottom of the wall 
#   "Tooth" because the contour changes in altitude, like crooked teeth
def wallSegmentBounds(contour, y):
  aliasedInXZPlane = groupXZAliased(contour)
  flatContour = map(lambda vs : (vs[0][0], y, vs[0][2]), aliasedInXZPlane)
  toothContour = map(lambda vs : (vs[0], vs[-1]), aliasedInXZPlane)
  return zip(flatContour, toothContour)

# A rectangular wall panel is composed of two identical right triangles: left ("L") and right ("R")
def connectToFloor(left_side, right_side):
  flat_L, (tooth_first_L, tooth_last_L) = left_side
  flat_R, (tooth_first_R, tooth_last_R) = right_side
  triangle1 = (tooth_last_L,        flat_R, flat_L)
  triangle2 = (tooth_last_L, tooth_first_R, flat_R)
  return filter(lambda t : not hasZeroArea(t), [triangle1, triangle2])

def connectToCeiling(left_side, right_side):
  flat_L, (tooth_first_L, tooth_last_L) = left_side
  flat_R, (tooth_first_R, tooth_last_R) = right_side
  triangle1 = (flat_L, tooth_first_R,  tooth_last_L)
  triangle2 = (flat_L,        flat_R, tooth_first_R)
  return filter(lambda t : not hasZeroArea(t), [triangle1, triangle2])

def triangulateWall(contour, y, triangulate):
  wallTriangles = []
  a = wallSegmentBounds(contour, y)
  cyclicPairs = [ (i,(i+1)%len(a)) for i in range(len(a)) ]
  for (i,j) in cyclicPairs:
    wallTriangles += triangulate(a[i], a[j])
  return wallTriangles

def addHiddenFloor(contour): # contour :: [(x,y,z)]
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
