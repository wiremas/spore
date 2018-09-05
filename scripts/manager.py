import os
import re
import sys
import collections

import pymel
import maya.cmds as cmds
import maya.OpenMaya as om

from PySide2.QtCore import Slot, QObject, Qt
from PySide2.QtWidgets import QAction

import manager_ui
import node_utils
import message_utils
import logging_util


manager = None


class SporeManager(object):

    def __init__(self):

        self.logger = logging_util.SporeLogger(__name__)

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
        """ add callbacks """

        self.callbacks.append(om.MEventMessage.addEventCallback('SelectionChanged', self.selection_changed))
        self.callbacks.append(om.MEventMessage.addEventCallback('NameChanged', self.refresh_spore))
        self.callbacks.append(om.MSceneMessage.addCallback(om.MSceneMessage.kAfterNew, self.refresh_spore))
        self.callbacks.append(om.MSceneMessage.addCallback(om.MSceneMessage.kAfterOpen, self.refresh_spore))

    def remove_callbacks(self):
        """ remove callbacks """

        for i in xrange(self.callbacks.length()):
            try:
                om.MMessage.removeCallback(self.callbacks[i])
            except RuntimeError:
                pass

    def selection_changed(self, *args):
        """ link selection im maya to highligthing widgets in the manager """

        selection = cmds.ls(sl=True, typ='sporeNode', l=True)
        for geo_item, spore_items in self.wdg_tree.iteritems():
            for spore_item in spore_items:
                if spore_item.node_name in selection:
                    spore_item.select()
                else:
                    spore_item.deselect()

    def refresh_spore(self, *args):
        """ refresh spore ui """

        self.wdg_tree = collections.defaultdict(list)
        self.ui.clear_layout()
        self.initialize_ui()

    def initialize_ui(self):
        """ build the actual hierarchical layout for the spore view.
        add a GeoItem widget for each entry in the targets list and
        a SporeItem widget for each sporeNode connected to the mesh """

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
                spore_wdg.view_solo.connect(self.solo_view)
                #  spore_wdg.view_instancer.connect(self.toggle_view)
                #  spore_wdg.view_bounding_box.connect(self.toggle_view)
                #  spore_wdg.view_bounding_boxes.connect(self.toggle_view)
                #  spore_wdg.view_hide.connect(self.toggle_view)

    def get_spore_setups(self):
        """ return a dictionary with an entry for each target mesh
        and for each entry a list with all connected spore nodes """

        spore_nodes = cmds.ls(type='sporeNode', l=True)
        targets = collections.defaultdict(list)

        #  TODO - once this can be debugged this would be the way to go
        #  [targets[node_utils.get_connected_in_mesh(node)].append(node) for node in spore_nodes]

        for node in spore_nodes:
            target = node_utils.get_connected_in_mesh(node)
            if target:
                targets[target].append(node)

            else: # May help to debbug a situation wherfe target is sometime None
                target = cmds.getConnection('{}.inMesh'.format(node))
                target_shape = cmds.listRelatives(cmds.ls(target), s=True, f=True)

                if len(target_shape) == 1:
                    obj_type = cmds.objectType(target_shape[0])
                    self.logger.warning(
                        'Getting target mesh failed but spore has been able '
                        'to use fallback. target: {}, shape: {}, type: '
                        '{}'.format(target, target_shape[0], obj_type))
                    targets[target_shape] = node
                else:
                    obj_type = [cmds.objectType(s) for s in target_shape]
                    raise RuntimeError(
                        'Could not get target mesh and spore failed to use '
                        'fallback. target {}, shapes {}, types: {}'.format(
                            target, target_shape, obj_type)
                    )

        return targets

    """ -------------------------------------------------- """
    """ slots """
    """ -------------------------------------------------- """

    @Slot(str)
    def add_spore(self, name):
        """ add a new spore setup to the scene """

        if cmds.ls(sl=True):
            spore_node, instancer = cmds.spore()
            cmds.select(spore_node)
            self.ui.clear_layout()
            self.refresh_spore()
            self.logger.debug(
                'Manager created new setup: {}, {}'.format(spore_node, instancer)
            )

        else:
            self.logger.warn('Failed to create Spore. Nothing selected')

    @Slot(QObject)
    def item_clicked(self, widget, event):

        item_name = widget.long_name
        item_state = widget.is_selected
        if cmds.objExists(item_name):

            is_modified = event.modifiers() == Qt.ControlModifier
            if not is_modified:
                cmds.select(clear=True)

            for geo_item, spore_items in self.wdg_tree.iteritems():
                for spore_item in spore_items:
                    if is_modified \
                    and spore_item.is_selected:
                        cmds.select(spore_item.long_name, add=True)
                    else:
                        spore_item.deselect()
                        cmds.select(spore_item.long_name, deselect=True)

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

    @Slot(QObject, bool)
    def solo_view(self, widget, solo):
        instancer = node_utils.get_instancer(widget.name)
        cmds.showHidden(instancer)

        for geo_wdg, spore_wdgs in self.wdg_tree.iteritems():
            for spore_wdg in spore_wdgs:
                if spore_wdg is not widget:
                    spore_wdg.view_buttons.solo_btn.setChecked(False)
                    instancer = node_utils.get_instancer(spore_wdg.name)
                    if solo:
                        cmds.hide(instancer)
                    else:
                        cmds.showHidden(instancer)

    @Slot(QObject, str)
    def name_changed(self, widget, name):
        """ triggered by one of the spore widgets when the user
        requests a name change
        :param widget: the source of the signal
        :param name: the new name """

        node_name = widget.long_name
        if cmds.objExists(node_name):
            if re.match('^[A-Za-z0-9_-]*$', name) and not name[0].isdigit():
                #  transform = cmds.listRelatives(node_name, p=True, f=True)[0]
                instancer = node_utils.get_instancer(node_name)
                cmds.rename(instancer, '{}Instancer'.format(name))
                cmds.rename(node_name, '{}Shape'.format(name))
                #  cmds.rename(transform, name)

            else:
                self.io.set_message('Invalid Name: Use only A-Z, a-z, 0-9, -, _', 2)
                return

        self.refresh_spore()



    @Slot(QAction)
    def context_request(self, widget, action):

        if action.text() == 'Delete':
            selection = cmds.ls(sl=1, typ='sporeNode')
            for geo_wdg, spore_wdgs in self.wdg_tree.iteritems():
                for spore_wdg in spore_wdgs:

                    spore_node = spore_wdg.name
                    print spore_node
                    if spore_wdg.is_selected and cmds.objExists(spore_node):
                        instancer = node_utils.get_instancer(spore_node)
                        transform = cmds.listRelatives(spore_node, p=True, f=True)

                        if len(cmds.listRelatives(transform, c=1)) == 1:
                            cmds.delete((spore_node, transform[0], instancer))
                        else:
                            cmds.delete((spore_node, instancer))

                        selection.remove(spore_node)
                        cmds.select(selection)

            self.refresh_spore()

    def show(self):
        self.add_callbacks()
        self.refresh_spore()
        self.ui.show(dockable=True)

    @Slot()
    def close_event(self):
        self.remove_callbacks()



#  if __name__ == 'manager':
#
#      #  spore_root = os.path.dirname(__file__)
#      #  os.environ['SPORE_ROOT_DIR'] = spore_root
#
#      #  if not spore_root in sys.path:
#      #      sys.path.append(spore_root)
#      #
#      #
#      #  if not cmds.pluginInfo('spore_plugin', q=True, l=True):
#      #      cmds.loadPlugin(os.path.join(spore_root, 'plugins', 'spore_plugin.py'))
#      #
#      #  global manager
#      if not manager:
#          manager = SporeManager()
#
#      manager.show()
