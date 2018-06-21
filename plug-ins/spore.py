import sys
from logging import DEBUG, INFO, WARN, ERROR

import pymel.core as pm
import maya.utils as mu
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx

import AEsporeNodeTemplate
import dispatcher
import environment_util
import logging_util
import dispatcher
from scripted import spore_node
from scripted import spore_context
from scripted import spore_command
from scripted import spore_sampler

reload(dispatcher)
reload(spore_node)
reload(spore_context)
reload(spore_command)
reload(spore_sampler)
reload(AEsporeNodeTemplate)
reload(logging_util)
reload(environment_util)

import maya.mel as mel
mel.eval('refreshEditorTemplates;')


__version__ = '0.5'


def initializePlugin(mobject):
    """ initialize plugins
    this is basically the entry point for everything. as soon as maya loads
    the spore plugin the initializePlugin function is triggered which is also
    used to set up things like callbacks, menu and log """

    # first instantiatet the global spore dispatcher class
    sys._global_spore_dispatcher = dispatcher.SporeDispatcher()

    mplugin = ompx.MFnPlugin(mobject, 'Anno Schachner', __version__)

    try: # register node prototype
        mplugin.registerNode(spore_node.SporeNode.name,
                             spore_node.SporeNode.id,
                             spore_node.SporeNode.creator,
                             spore_node.SporeNode.initialize,
                             ompx.MPxNode.kDependNode)
    except:
        sys.stderr.write("Failed to register node: %s" % spore_node.SporeNode.name)
        raise

    try: # register context & tool command
        mplugin.registerContextCommand(spore_context.K_CONTEXT_NAME,
                                       spore_context.SporeContextCommand.creator,
                                       spore_context.K_TOOL_CMD_NAME,
                                       spore_context.SporeToolCmd.creator,
                                       spore_context.SporeToolCmd.syntax)
    except:
        sys.stderr.write("Failed to register context command: {}".format(spore_context.K_CONTEXT_NAME))
        raise

    try: # register spore command
        mplugin.registerCommand(spore_command.SporeCommand.name,
                                spore_command.SporeCommand.creator,
                                spore_command.SporeCommand.syntax)
    except:
        sys.stderr.write('Failed to register spore command: {}'.format(spore_command.SporeCommand.name))

    try: # register sample command
        mplugin.registerCommand(spore_sampler.SporeSampler.name,
                                spore_sampler.creator,
                                spore_sampler.syntax)
    except:
        sys.stderr.write('Failed to register spore command: {}'.format(spore_sampler.SporeSampler.name))
        raise


def uninitializePlugin(mobject):
    """ uninitialize plugins in reverse order & delete menu """

    mplugin = ompx.MFnPlugin(mobject)

    try:
        mplugin.deregisterCommand(spore_sampler.SporeSampler.name)
    except:
        sys.stderr.write("Failed to deregister command: %s" % spore_sampler.SporeSampler.name)
        raise

    try:
        mplugin.deregisterCommand(spore_command.SporeCommand.name)
    except:
        sys.stderr.write("Failed to deregister command: %s" % spore_command.SporeCommand.name)
        raise

    try: # deregister context and tool command
        mplugin.deregisterContextCommand(spore_context.K_CONTEXT_NAME,
                                         spore_context.K_TOOL_CMD_NAME)
    except:
        sys.stderr.write("Failed to deregister node: %s" % spore_context.K_CONTEXT_NAME)
        raise

    try: # deregister spore node
        mplugin.deregisterNode(spore_node.SporeNode.id)
    except:
        sys.stderr.write("Failed to deregister node: %s" % spore_node.SporeNode.name)
        raise

    sys._global_spore_dispatcher.clean_up()
    del sys._global_spore_dispatcher

