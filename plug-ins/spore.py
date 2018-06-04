import sys

import pymel.core as pm
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx

import AEsporeNodeTemplate
from scripted import spore_node
from scripted import spore_context
from scripted import spore_command
from scripted import spore_sampler

reload(spore_node)
reload(spore_context)
reload(spore_command)
reload(spore_sampler)
reload (AEsporeNodeTemplate)

import maya.mel as mel
mel.eval('refreshEditorTemplates;')


CALLBACKS = om.MCallbackIdArray()
MENU = None
# menu items   #Label                   #commande
MENU_ITEMS = (('Spore',                 'import manager;reload(manager)'),
              (None,                    None), # None is a separator
              ('Create Spore Setup',    'cmds.spore()'),
              ('Help',                  ''))


def initializePlugin(mobject):
    """ initialize plugins & create menu"""

    # create global tracking dir to keep track of out nodes
    if not hasattr(sys, '_global_spore_tracking_dir'):
        sys._global_spore_tracking_dir = dict()

    # set up callbacks
    CALLBACKS.append(om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeOpen,
                                                  clear_tracking_dir))
    CALLBACKS.append(om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeNew,
                                                  clear_tracking_dir))

    mplugin = ompx.MFnPlugin(mobject)

    try: # register node prototype
        mplugin.registerNode(spore_node.SporeNode.name,
                             spore_node.SporeNode.id,
                             spore_node.SporeNode.creator,
                             spore_node.SporeNode.initialize,
                             ompx.MPxNode.kDependNode)
    except:
        sys.stderr.write( "Failed to register node: %s" % spore_node.SporeNode.name)
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
    #
    #  try:
    #      mplugin.registerCommand(motionTraceCmd.kPluginCmdName, motionTraceCmd.cmdCreator, motionTraceCmd.syntaxCreator)
    #  except:
    #      sys.stderr.write("Failed to register command: %s\n" % motionTraceCmd.kPluginCmdName)
        raise

    # cereate spore menu
    global MENU
    if not MENU:
        main_wnd = pm.language.melGlobals['gMainWindow']
        MENU = pm.menu('Spore', parent=main_wnd)

    # add menu items
    pm.menuItem(l='Spore', c='import manager;reload(manager)', parent=MENU)
    pm.menuItem(divider=True)
    pm.menuItem(l='Create Spore Setup', c='cmds.spore()', parent=MENU)
    pm.menuItem(divider=True)
    pm.menuItem(l='Help', c='print help', parent=MENU)

def uninitializePlugin(mobject):
    """ uninitialize plugins in reverse order & delete menu """

    mplugin = ompx.MFnPlugin(mobject)

    #  try:
    #      mplugin.deregisterCommand(motionTraceCmd.kPluginCmdName)
    #  except:
    #      sys.stderr.write("Failed to unregister command: %s\n" % motionTraceCmd.kPluginCmdName)
        #  raise
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

    # delete menu
    pm.deleteUI(MENU)

    # remove callbacks
    for i in xrange(CALLBACKS.length()):
        callback = CALLBACKS[i]
        om.MSceneMessage.removeCallback(callback)

def clear_tracking_dir(*args):
    """ clean up the global spore tracking dir when a new file is created
    or opened """

    print args
    sys._global_spore_tracking_dir = {}



