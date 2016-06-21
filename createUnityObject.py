usingDirectives = "using UnityEngine; using System.Collections;\n"

def generateInvisibleMesh(name, isConcave, triangles):
  cavex = "Concave_only" if isConcave else "Convex_only"
  mesh = usingDirectives+"public class "+name+" : "+cavex+" {\nVector3[] my_verts = new Vector3[] {\n"
  for v1,v2,v3 in triangles:
    mesh += "new Vector3"+str(v1)+", new Vector3"+str(v3)+", new Vector3"+str(v2)+",\n"
  mesh += "}; public "+name+"() {vertices = my_verts;} }"
  return mesh

def generateConcaveMesh(name, triangles):
  return generateInvisibleMesh(name, True, triangles)

def generateConvexMesh(name, triangles):
  return generateInvisibleMesh(name, False, triangles)

def generateVisibleMesh(name, triangles):
  mesh = usingDirectives+"public class "+name+" : Visible_surface {\nVector3[] verts = new Vector3[] {\n"
  for v1,v2,v3 in triangles:
    mesh += "new Vector3"+str(v1)+", new Vector3"+str(v3)+", new Vector3"+str(v2)+",\n"
  mesh += "}; public "+name+"() {concaveVerts = verts;} }"
  return mesh
