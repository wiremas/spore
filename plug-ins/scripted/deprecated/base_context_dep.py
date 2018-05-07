import sys
import traceback

import maya.cmds as cmds

import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.OpenMayaMPx as ompx
import maya.OpenMayaRender as omr

from shiboken2 import wrapInstance
from PySide2.QtWidgets import QWidget
from PySide2.QtCore import QObject, QEvent, Signal, Slot, QPoint, Qt
from PySide2.QtGui import QKeyEvent

#  from spore.utils import window_utils
#  import ..data.brush_state as brush_state
#  relaod(brush_stateoo)
#  import ..utils.mesh_utils

import window_utils
import mesh_utils
import node_utils
import message_utils
import canvas
import brush_state

#  from node import spore_node
#  from command import spore_tool_cmd
#  from spore.controller import brush_ctrl

#  reload(spore_tool_cmd)
#  reload(brush_ctrl)
reload(window_utils)
reload(node_utils)
reload(mesh_utils)
reload(brush_state)
reload(canvas)
#  import spore.utils.window_utils as window_utils

class KeyEventFilter(QObject):

    # modifier
    meta_pressed = Signal() # ctrl on MacOs, windows ond win
    meta_released = Signal()
    ctrl_pressed = Signal()
    ctrl_released = Signal()
    shift_pressed = Signal()
    shift_released = Signal()
    ctrl_shift_pressed = Signal()
    ctrl_shift_released = Signal()
    meta_shift_preffed = Signal()
    mata_shift_released = Signal()

    # key event signals
    space_pressed = Signal()
    space_pressed = Signal()
    b_pressed = Signal()
    b_released = Signal()

    def __init__(self, parent):
        super(KeyEventFilter, self).__init__()
        self.parent = parent

    def eventFilter(self, source, event):
        if isinstance(event, QKeyEvent) and not event.isAutoRepeat():
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Control:
                    self.ctrl_pressed.emit()
                    return True

                if event.key() == Qt.Key_Shift:
                    print 'shift'
                    self.shift_pressed.emit()
                    return True

                if event.key() == Qt.Key_Meta:
                    print 'meta'
                    self.meta_pressed.emit()
                    return True

                if event.key() == Qt.Key_B:
                    self.b_pressed.emit()
                    return True

            if event.type() == QEvent.KeyRelease:
                if event.key() == Qt.Key_Control:
                    self.ctrl_released.emit()
                    return True

                if event.key() == Qt.Key_Shift:
                    self.shift_released.emit()
                    return True

                if event.key() == Qt.Key_Meta:
                    print 'meta'
                    self.meta_released.emit()
                    return True

                if event.key() == Qt.Key_B:
                    self.b_released.emit()
                    return True

        return False


class MouseEventFilter(QObject):
    """ event filter for the brush context
    filter mouse and key events to trigger the user interaction """

    # mouse event signals
    mouse_moved = Signal(QPoint)
    clicked = Signal(QPoint)
    dragged = Signal(QPoint)
    released = Signal(QPoint)
    leave = Signal()


    def __init__(self, parent):
        super(MouseEventFilter, self).__init__()
        self.parent = parent
        self.is_clicked = False
        self.is_modified = False

    def eventFilter(self, source, event):

        if isinstance(event, QKeyEvent) and not event.isAutoRepeat():
            if event.type() == QEvent.KeyPress and not self.is_clicked:
                if event.key() != Qt.Key_Shift:
                    self.is_modified = True
            if event.type() == QEvent.KeyRelease and not self.is_clicked:
                print 'mod_off'

            #  if event.type() == QEvent.KeyRelease:
            #      self.is_modified = False

        # Mouse Events
        if event.type() == QEvent.MouseMove:
            position = event.pos()
            self.mouse_moved.emit(position)
            if self.is_clicked and not self.is_modified:
                self.dragged.emit(position)
            return False

        if event.type() == QEvent.Wheel:
            position = event.pos()
            self.mouse_moved.emit(position)

        if event.type() == QEvent.MouseButtonPress:
            self.is_clicked = True
            if not self.is_modified:
                position = event.pos()
                self.clicked.emit(position)
                return False

        if event.type() == QEvent.MouseButtonRelease:
            self.is_clicked = False
            if not self.is_modified:
                position = event.pos()
                self.released.emit(position)
                return False
            else:
                self.is_modified = False


        if event.type() == QEvent.Leave:
            self.leave.emit()
            return False

        return False

#  class SenderObj(QObject):
#      #  trigger = Signal(object)
#      press = Signal(dict)
#      drag = Signal(dict)
#      release = Signal(dict)


