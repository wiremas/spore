import math
import random
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
import brush_utils

#  from scripted import spore_tool_cmd
from scripted import spore_tool

reload(canvas)
reload(mesh_utils)
reload(node_utils)
reload(message_utils)
reload(brush_state)
reload(event_filter)
reload(spore_tool)
reload(brush_utils)


""" -------------------------------------------------------------------- """
""" GLOBALS """
""" -------------------------------------------------------------------- """

K_TOOL_CMD_NAME="sporePlaceToolCmd"
K_CONTEXT_NAME="sporePlaceContext"

K_TRACKING_DICTIONARY = {}


""" -------------------------------------------------------------------- """
""" TOOL COMMAND """
""" -------------------------------------------------------------------- """


class PlaceToolCmd(spore_tool.SporeToolCmd):
    """ spore base tool command - abstract tool command class ment to """
    k_clicked, k_dragged, k_released = 0, 1, 2

    def __init__(self):
        super(PlaceToolCmd, self).__init__()
        self.setCommandString(K_TOOL_CMD_NAME)
        #  K_TRACKING_DICTIONARY[ompx.asHashable(self)] = self
        #  self.brush_state = Noneo

        self.points = []

    #  def __del__(self):
    #      del K_TRACKING_DICTIONARY[ompx.asHashable(self)]
    #      print 'cleanup cmd'

    @staticmethod
    def creator():
        return ompx.asMPxPtr(PlaceToolCmd())

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
        #  super(PlaceToolCmd, self).doIt()
        print 'doIt not implemented as command'


    def redoIt(self, flag):
        """ we generate a set of points located on a disk around the
        center of the brush. this set of points can be placed, moved
        or aligend every time a brush event ticks """

        print 'PLACE'
        position = om.MPoint(self.brush_state.position[0],
                             self.brush_state.position[1],
                             self.brush_state.position[2])
        normal = om.MVector(self.brush_state.normal[0],
                            self.brush_state.normal[1],
                            self.brush_state.normal[2])
        tangent = om.MVector(self.brush_state.tangent[0],
                             self.brush_state.tangent[1],
                             self.brush_state.tangent[2])

        # first generatate a set of point coords within the brush radius
        if not self.points and self.brush_state.drag_mode:
            for i in xrange(self.brush_state.settings['num_samples']):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(0, self.brush_state.radius)
                self.points.append((angle, distance))

        for i, (angle, distance) in enumerate(self.points):
            rotation = om.MQuaternion(angle, normal)
            tangential_vector = tangent.rotateBy(rotation)
            rand_pos =  position + tangential_vector * distance
            position, normal = mesh_utils.get_closest_point_and_normal(rand_pos, self.brush_state.target)
            tangent = mesh_utils.get_tangent(normal)

            # get orientation values
            direction = normal
            if self.brush_state.settings['align_to'] == 1:
                # TODO - get object up vector
                pass

            elif self.brush_state.settings['align_to'] == 2\
            or self.brush_state.align_mode:
                direction = om.MVector(self.brush_state.direction[0],
                                       self.brush_state.direction[1],
                                       self.brush_state.direction[2])

            rotation = brush_utils.get_rotation(self.brush_state.settings['min_rot'],
                                                self.brush_state.settings['max_rot'],
                                                direction,
                                                self.brush_state.settings['strength'])

            # get scale
            scale = brush_utils.get_scale(self.brush_state.settings['min_scale'],
                                          self.brush_state.settings['max_scale'],
                                          self.brush_state.settings['uni_scale'])

            # get instance id
            instance_id = random.randint(self.brush_state.settings['min_id'],
                                         self.brush_state.settings['max_id'])

            # TODO - not yet implemented
            v_coord = 0
            u_coord = 0
            poly_id = 0
            color = om.MVector(0, 0, 0)

            if self.brush_state.drag_mode:
                # TODO - drag points / set last n points
                pass
                index = self.node_state.length() - len(self.points) + i + 1
                self.node_state.set_point(index,
                                          position,
                                          scale,
                                          rotation,
                                          instance_id,
                                          normal,
                                          tangent,
                                          u_coord,
                                          v_coord,
                                          poly_id,
                                          color)

            else:
                index = self.node_state.append_point(position,
                                                     scale,
                                                     rotation,
                                                     instance_id,
                                                     normal,
                                                     tangent,
                                                     v_coord,
                                                     u_coord,
                                                     poly_id,
                                                     color)

        self.node_state.set_state()

    def undoIt(self):
        print 'undoItP'

    def isUndoable(self):
        return True

    def finalize(self):
        """ Command is finished, construct a string
        for the command for journalling. """

        print 'FINALIZE TOOL CMD'
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


class PlaceContext(spore_tool.SporeContext):

    def __init__(self):
        super(PlaceContext, self).__init__()
        self._setTitleString('placeContext')
        #  self.setImage("moveTool.xpm", ompx.MPxContext.kImage1)
        #  self.state =
        #  self.canvas = canvas.DotBrush(


    def toolOnSetup(self, event):
        super(PlaceContext, self).toolOnSetup(event)
        print 'derivedSetup'
        print self.__dict__
        #  self.canvas = canvas.DotBrush(self.state)

    def toolOffCleanup(self):
        super(PlaceContext, self).toolOffCleanup()

    @Slot(QPoint)
    def clicked(self, position):
        super(PlaceContext, self).clicked(position)

        if self.state.draw:
            self.tool_cmd.redoIt('clicked')

    @Slot(QPoint)
    def dragged(self, position):
        super(PlaceContext, self).dragged(position)

        if self.state.draw:
            self.tool_cmd.redoIt('dragged')

    @Slot(QPoint)
    def released(self, position):
        super(PlaceContext, self).released(position)

        if self.state.draw:
            self.tool_cmd.redoIt('released')


class PlaceContextCommand(ompx.MPxContextCommand):
    def __init__(self):
        ompx.MPxContextCommand.__init__(self)

    def makeObj(self):
        return ompx.asMPxPtr(PlaceContext())

    @staticmethod
    def creator():
        return ompx.asMPxPtr(PlaceContextCommand())


