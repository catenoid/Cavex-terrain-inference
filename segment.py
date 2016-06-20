import numpy as np
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
  # Though in the context of ignoring acyclic paths, this may not be necessary
  
  # Think this needs rewriting in taking the abs value of cross
  d1_x, d1_y, d1_z = delta1
  d2_x, d2_y, d2_z = delta2
  x = d1_y * d2_z - d1_z * d2_y
  y = d1_z * d2_x - d1_x * d2_z
  z = d1_x * d2_y - d1_y * d2_x
  return (unit(x), unit(y), unit(z))

# How embarassing
def cross(delta1,delta2):
  d1_x, d1_y, d1_z = delta1
  d2_x, d2_y, d2_z = delta2
  x = d1_y * d2_z - d1_z * d2_y
  y = d1_z * d2_x - d1_x * d2_z
  z = d1_x * d2_y - d1_y * d2_x
  return (x,y,z)

def dot(delta1,delta2):
  d1_x, d1_y, d1_z = delta1
  d2_x, d2_y, d2_z = delta2
  return d1_x * d2_x + d1_y * d2_y + d1_z * d2_z

def norm(v):
  x,y,z = v
  return np.sqrt(x**2 + y**2 + z**2)

def isReversedEdge(e1,e2):
  v1,v2 = e1
  v3,v4 = e2
  return (v1 == v4) and (v2 == v3)

def reverse(e):
  v1,v2 = e
  return (v2,v1)

def separateIntoPolygons(verts3D, directedEdges):
  def doesEdgeFollow(edge):
    v_start, v_end = edge
    return (lambda nextEdge : nextEdge[0] == v_end)

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

  def closerToInterior(edge):
    v_previous, v_shared = edge
    delta0 = subtract3(verts3D[v_previous], verts3D[v_shared])
    def angleCCW(e):
      assert(e[0] == v_shared)
      delta1 = subtract3(verts3D[e[1]], verts3D[e[0]])
      theta = np.arccos(dot(delta0, delta1) / (norm(delta0) * norm(delta1)))
      return theta if cross(delta0, delta1)>0 else theta + np.pi
    return (lambda e1,e2 : cmp(angleCCW(e1),angleCCW(e2)))

  def completeFace(e1,e2):
    face = [e1,e2]
    faceNormal = normalTo(e1,e2)
    # This still fails. But it only seems to be wrong if you begin at a vertex where *four* planes intersect, like 0
    # Because the plane trace goes around and tries to do the other face too instead of terminating
    # However it's the only vertex met during foreground traversal, unless you use two ground plane pieces

    def addNextCoplanarEdge(edge):
      isValidNextEdge = lambda e : (e not in face) \
                               and (not isReversedEdge(e,edge)) \
                               and ((normalTo(edge,e) == faceNormal) or areColinear(edge,e))
      possibleNextEdges = sorted(filter(isValidNextEdge, edgesFollowing[edge]), closerToInterior(edge))
      if (possibleNextEdges != []):
        nextEdge = possibleNextEdges[0]
        face.append(nextEdge)
        addNextCoplanarEdge(nextEdge)

    addNextCoplanarEdge(e2)
    isCompleteFace = face[-1][1] == face[0][0]
    return face if (isCompleteFace) else []
  
  def normalIsUnitVector(e1,e2):
    n = normalTo(e1,e2)
    return (n==(1,0,0) or n==(0,1,0) or n==(0,0,1))

  polygons = []
  def clipFace(es):
    if (len(es) >= 3):
      e1 = es[0]
      e2s = filter(lambda e2 : doesEdgeFollow(e1)(e2) and normalIsUnitVector(e1,e2), es[1:])
      polygon = []
      while (polygon == []):
        polygon = completeFace(e1, e2s.pop())
        # Can e2s exhaust without completing a face? Shouldn't be possible, as each undirected edge represents a face to be completed
        # Hah hah, what foolish optimism. IndexError, pop from an empty list
      polygons.append(polygon)
      clipFace(filter(lambda edge : edge not in polygon, es))

  clipFace(directedEdges)
  return polygons

#print separateIntoPolygons(sampleVerts3D, sampleDirectedEdges)