class SporeBaseContext(ompx.MPxContext):

    #  brush_trigger = Signal(object)

    def __init__(self):
        super(SporeContext, self).__init__()
        self._setTitleString("SporeBrush")
        #  self.setImage("moveTool.xpm", ompx.MPxContext.kImage1)

        #  from spore.data import brush_state
        #  self.sender = SenderObj()
        self.state = brush_state.BrushState()
        #  self.ctrl = brush_ctrl.BrushCtrl(self, self.state)
        self.msg_io = message_utils.IOHandler()
        self.canvas = None

        self.mouse_event_filter = MouseEventFilter(self)
        self.key_event_filter = KeyEventFilter(self)


        self.connect_signals()

    def connect_signals(self):
        # mouse event signals
        self.mouse_event_filter.clicked.connect(self.clicked)
        self.mouse_event_filter.released.connect(self.released)
        self.mouse_event_filter.dragged.connect(self.dragged)
        self.mouse_event_filter.mouse_moved.connect(self.mouse_moved)
        self.mouse_event_filter.leave.connect(self.leave)

        # key event signals
        self.key_event_filter.ctrl_pressed.connect(self.ctrl_pressed)
        self.key_event_filter.ctrl_released.connect(self.ctrl_released)
        self.key_event_filter.meta_pressed.connect(self.meta_pressed)
        self.key_event_filter.meta_released.connect(self.meta_released)
        self.key_event_filter.shift_pressed.connect(self.shift_pressed)
        self.key_event_filter.shift_released.connect(self.shift_released)
        self.key_event_filter.b_pressed.connect(self.b_pressed)
        self.key_event_filter.b_released.connect(self.b_released)

    def toolOnSetup(self, event):
        """ Node setup:
        - get the node's inMesh and set it as target for the tool
        - update the context controller
        - install mouse & key events
        - build the canvas frot drawing """

        # get spore_node's inMesh and set it as target
        # note: we expect the target node to be selected when we setup the tool
        # if no sporeNode is selected we try to use the last target as fallback
        # if there is no fallback, tool initialization will fail and display a
        # warning
        try: # try to get selection of type sporeNode
            node_name = cmds.ls(sl=True, l=True, type='sporeNode')[0]
        except IndexError:
            node_name = None

        # try to get inMesh of selected spore node
        if node_name:
            self.state.target = node_utils.get_connected_in_mesh()
            self.state.node = node_name
            #  node_fn = node_utils.get_dgfn_from_dagpath(node_name)
            #  inmesh_plug = node_fn.findPlug('inMesh')
            #  in_mesh = om.MDagPath()
            #  if not inmesh_plug.isNull():
            #      plugs = om.MPlugArray()
            #      if inmesh_plug.connectedTo(plugs, True, False):
            #          input_node = plugs[0].node()
            #          if input_node.hasFn(om.MFn.kMesh):
            #              om.MDagPath.getAPathTo(input_node, in_mesh)
            #              if in_mesh.isValid():
            #                  self.target_mesh = in_mesh.fullPathName()
            #                  self.state.target = in_mesh.fullPathName()
            #                  self.target_node = node_name

            if not self.state.target or not self.state.node:
                raise RuntimeError('Failed initializing sporeTool')

        # fallback to old target, just pass since target is already set
        elif self.state.target and self.state.node: pass

        # if we neither have a sporeNode selected nor have a fallback, tool init fails
        else:
            self.msg_io.set_message('No sporeNode selected: Can\'t operate on: {}'.format(cmds.ls(sl=1), 1))
            return

        # fetch the node state
        #  self.ctrl.get_node_state(self.state.node)

        # install event filter
        view = window_utils.active_view_wdg()
        view.installEventFilter(self.mouse_event_filter)
        window = window_utils.maya_main_window()
        window.installEventFilter(self.key_event_filter)

        # set up canvas for drawing
        self.canvas = canvas.BrushDrawOverride(self.state)

        # instanciate the tool command
        #  self.tool_cmd.public_method()
        tool_cmd = self._newToolCommand()
        print tool_cmd # spore_tool_cmd.SporeToolCmd.tracking_dir # .get(ompx.asHashable(tool_cmd))
        #  self.tool_cmd = spore_tool_cmd.SporeToolCmd.tracking_dir.get(ompx.asHashable(tool_cmd))



    def toolOffCleanup(self):
        view = window_utils.active_view_wdg()
        view.removeEventFilter(self.mouse_event_filter)
        window = window_utils.maya_main_window()
        window.removeEventFilter(self.key_event_filter)

        self.state.draw = False
        self.canvas.update()
        del self.canvas


    @Slot(QPoint)
    def mouse_moved(self, position):
        """ update the brush as soon as the mouse moves """

        self.state.cursor_x = position.x()
        self.state.cursor_y = position.y()

        result = None
        if not self.state.first_scale:

            result = mesh_utils.hit_test(self.state.target, self.state.first_x, self.state.first_y)

        else:
            result = mesh_utils.hit_test(self.state.target, position.x(), position.y())

        if result:
            position, normal, tangent = result
            self.state.position = position
            self.state.normal = normal
            self.state.tangent = tangent
            self.state.draw = True
            if not self.state.last_position:
                self.state.last_position = position
            else:
                pos = om.MPoint(position[0], position[1], position[2])
                last_pos = om.MPoint(self.state.last_position[0],
                                     self.state.last_position[1],
                                     self.state.last_position[2])
                stroke_dir = pos - last_pos
                self.state.stroke_direction = (stroke_dir[0],
                                               stroke_dir[1],
                                               stroke_dir[2])
                print 'stroke dir: ', self.state.stroke_direction
                self.state.last_position = position

        else:
            self.state.draw = False

        # redraw after coursor has been move
        self.canvas.update()

    @Slot(QPoint)
    def clicked(self, position):

        if self.state.draw and not self.state.modify_radius:
            state = self.get_state()
            #  self.sender.press.emit(state)


    @Slot(QPoint)
    def dragged(self, position):
        if self.state.draw:
            if self.state.modify_radius:
                if self.state.first_scale:
                    self.state.first_x = position.x()
                    self.state.first_y = position.y()
                    self.state.last_x = position.x()
                    self.state.last_y = position.y()
                    self.state.first_scale = False

                self.modify_radius()
                self.state.last_x = position.x()
                self.state.last_y = position.y()

            else:
                state = self.get_state()
                #  self.sender.drag.emit(state)


    @Slot(QPoint)
    def released(self, position):

        if self.state.draw and not self.state.modify_radius:
            state = self.get_state()
            #  self.sender.release.emit(state)

    @Slot()
    def leave(self):
        self.state.draw = False
        self.canvas.update()

    """ ------------------------------------------------------ """
    """ Key Events """
    """ ------------------------------------------------------ """

    @Slot()
    def ctrl_pressed(self):
        pass

    @Slot()
    def ctrl_released(self):
        pass

    @Slot()
    def meta_pressed(self):
        pass

    @Slot()
    def meta_released(self):
        pass

    @Slot()
    def shift_pressed(self):
        self.state.drag_mode = True
        self.canvas.update()

    @Slot()
    def shift_released(self):
        self.state.drag_mode = False
        self.canvas.update()


    @Slot()
    def b_pressed(self):
        self.state.modify_radius = True
        #  self.state.first_x = position.x()

    @Slot()
    def b_released(self):
        self.state.modify_radius = False
        self.state.first_scale = True

    def get_state(self):
        """ get the current state and return it as a dictionary """

        state = {'position': self.state.position,
                 'normal': self.state.normal,
                 'tangent': self.state.tangent,
                 'radius': self.state.radius}

        return state

    def modify_radius(self):
        delta_x = self.state.last_x - self.state.cursor_x

        view = window_utils.active_view()
        cam_dag = om.MDagPath()
        view.getCamera(cam_dag)
        cam_node_fn = node_utils.get_dgfn_from_dagpath(cam_dag.fullPathName())
        cam_coi = cam_node_fn.findPlug('centerOfInterest').asDouble()

        step = delta_x * (cam_coi * -0.025) # TODO - finetune static factor for different scene sizes!
        if (self.state.radius + step) >= 0.01:
            self.state.radius += step

        else:
            self.state.radius = 0.01

    #  def doPress(self, event):
    #      print 'press', event
    #
    #  def doRelease(self, event):
    #      print 'release', event
    #
    #  def doDrag(self, event):
    #      print 'doDrag', event


