import sys
import traceback

import maya.cmds as cmds

import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.OpenMayaMPx as ompx
import maya.OpenMayaRender as omr

from scripted import spore_context

class SporeToolCmd(ompx.MPxToolCommand):

    def __init__(self):
        ompx.MPxToolCommand.__init__(self)
        self.setCommandString(K_TOOL_CMD_NAME)
        spore_context.K_TRACKING_DICTIONARY[ompx.asHashable(self)] = self
        print 'init cmd'

    def __del__(self):
        del spore_context.K_TRACKING_DICTIONARY[ompx.asHashable(self)]
        print 'cleanup cmd'

    def doIt(self, args):
        print 'doIt'

    def redoIt(self):
        print 'redoIt'

    def undoIt(self):
        print 'undoIt'

    def isUndoable(self):
        return True

    def finalize(self):
        """ Command is finished, construct a string for the command
        for journalling. """
        command = om.MArgList()
        command.addArg(self.commandString())
        command.addArg(self.__delta.x)
        command.addArg(self.__delta.y)
        command.addArg(self.__delta.z)

        # This call adds the command to the undo queue and sets
        # the journal string for the command.
        #
        try:
            ompx.MPxToolCommand._doFinalize(self, command)
        except:
            pass

def cmdCreator():
    return ompx.asMPxPtr(SporeToolCmd())

def syntaxCreator():
    syntax = om.MSyntax()
    syntax.addArg(om.MSyntax.kDouble)
    syntax.addArg(om.MSyntax.kDouble)
    syntax.addArg(om.MSyntax.kDouble)
    return syntax


