2Dverts = [] # list of (a,b)
edges = [] # list of (v1,v2), 'c'|'v'|'u'
faces = [] # list of [e,e,e,e ...],'B'|'G'|'W'
# Are enums possible for the above?
offset = (0,0,0)

seenVerts = []
seenEdges = []
3Dverts = []
3Dverts.append(offset)

# there's nothing in here!
#DFS(2Dverts[0])

def DFS(v1):
  seenVerts.append(v1)
  for edge in incidentEdges(v1):
    if (edge not in seenEdges):
      v2 = nextVert(v1, edge)
      if (v2 not in seenVerts):
        seenEdges.append(edge)
        2Ddisplacement = subtract(v2,v1)
        3Dverts[v2] = 3Dverts[v1] + planarDisplacement(faceColour(edge), 2Ddisplacement)
        DFS(v2)

def incidentEdges(vertex):
  # return a list of edges attached to vertex
  pass

def nextVert(vertex, edge):
  # cross the edge to the next vert
  pass

def subtract(v1,v2):
  # 2-vector subtraction of coordinates
  # Pip can't install numpy because pip won't install numpy
  return (v1[0]-v2[0], v1[1]-v2[1]) 

def faceColour(edge):
  # the colour of an incident face (there can be one or two)
  pass

def planarDisplacement(colour, 2Ddispl):
  pass

