import math
import random

import maya.OpenMaya as om




def get_rotation(initial_rotation, dir_vector, vector_weight):
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
    #  r_x = math.radians(random.uniform(min_rotation[0], max_rotation[0]))
    #  r_y = math.radians(random.uniform(min_rotation[1], max_rotation[1]))
    #  r_z = math.radians(random.uniform(min_rotation[2], max_rotation[2]))

    mat = om.MTransformationMatrix()

    util = om.MScriptUtil()
    util.createFromDouble(initial_rotation[0], initial_rotation[1], initial_rotation[2])
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
