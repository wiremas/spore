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


import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx

import logging_util

k_name_flag = "-n"
k_name_long_flag = "-name"


class SporeCommand(ompx.MPxCommand):
    name = 'spore'

    def __init__(self):
        ompx.MPxCommand.__init__(self)

        self.logger = logging_util.SporeLogger(__name__)
        self.dag_mod = om.MDagModifier()
        self.dg_mod = om.MDGModifier()
        self.spore = om.MObject()
        self.instancer = om.MObject()
        self.target = om.MObject()
        self.source = om.MObjectArray()
        self.name = ''

    @staticmethod
    def creator():
        return ompx.asMPxPtr(SporeCommand())

    @staticmethod
    def syntax():
        syntax = om.MSyntax()
        syntax.setObjectType(om.MSyntax.kSelectionList, 1)
        syntax.useSelectionAsDefault(True)
        syntax.addFlag(k_name_flag, k_name_long_flag, om.MSyntax.kString)
        return syntax

    def doIt(self, args):
        """ do """

        if not self.parse_args(args):
            return

        # create sporeNode and instancer
        #  spore_transform = self.dg_mod.createNode('transform')
        self.spore = self.dg_mod.createNode('sporeNode')
        self.instancer = self.dag_mod.createNode('instancer')

        # rename nodes
        if self.name:
            self.name = '{}_'.format(self.name)
        #  self.dg_mod.renameNode(spore_transform, '{}spore'.format(self.name))
        self.dg_mod.renameNode(self.spore, '{}spore'.format(self.name))
        self.dag_mod.renameNode(self.instancer, '{}sporeInstancer'.format(self.name))

        # get spore node plugs
        dg_fn = om.MFnDependencyNode(self.spore)
        in_mesh_plug = dg_fn.findPlug('inMesh')
        instance_data_plug = dg_fn.findPlug('instanceData')

        # get instancer plugs
        dg_fn = om.MFnDagNode(self.instancer)
        in_points_plug = dg_fn.findPlug('inputPoints')
        in_hierarchy_plug = dg_fn.findPlug('inputHierarchy')

        # get target out mesh plug
        dag_fn = om.MFnDagNode(self.target)
        out_mesh_plug = dag_fn.findPlug('outMesh')

        # get source matrix plugs
        matrix_plug_array = om.MPlugArray()
        for i in xrange(self.source.length()):
            dag_fn = om.MFnDagNode(self.source[i])
            matrix_plug = dag_fn.findPlug('matrix')
            matrix_plug_array.append(matrix_plug)

        # hook everything up
        self.dg_mod.connect(instance_data_plug, in_points_plug)
        self.dg_mod.connect(out_mesh_plug, in_mesh_plug)
        for i in xrange(matrix_plug_array.length()):
            in_plug = in_hierarchy_plug.elementByLogicalIndex(i)
            self.dg_mod.connect(matrix_plug_array[i], in_plug)

        self.redoIt()

    def redoIt(self):
        """ redo """

        self.dag_mod.doIt()
        self.dg_mod.doIt()

        # get result
        result = []
        dg_fn = om.MFnDependencyNode(self.spore)
        result.append(dg_fn.name())
        dag_fn = om.MFnDagNode(self.instancer)
        result.append(dag_fn.fullPathName())
        self.clearResult()
        self.setResult(result)


    def undoIt(self):
        """ undo """

        self.dag_mod.undoIt()
        self.dg_mod.undoIt()

    def isUndoable(self):
        """ set undoable """

        return True

    def parse_args(self, args):
        """ parse args """


        arg_data = om.MArgDatabase(self.syntax(), args)

        if arg_data.isFlagSet(k_name_flag):
            self.name = arg_data.getFlagArgument(k_name_flag, 0)

        selection = om.MSelectionList()
        arg_data.getObjects(selection)

        #  # check if we got at least on item
        if selection.length() == 0:
            self.logger.error('Spore Command failed: Nothing Selected')
            return False

        for i in xrange(selection.length()):
            dag_path = om.MDagPath()
            selection.getDagPath(i, dag_path)

            # get target
            if i == 0:

                try:
                    dag_path.extendToShape()
                except RuntimeError:
                    self.logger.error('Spore Command failed: Object has more than one shape')
                    return False

                if dag_path.hasFn(om.MFn.kMesh):
                    self.target = dag_path.node()
                else:
                    self.logger.error('Spore Command failed: Object is not of type kMesh')
                    return False

            # get source
            else:
                self.source.append(dag_path.node())

        return True



