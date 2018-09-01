import sys
import time

import maya.cmds as cmds
import maya.OpenMaya as om

import numpy as np

try:
    from scipy.spatial import cKDTree as kd_tree
except ImportError:
    from scipy.spatial import cKDTree as kd_tree

import node_utils
import window_utils
import logging_util



class InstanceData(object):
    """ the spore node's internal instance data object keeps track of
    scattered points and allows to set, add, modify or query points """

    def __init__(self, node):

        log_lvl = sys._global_spore_dispatcher.spore_globals['LOG_LEVEL']
        self.logger = logging_util.SporeLogger(__name__, log_lvl)


        dg_fn = om.MFnDependencyNode(node)
        self.node_name = dg_fn.name()
        self.node = node # TODO - hold on to selection list instead of mobj
        #  self.bounding_box = None
        self.state = None
        self.data_plug = om.MPlug()
        self.data_object = om.MObject()

        # instance data attributes
        self.position = om.MVectorArray()
        self.scale = om.MVectorArray()
        self.rotation = om.MVectorArray()
        self.instance_id = om.MIntArray()
        self.visibility = om.MIntArray()
        self.normal = om.MVectorArray()
        self.tangent = om.MVectorArray()
        self.u_coord = om.MDoubleArray()
        self.v_coord = om.MDoubleArray()
        self.poly_id = om.MIntArray()
        self.color = om.MVectorArray()
        self.unique_id = om.MIntArray()

        self.exclusive_paint = []

        # collect points for kd tree
        self.np_position = np.empty((0,3), float)
        self.tree = None

        self.logger.info('Instanciate new InstanceData object for: {}'.format(self.node_name))

    def initialize_data(self):
        """ get cache data from the sporeNode's instanceData plug/
        :param instance_data_plug MPlug: instanceData plug """

        node_fn = om.MFnDependencyNode(self.node)
        self.data_plug = node_fn.findPlug('instanceData')
        self.data_object = self.data_plug.asMObject()
        array_attr_fn = om.MFnArrayAttrsData(self.data_object)

        self.position = array_attr_fn.vectorArray('position')
        self.scale = array_attr_fn.vectorArray('scale')
        self.rotation = array_attr_fn.vectorArray('rotation')
        self.instance_id = array_attr_fn.intArray('objectIndex')
        self.visibility = array_attr_fn.intArray('visibility')
        self.normal = array_attr_fn.vectorArray('normal')
        self.tangent = array_attr_fn.vectorArray('tangent')
        self.u_coord = array_attr_fn.doubleArray('u_coord')
        self.v_coord = array_attr_fn.doubleArray('v_coord')
        self.poly_id = array_attr_fn.intArray('poly_id')
        self.color = array_attr_fn.vectorArray('color')
        self.unique_id = array_attr_fn.intArray('unique_id')

        # TODO - set bb

        # get position as numpy array
        for i in xrange(self.position.length()):
            position = [[self.position[i].x, self.position[i].y, self.position[i].z]]
            self.np_position = np.append(self.np_position, position, axis=0)

        self.logger.debug('Initialize InstanceData object for: {}'.format(self.node_name))

    def set_state(self):
        """ set the currently cached point data as node instanceData attribute
        and refresh the view to make changes visible """

        self.data_plug.setMObject(self.data_object)
        view = window_utils.active_view()
        view.refresh(True, False)

        node_fn = om.MFnDependencyNode(self.node)
        num_spores_plug = node_fn.findPlug('numSpores')
        num_spores_plug.setInt(len(self))


    def get_data_object(self):
        """ return the mObject containing instanceData attribute
        :return mObject: """

        return self.data_object


    def append_points(self, position, scale, rotation, instance_id, visibility, normal, tangent, u_coord, v_coord, poly_id, color):
        """ append the given array to the instance data object
        :param position:
        :param scale:
        :param rotation:
        :param instance_id:
        :param visibility:
        :param normal:
        :param tangent:
        :param u_coord:
        :param v_coord:
        :param poly_id:
        :param color:
        :return: """

        appended_ids = om.MIntArray()
        for i in xrange(position.length()):
            self.position.append(position[i])
            self.scale.append(scale[i])
            self.rotation.append(rotation[i])
            self.instance_id.append(instance_id[i])
            self.visibility.append(visibility[i])
            self.normal.append(normal[i])
            self.tangent.append(tangent[i])
            self.u_coord.append(u_coord[i])
            self.v_coord.append(v_coord[i])
            self.poly_id.append(poly_id[i])
            self.color.append(color[i])

            # append position to numpy array
            np_position = [[position[i].x, position[i].y, position[i].z]]
            self.np_position = np.append(self.np_position, np_position, axis=0)

            self.unique_id.append(self.position.length() - 1)
            appended_ids.append(self.position.length() - 1)

        return appended_ids


    def set_points(self, index, position=None, scale=None, rotation=None,
                   instance_id=None, visibility=None, normal=None,
                   tangent=None, u_coord=None, v_coord=None, poly_id=None,
                   color=None):
        """ set points identified by the given index(s) for the given array(s)
        if an index is not within the bounds of the instance data object
        the operation will fail. if length of the given arrays is not the same
        the operation will fail.
        :param index list: list in indexes to set
        :param position MVectorArray: array of position data
        :param scalae MVectorArray:
        :param rotation MVectorArray:
        :param instance_id MIntArray
        :param visibility MIntArray
        :param normal MVectorArray
        :param tangent MVectorArray
        :param u_coord MDoubleArray
        :param v_coord MDoubleArray
        :param poly_id MIntArray
        :param color MVectorArray """

        # check input
        try:
            if position:
                assert len(index) == position.length()
            if scale:
                assert len(index) == scale.length()
            if rotation:
                assert len(index) == rotation.length()
            if instance_id:
                assert len(index) == instance_id.length()
            if visibility:
                assert len(index) == visibility.length()
            if normal:
                assert len(index) == normal.length()
            if tangent:
                assert len(index) == tangent.length()
            if u_coord:
                assert len(index) == u_coord.length()
            if v_coord:
                assert len(index) == v_coord.length()
            if poly_id:
                assert len(index) == poly_id.length()
            if color:
                assert len(index) == color.length()
        except AssertionError:
            self.logger.error('Could not set points: Array length does not match'.format(self.node_name))
            return

        if index:
            if sorted(index)[-1] >= len(self):
                self.logger.error('Could not set points: Operation would generate null pointer')
                return

        # set points
        for i in xrange(len(index)):
            if position:
                self.position.set(position[i], index[i])
                self.np_position.itemset((index[i], 0), position[i].x)
                self.np_position.itemset((index[i], 1), position[i].y)
                self.np_position.itemset((index[i], 2), position[i].z)
            if scale:
                self.scale.set(scale[i], index[i])
            if rotation:
                self.rotation.set(rotation[i], index[i])
            if instance_id:
                self.instance_id.set(instance_id[i], index[i])
            if visibility:
                self.visibility.set(visibility[i], index[i])
            if normal:
                self.normal.set(normal[i], index[i])
            if tangent:
                self.tangent.set(tangent[i], index[i])
            if u_coord:
                self.u_coord.set(u_coord[i], index[i])
            if v_coord:
                self.v_coord.set(v_coord[i], index[i])
            if poly_id:
                self.poly_id.set(poly_id[i], index[i])
            if color:
                self.color.set(color[i], index[i])

            self.unique_id.set(index[i], index[i])

    def set_length(self, length):
        """ set the instance data arrays to the given length
        do nothing when the given length is shorter than the current
        arrays since this would destroy instance data """

        if len(self) > length:
            self.logger.warn('Set length would destroy instance Data. Skipped...')
            return

        self.position.setLength(length)
        self.rotation.setLength(length)
        self.scale.setLength(length)
        self.instance_id.setLength(length)
        self.visibility.setLength(length)
        self.normal.setLength(length)
        self.tangent.setLength(length)
        self.u_coord.setLength(length)
        self.v_coord.setLength(length)
        self.poly_id.setLength(length)
        self.color.setLength(length)
        self.unique_id.setLength(length)
        self.np_position.resize(length, 3, refcheck=False)

    def set_point(self, index, position, scale, rotation, instance_id,
                  visibility, normal, tangent, u_coord, v_coord, poly_id, color):
        """ set the given index of the array to the given data """

        if index >= self.position.length():
            self.logger.error('Can\'t set point data: Index out of range')
            return

        self.position.set(position, index)
        self.rotation.set(rotation, index)
        self.scale.set(scale, index)
        self.instance_id.set(instance_id, index)
        self.visibility.set(visibility, index)
        self.normal.set(normal, index)
        self.tangent.set(tangent, index)
        self.u_coord.set(u_coord, index)
        self.v_coord.set(v_coord, index)
        self.poly_id.set(poly_id, index)
        self.color.set(color, index)
        self.unique_id.set(index, index)
        self.np_position[index] = [position.x, position.y, position.z]

    def insert_point(self, index, position, scale, rotation, instance_id,
                     visibility, normal, tangent, u_coord, v_coord, poly_id,
                     color):

        if index > len(self):
            self.logger.error('Failed to insert point: index out of range')
            return

        self.position.insert(position, index)
        self.scale.insert(scale, index)
        self.rotation.insert(rotation, index)
        self.instance_id.insert(instance_id, index)
        self.visibility.insert(visibility, index)
        self.normal.insert(normal, index)
        self.tangent.insert(tangent, index)
        self.u_coord.insert(u_coord, index)
        self.v_coord.insert(v_coord, index)
        self.poly_id.insert(poly_id, index)
        self.color.insert(color, index)
        self.unique_id.insert(index, index)
        self.np_position = np.insert(self.np_position, index, [position.x,
                                                               position.y,
                                                               position.z],
                                    axis=0)

    def update_unique_id(self):
        """ make sure each point has a unique id.
        this method should be called after inserting or deleting points """

        for i in xrange(len(self) - 1):
            self.unique_id[i] = i

    def length(self):
        # TODO - do some checking if all the array are the same length?
        # TODO - this should be deprecated since we can use len()
        return len(self)

    def build_kd_tree(self, refresh_position=False):
        """ build the kd tree """

        t1 = time.time()

        if refresh_position:
            self.np_position = np.empty((0, 3), float)
            for i in xrange(self.position.length()):
                position = [[self.position[i].x, self.position[i].y, self.position[i].z]]
                self.np_position = np.append(self.np_position, position, axis=0)

        self.tree = kd_tree(self.np_position)

        t_result = round(time.time() - t1, 5)
        #  self.logger.debug('Built KDTree ({}) for {} points in: {}s'.format(self.node_name, len(self), t_result))

    def get_scale_average(self, index):
        """ get the average scale value for the given list of indexes
        @param index list: list of indexes
        @return x, y, z scale mean """

        scale_values = np.empty((0,3), float)
        for i in index:
            scale_values = np.append(scale_values, [[self.scale[i].x,
                                                     self.scale[i].y,
                                                     self.scale[i].z]],
                                     axis=0)

        scale_mean = np.mean(scale_values, axis=0)
        return scale_mean

    def get_rotation_average(self, index):
        """ get the average scale value for the given list of indexes
        @param index list: list of indexes
        @return x, y, z scale mean """

        rotation_value = np.empty((0,3), float)
        for i in index:
            rotation_value = np.append(rotation_value, [[self.rotation[i].x,
                                                         self.rotation[i].y,
                                                         self.rotation[i].z]],
                                     axis=0)

        rotation_value = np.mean(rotation_value, axis=0)
        return rotation_value

    def get_closest_points(self, position, radius, exclude=[]):
        """ get a list of all indexes within the given radius from the
        given position
        :param position: MPoint, List, tupe or np.array
        :param radius
        :param exclude: list of instance ids to exclude from nearest
                        neighbour search """

        if isinstance(position, om.MPoint):
            position = (position.x, position.y, position.z)
        neighbours = self.tree.query_ball_point(position, radius, eps=radius/10)

        if exclude:
            instance_ids = np.array([])
            for index in neighbours:
                instance_ids = np.append(instance_ids, self.instance_id[index])

            valid_index = np.array([])
            for index in exclude:
                valid_index = np.append(valid_index, np.where(instance_ids==index))

            neighbours = [neighbours[int(i)] for i in valid_index]
            return neighbours

        else:
            return list(neighbours)

    def is_valid(self):
        """ check if the internal data is in sync. otherwise try to
        repair some of the arrays if possible. """

        try:
            assert len(self) == self.rotation.length()
            assert len(self) == self.scale.length()
            assert len(self) == self.instance_id.length()
            assert len(self) == self.normal.length()
            assert len(self) == self.tangent.length()
            assert len(self) == len(self.np_position)
        except AssertionError:
            self.logger.error('InstanceData validation failed!')
            return False

        try:
            assert len(self) == self.visibility.length()
        except AssertionError:
            self.logger.warn(
                'InstanceData validation faild. Trying to repair visibility...'
            )
            self.visibility.setLength(len(self))
            [self.visibility.set(1, i) for i in range(len(self))]
        try:
            assert len(self) == self.u_coord.length()
        except AssertionError:
            self.logger.warn(
                'InstanceData validation faild. Trying to repair u coords...'
            )
            self.u_coord.setLength(len(self))
            [self.u_coord.set(0, i) for i in range(len(self))]
        try:
            assert len(self) == self.v_coord.length()
        except AssertionError:
            self.logger.warn(
                'InstanceData validation faild. Trying to repair v coords...'
            )
            self.v_coord.setLength(len(self))
            [self.v_coord.set(0, i) for i in range(len(self))]
        try:
            assert len(self) == self.poly_id.length()
        except AssertionError:
            self.logger.warn(
                'InstanceData validation faild. Trying to repair poly id...'
            )
            self.poly_id.setLength(len(self))
            [self.poly_id.set(0, i) for i in range(len(self))]
        try:
            assert len(self) == self.color.length()
        except AssertionError:
            self.logger.warn(
                'InstanceData validation faild. Trying to repair color...'
            )
            self.color.setLength(len(self))
            [self.color.set(1, i) for i in range(len(self))]
        try:
            assert len(self) == self.unique_id.length()
        except AssertionError:
            self.logger.warn(
                'InstanceData validation faild. Trying to repair point id...'
            )
            self.unique_id.setLength(len(self))
            [self.unique_id.set(i, i) for i in range(len(self))]

        return True

    def clear(self):
        """ remove all points from the object """

        [self.visibility.set(0, i) for i in xrange(self.visibility.length())]
        self.clean_up()
        self.set_state()

    def clean_up(self):
        """ remove all points that a invisible after the delete brush
        has initially hidden them and is tearn down when the has been context left """

        self.logger.debug('Cleaning up InstanceData...')

        if not self.is_valid():
            self.logger.error('Cleanup operation failed, Instance Data is out of sync.')
            return

        invalid_ids = sorted([i for i in xrange(self.visibility.length()) if self.visibility[i] == 0],
                             reverse=True)

        if invalid_ids:
            for index in invalid_ids:
                self.position.remove(index)
                self.scale.remove(index)
                self.rotation.remove(index)
                self.instance_id.remove(index)
                self.visibility.remove(index)
                self.normal.remove(index)
                self.tangent.remove(index)
                self.u_coord.remove(index)
                self.v_coord.remove(index)
                self.poly_id.remove(index)
                self.color.remove(index)
                self.unique_id.remove(index)
                self.np_position = np.delete(self.np_position, index, 0)
            self.update_unique_id()


    def __len__(self):
        return self.position.length()

    def __iter__(self):
        for i in xrange(self.position.length()):
            point = {'position': self.position[i],
                     'scale': self.scale[i],
                     'rotation': self.rotation[i],
                     'instance_id': self.instance_id[i],
                     'visibility': self.visibility[i],
                     'normal': self.normal[i],
                     'tangent': self.tangent[i],
                     'u': self.u_coord[i],
                     'v': self.v_coord[i],
                     'poly_id': self.poly_id[i],
                     'color': self.color[i],
                     'unique_id': self.unique_id[i]}

            yield point

    def __add__(self, other):
        """ add the given other instance data object to this one
        note: the unique_id will be updated """

        if isinstance(other, InstanceData):
            self.is_valid()
            other.is_valid()

            if not len(other):
                return

            ids = range(len(self), len(self) + len(other))
            self.set_length(len(self) + len(other))
            self.set_points(ids, other.position, other.rotation, other.scale,
                            other.instance_id, other.visibility, other.normal,
                            other.tangent, other.u_coord, other.v_coord,
                            other.poly_id, other.color)
            return self

        else:
            self.logger.error('Can only add InstanceData to InstanceData. Not {} to InstanceData'.format(type(other)))
            return

    def __iadd__(self, other):
        return self + other

    def __del__(self):
        #  print 'del ptc'
        pass