class ContextCommand(ompx.MPxContextCommand):
    name = 'sporeContext'

    def __init__(self):
        super(ContextCommand, self).__init__()

    @staticmethod
    def creator():
        return ompx.asMPxPtr(ContextCommand())

    def makeObj(self):
        return ompx.asMPxPtr(SporeContext())


def initializePlugin(mobject):
    mplugin = ompx.MFnPlugin(mobject)

    #  try:
    #      mplugin.registerNode(spore_node.SporeNode.name,
    #                           spore_node.SporeNode.id,
    #                           spore_node.SporeNode.creator,
    #                           spore_node.SporeNode.initialize)
    #  except:
    #      sys.stderr.write( "Failed to register node: %s" % spore_node.SporeNode.name)
    #      raise

    try:
        mplugin.registerContextCommand(ContextCommand.name,
                                       ContextCommand.creator)
    except:
        sys.stderr.write( "Failed to register node: %s" % ContextCommand.name)
        raise

def uninitializePlugin(mobject):

    mplugin = ompx.MFnPlugin(mobject)

    #  try:
    #      mplugin.deregisterNode(spore_node.SporeNode.id)
    #  except:
    #      sys.stderr.write("Failed to deregister node: %s" % spore_node.SporeNode.name)
    #      raise

    try:
        mplugin.deregisterContextCommand(ContextCommand.name)
    except:
        sys.stderr.write("Failed to deregister node: %s" % ContextCommand.name)
        raise

