"""
the following "vocabulary" is uses:
    "soil" - target surface
    "spore" - sporeNode
"""

import os
import sys
import collections

import pymel
import maya.cmds as cmds
import maya.OpenMaya as om

from PySide2.QtCore import Slot, QObject

try:
    import numpy
except ImportError:
    raise ImportError('Could not import Numpy')

print __name__, __file__

from spore.ui import AEsporeNodeTemplate, manager_ui
from spore.utils import node_utils
reload(manager_ui)


manager = None

class SporeManager(object):

    def __init__(self):

        self.ui = manager_ui.ManagerWindow()
        self.update_ui()
        self.connect_signals()


    def connect_signals(self):

        self.ui.add_spore_clicked.connect(self.add_spore)

    def update_ui(self):

        self.ui.clear_items()

        spore_nodes = cmds.ls(type='sporeNode', l=True)
        targets = collections.defaultdict(list)
        [targets[self.get_spore_target(node)].append(node) for node in spore_nodes]
        for soil, spore_nodes in targets.iteritems():
            item_wdg = manager_ui.ItemWidget(soil.split('|')[-1], True, self.ui)
            item_wdg.clicked.connect(self.item_clicked)
            self.ui.append_item(item_wdg)

            for spore in spore_nodes:
                spore_item_wdg = manager_ui.ItemWidget(spore, False, item_wdg)
                spore_item_wdg.clicked.connect(self.item_clicked)
                item_wdg.add_child(spore_item_wdg)

    def get_spore_target(self, node_name): # get_soil
        node_fn = node_utils.get_dgfn_from_dagpath(node_name)
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

    @Slot(QObject)
    def item_clicked(self, item_wdg):
        item_name = item_wdg.name
        if cmds.objExists(item_name):
            if item_wdg.is_root:
                cmds.select(cmds.listRelatives(item_name, p=True))
            else:
                cmds.select(item_name)



    def show(self):
        self.ui.show(dockable=True)

    def add_spore(self):
        selection = cmds.ls(sl=True, l=True)

        if len(selection) == 0:
            #TODO - show some kind of dialog do add source and target
            pass

        else:
            target = selection.pop(0)
            source = selection

            instancer = cmds.instancer()
            mesh = cmds.listRelatives(target, s=True)[0]
            node = cmds.createNode("sporeNode")
            cmds.connectAttr(node + '.instanceData', instancer + '.inputPoints')
            cmds.connectAttr(mesh + '.outMesh', node + '.inMesh')

            self.update_ui()


if __name__ == 'spore.manager':

    spore_root = os.path.dirname(__file__)
    os.environ['SPORE_ROOT_DIR'] = spore_root

    if not spore_root in sys.path:
        sys.path.append(spore_root)


    if not cmds.pluginInfo('spore_plugin', q=True, l=True):
        cmds.loadPlugin(os.path.join(spore_root, 'plugins', 'spore_plugin.py'))

    global manager
    if not manager:
        manager = SporeManager()

    manager.show()
