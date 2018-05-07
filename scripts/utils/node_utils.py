"""
module provides quick acces to frequently used node utilities
"""


import maya.OpenMaya as om
#  from maya import OpenMaya
#  from maya.api import OpenMaya as om


def getFullDagPath(mObject):
    """ return the full DAG path of an mObject """

    dagFn = om.MFnDagNode(mObject)
    return dagFn.fullPathName()


def getPartialDagPath(mObject):
    """ return the partial DAG path of an mObject"""

    dagFn = om.MFnDagNode(mObject)
    return dagFn.partialPathName()


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


def get_instancer(spore_node):
    """ the the instancer node connected to a spore node """

    node_fn = get_dgfn_from_dagpath(spore_node)
    instance_plug = node_fn.findPlug('instanceData')
    plugs = om.MPlugArray()
    instancer_plugs = om.MPlugArray()
    instance_geo = []

    if not instance_plug.isNull():
        if instance_plug.connectedTo(plugs, False, True):
            node = plugs[0].node()
            node_fn = om.MFnDagNode(node)
            instancer_node = node_fn.name()
            return instancer_node



def get_connected_in_mesh(spore_node):
    """ get the full path name of the shape node connected
    to the given spore node """

    node_fn = get_dgfn_from_dagpath(spore_node)
    inmesh_plug = node_fn.findPlug('inMesh')
    in_mesh = om.MDagPath()
    if not inmesh_plug.isNull():
        plugs = om.MPlugArray()
        if inmesh_plug.connectedTo(plugs, True, False):
            input_node = plugs[0].node()
            if input_node.hasFn(om.MFn.kMesh):
                om.MDagPath.getAPathTo(input_node, in_mesh)
                if in_mesh.isValid():
                    return in_mesh.fullPathName()



