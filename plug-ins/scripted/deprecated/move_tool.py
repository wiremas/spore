from abc import ABCMeta, abstractmethod

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

#  from scripted import spore_tool_cmd
from scripted import spore_tool

reload(canvas)
reload(mesh_utils)
reload(node_utils)
reload(message_utils)
reload(brush_state)
reload(event_filter)
reload(spore_tool)


""" -------------------------------------------------------------------- """
""" GLOBALS """
""" -------------------------------------------------------------------- """

K_TOOL_CMD_NAME="sporeMoveToolCmd"
K_CONTEXT_NAME="sporeMoveContext"

K_TRACKING_DICTIONARY = {}


""" -------------------------------------------------------------------- """
""" TOOL COMMAND """
""" -------------------------------------------------------------------- """


class MoveToolCmd(spore_tool.SporeToolCmd):
    """ spore base tool command - abstract tool command class ment to """

    def __init__(self):
        super(MoveToolCmd, self).__init__()
        self.setCommandString(K_TOOL_CMD_NAME)
        #  K_TRACKING_DICTIONARY[ompx.asHashable(self)] = self
        #  self.brush_state = None

    #  def __del__(self):
    #      del K_TRACKING_DICTIONARY[ompx.asHashable(self)]
    #      print 'cleanup cmd'

    @staticmethod
    def creator():
        return ompx.asMPxPtr(MoveToolCmd())

    @staticmethod
    def syntax():
        syntax = om.MSyntax()
        syntax.addArg(om.MSyntax.kDouble)
        syntax.addArg(om.MSyntax.kDouble)
        syntax.addArg(om.MSyntax.kDouble)
        return syntax

    """ -------------------------------------------------------------------- """
    """ reimplemented from MPxToolCommand """
    """ -------------------------------------------------------------------- """

    def doIt(self, args):
        super(MoveToolCmd, self).doIt()
        print 'doItP'

    def redoIt(self):
        print 'redoItP'

    def undoIt(self):
        print 'undoItP'

    def isUndoable(self):
        return True

    def finalize(self):
        """ Command is finished, construct a string
        for the command for journalling. """

        command = om.MArgList()
        #  command.addArg(self.commandString())
        #  command.addArg(self.__delta.x)
        #  command.addArg(self.__delta.y)
        #  command.addArg(self.__delta.z)

        # This call adds the command to the undo queue and sets
        # the journal string for the command.
        try:
            ompx.MPxToolCommand._doFinalize(self, command)
        except:
            pass

    """ -------------------------------------------------------------------- """
    """ utils """
    """ -------------------------------------------------------------------- """

    def parse_args(self, args):
        pass
        #  arg_data = om.MArgDatabase(self.syntax(), args)

    #  def set_brush_state(self, brush_state):
    #      self.brush_state = brush_state

""" -------------------------------------------------------------------- """
""" CONTEXT """
""" -------------------------------------------------------------------- """


class MoveContext(spore_tool.SporeContext):

    def __init__(self):
        super(MoveContext, self).__init__()
        self._setTitleString('MoveContext')
        #  self.setImage("moveTool.xpm", ompx.MPxContext.kImage1)
        #  self.state =
        #  self.canvas = canvas.DotBrush(


    def toolOnSetup(self, event):
        super(MoveContext, self).toolOnSetup(event)
        print 'derivedSetup'
        print self.__dict__
        self.canvas = canvas.CircularBrush(self.state)

    def toolOffCleanup(self, event):
        super(MoveContext, self).toolOffCleanup(event)



class MoveContextCommand(ompx.MPxContextCommand):
    def __init__(self):
        ompx.MPxContextCommand.__init__(self)

    def makeObj(self):
        return ompx.asMPxPtr(MoveContext())

    @staticmethod
    def creator():
        return ompx.asMPxPtr(MoveContextCommand())


