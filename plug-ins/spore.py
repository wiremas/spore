import sys
import traceback

import pymel
import pymel.core as pm
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
import maya.OpenMayaUI as omui
import maya.OpenMayaRender as omr

#  print __file__
#  print sys.path

from scripted import spore_node
from scripted import spore_context
#  from scripted import spore_tool
#  from scripted import place_tool
#  from scripted import spray_tool
#  from scripted import scale_tool
#  from scripted import align_tool
#  from scripted import move_tool

#  from scripted import context
#  from scripted import spore_tool
#  from scripted import spore_tool_cmd
#  from scripted import spray_cmd
#  from spore.ui import navigator
#  reload(navigator)
reload(spore_node)
reload(spore_context)
#  reload(spore_tool)
#  reload(place_tool)
#  reload(spray_tool)
#  reload(spore_tool)
#  reload(scale_tool)
#  reload(align_tool)
#  reload(move_tool)
#  reload(spore_tool_cmd)


def initializePlugin(mobject):

    mplugin = ompx.MFnPlugin(mobject)

    # TODO add menu!
    #  mplugin.addMenuItem("Instance Along Curve", "MayaWindow|mainEditMenu", kPluginCmdName, "")

    #  pm.callbacks(addCallback=load_spore_template,
    #               hook='provideAETemplateForNodeType',
    #               owner='sporeNode')

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

    #  try:
    #      mplugin.registerContextCommand(place_tool.K_CONTEXT_NAME,
    #                                     place_tool.PlaceContextCommand.creator,
    #                                     place_tool.K_TOOL_CMD_NAME,
    #                                     place_tool.PlaceToolCmd.creator,
    #                                     place_tool.PlaceToolCmd.syntax)
    #  except:
    #      sys.stderr.write("Failed to register context command: %s\n" % place_tool.K_CONTEXT_NAME)
    #      raise
    #
    #  try:
    #      mplugin.registerContextCommand(spray_tool.K_CONTEXT_NAME,
    #                                     spray_tool.SprayContextCommand.creator,
    #                                     spray_tool.K_TOOL_CMD_NAME,
    #                                     spray_tool.SprayToolCmd.creator,
    #                                     spray_tool.SprayToolCmd.syntax)
    #  except:
    #      sys.stderr.write("Failed to register context command: %s\n" % spray_tool.K_CONTEXT_NAME)
    #      raise

    #  try:
    #      mplugin.registerContextCommand(move_tool.K_CONTEXT_NAME,
    #                                     move_tool.SprayContextCommand.creator,
    #                                     move_tool.K_TOOL_CMD_NAME,
    #                                     move_tool.SprayToolCmd.creator,
    #                                     move_tool.SprayToolCmd.syntax)
    #  except:
    #      sys.stderr.write("Failed to register context command: %s\n" % move_tool.K_CONTEXT_NAME)
    #      raise
    #
    #  try:
    #      mplugin.registerContextCommand(scale_tool.K_CONTEXT_NAME,
    #                                     scale_tool.ScaleContextCommand.creator,
    #                                     scale_tool.K_TOOL_CMD_NAME,
    #                                     scale_tool.ScaleToolCmd.creator,
    #                                     scale_tool.ScaleToolCmd.syntax)
    #  except:
    #      sys.stderr.write("Failed to register context command: %s\n" % scale_tool.K_CONTEXT_NAME)
    #      raise
    #
    #
    #  try:
    #      mplugin.registerContextCommand(align_tool.K_CONTEXT_NAME,
    #                                     align_tool.AlignContextCommand.creator,
    #                                     align_tool.K_TOOL_CMD_NAME,
    #                                     align_tool.AlignToolCmd.creator,
    #                                     align_tool.AlignToolCmd.syntax)
    #  except:
    #      sys.stderr.write("Failed to register context command: %s\n" % align_tool.K_CONTEXT_NAME)
    #      raise
    #
    #  try:
    #      mplugin.registerContextCommand(move_tool.K_CONTEXT_NAME,
    #                                     move_tool.MoveContextCommand.creator,
    #                                     move_tool.K_TOOL_CMD_NAME,
    #                                     move_tool.MoveToolCmd.creator,
    #                                     move_tool.MoveToolCmd.syntax)
    #  except:
    #      sys.stderr.write("Failed to register context command: %s\n" % move_tool.K_CONTEXT_NAME)
    #      raise
    #




    #  try:
    #      mplugin.registerContextCommand(spore_tool.ContextCommand.name,
    #                                     spore_tool.ContextCommand.creator,
    #                                     spore_tool.tool_cmd_name,
    #                                     spore_tool.cmd_creator)
    #  except:
    #      sys.stderr.write( "Failed to register node: %s" % spore_tool.ContextCommand.name)
    #      raise
    #
    #  try:
    #      mplugin.registerCommand(spray_cmd.SprayCommnad.kPluginCmdName,
    #                              spray_cmd.SprayCommand.cmdCreator,
    #                              spray_cmd.SprayCommand.syntaxCreator)
    #  except:
    #      sys.stderr.write("Failed to register command: %s\n" % kPluginCmdName)
    #      raise
    #


def uninitializePlugin(mobject):

    mplugin = ompx.MFnPlugin(mobject)

    #  pm.callbacks(removeCallback=load_spore_template,
    #               hook='AETemplateCustomContent',
    #               owner=spore_node.SporeNode.name)

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


    #  try:
    #      mplugin.deregisterContextCommand(spray_tool.K_CONTEXT_NAME)
    #  except:
    #      sys.stderr.write("Failed to deregister node: %s" % spray_tool.K_CONTEXT_NAME)
    #      raise
    #
    #  #  try:
    #  #      mplugin.deregisterContextCommand(move_tool.K_CONTEXT_NAME)
    #  #  except:
    #  #      sys.stderr.write("Failed to deregister node: %s" % move_tool.K_CONTEXT_NAME)
    #  #      raise
    #  #
    #  try:
    #      mplugin.deregisterContextCommand(scale_tool.K_CONTEXT_NAME)
    #  except:
    #      sys.stderr.write("Failed to deregister node: %s" % scale_tool.K_CONTEXT_NAME)
    #      raise
    #
    #  try:
    #      mplugin.deregisterContextCommand(align_tool.K_CONTEXT_NAME)
    #  except:
    #      sys.stderr.write("Failed to deregister node: %s" % align_tool.K_CONTEXT_NAME)
    #      raise
    #
    #  try:
    #      mplugin.deregisterContextCommand(move_tool.K_CONTEXT_NAME)
    #  except:
    #      sys.stderr.write("Failed to deregister node: %s" % move_tool.K_CONTEXT_NAME)
    #      raise

#  def load_spore_template(node_name):
#      from spore.ui import AEsporeNodeTemplate
#      ae_template = AEsporeNodeTemplate.AEsporeNodeTemplate(node_name[0])
#      print 'NODE SPECIFIC AE', node_name[0], ae_template
