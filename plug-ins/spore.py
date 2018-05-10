import sys

import pymel
from maya import mel
import pymel.core as pm
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.OpenMayaMPx as ompx
import maya.OpenMayaRender as omr

from scripted import spore_node
from scripted import spore_context
reload(spore_node)
reload(spore_context)


import AEsporeNodeTemplate
reload (AEsporeNodeTemplate)
from maya import mel
mel.eval('refreshEditorTemplates;')
#  try
#      import AEsporeNodeTemplate
#      reload (AEsporeNodeTemplate)
#      from maya import mel
#      mel.eval('refreshEditorTemplates;')
#  except:
#      raise ImportWarning('Could not import sporeNode Attribute Editor ui')

def initializePlugin(mobject):

    mplugin = ompx.MFnPlugin(mobject)

    # TODO add menu!
    #  mplugin.addMenuItem("Instance Along Curve", "MayaWindow|mainEditMenu", kPluginCmdName, "")

    pm.callbacks(addCallback=load_spore_template,
                 hook='provideAETemplateForNodeType',
                 owner=spore_node.SporeNode.name)

    try:
        mplugin.registerNode(spore_node.SporeNode.name,
                             spore_node.SporeNode.id,
                             spore_node.SporeNode.creator,
                             spore_node.SporeNode.initialize,
                             ompx.MPxNode.kLocatorNode)

    except:
        sys.stderr.write( "Failed to register node: %s" % spore_node.SporeNode.name)
        raise


    try:
        mplugin.registerContextCommand(spore_context.K_CONTEXT_NAME,
                                       spore_context.SporeContextCommand.creator,
                                       spore_context.K_TOOL_CMD_NAME,
                                       spore_context.SporeToolCmd.creator,
                                       spore_context.SporeToolCmd.syntax)
    except:
        sys.stderr.write("Failed to register context command: %s\n" % spore_context.K_CONTEXT_NAME)
        raise

def uninitializePlugin(mobject):

    mplugin = ompx.MFnPlugin(mobject)

    pm.callbacks(removeCallback=load_spore_template,
                 hook='AETemplateCustomContent',
                 owner=spore_node.SporeNode.name)

    try:
        mplugin.deregisterContextCommand(spore_context.K_CONTEXT_NAME,
                                         spore_context.K_TOOL_CMD_NAME)
    except:
        sys.stderr.write("Failed to deregister node: %s" % spore_context.K_CONTEXT_NAME)
        raise

    try:
        mplugin.deregisterNode(spore_node.SporeNode.id)
    except:
        sys.stderr.write("Failed to deregister node: %s" % spore_node.SporeNode.name)
        raise


def load_spore_template(node_name):

    print 'ae cb'
    #  try:
    import AEsporeNodeTemplate
    reload (AEsporeNodeTemplate)
    from maya import mel
    mel.eval('refreshEditorTemplates;')

    ae_template = AEsporeNodeTemplate.AEsporeNodeTemplate(node_name)
    print ae_template
    #  except:
    #      raise ImportWarning('Could not import sporeNode Attribute Editor ui')
