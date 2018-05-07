import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.OpenMayaMPx as ompx
import maya.OpenMayaRender as omr

from shiboken2 import wrapInstance
from PySide2.QtWidgets import QWidget
from PySide2.QtCore import QObject, QEvent, Signal, Slot, QPoint, Qt
from PySide2.QtGui import QKeyEvent

import canvas
import mesh_utils
import node_utils
import window_utils
import message_utils
import brush_state
import event_filter

from scripted import spore_tool_cmd

reload(canvas)
reload(mesh_utils)
reload(node_utils)
reload(message_utils)
reload(brush_state)
reload(event_filter)


class SporeContext(ompx.MPxContext):

    #  brush_trigger = Signal(object)

    def __init__(self):
        super(SporeContext, self).__init__()
        self._setTitleString("SporeBrush")

        self.state = brush_state.BrushState()
        self.msg_io = message_utils.IOHandler()
        self.canvas = None

        self.mouse_event_filter = event_filter.MouseEventFilter(self)
        self.key_event_filter = event_filter.KeyEventFilter(self)

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
        """ tool setup:
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
            self.state.target = node_utils.get_connected_in_mesh(node_name)
            self.state.node = node_name

            if not self.state.target or not self.state.node:
                raise RuntimeError('Failed initializing sporeTool')

        # fallback to old target, just pass since target is already set
        elif self.state.target and self.state.node:
            pass

        # if we neither have a sporeNode selected nor have a fallback, tool init fails
        else:
            self.msg_io.set_message('No sporeNode selected: Can\'t operate on: {}'.format(cmds.ls(sl=1), 1))
            return


        # install event filter
        view = window_utils.active_view_wdg()
        view.installEventFilter(self.mouse_event_filter)
        window = window_utils.maya_main_window()
        window.installEventFilter(self.key_event_filter)

        # set up canvas for drawing
        self.canvas = canvas.CircularBrush(self.state)

        # instanciate the tool command
        #  self.tool_cmd.public_method()
        tool_cmd = self._newToolCommand()
        print 'toolcmd: ', tool_cmd # spore_tool_cmd.SporeToolCmd.tracking_dir # .get(ompx.asHashable(tool_cmd))
        self.tool_cmd = spore_tool_cmd.SporeToolCmd.tracking_dir.get(ompx.asHashable(tool_cmd))

    def toolOffCleanup(self):
        view = window_utils.active_view_wdg()
        view.removeEventFilter(self.mouse_event_filter)
        window = window_utils.maya_main_window()
        window.removeEventFilter(self.key_event_filter)

        self.state.draw = False
        self.canvas.update()
        del self.canvas

    """ -------------------------------------------------------------------- """
    """ mouse events """
    """ -------------------------------------------------------------------- """

    @Slot(QPoint)
    def mouse_moved(self, position):
        """ update the brush as soon as the mouse moves """

        self.state.cursor_x = position.x()
        self.state.cursor_y = position.y()

        result = None
        if not self.state.first_scale:
            result = mesh_utils.hit_test(self.state.target,
                                         self.state.first_x,
                                         self.state.first_y)

        else:
            result = mesh_utils.hit_test(self.state.target,
                                         position.x(),
                                         position.y())

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

                self.state.last_position = position

        else:
            self.state.draw = False

        # redraw after coursor has been move
        self.canvas.update()

    @Slot(QPoint)
    def clicked(self, position):

        if self.state.draw and not self.state.modify_radius:
            state = self._get_state()
            #  self.sender.press.emit(state)

            self.tool_cmd.doIt()



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
                state = self._get_state()
                #  self.sender.drag.emit(state)


    @Slot(QPoint)
    def released(self, position):

        if self.state.draw and not self.state.modify_radius:
            state = self._get_state()
            #  self.sender.release.emit(state)

    @Slot()
    def leave(self):
        self.state.draw = False
        self.canvas.update()


    """ -------------------------------------------------------------------- """
    """ key events """
    """ -------------------------------------------------------------------- """

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

    @Slot()
    def b_released(self):
        self.state.modify_radius = False
        self.state.first_scale = True

    """ -------------------------------------------------------------------- """
    """ utils """
    """ -------------------------------------------------------------------- """

    def _get_state(self):
        """ get the current state and return it as a dictionary """

        state = {'position': self.state.position,
                 'normal': self.state.normal,
                 'tangent': self.state.tangent,
                 'radius': self.state.radius}

        return state




class ContextCommand(ompx.MPxContextCommand):
    name = 'sporeContext'

    def __init__(self):
        super(ContextCommand, self).__init__()

    @staticmethod
    def creator():
        return ompx.asMPxPtr(ContextCommand())

    def makeObj(self):
        return ompx.asMPxPtr(SporeContext())





tracking_dir = {}
tool_cmd_name = 'sporeToolCmd'
print type(tool_cmd_name)

class SporeToolCmd(ompx.MPxToolCommand):

    def __init__(self):
        ompx.MPxToolCmd.__init__(self)
        #  self.setCommandSting(tool_cmd_name)

        #  tracking_dir[ompx.asHashable(self)] = self
        #  print 'cmdself: ', self

    def __del__(self):
        #  del tracking_dir[ompx.asHashable(self)]
        pass


    #  @staticmethod
    #  def syntax():
    #      print 'create syntax'
    #      syntax = om.MSyntax()
    #      syntax.addArg(om.MSyntax.kDouble)
    #      #  syntax.addFlag('pos', 'position', om.kDouble, om.kDOuble, om.kDOuble)
    #      #  syntax.addArg(om.MSyntax.kDouble)
    #      return syntax# syntax

    def doIt(self, args):
        print 'doIt', args

    def redoIt(self):
        print 'redoIt'

    def undoIt(self):
        print 'undoIt'

    def isUndoable(self):
        return False

    def finalize(self):
        pass

    # ---------------------------------------------------- #

    def public_method(self):
        print 'some random stuf'

def cmd_creator():
    return ompx.asMPxPtr(SporeToolCmd())
