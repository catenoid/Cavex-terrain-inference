# The visible faces of a set of two steps
sampleVerts3D = [
  ( 0, 0,  0),
  ( 0, 0, -2),
  ( 0, 2, -2),
  ( 0, 2, -1),
  ( 0, 1, -1),
  ( 0, 1,  0),
  (-2, 2, -2),
  (-2, 2, -1),
  (-2, 1, -1),
  (-2, 1,  0),
  (-2, 0,  0),
]

# Faces are directed clockwise
sampleDirectedEdges = [
# "L-shape"
  (0, 1),
  (1, 2),
  (2, 3),
  (3, 4),
  (4, 5),
  (5, 0),
# Top of upper step
  (2, 6),
  (6, 7),
  (7, 3),
  (3, 2),
# Side of upper step	
  (7, 8),
  (8, 4),
  (4, 3),
  (3, 7),
# Top of lower step
  (8, 9),
  (9, 5),
  (5, 4),
  (4, 8),
# Side of lower step
  (5, 9),
  (9, 10),
  (10, 0),
  (0, 5),
]

def subtract3(v1,v2):
  x1,y1,z1 = v1
  x2,y2,z2 = v2
  return (x1-x2, y1-y2, z1-z2)

def unit(n):
  return n/n if (n != 0) else 0

def normalisedCrossProduct(delta1, delta2):
  # We need to distinguish cases where the surface normal renders the face invisble.
  # to avoid the possibiliy of treating the unattached contour as a face,
  # hence getting stuck because the normals change freely
  d1_x, d1_y, d1_z = delta1
  d2_x, d2_y, d2_z = delta2
  x = d1_y * d2_z - d1_z * d2_y
  y = d1_z * d2_x - d1_x * d2_z
  z = d1_x * d2_y - d1_y * d2_x
  return (unit(x), unit(y), unit(z))

def isReversedEdge(e1,e2):
  v1,v2 = e1
  v3,v4 = e2
  return (v1 == v4) and (v2 == v3)

def separateIntoPolygons(verts3D, directedEdges):
  def doesEdgeFollow(edge):
    v_start, v_end = edge
    return (lambda nextEdge : nextEdge[0] == v_end)

  # Change to reflect undirected edges
  edgesFollowing = {}
  for edge in directedEdges:
    edgesFollowing[edge] = filter(doesEdgeFollow(edge), directedEdges) 

  def normalTo(e1,e2):
    v1,v2 = e1
    v3 = e2[1]
    d1 = subtract3(verts3D[v2], verts3D[v1]) 
    d2 = subtract3(verts3D[v3], verts3D[v2]) 
    return normalisedCrossProduct(d2,d1)

  def areColinear(e1,e2):
    return (normalTo(e1,e2) == (0,0,0))

  def completeFace(e1,e2):
    face = [e1,e2]
    faceNormal = normalTo(e1,e2)
    # Follow undirected edges. All because you might begin a face on two attached edges, and trace the wrong way
    def addNextCoplanarEdge(edge):
      foundNextEdge = False
      nextEdge = (0,0)
      for e in edgesFollowing[edge]:
        # Direct undirected e according to edge's end vertex
        # [(a,b), (b,c), (d,c)] -> [(a,b), (b,c), (c,d)]
        if (not foundNextEdge \
            and (e not in face) \
            and (not isReversedEdge(e,edge)) \
            and ((normalTo(edge,e) == faceNormal) or areColinear(edge,e))):
          foundNextEdge = True
          nextEdge = e
      if (foundNextEdge):
        face.append(nextEdge)
        addNextCoplanarEdge(nextEdge)

    addNextCoplanarEdge(e2)
    # (If successful...)
    # Upon completion, direct edges clockwise
    # Orientation test:
    #   Draw a line +90 degrees from the center of a directed edge (center offset to avoid corner cases)
    #   If it intersects an odd number of other edges, then clockwise
    #   Else, reverse all edges
    # What if unsuccessful? return [], and test in clipFace?
    # Why do we need to follow undirected edges? The idea itself is a bit of a fudge, because it is using directed edges not explictly beloning to that face
    return face

  polygons = []
  def clipFace(es):
    if (len(es) >= 3):
      # Choose directed edge 1
      e1 = es[0]
      # Choose directed edge 2 by filtering es such that:
      #   e2 follows e1
      #   e1xe2 goes in a unit vector direction [subsumed not isReversedEdge test]

      e2 = filter(lambda e2 : not isReversedEdge(e1,e2), edgesFollowing[e1])[0] # Is Python's filter lazy!?
      polygon = completeFace(e1, e2)
      # e1,e2 still may not represent a face.
      # May fail safe, if in which case the path terminates without rejoining.
      # Select the next possible e1, repeat until face found.
      polygons.append(polygon)
      # Remove polygon from directedEdges and call recursively
      clipFace(filter(lambda edge : edge not in polygon, es))

  clipFace(directedEdges)
  return polygons

#print separateIntoPolygons(sampleVerts3D, sampleDirectedEdges)
