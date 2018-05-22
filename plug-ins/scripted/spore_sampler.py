"""
spore command takes one or more objects and creates a spore network
containing a spore node and an instancer node
the first object will be the target mesh for the spore node.
all following objects will be attached to the instancer node
-n / -name      : give the node an appropriate name
-

return: list containing the sporeShape as first and
        the instancer as second element
"""
import sys


import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx

import geo_cache
reload(geo_cache)

k_sample_type_flag = "-st"
k_sample_type_long_flag = "-sampleType"
k_num_samples_flag = "-nos"
k_num_samples_long_flag = "-numberOfSamples"
k_min_radius_flag = "-mr"
k_min_radius_long_flag = "-minimumRadius"
k_cell_size_flat = '-cs'
k_cell_size_long_flag = '-cellSize'


class SporeSampler(ompx.MPxCommand):
    name = 'sporeSampler'

    def __init__(self):
        ompx.MPxCommand.__init__(self)

        self.target = om.MObject()

        self.geo_cache = geo_cache.GeoCache()
        self.sample_type = 'random'
        self.num_samples = None
        self.min_radius = None
        self.cell_size = None

    @staticmethod
    def creator():
        return ompx.asMPxPtr(SporeSampler())

    @staticmethod
    def syntax():
        syntax = om.MSyntax()
        syntax.setObjectType(om.MSyntax.kSelectionList, 1, 1)
        syntax.useSelectionAsDefault(True)
        syntax.addFlag(k_sample_type_flag, k_sample_type_long_flag, om.MSyntax.kString)
        syntax.addFlag(k_num_samples_flag, k_num_samples_long_flag, om.MSyntax.kInt)
        syntax.addFlag(k_min_radius_flag, k_min_radius_long_flag, om.MSyntax.kDouble)
        syntax.addFlag(k_cell_size_flat, k_cell_size_long_flag, om.MSyntax.kDouble)
        #  syntax.addFlag(k_name_flag, k_name_long_flag, om.MSyntax.kString)
        return syntax

    def doIt(self, args):
        """ do """

        self.parse_args(args)
        self.redoIt()

    def redoIt(self):
        """ redo """

        # check if we can find a geo cache on the node we operate on
        # else build a new one
        obj_handle = om.MObjectHandle(self.target)
        if hasattr(sys, '_global_spore_tracking_dir'):
            try:
                spore_locator = sys._global_spore_tracking_dir[obj_handle.hashCode()]
            except IndexError:
                self.geo_cache.cache_geometry(self.target)
            else:
                self.geo_cache = spore_locator.geo_cache
        else:
            self.geo_cache.cache_geometry(self.target)

    def undoIt(self):
        """ undo """
        pass

    def isUndoable(self):
        """ set undoable """
        return True

    def sample_ptc(self):
        pass

    def sample_grd(self):
        pass

    def sample_dsk(self):
        pass

    def parse_args(self, args):
        """ parse args """


        arg_data = om.MArgDatabase(self.syntax(), args)

        if arg_data.isFlagSet(k_sample_type_flag):
            self.sample_type = arg_data.getFlagArgument(k_sample_type_flag, 0)

        if arg_data.isFlagSet(k_num_samples_flag, k_num_samples_long_flag):
            self.num_samples = arg_data.getFlagArgument(k_num_samples_flag, 0)

        if arg_data.isFlagSet(k_min_radius_flag, k_min_radius_long_flag):
            self.min_radius = arg_data.getFlagArgument(k_min_radius_flag, 0)

        if arg_data.isFlagSet(k_cell_size_flat, k_cell_size_long_flag):
            self.cell_size = arg_data.getFlagArgument(k_cell_size_flat, 0)

        selection = om.MSelectionList()
        arg_data.getObjects(selection)
        if selection.length() == 1:
            dag_path = om.MDagPath()
            selection.getDagPath(0, dag_path)
            dag_path.extendToShape()
            self.target = dag_path.node()
        else:
            raise RuntimeError('The spore command requires at least 1 argument(s) to be specified or selected;  found 0.')

