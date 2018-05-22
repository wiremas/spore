import sys
import maya.OpenMaya as om


class PtcCache(object):
    """
    container for sampled points
    usage:  1. cache gets filled with point data from the sampler
            2. once sampling is finished the cache gets locked
    """

    def __init__(self):

        self._locked = False

        # sampled data from the ptc
        self.points = om.MPointArray()
        self.normals = om.MVectorArray()
        self.poly_ids = om.MIntArray()
        self.u_coords = om.MDoubleArray()
        self.v_coords = om.MDoubleArray()
        self.user = []
        self.bb = None

    @property
    def bounding_box(self):
        return self.bb

    @bounding_box.setter
    def bounding_box(self, bb):
        self.bb = bb

    def length(self):
        return self.points.length()

    def append(self, point, normal, index, u, v, user_data=None):
        """
        append a given point and its associated data to the cache.
        note:   this method gets called a lot from the ptc_sampler.
                therefore no type checking is done.

        :param point:   position of the point                   - MPoint
        :param normal:  normal of closest triangle              - MVector
        :param index:   index of the closest polygon            - MInt
        :param u:       u_coordinate of the closest polygon     - MDouble
        :param v:       v coordinate of the closest polygon     - MDouble
        :return:
        """

        if self.bb:
            self.points.append(point)
            self.normals.append(normal)
            self.poly_ids.append(index)
            self.u_coords.append(u)
            self.v_coords.append(v)
            self.user.append(user_data)
        else:
            raise RuntimeError ('No bounding box set for point cache')

    def remove(self, index):

        def remove_point(index):
            # if index >= self.points.length():
            self.points.remove(index)
            self.normals.remove(index)
            self.poly_ids.remove(index)
            self.u_coords.remove(index)
            self.v_coords.remove(index)

            # self.user.pop(index)

            # self.orig_points.remove(index)
            # self.lifespan_pp.remove(index)
            # self.age_pp.remove(index)

            # self.id_pp.remove(index)
            # self.rgb_pp.remove(index)
            # self.rotation_pp.remove(index)
            # self.scale_pp.remove(index)
            # else:
            #     raise IndexError ('Remove point from cache: Index out of range')

        if type(index) == type(list()):

            for i in index:
                remove_point(i)

        elif type(index) == type(int()):
            remove_point(index)

        else:
            raise TypeError ('Unsupported type: {} - must be of type int() or list(int(), int())'.format(type(index)))

    def get_point(self, index):
        """
        return a point at the given position in the cache
        :param index:   position of the point in the cache
        :return:        MPoint        - position of the point
                        MVector       - normal of closest triangle
                        MInt          - index of the closest polygon
                        MDouble       - u_coordinate of the closest polygon
                        MDouble       - v coordinate of the closest polygon
        """

        p = self.points[index]
        n = self.normals[index]
        i = self.poly_ids[index]
        u = self.u_coords[index]
        v = self.v_coords[index]
        user = self.user[index]

        return p, n, i, u, v, user

    def get_points(self):
        """
        return all points from the cache
        :return:        MPointArray   - list of all point positions
                        MVectorArray  - list of all normals
                        MIntArray     - list of all polygon ids
                        MDoubleArray  - list of all u_coordinates
                        MDoubleArray  - list of all v coordinates
        """

        return self.points, self.normals, self.poly_ids, self.u_coords, self.v_coords, self.user

    def validate_cache(self):

        try:
            assert self.points.length() == \
                   self.normals.length() == \
                   self.poly_ids.length() == \
                   self.u_coords.length() == \
                   self.v_coords.length()
        except AssertionError:
            raise RuntimeError('Point Cache Error: cached arrays do not match in size')

