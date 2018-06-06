
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaRender as omr


def sample_shading_node(shading_node, point_data, filter_size=0):
    """ sample the given shading node for each point in
    the given point data object
    :return """

    #  view = om.M3dView().active3dView()
    #  cam_dag = om.MDagPath()
    #  view.getCamera(cam_dag)
    #  dag_fn = om.MFnDagNode(cam_dag)
    #  matrix_plug = dag_fn.findPlug('worldMatrix')

    # create temp material and shading engine for sampling
    old_selection = cmds.ls(sl=True, l=True)
    shd = cmds.shadingNode('surfaceShader', name='shaderEvalTemp', asShader=True)
    shd_grp = cmds.sets(name='%sSG' % shd, empty=True, renderable=True, noSurfaceShader=True)
    cmds.connectAttr('%s.outColor' % shd, '%s.surfaceShader' % shd_grp)
    cmds.connectAttr(shading_node + '.outColor', shd + '.outColor')

    points = om.MFloatPointArray()
    #  ref_points = om.MFloatPointArray()
    normals = om.MFloatVectorArray()
    #  u_tangent = om.MFloatVectorArray() # get binormals to sample dependend shaders
    #  v_tangent = om.MFloatVectorArray()
    u_coords = om.MFloatArray()
    v_coords = om.MFloatArray()
    filter_size_array = om.MFloatArray()
    cam_matrix = om.MFloatMatrix() # get camera matrix to sample view dependend shader

    for i, (position, normal, poly_id, u_coord, v_coord) in enumerate(point_data):

        points.append(om.MFloatPoint(position[0], position[1], position[2]))
        normals.append(om.MFloatVector(normal[0], normal[1], normal[2]))
        u_coords.append(u_coord)
        v_coords.append(v_coord)
        #  u_tangent.append(om.MFloatVector(0,1,0))
        #  v_tangent.append(om.MFloatVector(1,0,0))
        filter_size_array.append(filter_size)

    color = om.MFloatVectorArray()
    alpha = om.MFloatVectorArray()
    omr.MRenderUtil.sampleShadingNetwork(shd_grp,
                                        len(point_data),
                                        False,
                                        False,
                                        cam_matrix,
                                        points,
                                        u_coords,
                                        v_coords,
                                        normals,
                                        points,
                                        None,
                                        None,
                                        None,
                                        color,
                                        alpha)

    color_result = [(color[i].x, color[i].y, color[i].z) for i in xrange(color.length())]
    alpha_result = [(alpha[i].x, alpha[i].y, alpha[i].z) for i in xrange(alpha.length())]

    cmds.delete((shd, shd_grp))
    cmds.select(old_selection)

    return color_result, alpha_result

