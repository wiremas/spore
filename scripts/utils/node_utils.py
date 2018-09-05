"""
module provides quick acces to frequently used node utilities
"""

import math

import maya.OpenMaya as om


def get_dynamic_attributes(mObject):
    """ return all dynamic attributes of a node """

    result = []

    mFnDep = om.MFnDependencyNode()
    objFn = om.MFnDependencyNode(mObject)
    refObj = mFnDep.create(objFn.typeName())
    refFn = om.MFnDependencyNode(refObj)

    if (objFn.attributeCount() > refFn.attributeCount()):
        for i in range(refFn.attributeCount(), objFn.attributeCount()):
            attr = objFn.attribute(i)
            attrFn = om.MFnAttribute(attr)
            result.append(attrFn.name())

    mDagMod = om.MDagModifier()
    mDagMod.deleteNode(refObj)

    return result


def get_mobject_from_name(name):
    """ get mObject from a given dag-path
    :param name : the name or dag-path to a shapenode to return a mObject to """
    sl = om.MSelectionList()
    om.MGlobal.getSelectionListByName(name, sl)
    node = om.MObject()
    sl.getDependNode(0, node)
    return node


def get_dagpath_from_name(name, get_shape=False):
    """ get MDagPath object from a given dag-path
    :param name : dag-path
    :param get_shape : returns the MDagPath object of a given transform's shape """

    sl = om.MSelectionList()
    om.MGlobal.getSelectionListByName(name, sl)
    m_path = om.MDagPath()
    sl.getDagPath(0, m_path)

    if get_shape:
        m_path = m_path.extendToShape()

    return m_path

def get_dgfn_from_dagpath(dagpath):
    """ return the functionset for the given dagpath """

    m_object = get_mobject_from_name(dagpath)
    return om.MFnDependencyNode(m_object)

def get_meshfn_from_dagpath(dagpath):
    """ return a functionset for a specified dagpath
    :param dagpath : input dagpath """

    m_dagpath = get_dagpath_from_name(dagpath)
    return om.MFnMesh(m_dagpath)


def get_dagfn_from_dagpath(dagpath):
    """ return a dag-node functionset to a given dag-path """

    m_dagpath = get_dagpath_from_name(dagpath)
    return om.MFnDagNode(m_dagpath)


def get_transformfn_from_dagpath(dagpath):
    """ return a transform functionset to a given dag-path """

    m_dagpath = get_dagpath_from_name(dagpath)
    return om.MFnTransform(m_dagpath)


def get_instanced_geo(spore_node):
    """ return a list of dag pathes of geometry transformes that
    are connected to the spore node's instancer
    @param spore_node str: the name of the spore node
    @return: list of string or None if no instancer is connected """

    node_fn = get_dgfn_from_dagpath(spore_node)
    instance_plug = node_fn.findPlug('instanceData')
    plugs = om.MPlugArray()
    instancer_plugs = om.MPlugArray()
    instance_geo = []

    if not instance_plug.isNull():
        if instance_plug.connectedTo(plugs, False, True):
            node = plugs[0].node()
            node_fn = om.MFnDagNode(node)
            inst_geo_plug = node_fn.findPlug('inputHierarchy')

            if not inst_geo_plug.isNull():
                for i in xrange(inst_geo_plug.numConnectedElements()):
                    input_plug = inst_geo_plug.elementByPhysicalIndex(i)

                    if input_plug.connectedTo(instancer_plugs, True, True):
                        geo_plug = instancer_plugs[0]
                        geo_node = geo_plug.node()
                        instance_geo.append(om.MFnDagNode(geo_node).fullPathName())

            dg_node_fn = om.MFnDependencyNode(node)
            instancer_node = dg_node_fn.name()

    return instance_geo

def get_instancer(spore_node, as_string=True):
    """ return the instancer node connected to a given spore node
    :param spore_node:
    :param as_string: if true return node name else return mObject """

    node_fn = get_dgfn_from_dagpath(spore_node)
    instance_plug = node_fn.findPlug('instanceData')
    plugs = om.MPlugArray()
    instancer_plugs = om.MPlugArray()
    instance_geo = []

    if not instance_plug.isNull():
        if instance_plug.connectedTo(plugs, False, True):
            node = plugs[0].node()
            node_fn = om.MFnDagNode(node)
            if as_string:
                return node_fn.fullPathName()
            else:
                return node

def connect_to_instancer(transform_node, spore_node):
    """ connect a transform's matrix attribute to a instancer node
    that is connected to the given spore node """

    # get instancer's inputHierarchy plug
    instancer_node = get_instancer(spore_node, False)
    dg_fn = om.MFnDependencyNode(instancer_node)
    in_plug = dg_fn.findPlug('inputHierarchy')

    # get transform's matrix plug
    transform_node = get_mobject_from_name(transform_node)
    dag_fn = om.MFnDagNode(transform_node)
    matrix_plug = dag_fn.findPlug('matrix')

    # get first free plug and connect
    plug_id = in_plug.numElements() + 1
    dag_mod = om.MDagModifier()
    dag_mod.connect(matrix_plug, in_plug.elementByLogicalIndex(plug_id))
    dag_mod.doIt()

def get_connected_in_mesh(spore_node, as_string=True):
    """ get the full path name or mDagPath of the shape node connected
    to the given spore node """

    # TODO - error when node name is not unique!
    if isinstance(spore_node, str) or isinstance(spore_node, unicode):
        node_fn = get_dgfn_from_dagpath(spore_node)
    elif isinstance(spore_node, om.MObject):
        node_fn = om.MFnDependencyNode(spore_node)
    else:
        raise TypeError('Expected type string or MObject, got: {}'.format(type(spore_node)))

    inmesh_plug = node_fn.findPlug('inMesh')
    in_mesh = om.MDagPath()
    if not inmesh_plug.isNull():
        plugs = om.MPlugArray()
        if inmesh_plug.connectedTo(plugs, True, False):
            input_node = plugs[0].node()
            if input_node.hasFn(om.MFn.kMesh):
                om.MDagPath.getAPathTo(input_node, in_mesh)
                if in_mesh.isValid():
                    if as_string:
                        return in_mesh.fullPathName()
                    else:
                        return in_mesh
                else:
                    raise RuntimeError('Invalid connectedion to: {}'.format(in_mesh.fullPathName()))
            else:
                raise RuntimeError('inMesh plug is not connected to a poly mesh')
        else:
            raise RuntimeError('spore nodes\'s inMesh plug is not connected')

def get_local_rotation(mobject):
    """ returns an transform node's world space rotation values
    in degrees """

    dag_path = om.MDagPath()
    om.MDagPath.getAPathTo(mobject, dag_path)
    matrix = dag_path.inclusiveMatrix()
    matrix = om.MTransformationMatrix(matrix)
    rotation = matrix.asEulerRotation()

    return om.MVector(math.degrees(rotation.x),
                      math.degrees(rotation.y),
                      math.degrees(rotation.z))


