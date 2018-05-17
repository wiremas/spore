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


k_name_flag = "-n"
k_name_long_flag = "-name"


class SporeCommand(ompx.MPxCommand):
    name = 'spore'

    def __init__(self):
        ompx.MPxCommand.__init__(self)
        self.m_dag_mod = om.MDagModifier()
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
        syntax.setObjectType(om.MSyntax.kSelectionList)
        syntax.useSelectionAsDefault(True)
        #  syntax.addFlag(k_name_flag, k_name_long_flag, om.MSyntax.kString)
        return syntax

    def doIt(self, args):
        """ do """

        print 'parse'
        self.parse_args(args)

        # create sporeNode and instancer
        spore_transform = self.m_dag_mod.createNode('transform')
        self.spore = self.m_dag_mod.createNode('sporeNode', spore_transform)
        self.instancer = self.m_dag_mod.createNode('instancer')

        # rename nodes
        if self.name:
            self.name = '{}_'.format(self.name)
            print 'name:', self.name
        self.m_dag_mod.renameNode(spore_transform, '{}spore'.format(self.name))
        self.m_dag_mod.renameNode(self.spore, '{}sporeShape'.format(self.name))
        self.m_dag_mod.renameNode(self.instancer, '{}sporeInstancer'.format(self.name))

        # get spore node plugs
        dag_fn = om.MFnDagNode(self.spore)
        in_mesh_plug = dag_fn.findPlug('inMesh')
        instance_data_plug = dag_fn.findPlug('instanceData')

        # get instancer plugs
        dg_fn = om.MFnDependencyNode(self.instancer)
        in_points_plug = dg_fn.findPlug('inputPoints')
        in_hierarchy_plug = dg_fn.findPlug('inputHierarchy')

        # get target out mesh plug
        dag_fn = om.MFnDependencyNode(self.target)
        out_mesh_plug = dag_fn.findPlug('outMesh')

        # get source matrix plugs
        matrix_plug_array = om.MPlugArray()
        for i in xrange(self.source.length()):
            dag_fn = om.MFnDagNode(self.source[i])
            matrix_plug = dag_fn.findPlug('matrix')
            matrix_plug_array.append(matrix_plug)

        # hook everything up
        self.m_dag_mod.connect(instance_data_plug, in_points_plug)
        self.m_dag_mod.connect(out_mesh_plug, in_mesh_plug)
        for i in xrange(matrix_plug_array.length()):
            in_plug = in_hierarchy_plug.elementByLogicalIndex(i)
            self.m_dag_mod.connect(matrix_plug_array[i], in_plug)

        self.redoIt()

    def redoIt(self):
        """ redo """

        self.m_dag_mod.doIt()

        # get result
        result = []
        dag_fn = om.MFnDagNode(self.spore)
        result.append(dag_fn.fullPathName())
        dg_fn = om.MFnDependencyNode(self.instancer)
        result.append(dg_fn.name())
        self.clearResult()
        self.setResult(result)


    def undoIt(self):
        """ undo """

        self.m_dag_mod.undoIt()

    def isUndoable(self):
        """ set undoable """

        return True

    def parse_args(self, args):
        """ parse args """

        selection = om.MSelectionList()

        arg_data = om.MArgDatabase(self.syntax(), args)
        arg_data.getObjects(selection)

        #  # check if we got at least on item
        if selection.length() == 0:
            raise RuntimeError('The spore command requires at least 1 argument(s) to be specified or selected;  found 0.')

        for i in xrange(selection.length()):
            dag_path = om.MDagPath()
            selection.getDagPath(i, dag_path)

            # get target
            if i == 0:
                #  script_util = om.MScriptUtil()
                #  #  script_util.createFromInt(0)
                #  int_ptr = script_util.asUintPtr()
                #  dag_path.numberOfShapesDirectlyBelow(int_ptr)
                #  num_shapes = script_util.asUint()
                #  print num_shapes, dag_path.fullPathName()
                #  if num_shapes > 1:
                #      self.displayError('{} has more than one shape'.format(dag_path.fullPathName()))
                # TODO check if is kMesh
                dag_path.extendToShape()
                self.target = dag_path.node()

            # get source
            else:
                self.source.append(dag_path.node())


        #  if arg_data.isFlagSet(k_name_flag):
        #      print 'flag is set'
        #      #  arg_ls = om.MArgList()
        #      self.name = arg_data.flagArgumentString(k_name_flag, 0)
        #      #  self.name = arg_data.getFlagArgument(k_name_flag, 0).asString()
        #      #  print 'name:', self.name
        #      #  self.name = arg_ls.asString(0)
        #

