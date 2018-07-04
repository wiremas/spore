import os
import sys

import maya.cmds as cmds
import maya.OpenMaya as om

from test_util import TestCase
import instance_data
import node_utils


class TestInstanceData(TestCase):

    def setUp(self):

        # create new scene & load plugin
        cmds.file(new=True, f=True)
        plugin = 'spore'
        self.load_plugin('spore')

        # setup a simple scene
        plane = cmds.polyPlane()
        cone = cmds.polyCone()
        cmds.select(plane[0], cone[0])
        spore = cmds.spore()

        # get new instance data object and connect it to the current node
        node = node_utils.get_mobject_from_name(spore[0])
        self.instance_data = instance_data.InstanceData(node)
        self.instance_data.initialize_data()

    def tearDown(self):
        cmds.file(new=True, f=True)

    def test_append(self):
        self.assertEqual(len(self.instance_data), 0)
        length = 10
        position, scale, rotation, instance_id, visibility, normal, tangent, u_coord, v_coord, poly_id, color = create_test_data(length)
        self.instance_data.append_points(position, scale, rotation, instance_id,
                                         visibility, normal, tangent, u_coord,
                                         v_coord, poly_id, color)
        self.assertTrue(self.instance_data.is_valid)

        position, scale, rotation, instance_id, visibility, normal, tangent, u_coord, v_coord, poly_id, color = create_test_data(length)
        self.instance_data.append_points(position, scale, rotation, instance_id,
                                         visibility, normal, tangent, u_coord,
                                         v_coord, poly_id, color)
        self.assertTrue(self.instance_data.is_valid)

        for i in xrange(length * 2):
            self.assertEqual(i, self.instance_data.unique_id[i])


    def test_set_points(self):
        position, scale, rotation, instance_id, visibility, normal, tangent, u_coord, v_coord, poly_id, color = create_test_data(20)
        self.instance_data.append_points(position, scale, rotation, instance_id,
                                         visibility, normal, tangent, u_coord,
                                         v_coord, poly_id, color)

        position, scale, rotation, instance_id, visibility, normal, tangent, u_coord, v_coord, poly_id, color = create_test_data(10)

        ids = range(10, 20)
        self.instance_data.set_points(ids, position=position)
        self.instance_data.set_points(ids, scale=scale)
        self.instance_data.set_points(ids, rotation=rotation)
        self.instance_data.set_points(ids, instance_id=instance_id)
        self.instance_data.set_points(ids, visibility=visibility)
        self.instance_data.set_points(ids, normal=normal)
        self.instance_data.set_points(ids, tangent=tangent)
        self.instance_data.set_points(ids, u_coord=u_coord)
        self.instance_data.set_points(ids, v_coord=v_coord)
        self.instance_data.set_points(ids, poly_id=poly_id)
        self.instance_data.set_points(ids, color=color)

        self.assertTrue(self.instance_data.is_valid)
        for i in xrange(len(self.instance_data)):
            self.assertEqual(self.instance_data.unique_id[i], i)

def create_test_data(length):
    """ helper function to create an instance data set of the given length """

    position = om.MVectorArray()
    scale = om.MVectorArray()
    rotation = om.MVectorArray()
    instance_id = om.MIntArray()
    visibility = om.MIntArray()
    normal = om.MVectorArray()
    tangent = om.MVectorArray()
    u_coord =  om.MIntArray()
    v_coord = om.MIntArray()
    poly_id = om.MIntArray()
    color = om.MVectorArray()
    for i in xrange(length):
        position.append(om.MVector(i, i, i))
        scale.append(om.MVector(i, i, i))
        rotation.append(om.MVector(i, i, i))
        instance_id.append(i)
        visibility.append(i)
        normal.append(om.MVector(i, i, i))
        tangent.append(om.MVector(i, i, i))
        u_coord.append(i)
        v_coord.append(i)
        poly_id.append(i)
        color.append(om.MVector(i, i, i))
    return position, scale, rotation, instance_id, visibility, normal, tangent, u_coord, v_coord, poly_id, color
