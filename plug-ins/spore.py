import sys

import maya.mel as mel
import pymel.core as pm
import maya.utils as mu
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx

# first instantiatet the global spore dispatcher class
# this must be the first thing bevore we import any of the plugins
import dispatcher
reload(dispatcher)
sys._global_spore_dispatcher = dispatcher.GlobalSporeDispatcher()

# now we can import the spore plugins
import AEsporeNodeTemplate
from scripted import spore_node
from scripted import spore_context
from scripted import spore_command
from scripted import spore_sampler

reload(spore_node)
reload(spore_context)
reload(spore_command)
reload(spore_sampler)
reload(AEsporeNodeTemplate)
mel.eval('refreshEditorTemplates;')


def initializePlugin(mobject):
    """ initialize plugins. this is the entry point for spore.
    as soon as maya loads the spore plugin the initializePlugin function is
    called which is also triggers everythin to set up. """

    sys._global_spore_dispatcher.logger.debug('Loading Spore plugin')
    mplugin = ompx.MFnPlugin(mobject, 'Anno Schachner', 'v0.1.0.beta')

    try: # register node prototype
        mplugin.registerNode(spore_node.SporeNode.name,
                             spore_node.SporeNode.id,
                             spore_node.SporeNode.creator,
                             spore_node.SporeNode.initialize,
                             ompx.MPxLocatorNode.kLocatorNode)
                             #  ompx.MPxNode.kDependNode)
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

    sys._global_spore_dispatcher.logger.debug('Unloading Spore plugin')
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