class PointData(PtcCache):
    def __init__(self):
        super(PointData, self).__init__()

        self.points = om.MVectorArray()
        self.normals = om.MVectorArray()
        self.u_coords = om.MDoubleArray()
        self.v_coords = om.MDoubleArray()
        self.poly_id = om.MDoubleArray()

        self.orig_points = om.MVectorArray()
        self.rotation = om.MVectorArray()
        self.scale = om.MVectorArray()
        self.rgb = om.MVectorArray()
        self.instance_id = om.MDoubleArray()
        self.lifespan = om.MDoubleArray()
        self.age = om.MDoubleArray()

    def __iadd__(self, ptc):

        self.__add__(ptc)

    def __add__(self, ptc):
        for i in xrange(ptc.length()):
            self.append(ptc.points[i],
                     ptc.normals[i],
                     ptc.u_coords[i],
                     ptc.v_coords[i],
                     ptc.poly_id[i],
                     ptc.orig_points[i],
                     ptc.rotation[i],
                     ptc.scale[i],
                     ptc.rgb[i],
                     ptc.instance_id[i],
                     ptc.lifespan[i],
                     ptc.age[i])
            return self

    #  def __repr__(self):
    #      self.validate_cache()
    #      return 'Valid point cache contains {} points'.format(self.length())

    def append(self,
               point,
               normal,
               u_coord,
               v_coord,
               poly_id,
               orig_point,
               rotation,
               scale,
               rgb,
               instance_id,
               lifespan, age):

        self.points.append(point)
        self.normals.append(normal)
        self.u_coords.append(u_coord)
        self.v_coords.append(v_coord)
        self.poly_id.append(poly_id)

        self.orig_points.append(orig_point)
        self.rotation.append(rotation)
        self.scale.append(scale)
        self.rgb.append(rgb)
        self.instance_id.append(instance_id)
        self.lifespan.append(lifespan)
        self.age.append(age)

    '''
    def set(self, index, point, normal, c_coord, v_coord, poly_id, orig_point,
            rotation, scale, rgb, instance_id, lifespan, age):
        if index <= self.length() - 1:
            self.points.set(point, index)
            self.normals.set(normal, index)
            self.u_coords.set(u_coord, index)
            self.v_coords.set(v_coord, index)
            self.poly_id.set(poly_id, index)

            self.orig_points.set(orig_point, index)
            self.rotation.set(rotation, index)
            self.scale.set(scale, index)
            self.rgb.set(rgb, index)
            self.instance_id.set(instance_id, index)
            self.lifespan.set(lifespacn, index)
            self.age.set(age, index)
        else:
            raise IndexError('Failed to set point: Index out of range')'''

    ''' def get_point(self, index):
        """ get a point specified by it's index
        :param index:
        :return: position, scale, rotation, normal, instance_id, color """
        if index <= self.length() - 1:
            p = self.points(index)
            n = self.normals(index)
            #  u = self.u_coords(index)
            #  v = self.v_coords(index)
            #  i = self.poly_id(index)

            #  o = self.orig_points(index)
            r = self.rotation(index)
            s = self.scale(index)
            c = self.rgb(index)
            i = self.instance_id(index)
            #  l = self.lifespan(index)
        else:
            raise IndexError('Failed to set point: Index out of range')

        return p, s, r, n, i, c '''

    def remove_point(self, index):
        if index <= self.length() - 1:
            self.points.remove(index)
            self.normals.remove(index)
            self.u_coords.remove(index)
            self.v_coords.remove(index)
            self.poly_id.remove(index)

            self.orig_points.remove(index)
            self.rotation.remove(index)
            self.scale.remove(index)
            self.rgb.remove(index)
            self.instance_id.remove(index)
            self.lifespan.remove(index)
            self.age.remove(index)
        else:
            raise IndexError('Remove point from cache: Index out of range')

        if type(index) == type(list()):

            for i in index:
                remove_point(i)

        elif type(index) == type(int()):
            remove_point(index)

        else:
            raise TypeError('Unsupported type: use single int or list of ints')

    def validate_cache(self):
        try:
            assert self.points == \
                self.normals == \
                self.u_coords == \
                self.v_coords == \
                self.poly_id == \
                self.orig_points == \
                self.rotation == \
                self.scale == \
                self.rgb == \
                self.instance_id == \
                self.lifespan == \
                self.age
        except AssertionError, e:
            raise RuntimeError('Point Cache error: Cache corrupted'), sys.exc_info(), sys.exc_info()
