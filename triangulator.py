# Triangulation by Ear Clipping
# 1. Iterate through vertices of polygon
#     a. If the vertex is concave (interior angle > 180 degrees), skip
#     b. If the triangle formed by the vertex has other vertices in it, skip
#     c. Otherwise, ear found
# 2. "Cut off" the ear from the polygon and store it
# 3. Go to 1

sample = [
  (1,2),
  (2,1),
  (1,0),
  (0,1)
]

def equalWithinTolerance(a, b, epsilon=0.00001):
  return (a + epsilon > b and a - epsilon < b)

def isInTriangle(v, triangle):
  # Convert vertex to test (v) to Barycentric coordinates
  v_x, v_y   = v
  (p1_x, p1_y), (p2_x, p2_y), (p3_x, p3_y) = triangle
  denominator = ((p2_y - p3_y) * (p1_x - p3_x) + (p3_x - p2_x) * (p1_y - p3_y))
  if equalWithinTolerance(denominator, 0.0): return False
  denominator = 1.0 / denominator
  alpha = denominator * ((p2_y - p3_y) * (v_x - p3_x) + (p3_x - p2_x) * (v_y - p3_y))
  if alpha < 0: return False
  beta = denominator  * ((p3_y - p1_y) * (v_x - p3_x) + (p1_x - p3_x) * (v_y - p3_y))
  if beta < 0: return False
  return (1.0 - alpha - beta) >= 0

def getEarOfVertex(polygonCoords, i):
  return (polygonCoords[i-1], polygonCoords[i], polygonCoords[(i+1)%len(polygonCoords)])

def isConcave(triangle):
  # True if the triangle orients with polygon, and visible polygons orient clockwise in Unity (...I think)
  # Check the sign of the cross product of (v2-v1) with (v3-v2)
  (v1_x, v1_y), (v2_x, v2_y), (v3_x, v3_y) = triangle
  d1_x, d1_y = v2_x - v1_x, v2_y - v1_y
  d2_x, d2_y = v3_x - v2_x, v3_y - v2_y
  return ((d1_x * d2_y) - (d1_y * d2_x)) > 0

def removeFirstEar(polygonCoords):
  return polygonCoords[1:]

def barrelShift(coords):
  return coords[1:] + [coords[0]]

def noOtherVertexInFirstEar(coords):
  firstEar = getEarOfVertex(coords, 0)
  # I don't like that we get the firstEar AGAIN here
  # But the range coords[2:-1] assumes we are testing against the firstEar
  #   so it doesn't make sense to include firstEar as a parameter to this function
  for i in range(len(coords[2:-1])):
    vertexTriangle = getEarOfVertex(coords, i)
    if (isConcave(vertexTriangle) and isInTriangle(coords[i], firstEar)):
      return False
  return True

def triangulate(polygonCoords):  # [(x,y)]
  triangulated = []              # [((x,y), (x,y), (x,y))]

  def clipEar(coords):
    if (len(coords) >= 3):
      firstEar = getEarOfVertex(coords, 0)
      if (not isConcave(firstEar) and noOtherVertexInFirstEar(coords)):
        triangulated.append(firstEar)
        clipEar(removeFirstEar(coords))
      else:
        clipEar(barrelShift(coords))

  clipEar(polygonCoords)
  return triangulated

def triangulate_v2(coords):
  triangulated = []              # [((x,y), (x,y), (x,y))]
  
  while (len(coords) >= 3):
    firstEar = getEarOfVertex(coords, 0)
    if (not isConcave(firstEar) and noOtherVertexInFirstEar(coords)):
      triangulated.append(firstEar)
      coords = removeFirstEar(coords)
    else:
      coords = barrelShift(coords)

  return triangulated

print "Triangulator v1 result:"
print triangulate(sample)
print "Triangulator v2 result:"
print triangulate_v2(sample)
