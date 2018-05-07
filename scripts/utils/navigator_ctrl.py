import collections
import maya.cmds as cmds
import maya.OpenMaya as om

from spore.ui import navigator_ui, widgets
from spore.utils import node_utils
reload(navigator_ui)
reload(widgets)


class Navigator():
    def __init__(self, node_name):

        self.node = node_name
        self.ui = navigator_ui.NavigatorUI()

        #  self.ui.add_spore_widget(widgets.TreeItemWidget('foo'))

        self.update_ui()

    def get_widget(self):
        return self.ui

    def update_ui(self):

        spore_nodes = cmds.ls(type='sporeNode', l=True)
        targets = collections.defaultdict(list)
        [targets[self.get_in_mesh(node)].append(node) for node in spore_nodes]
        for target, spore_nodes in targets.iteritems():
            target_name = target.split('|')[-1]
            item_wdg = widgets.GeoItem(target_name, self.ui)
            #  item_wdg.clicked.connect(self.item_clicked)
            self.ui.add_item(item_wdg)

            for spore in spore_nodes:
                spore_item = widgets.SporeItem(spore, item_wdg)
                #  spore_item_wdg = manager_ui.ItemWidget(spore, False, item_wdg)
                #  spore_item_wdg.clicked.connect(self.item_clicked)
                item_wdg.add_child(spore_item)

    def get_in_mesh(self, node_name): # get_soil
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


