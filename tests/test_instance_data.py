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
        self.node = node_utils.get_mobject_from_name(spore[0])
        self.instance_data = instance_data.InstanceData(self.node)
        self.instance_data.initialize_data()

    def tearDown(self):
        cmds.file(new=True, f=True)

    def test_append(self):
        """ test the append method """

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
        """ test the set_points method """

        position, scale, rotation, instance_id, visibility, normal, tangent, u_coord, v_coord, poly_id, color = create_test_data(20)
        self.instance_data.append_points(position, scale, rotation, instance_id,
                                         visibility, normal, tangent, u_coord,
                                         v_coord, poly_id, color)
        self.instance_data_validation(20)

        position, scale, rotation, instance_id, visibility, normal, tangent, u_coord, v_coord, poly_id, color = create_test_data(10)

        # test set data
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
        self.instance_data_validation(20)

        # test invalid length within range
        self.assertFalse(self.instance_data.set_points(range(0,2), position=position))
        self.assertFalse(self.instance_data.set_points(range(0,2), scale=scale))
        self.assertFalse(self.instance_data.set_points(range(0,2), rotation=rotation))
        self.assertFalse(self.instance_data.set_points(range(0,2), instance_id=instance_id))
        self.assertFalse(self.instance_data.set_points(range(0,2), visibility=visibility))
        self.assertFalse(self.instance_data.set_points(range(0,2), normal=normal))
        self.assertFalse(self.instance_data.set_points(range(0,2), tangent=tangent))
        self.assertFalse(self.instance_data.set_points(range(0,2), u_coord=u_coord))
        self.assertFalse(self.instance_data.set_points(range(0,2), v_coord=v_coord))
        self.assertFalse(self.instance_data.set_points(range(0,2), poly_id=poly_id))
        self.assertFalse(self.instance_data.set_points(range(0,2), color=color))
        self.instance_data_validation(20)

        # test valid length outside of range
        ids = range(20, 30)
        self.assertFalse(self.instance_data.set_points(ids, position=position))
        self.assertFalse(self.instance_data.set_points(ids, scale=scale))
        self.assertFalse(self.instance_data.set_points(ids, rotation=rotation))
        self.assertFalse(self.instance_data.set_points(ids, instance_id=instance_id))
        self.assertFalse(self.instance_data.set_points(ids, visibility=visibility))
        self.assertFalse(self.instance_data.set_points(ids, normal=normal))
        self.assertFalse(self.instance_data.set_points(ids, tangent=tangent))
        self.assertFalse(self.instance_data.set_points(ids, u_coord=u_coord))
        self.assertFalse(self.instance_data.set_points(ids, v_coord=v_coord))
        self.assertFalse(self.instance_data.set_points(ids, poly_id=poly_id))
        self.assertFalse(self.instance_data.set_points(ids, color=color))
        self.instance_data_validation(20)

    def test_set_point(self):
        """ test the set_points and set_length method """

        length = 20
        position, scale, rotation, instance_id, visibility, normal, tangent, u_coord, v_coord, poly_id, color = create_test_data(length)
        self.instance_data.set_length(length)
        ids = range(length)
        for i in range(length):
            self.instance_data.set_point(i, position[i], scale[i], rotation[i],
                                         instance_id[i], visibility[i],
                                         normal[i], tangent[i], u_coord[i],
                                         v_coord[i], poly_id[i], color[i])
        self.instance_data_validation(length)

        # test set out of range index
        self.assertFalse(self.instance_data.set_point(50, position[0], scale[0],
                                                      rotation[0],
                                                      instance_id[0],
                                                      visibility[0],
                                                      normal[0], tangent[0],
                                                      u_coord[0], v_coord[0],
                                                      poly_id[0], color[0]))

    def test_insert_point(self):
        length = 20
        position, scale, rotation, instance_id, visibility, normal, tangent, u_coord, v_coord, poly_id, color = create_test_data(length)
        for i in range(length):
            self.instance_data.insert_point(i, position[i], scale[i],
                                            rotation[i], instance_id[i],
                                            visibility[i], normal[i],
                                            tangent[i], u_coord[i],
                                            v_coord[i], poly_id[i],
                                            color[i])
        self.instance_data_validation(length)

    def test_clean_up(self):

        # test nothing to do on empty instance data
        self.assertFalse(self.instance_data.clean_up())

        # test cleanup range
        length = 20
        position, scale, rotation, instance_id, visibility, normal, tangent, u_coord, v_coord, poly_id, color = create_test_data(length)
        self.instance_data.append_points(position, scale, rotation, instance_id,
                                         visibility, normal, tangent, u_coord,
                                         v_coord, poly_id, color)
        for i in range(10, 20):
            self.instance_data.visibility[i] = 0
        self.instance_data.clean_up()
        self.instance_data_validation(10)

        # test cleanup empty
        for i in range(10):
            self.instance_data.visibility[i] = 0
        self.instance_data.clean_up()
        self.instance_data_validation(0)

        # test cleanup with nothing to do
        self.assertFalse(self.instance_data.clean_up())

    def test_add(self):
        instance_data_2 = instance_data.InstanceData(self.node)
        instance_data_2.initialize_data()

        length = 20
        position, scale, rotation, instance_id, visibility, normal, tangent, u_coord, v_coord, poly_id, color = create_test_data(length)
        self.instance_data.append_points(position, scale, rotation, instance_id,
                                         visibility, normal, tangent, u_coord,
                                         v_coord, poly_id, color)

        instance_data_2.append_points(position, scale, rotation, instance_id,
                                      visibility, normal, tangent, u_coord,
                                      v_coord, poly_id, color)

        self.instance_data = self.instance_data + instance_data_2
        self.instance_data_validation(40)

        self.instance_data += instance_data_2
        self.instance_data_validation(60)

    def instance_data_validation(self, predicted_length):
        """ validate the instance data object """
        self.assertTrue(self.instance_data.is_valid)
        self.assertEqual(len(self.instance_data), predicted_length)
        for i in xrange(len(self.instance_data)):
            self.assertEqual(self.instance_data.unique_id[i], i)
            self.assertEqual(self.instance_data.position[i].x,
                             self.instance_data.np_position[i][0])
            self.assertEqual(self.instance_data.position[i].y,
                             self.instance_data.np_position[i][1])
            self.assertEqual(self.instance_data.position[i].z,
                             self.instance_data.np_position[i][2])




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
    def instance_data_validation(self, predicted_length):
        """ validate the instance data object """
        self.assertTrue(self.instance_data.is_valid)
        self.assertEqual(len(self.instance_data), predicted_length)
        for i in xrange(len(self.instance_data)):
            self.assertEqual(self.instance_data.unique_id[i], i)
            self.assertEqual(self.instance_data.position[i].x,
                             self.instance_data.np_position[i][0])
            self.assertEqual(self.instance_data.position[i].y,
                             self.instance_data.np_position[i][1])
            self.assertEqual(self.instance_data.position[i].z,
                             self.instance_data.np_position[i][2])




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
        visibility.append(1)
        normal.append(om.MVector(i, i, i))
        tangent.append(om.MVector(i, i, i))
        u_coord.append(i)
        v_coord.append(i)
        poly_id.append(i)
        color.append(om.MVector(i, i, i))
    return position, scale, rotation, instance_id, visibility, normal, tangent, u_coord, v_coord, poly_id, color
