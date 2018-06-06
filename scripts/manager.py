import os
import re
import sys
import collections

import pymel
import maya.cmds as cmds
import maya.OpenMaya as om

from PySide2.QtCore import Slot, QObject, Qt
from PySide2.QtWidgets import QAction

#  print __name__, __file__

import manager_ui
import node_utils
reload(manager_ui)
import message_utils


manager = None

class SporeManager(object):

    def __init__(self):

        self.wdg_tree = collections.defaultdict(list)

        self.ui = manager_ui.ManagerWindow()
        self.io = message_utils.IOHandler()
        self.callbacks = om.MCallbackIdArray()

        self.initialize_ui()
        self.connect_signals()

    def connect_signals(self):

        self.ui.add_spore_clicked.connect(self.add_spore)
        #  self.ui.remove_spore_clicked.connect(self.add_spore)
        self.ui.refresh_spore_clicked.connect(self.refresh_spore)
        self.ui.close_event.connect(self.close_event)

    def add_callbacks(self):
        self.callbacks.append(om.MEventMessage.addEventCallback('SelectionChanged', self.selection_changed))

    def remove_callbacks(self):
        for i in xrange(self.callbacks.length()):
            om.MMessage.removeCallback(self.callbacks[i])

    def selection_changed(self, *args):
        selection = cmds.ls(sl=True, typ='sporeNode')
        print selection
        for geo_item, spore_items in self.wdg_tree.iteritems():
            for spore_item in spore_items:
                if spore_item.node_name in selection:
                    spore_item.select()
                else:
                    spore_item.deselect()

    @Slot(str)
    def add_spore(self, name):
        """ add a new spore setup to the scene """

        spore_node, instancer = cmds.spore()
        #  spore_transform = cmds.listRelatives(spore_node, p=True, f=True)[0]
        cmds.rename(spore_node, '{}Spore'.format(name))
        cmds.rename(instancer, '{}SporeInstancer'.format(name))

        self.ui.clear_layout()
        self.initialize_ui()
        self.refresh_spore()

    def remove_spore(self):
        """ remove selected spore setup(s) from the scene """

        pass

    def refresh_spore(self):
        """ refresh spore ui """

        self.wdg_tree = collections.defaultdict(list)
        self.ui.clear_layout()
        self.initialize_ui()


    def initialize_ui(self):

        targets = self.get_spore_setups()
        for target, spore_nodes in targets.iteritems():
            geo_wdg = manager_ui.GeoItem(target) # , self.ui.spore_layout)
            geo_wdg.clicked.connect(self.item_clicked)
            self.ui.append_item(geo_wdg)

            for spore in spore_nodes:
                # create and add new spore widget
                spore_wdg = manager_ui.SporeItem(spore, geo_wdg)
                geo_wdg.add_child(spore_wdg)
                self.wdg_tree[geo_wdg].append(spore_wdg)

                # hook up some signals
                spore_wdg.clicked.connect(self.item_clicked)
                spore_wdg.context_requested.connect(self.context_request)
                spore_wdg.view_toggled.connect(self.toggle_view)
                spore_wdg.name_changed.connect(self.name_changed)
                #  spore_wdg.view_solo
                #  spore_wdg.view_instancer.connect(self.toggle_view)
                #  spore_wdg.view_bounding_box.connect(self.toggle_view)
                #  spore_wdg.view_bounding_boxes.connect(self.toggle_view)
                #  spore_wdg.view_hide.connect(self.toggle_view)




    def get_spore_setups(self):
        """ return a dictionary with an entry for each target mesh
        and for each entry a list with all connected spore nodes """

        spore_nodes = cmds.ls(type='sporeNode', l=True)
        targets = collections.defaultdict(list)
        [targets[node_utils.get_connected_in_mesh(node)].append(node) for node in spore_nodes]
        return targets


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
    def item_clicked(self, widget, event):

        item_name = widget.long_name
        item_state = widget.is_selected
        if cmds.objExists(item_name):

            is_modified = event.modifiers() == Qt.ControlModifier
            if not is_modified:
                cmds.select(clear=True)

            for geo_item, spore_items in self.wdg_tree.iteritems():
                #  print geo_item, spore_items
                for spore_item in spore_items:
                    if is_modified \
                    and spore_item.is_selected:
                        cmds.select(spore_item.long_name, add=True)
                    else:
                        spore_item.deselect()

            widget.set_select(item_state)
            if not is_modified:
                cmds.select(item_name)

        else:
            self.refresh_spore()

    @Slot(QObject, int)
    def toggle_view(self, widget, mode):
        """ triggered by one of the spore widget's display toggle buttons
        :param widget: the source of the signal
        :param mode: 1==geometry, 2==bounding box, 3==bounding boxes """

        node_name = widget.long_name
        if cmds.objExists(node_name):
            instancer = node_utils.get_instancer(node_name)
            if instancer:
                cmds.setAttr('{}.levelOfDetail'.format(instancer), mode)

    @Slot(QObject, str)
    def name_changed(self, widget, name):
        """ triggered by one of the spore widgets when the user
        requests a name change
        :param widget: the source of the signal
        :param name: the new name """

        node_name = widget.long_name
        if cmds.objExists(node_name):
            if re.match('^[A-Za-z0-9_-]*$', name) and not name[0].isdigit():
                transform = cmds.listRelatives(node_name, p=True, f=True)[0]
                instancer = node_utils.get_instancer(node_name)
                cmds.rename(instancer, '{}Instancer'.format(name))
                cmds.rename(node_name, '{}Shape'.format(name))
                cmds.rename(transform, name)

            else:
                self.io.set_message('Invalid Name: Use only A-Z, a-z, 0-9, -, _', 2)
                return

        self.refresh_spore()



    @Slot(QAction)
    def context_request(self, action):
        print 'context request', action

    def show(self):
        self.add_callbacks()
        self.ui.show(dockable=True)

    @Slot()
    def close_event(self):
        self.remove_callbacks()



if __name__ == 'manager':

    #  spore_root = os.path.dirname(__file__)
    print __file__
    #  os.environ['SPORE_ROOT_DIR'] = spore_root

    #  if not spore_root in sys.path:
    #      sys.path.append(spore_root)
    #
    #
    #  if not cmds.pluginInfo('spore_plugin', q=True, l=True):
    #      cmds.loadPlugin(os.path.join(spore_root, 'plugins', 'spore_plugin.py'))
    #
    global manager
    if not manager:
        manager = SporeManager()

    manager.show()
