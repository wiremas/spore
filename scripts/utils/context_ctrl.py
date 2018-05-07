import math
import random

from maya import cmds
import maya.OpenMaya as om

from PySide2.QtCore import Slot

from spore.utils import node_utils, window_utils, mesh_utils
from spore.data import point_cache
reload(point_cache)


class ContextCtrl(object):

    def __init__(self, parent, brush_state):
        self.parent = parent
        self.brush_state = brush_state
        self.node_state = None
        self.node_name = None
        self.node_fn = None
        self.data_plug = None
        self.point_cache = point_cache.PointCloud()
        self.last_points = point_cache.PointCloud()
        #  self.node_fn = None

        self.connect_signal()

    def connect_signal(self):
        self.parent.sender.press.connect(self.do_press)
        self.parent.sender.drag.connect(self.do_drag)
        self.parent.sender.release.connect(self.do_release)

    def set_node(self, node_name):
        self.node_name = node_name
        #  node = node_utils.get_mobject_from_name(node_name)
        #  self.node_fn = node_utils.get_dgfn_from_dagpath(node_name)


    def get_node_state(self, node_name):
        """ fetch all node attributes that we need for painting
        :parama node_name str: the full path name of the node """

        self.node_name = node_name
        self.node_state = {'mode': cmds.getAttr('{}.contextMode'.format(self.node_name)),
                        'num_samples': cmds.getAttr('{}.numBrushSamples'.format(self.node_name)),
                        'min_distance': cmds.getAttr('{}.minDistance'.format(self.node_name)),
                        'align_to': cmds.getAttr('{}.alignTo'.format(self.node_name)),
                        'strength': cmds.getAttr('{}.strength'.format(self.node_name)),
                        'min_rot': cmds.getAttr('{}.minRotation'.format(self.node_name))[0],
                        'max_rot': cmds.getAttr('{}.maxRotation'.format(self.node_name))[0],
                        'uni_scale': cmds.getAttr('{}.uniformScale'.format(self.node_name)),
                        'min_scale': cmds.getAttr('{}.minScale'.format(self.node_name))[0],
                        'max_scale': cmds.getAttr('{}.maxScale'.format(self.node_name))[0],
                        'min_offset': cmds.getAttr('{}.minOffset'.format(self.node_name)),
                        'max_offset': cmds.getAttr('{}.maxOffset'.format(self.node_name)),
                        'min_id': cmds.getAttr('{}.minId'.format(self.node_name)),
                        'max_id': cmds.getAttr('{}.maxId'.format(self.node_name))}

        print self.node_state

        node_fn = node_utils.get_dgfn_from_dagpath(node_name)
        self.data_plug = node_fn.findPlug('instanceData')
        self.point_cache.get_from_plug(self.data_plug)


    @Slot(dict)
    def do_press(self, brush_state):

        # place mode
        if self.node_state['mode'] == 0:

            position, scale, rotation, instance_id, normal, tangent, u_coord, v_coord, poly_id, color = self.insert_point()
            self.last_points = point_cache.PointCloud()
            self.last_points.append_point(position, scale, rotation, instance_id,
                                          normal, tangent, u_coord, v_coord,
                                          poly_id, color)

        # spray mode
        if self.node_state['mode'] == 1:
            self.last_points = point_cache.PointCloud()
            for i in xrange(self.node_state['num_samples']):
                position, scale, rotation, instance_id, normal, tangent, u_coord, v_coord, poly_id, color = self.insert_point()
                self.last_points.append_point(position, scale, rotation, instance_id,
                                            normal, tangent, u_coord, v_coord,
                                            poly_id, color)

    @Slot(dict)
    def do_drag(self, brush_state):

        print self.brush_state.stroke_direction
        # insert mode
        if not self.brush_state.drag_mode:
            if (self.node_state['mode'] == 0\
            or self.node_state['mode'] == 1):
                self.insert_point()

        # drag mode
        if self.brush_state.drag_mode:
            if (self.node_state['mode'] == 0\
            or self.node_state['mode'] == 1):
                self.transform_points(self.last_points)



    @Slot(dict)
    def do_release(self, brush_state):

        if (self.node_state['mode'] == 0 or self.node_state['mode'] == 1):
            self.insert_point()


    def insert_point(self):
        """ get a random point within the brush radius """


        position = om.MPoint(self.brush_state.position[0],
                             self.brush_state.position[1],
                             self.brush_state.position[2])
        normal = om.MVector(self.brush_state.normal[0],
                            self.brush_state.normal[1],
                            self.brush_state.normal[2])
        tangent = om.MVector(self.brush_state.tangent[0],
                             self.brush_state.tangent[1],
                             self.brush_state.tangent[2])

        if self.node_state['mode'] == 1:
            brush_rad = self.brush_state.radius

            rotation = om.MQuaternion(random.uniform(0, 2 * math.pi), normal)
            tangential_vector = tangent.rotateBy(rotation)
            rand_pos =  position + tangential_vector * random.uniform(0, brush_rad)
            position, normal = mesh_utils.get_closest_point_and_normal(rand_pos, self.brush_state.target)
            tangent = mesh_utils.get_tangent(normal)

        scale = get_scale(self.node_state['min_scale'],
                          self.node_state['max_scale'],
                          self.node_state['uni_scale'])

        direction = normal
        if self.node_state['align_to'] == 1:
            # TODO - get object up vector
            pass

        elif self.node_state['align_to'] == 2:
            # TODO - get stroke direction
            direction = om.MVector(self.brush_state.direction[0],
                                   self.brush_state.direction[1],
                                   self.brush_state.direction[2])

        rotation = get_rotation(self.node_state['min_rot'],
                                self.node_state['max_rot'],
                                direction,
                                self.node_state['strength'])

        if self.node_state['min_offset'] or self.node_state['max_offset']:
            position = get_offset(self.node_state['min_offset'],
                                  self.node_state['max_offset'],
                                  normal, position)


        # might be expensive?
        print self.brush_state.target
        u_coord, v_coord = mesh_utils.get_uv_at_point(self.brush_state.target,
                                                      position)

        poly_id = 0
        color = om.MVector(0, 0, 0)
        position = om.MVector(position[0], position[1], position[2])

        # TODO - get ID
        instance_id = random.randint(self.node_state['min_id'],
                               self.node_state['max_id'])

        index = self.point_cache.append_point(position, scale, rotation,
                                              instance_id, normal, tangent,
                                              u_coord, v_coord, poly_id, color)

        # set mObject to instanceData plug
        data_object = self.point_cache.get_data_object()
        self.data_plug.setMObject(data_object)

        # refresh view
        view = window_utils.active_view()
        view.refresh(True, False)

        # return data to cache points for drag mode
        return (position, scale, rotation, instance_id,
                normal, tangent, u_coord, v_coord,
                poly_id, color)

    def transform_points(self, point_cloud):
        """ transform a set of points alsong the target surface and adjust
        all adjust all properties of the point to the new surface location
        @param point_cache PointCloude: point cloud object containing the
                                        the points to be transformed """

        for point in point_cloud:
            index = int(point['unique_id'])
            new_scale = point['scale']
            instance_id = point['instance_id']
            color = point['color']
            new_poly_id = point['poly_id']

            stroke = self.brush_state.stroke_direction
            print 'dir: ', stroke
            position = om.MPoint(point['position'][0], point['position'][1], point['position'][2])
            direction = om.MVector(stroke[0], stroke[1], stroke[2])
            offset_position = position + direction

            new_position, new_normal = mesh_utils.get_closest_point_and_normal(
                                       offset_position, self.brush_state.target)
            new_tangent = mesh_utils.get_tangent(new_normal)
            new_u, new_v = mesh_utils.get_uv_at_point(self.brush_state.target,
                                                      offset_position)

            new_rotation = point['rotation']
            #  new_rotation =

            self.point_cache.set_point(index, new_position, new_scale, new_rotation,
                                 instance_id, new_normal, new_tangent, new_u,
                                 new_v, new_poly_id, color)

            print new_position.x, new_position.y, new_position.z
            view = window_utils.active_view()
            view.refresh(True, False)

            return point_cloud


