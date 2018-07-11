import os
import sys

import maya.cmds as cmds
import maya.OpenMaya as om

from test_util import TestCase
import geo_cache
import node_utils


class TestGeoCache(TestCase):

    def setUp(self):

        # create new scene & load plugin
        cmds.file(new=True, f=True)
        plugin = 'spore'
        self.load_plugin('spore')

        # setup a simple scene
        plane = cmds.polyPlane(sx=10, sy=10, w=10, h=10)
        #  cone = cmds.polyCone()
        #  cmds.select(plane[0], cone[0])
        #  spore = cmds.spore()

        # get new instance data object and connect it to the current node
        #  self.node = node_utils.get_mobject_from_name(spore[0])
        self.plane = node_utils.get_dagpath_from_name(plane[0])
        self.geo_cache = geo_cache.GeoCache()

    def tearDown(self):
        cmds.file(new=True, f=True)

    def test_cache(self):

        self.geo_cache.cache_geometry(self.plane)

        self.assertEqual(self.geo_cache.p0.length(), 200)
        self.assertEqual(self.geo_cache.p1.length(), 200)
        self.assertEqual(self.geo_cache.p2.length(), 200)
        self.assertEqual(self.geo_cache.normals.length(), 200)
        self.assertEqual(self.geo_cache.poly_id.length(), 200)
        self.assertEqual(self.geo_cache.AB.length(), 200)
        self.assertEqual(self.geo_cache.AC.length(), 200)

        for i in range(100):
            self.assertEqual(self.geo_cache.poly_id[i * 2], i)
            self.assertEqual(self.geo_cache.poly_id[i * 2 + 1], i)

        self.geo_cache.create_uv_lookup()





