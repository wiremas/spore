import maya.cmds as cmds
import maya.OpenMaya as om

import numpy as np

try:
    from scipy.spatial import cKDTree as kd_tree
except ImportError:
    from scipy.spatial import cKDTree as kd_tree

import node_utils
import window_utils


class SporeState(object):
    def __init__(self, node):
        self.node = node
        self.state = None
        self.data_plug = om.MPlug()
        self.data_object = om.MObject()

        self.position = om.MVectorArray()
        self.scale = om.MVectorArray()
        self.rotation = om.MVectorArray()
        self.instance_id = om.MIntArray()

        self.normal = om.MVectorArray()
        self.tangent = om.MVectorArray()
        self.u_coord = om.MDoubleArray()
        self.v_coord = om.MDoubleArray()
        self.poly_id = om.MIntArray()
        self.color = om.MVectorArray()
        self.unique_id = om.MIntArray()

        self.bounding_box = om.MBoundingBox()

        self.np_position = np.empty((0,3), float)
        self.tree = None

        self.initialize_cache()

    def initialize_cache(self):
        """ get cache data from the sporeNode's instanceData plug/
        :param instance_data_plug MPlug: instanceData plug """

        node_fn = node_utils.get_dgfn_from_dagpath(self.node)
        self.data_plug = node_fn.findPlug('instanceData')
        self.data_object = self.data_plug.asMObject()
        array_attr_fn = om.MFnArrayAttrsData(self.data_object)

        self.position = array_attr_fn.vectorArray('position')
        self.scale = array_attr_fn.vectorArray('scale')
        self.rotation = array_attr_fn.vectorArray('rotation')
        self.instance_id = array_attr_fn.intArray('objectIndex')

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
        #  print 'init np arrat:', self.np_position


    def get_node_state(self):
        modes = ['place', 'spray', 'scale', 'align', 'smooth', 'random', 'move', 'id']
        mode_id = cmds.getAttr('{}.contextMode'.format(self.node))
        align_modes = ['normal', 'world', 'object', 'stroke']
        align_id = cmds.getAttr('{}.alignTo'.format(self.node))
        self.state = {'mode': modes[mode_id],
                      'num_samples': cmds.getAttr('{}.numBrushSamples'.format(self.node)),
                      'min_distance': cmds.getAttr('{}.minDistance'.format(self.node)),
                      'align_to': align_modes[align_id],
                      'strength': cmds.getAttr('{}.strength'.format(self.node)),
                      'min_rot': cmds.getAttr('{}.minRotation'.format(self.node))[0],
                      'max_rot': cmds.getAttr('{}.maxRotation'.format(self.node))[0],
                      'uni_scale': cmds.getAttr('{}.uniformScale'.format(self.node)),
                      'min_scale': cmds.getAttr('{}.minScale'.format(self.node))[0],
                      'max_scale': cmds.getAttr('{}.maxScale'.format(self.node))[0],
                      'scale_factor': cmds.getAttr('{}.scaleFactor'.format(self.node)),
                      'min_offset': cmds.getAttr('{}.minOffset'.format(self.node)),
                      'max_offset': cmds.getAttr('{}.maxOffset'.format(self.node)),
                      'min_id': cmds.getAttr('{}.minId'.format(self.node)),
                      'max_id': cmds.getAttr('{}.maxId'.format(self.node))}

    def build_kd_tree(self, refresh_position=False):
        """ build the kd tree """

        if refresh_position:
            self.np_position = np.empty((0, 3), float)
            for i in xrange(self.position.length()):
                position = [[self.position[i].x, self.position[i].y, self.position[i].z]]
                self.np_position = np.append(self.np_position, position, axis=0)

        self.tree = kd_tree(self.np_position)

    def set_state(self):
        """ set the currently cached point data as node instanceData attribute
        and refresh the view to make changes visible """

        self.data_plug.setMObject(self.data_object)
        view = window_utils.active_view()
        view.refresh(True, False)

        print '{} instances place'.format(self.position.length())

    def get_data_object(self):
        """ return the mObject containing instanceData attribute
        :return mObject: """

        return self.data_object

    def append_point(self, position, scale, rotation, instance_id, normal, tangent, u_coord, v_coord, poly_id, color):
        """ append a new point to the cache """

        if isinstance(position, om.MVector):
            self.position.append(position)
            self.np_position = np.append(self.np_position,
                                        np.array([[position.x,
                                                    position.y,
                                                    position.z]]),
                                        axis=0)
        elif isinstance(position, om.MPoint):
            self.position.append(om.MVector(position.x, position.y, position.z))
            self.np_position = np.append(self.np_position,
                                        np.array([[position.x,
                                                    position.y,
                                                    position.z]]),
                                        axis=0)
        elif (isinstance(position, tuple) or isinstance(position, list)) and len(position) == 3:
            self.position.append(om.MVector(position[0], position[1], position[2]))
            self.np_position = np.append(self.np_position,
                                        np.array([[position[0],
                                                    position[1],
                                                    position[2]]]),
                                        axis=0)
        else:
            raise TypeError('Position attribute must be of type: MVector, MPoint, tuple or list.')

        if isinstance(scale, om.MVector):
            self.scale.append(scale)
        elif (isinstance(scale, tuple) or isinstance(scale, list)) and len(scale) == 3:
            self.scale.append(om.MVector(scale[0], scale[1], scale[2]))
        else:
            raise TypeError('Invalid input for scale attr: {}'.format(type(scale)))

        if isinstance(rotation, om.MVector):
            self.rotation.append(rotation)
        elif (isinstance(rotation, tuple) or isinstance(rotation, list)) and len(rotation) == 3:
            self.scale.append(om.MVector(rotation[0], rotation[1], rotation[2]))
        else:
            raise TypeError('Invalid input for rotation attr: {}'.format(type(scale)))

        if isinstance(instance_id, int) or isinstance(instance_id, float):
            self.instance_id.append(int(instance_id))
        else:
            raise TypeError('Invalid input for instance id attr: {}'.format(type(scale)))

        if isinstance(normal, om.MVector):
            self.normal.append(normal)
        elif (isinstance(normal, tuple) or isinstance(normal, list)) and len(normal) == 3:
            self.normal.append(om.MVector(normal[0], normal[1], normal[2]))
        else:
            raise TypeError('Invalid input for normal attr: {}'.format(type(normal)))

        if isinstance(tangent, om.MVector):
            self.tangent.append(tangent)
        elif (isinstance(tangent, tuple) or isinstance(tangent, list)) and len(tangent) == 3:
            self.tangent.append(om.MVector(tangent[0], tangent[1], tangent[2]))
        else:
            raise TypeError('Invalid input for tangent attr: {}'.format(type(tangent)))


        if isinstance(u_coord, float) or isinstance(u_coord, int):
            self.u_coord.append(u_coord)
        else:
            raise TypeError('Invalid input for u coord attr: {}'.format(type(u_coord)))

        if isinstance(v_coord, float) or isinstance(v_coord, int):
            self.v_coord.append(v_coord)
        else:
            raise TypeError('Invalid input for v coord attr: {}'.format(type(v_coord)))

        if isinstance(poly_id, int) or isinstance(poly_id, float):
            self.poly_id.append(int(poly_id))
        else:
            raise TypeError('Invalid input for poly id attr: {}'.format(type(tangent)))

        if isinstance(color, om.MVector):
            self.color.append(color)
        elif (isinstance(color, tuple) or isinstance(color, list)) and len(color) == 3:
            self.color.append(om.MVector(color[0], color[1], color[2]))
        else:
            raise TypeError('Invalid input for color attr: {}'.format(type(tangent)))

        # set position also as np array to set up the kd tree
        #  self.np_position = np.append(self.np_position,
        #                               np.array([[self.position[-1].x,
        #                                          self.position[-1].y,
        #                                          self.position[-1].z]]),
        #                               axis=0)


        # finally append a unique id to each point
        unique_id = self.position.length()
        self.unique_id.append(unique_id)

        return unique_id


    def append_points(self, position, scale, rotation, instance_id, normal, tangent, u_coord, v_coord, poly_id, color):

        appended_ids = om.MIntArray()
        for i in xrange(position.length()):
            self.position.append(position[i])
            self.scale.append(scale[i])
            self.rotation.append(rotation[i])
            self.instance_id.append(instance_id[i])
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


    def set_points(self, index, position, scale, rotation, instance_id, normal, tangent, u_coord, v_coord, poly_id, color):
        for i in xrange(position.length()):
            print 'set point:', index[i]
            self.position.set(position[i], index[i])
            self.scale.set(scale[i], index[i])
            self.rotation.set(rotation[i], index[i])
            self.instance_id.set(instance_id[i], index[i])
            self.normal.set(normal[i], index[i])
            self.tangent.set(tangent[i], index[i])
            self.u_coord.set(u_coord[i], index[i])
            self.v_coord.set(v_coord[i], index[i])
            self.poly_id.set(poly_id[i], index[i])
            self.color.set(color[i], index[i])

            self.np_position.itemset((index[i], 0), position[i].x)
            self.np_position.itemset((index[i], 1), position[i].y)
            self.np_position.itemset((index[i], 2), position[i].z)

    def set_point(self, index, position, scale, rotation, instance_id, normal, tangent, u_coord, v_coord, poly_id, color):

        # TODO - check if index is out of bounds
        if isinstance(position, om.MPoint):
            position = om.MVector(position.x, position.y, position.z)

        self.position.set(position, index)
        self.scale.set(scale, index)
        self.rotation.set(rotation, index)
        self.instance_id.set(instance_id, index)

        self.normal.set(normal, index)
        self.tangent.set(tangent, index)

        self.u_coord.set(u_coord, index)
        self.v_coord.set(v_coord, index)
        self.poly_id.set(poly_id, index)
        self.color.set(color, index)

        # TODO - set as tuple
        #  self.np_position[index] = [position.x, position.y, position.z]

        self.unique_id.set(index + 1, index)



    def length(self):
        # TODO - do some checking if all the array are the same length?

        return self.position.length()

    def get_scale_average(self, index):

        scale_values = np.empty((0,3), float)
        for i in index:
            np.append(scale_values, [[self.scale[i].x,
                                      self.scale[i].y,
                                      self.scale[i].z]], axis=0)

        scale_mean = np.mean(scale_values, axis=0)
        print scale_values, scale_mean

    def get_closest_points(self, position, radius):
        if isinstance(position, om.MPoint):
            position = (position.x, position.y, position.z)
        neighbours = self.tree.query_ball_point(position, radius)
        return neighbours

    def __iter__(self):
        for i in xrange(self.position.length()):
            point = {'position': self.position[i],
                     'scale': self.scale[i],
                     'rotation': self.rotation[i],
                     'instance_id': self.instance_id[i],
                     'normal': self.normal[i],
                     'tangent': self.tangent[i],
                     'u': self.u_coord[i],
                     'v': self.v_coord[i],
                     'poly_id': self.poly_id[i],
                     'color': self.color[i],
                     'unique_id': self.unique_id[i]}

            yield point


    def __del__(self):
        print 'del ptc'