#  def slerp_rotation(rotation, direction, weigth):
#      """ spherical linear interpolation from an euler rotation into a
#      new direction multiplied by the given weight
#      @param rotation tuple(x,y,z): euler rotation values which will be transformed
#      @param direction tuple(x,y,z): the direction into which we will interpolate
#      @param weight float(0-1): muliplier for interpolation """
#
#      euler_rot = om.MEulerRotation(old_rotation)
#      mat = om.MTransformationMatrix().rotateBy(euler_rot)
#
#      rotation_delta = om.MQuaternion(
#
#  def get_up_from_euler(rotation):



def get_rotation(min_rotation, max_rotation, dir_vector, vector_weight):
    """ Get euler rotation values based on given min/max rotation, a direction
    vector and a weight for the given vector. slerp between direction vector and
    world up vector.
    :param min_rotation tuple(x,y,z): minimum rotation values
    :param max_rotation tuple(x,y,z): maximum rotation values
    :param dir_vector MVector: direction of instance y-up
    :param weight float(0-1): the weigth of the direction
    :return MVector: Mvector containing euler rotation values """

    world_up = om.MVector(0, 1, 0)
    rotation = om.MQuaternion(world_up, dir_vector, vector_weight)

    # get random rotation
    r_x = math.radians(random.uniform(min_rotation[0], max_rotation[0]))
    r_y = math.radians(random.uniform(min_rotation[1], max_rotation[1]))
    r_z = math.radians(random.uniform(min_rotation[2], max_rotation[2]))

    mat = om.MTransformationMatrix()

    util = om.MScriptUtil()
    util.createFromDouble(r_x, r_y, r_z)
    rotation_ptr = util.asDoublePtr()
    mat.setRotation(rotation_ptr, om.MTransformationMatrix.kXYZ)

    mat = mat.asMatrix() * rotation.asMatrix()
    rotation = om.MTransformationMatrix(mat).rotation()

    return om.MVector(math.degrees(rotation.asEulerRotation().x),
                      math.degrees(rotation.asEulerRotation().y),
                      math.degrees(rotation.asEulerRotation().z))

def get_scale(min_scale, max_scale, uniform=True):
    """ return a random scale value between min and max scale
    :param min_scale tupe(x,y,z)
    :param max_scale tupe(x,y,z)
    :param uniform bool: if True get a uniform x,y,z scale
    :return MVector: conaining scale values"""

    if uniform:
        print min_scale, max_scale
        scale_x = scale_y = scale_z = random.uniform(min_scale[0], max_scale[0])

    else:
        scale_x = random.uniform(min_scale[0], max_scale[0])
        scale_y = random.uniform(min_scale[1], max_scale[1])
        scale_z = random.uniform(min_scale[2], max_scale[2])

    return om.MVector(scale_x, scale_y, scale_z)

def get_offset(min_offset, max_offset, position, normal):
    """ offset a given point along the normal
    :param min_offset float():
    :param max_offset float():
    :param position MPoint:
    :param normal MVector:
    :return MVector: containing the offset position """

    rand_o = random.uniform(min_offset, max_offset)
    return om.MVector(position + normal * rand_o)
