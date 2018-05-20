import math

import maya.OpenMaya as om

import progress_bar


class GeoCache(object):
    """
    container for cached triangulated geometry
    note: no extra type checking or error handling is done!
    """

    def __init__(self):
        self.p0 = om.MPointArray()
        self.p1 = om.MPointArray()
        self.p2 = om.MPointArray()
        self.normals = om.MVectorArray()
        self.poly_id = om.MIntArray()
        self.AB = om.MVectorArray()
        self.AC = om.MVectorArray()

        self.mesh = None
        self.cached = True
        self.weighted_ids = []

    @progress_bar.ProgressBar('Caching Geometry...')
    def cache_geometry(self, mesh):

        self.flush_cache()
        self.mesh = mesh

        #  in_mesh = node_utils.get_connected_in_mesh(self.thisMObject(), False)
        mesh_fn = om.MFnMesh(self.mesh)
        num_polys = mesh_fn.numPolygons() # TODO - get in mesh fn
        num_iter = num_polys / 100

        # get bb in world space
        dag_fn = om.MFnDagNode(self.mesh)
        bb = dag_fn.boundingBox()
        inv_matrix = self.mesh.exclusiveMatrix()
        bb.transformUsing(inv_matrix)

        # initialize triangle data
        tri_points = om.MPointArray()
        tri_ids = om.MIntArray()
        tris_area = []
        smallest_tri = None

        # iter mesh
        poly_iter = om.MItMeshPolygon(self.mesh)
        while not poly_iter.isDone():

            # get face triangles
            poly_index = poly_iter.index()
            poly_iter.getTriangles(tri_points, tri_ids, om.MSpace.kWorld)

            # get triangle data
            for i in xrange(tri_points.length() / 3):
                p0 = tri_points[i * 3]
                p1 = tri_points[i * 3 + 1]
                p2 = tri_points[i * 3 + 2]
                area, AB, AC, normal = self.get_triangle_area(p0, p1, p2)

                if area < smallest_tri or smallest_tri is None:
                    smallest_tri = area

                tris_area.append(area)
                self.cache = (p0, p1, p2, normal, poly_index, AB, AC)

            # update progressbar
            if poly_index >= num_iter:
                self.cache_geometry.increment()
                num_iter += num_polys / 100

            poly_iter.next()

        probability = [int(math.ceil(area / smallest_tri)) for area in tris_area]
        [self.weighted_ids.extend([idx] * chance) for idx, chance in enumerate(probability)]

        self.cached = True

    def get_triangle_area(self, p0, p1, p2):
        """
        return size of a triangle and the vector p1-p0 and p2-p0
        :param p0: MPoint 1
        :param p1: MPoint 2
        :param p2: MPoint 3
        :return: triangle area, vector AB, vector AC, and the normalized triangle normal
        """

        AB = om.MVector(p1 - p0)
        AC = om.MVector(p2 - p0)

        normal = (AB ^ AC)

        # actually the real surface area is area/2
        # but since all tris are handled the same way it does not make any difference
        # hence I can save computation by omitting area/2
        area = math.sqrt(normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2)

        normal.normalize()

        return area, AB, AC, normal

    ################################################################################################
    # cache property
    ################################################################################################

    @property
    def cache(self):
        """ cache getter
        :return:    tuple of entire geo cache:
        id  content           data type
        0 - p0              - MPointArray
        1 - p2              - MPointArray
        2 - p1              - MPointArray
        3 - face normal     - MVectorArray
        4 - polygon id      - MIntArray
        5 - vector AB       - MVectorArray
        6 - vector AC       - MvectorArray
        """

        return self.p0,\
                self.p1,\
                self.p2,\
                self.normals,\
                self.poly_id,\
                self.AB,\
                self.AC

    @cache.setter
    def cache(self, triangle):
        """ cache setter
        append one triangle to the end of the current cache
        :param triangle:    argument must be of type tuple or list
        it must consist of the following items in the exact same order:
        id  content           data type
        0 - p0              - MPointArray
        1 - p2              - MPointArray
        2 - p1              - MPointArray
        3 - face normal     - MVectorArray
        4 - polygon id      - MIntArray
        5 - vector AB       - MVectorArray
        6 - vector AC       - MvectorArray
        note: no error or type checking is done!
        """

        self.p0.append(triangle[0])
        self.p1.append(triangle[1])
        self.p2.append(triangle[2])
        self.normals.append(triangle[3])
        self.poly_id.append(int(triangle[4]))
        self.AB.append(triangle[5])
        self.AC.append(triangle[6])

    def flush_cache(self):

        self.p0 = om.MPointArray()
        self.p1 = om.MPointArray()
        self.p2 = om.MPointArray()
        self.normals = om.MVectorArray()
        self.poly_id = om.MIntArray()
        self.AB = om.MVectorArray()
        self.AC = om.MVectorArray()
        self.cached = False


    def __len__(self):
        return p0.length()

