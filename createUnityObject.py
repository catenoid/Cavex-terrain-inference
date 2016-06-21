name = "sample"
triangles = [
((-2, 1, -1), (-2, 1, 0), (0, 1, 0)),
((-2, 1, -1), (0, 1, 0), (0, 1, -1)),
((0, 0, 0), (-3, 0, 0), (-2, 1, 0)),
((0, 0, 0), (-2, 1, 0), (0, 1, 0)),
((-2, 2, -2), (-2, 2, -1), (0, 2, -1)),
((-2, 2, -2), (0, 2, -1), (0, 2, -2)),
((0, 1, -1), (-2, 1, -1), (-2, 2, -1)),
((0, 1, -1), (-2, 2, -1), (0, 2, -1)),
((0, 1, -1), (0, 2, -1), (0, 2, -2)),
((0, 1, -2), (0, 0, -3), (0, 0, 0)),
((0, 1, -2), (0, 0, 0), (0, 1, 0)),
((0, 1, -2), (0, 1, 0), (0, 1, -1)),
((0, 1, -2), (0, 1, -1), (0, 2, -2))
]

def generateMesh(name, isConcave, triangles):
  cavex = "Concave" if isConcave else "Convex"
  print """using UnityEngine;
using System.Collections;

public class """+name+""" : """+cavex+"""_only {
    Vector3[] my_verts = new Vector3[] {"""
  for v1,v2,v3 in triangles:
    print "        new Vector3",v1,", new Vector3",v2,", new Vector3",v3,","
  print """    };
    
    public """+name+"""() {
        vertices = my_verts;
    }
}"""

generateMesh(name,True,triangles)
