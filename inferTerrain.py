import projectionTriangulator

# INFER HIDDEN TERRAIN
# Follow unattached edge contours which alias foreground and background vertices
# Add triangles for
#  - the hidden floor/ceiling
#  - the wall connecting the hidden floor / ceiling to the visible mesh

def birdsEyeView((x,y,z)):
  return (x,z)

def isXZaliased(v1,v2):
  return birdsEyeView(v1) == birdsEyeView(v2)

# Group coordinates into "chords" that are aliased in the XZ plane (i.e. consecutive and vertically colinear)
# Each chord represents a wall corner
def groupXZAliased(path): # path :: [(x,y,z)]
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

# Whether or not we add a floor or ceiling depends on which side is in the foreground
# If the lower (closer to the bottom of the page) side is the foreground => hidden floor
# If the lower side is the background => hidden ceiling
# However I do not yet know how to algorithmically determine this
def floorHeight(contour):
  return min(map(lambda (x,y,z) : y, contour))

def ceilingHeight(contour):
  return max(map(lambda (x,y,z) : y, contour))

# A "wall" of rectangles joins the hidden floor/ceiling to the visible mesh
# The wall is bound in the y-axis by two contours:
#   The "flat" contour traces the coplanar face that is hidden from the camera (the "floor"/"ceiling")
#   The "tooth" contour runs along the top/bottom of the wall 
#   "Tooth" because the contour changes in altitude at right angles, like crooked teeth
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

def addHiddenFloor(contour): # contour :: [(x,y,z)]
  aliasedInXZPlane = groupXZAliased(contour)
  y = floorHeight(contour)
  flatContour  = map(lambda vs : (vs[0][0], y, vs[0][2]), aliasedInXZPlane)
  toothContour = map(lambda vs :         (vs[0], vs[-1]), aliasedInXZPlane)

  wallCorners = zip(flatContour, toothContour)
  wallTriangles = []
  cyclicPairs = [ (i,(i+1)%len(wallCorners)) for i in range(len(wallCorners)) ]
  for (i,j) in cyclicPairs:
    wallTriangles += connectToFloor(wallCorners[i], wallCorners[j])

  flatContour.reverse()
  floorTriangles = projectionTriangulator.triangulate(flatContour)

  return floorTriangles + wallTriangles
