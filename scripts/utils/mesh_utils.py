import maya.OpenMaya as om

import window_utils

def hit_test(target, x, y, invert_y=True):

    origin = om.MPoint()
    direction = om.MVector()
    view = window_utils.active_view()

    if invert_y:
        y = view.portHeight() - y

    view.viewToWorld(x, y, origin, direction)
    mesh_fn = get_mesh_fn(target)

    if mesh_fn:
        points = om.MPointArray()
        intersect = mesh_fn.intersect(origin, direction, points, 1.0e-3, om.MSpace.kWorld)
        if intersect:
            point = points[0]
            normal = om.MVector()
            mesh_fn.getClosestNormal(point, normal, om.MSpace.kWorld)
            tangent = get_tangent(normal)

            position = (point.x, point.y, point.z)
            tangent = (tangent.x, tangent.y, tangent.z)
            normal = (normal.x, normal.y, normal.z)
            return (position, normal, tangent)


def get_mesh_fn(target):
    """ get mesh function set for the given target
    :param target: dag path of the mesh
    :return MFnMesh """

    if isinstance(target, str) or isinstance(target, unicode):
        slls = om.MSelectionList()
        slls.add(target)
        ground_path = om.MDagPath()
        slls.getDagPath(0, ground_path)
        ground_path.extendToShapeDirectlyBelow(0)
        ground_node = ground_path.node()
    elif isinstance(target, om.MObject):
        ground_node = target
        ground_path = target
    elif isinstance(target, om.MDagPath):
        ground_node = target.node()
        ground_path = target
    else:
        raise TypeError('Must be of type str, MObject or MDagPath, is type: {}'.format(type(target)))

    if ground_node.hasFn(om.MFn.kMesh):
        return om.MFnMesh(ground_path)
    else:
        raise TypeError('Target must be of type kMesh')


def get_closest_point_and_normal(point, target):
    """ find the closest point and normal to the given point
    :return: closest point
             closest normal
             distance to the closest point """

    closest_point = None
    closest_normal = None
    #  shortest_distance = None

    #  for target in targets:
    mesh_fn = get_mesh_fn(target)
    out_point = om.MPoint()
    out_normal = om.MVector()
    mesh_fn.getClosestPointAndNormal(point, out_point, out_normal, om.MSpace.kWorld)
    #  out_tangent = get_tangent(normal)

    return out_point, out_normal


def get_tangent(normal):
    """ return a normalized tangent for the given normal I
    :param normal MVector: normal vector
    :return MVector: tangent """

    if isinstance(normal, om.MVector):
        normal = normal.x, normal.y, normal.z
    else:
        raise TypeError('Input must be of type MVector, is: {}'.format(type(normal)))

    if normal[0] >= normal[1]:
        u = om.MVector(normal[2], 0, -normal[1])
    else:
        u = om.MVector(0, normal[2], -normal[1])

    normal = om.MVector(normal[0], normal[1], normal[2])
    tangent = (normal ^ u).normal()
    return tangent


def normal_to_eulter(position, normal):
    pass

def get_uv_at_point(target, point, uv_set=None, poly_id=None):
    """ get closest UV coords of the target at the given point
    :param target str: name of the target object
    :param point MPoint: """

    util = om.MScriptUtil()
    uv_coords_ptr = util.asFloat2Ptr()

    mesh_fn = get_mesh_fn(target)
    mesh_fn.getUVAtPoint(point, uv_coords_ptr, om.MSpace.kObject, uv_set, poly_id)

    u_coord = util.getFloat2ArrayItem(uv_coords_ptr, 0, 0)
    v_coord = util.getFloat2ArrayItem(uv_coords_ptr, 0, 1)

    return u_coord, v_coord
