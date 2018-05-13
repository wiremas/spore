from maya import cmds

import pymel.core as pm
import maya.mel as mel
from pymel.core.uitypes import AETemplate
import maya.OpenMayaUI as omui
import maya.OpenMaya as om

from PySide2.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout, QListWidget
from shiboken2 import wrapInstance


import window_utils
import node_utils
#  import navigator_ctrl
reload(window_utils)
#  reload(navigator_ctrl)
reload(node_utils)


class AEsporeNodeTemplate(AETemplate):

    def __init__(self, node):
        super(AEsporeNodeTemplate, self).__init__(node)

        self._node = node
        self.callbacks = om.MCallbackIdArray()
        self.navigator = None
        self.context = None

        #  print self.__dict__, self
        #  print cmds.setParent(q=True)

        #  self.emit_crtls = ('gridSize', 'minEmitDistance')
        #
        self.beginScrollLayout()

        self.build_ui()
        #  mel.AEdependNodeTemplate(node)
        #  self.dim_controls()
        #  mel.AElocatorTemplate(node)
        #  mel.AElocatorInclude(node)
        #  pm.mel.AElocatorCommon(node)
        #  pm.mel.AElocatorInclude(node)  # TODO - maybe?
        #  mel.AELocatorMain(node)
        #  mel.AEtransformNoScroll(node)
        #  mel.editorTemplate(add
        #  cmds.editorTemplate(addExtraControls=True)
        self.addExtraControls('Extra Attributes')

        self.endScrollLayout()

        #  navigator_wdg = get_nav_layout()
        #  navigator_lay = QGridLayout()
        #
        #  l = QListWidget()
        #  navigator_lay.addWidget(l)
        #  self.add_callbacks()

        #  self.add_callbacks()

    def __del__(self):
        for i in xrange(self.callbacks.length()):
            print 'remove cb'
            om.Message().removeCallback(self.callbacks[i])


    def add_callbacks(self):
        """ register a bunch of node callbacks to hook our qt widget
        this is kind of hacky solution since this only adds our custom
        navigator widgets after one of the callbacks has been triggered.
        desireably we'd like to hook the widget after node initialization.
        but since the the parent layout in the AE does not exist at node init,
        we need to find a way to parent the widget at a later point in time """

        if self.callbacks.length() <= 1:
            m_node = node_utils.get_mobject_from_name(self._node)
            self.callbacks.append(om.MNodeMessage().addAttributeChangedCallback(m_node, self.hook_qt_widget))
            self.callbacks.append(om.MDGMessage().addConnectionCallback(self.hook_qt_widget))

    def hook_qt_widget(self, *args):
        """ hook the navigator widget to the attribute editor
        update the navigator widget if it already exists """

        print 'attr changed', args

        #  if not container_lay.children():
        if not self.navigator:
            container_wdg = get_nav_layout()
            container_lay = container_wdg.layout() #.children()
            self.navigator = navigator_ctrl.Navigator(self._node)
            navigator_wdg = self.navigator.get_widget()
            container_lay.addWidget(navigator_wdg)

        else:
            self.navigator.update_ui()

    #  def add_callbacks(self):
    #      print 'addcb'
    #      cmds.callbacks(addCallback=self.foo,
    #                     hook='AETemplateCustomContent',
    #                     o=self._node)
    #
    #  def foo(self, *args):
    #      print 'aaaa', get_nav_layout(), args

    def build_ui(self):

        # instance list
        #  self.beginLayout('Instance Properties', collapse=0)
        #  self.addControl('numInstances', label='Number Of Instances')
        #  tsl = cmds.textScrollList(parent=foo)
        #  self.endLayout(

        # emit properties
        self.beginLayout('Emit', collapse=1)
        self.addControl('emitType', label='Type', changeCommand=self.emit_type_cc)
        self.addControl('numSamples', label='Number Of Samples')
        self.addControl('minRadius', label='Number Of Samples')

        self.beginLayout('Filter', collapse=1)
        self.addControl('emitFromTexture', label='Emit from Texture')
        self.addControl('emitTexture', label='Texture')
        self.addSeparator()
        self.addControl('minAltitude', 'Min Altitude')
        self.addControl('maxAltitude', 'Max Altitude')
        self.addSeparator()
        self.addControl('minSlope', 'Min Slope')
        self.addControl('maxSlope', 'Max Slope')
        self.endLayout()
        self.callCustom(self.add_emit_btn, self.update_emit_btn, "emit" )
        self.endLayout()

        # brush properties
        self.beginLayout('Brush', collapse=0)
        self.callCustom(self.add_brush_btn, self.update_brush_btn, 'contextMode')
        self.addControl('numBrushSamples', label='Number Of Samples')
        self.addSeparator()
        self.addControl('minDistance', label='Min Distance')
        self.addSeparator()
        self.addControl('fallOff', label='Falloff')
        self.dimControl(self._node, 'fallOff', True)
        self.addSeparator()
        self.addControl('alignTo', label='Align To')
        self.addControl('strength', label='Weight')
        self.addControl('minRotation', label='Min Rotation')
        self.addControl('maxRotation', label='Max Rotation')
        self.addSeparator()
        self.addControl('uniformScale', label='Uniform Scale', changeCommand=self.uniform_scale_toggle)
        self.addControl('minScale', label='Min Scale')
        self.addControl('maxScale', label='Max Scale')
        self.addControl('scaleFactor', label='Scale Factor')
        self.addControl('scaleAmount', label='Randomize / Smooth')
        self.dimControl(self._node, 'scaleFactor', True)
        self.addSeparator()
        self.addControl('minOffset', label='Min Offset')
        self.addControl('maxOffset', label='Max Offset')
        self.addSeparator()
        self.addControl('minId', label='Min Id', changeCommand=lambda _: self.index_cc('min'))
        self.addControl('maxId', label='Max Id', changeCommand=lambda _: self.index_cc('max'))
        self.addSeparator()
        self.addControl('usePressureMapping', label='Use Pen Pressure', changeCommand=self.use_pressure_cc)
        self.addControl('pressureMapping', label='Pessure Mapping')
        self.addControl('minPressure', label='Min Pessure')
        self.addControl('maxPressure', label='Max Pessure')
        #  self.callCustom(self.add_pressure_cbx, self.update_pressure_cbx, 'usePressureMapping')
        self.endLayout()

        self.beginLayout('Instanced Objects', collapse=0)
        self.callCustom(self.add_instance_list, self.update_instance_list)
        self.endLayout()


        self.beginLayout('I/O', collapse=1)
        self.beginLayout('input', collapse=1)
        self.endLayout()
        self.beginLayout('output', collapse=1)
        self.endLayout()
        self.endLayout()


        # display properties
        self.beginLayout('Display', collapse=1)
        self.addControl('numSpores', label='Number of Points')
        #  self.addControl('pointVisibility', label='Display Spores')
        #  self.addControl('normalVisibility', label='Display Normals')
        #  self.addControl('displaySize', label='Spore Radius')
        self.endLayout()

        #  self.callCustom(self.dim_controls, self.dim_controls)
        #  self.dimControl(self._node, 'numSpraySamples', True)
        #  self.dimControl(self._node, 'minDistance', True)
        #  self.dimControl(self._node, 'strength', False)
        #  self.suppress('minDistance')


    # ------------------------------------------------------------------------ #
    # instance geometry list
    # ------------------------------------------------------------------------ #
    def add_instance_list(self, *args):

        instanced_geo = node_utils.get_instanced_geo(self._node)
        if instanced_geo:
            instanced_geo = ['[{}]: {}'.format(i, name) for i, name in enumerate(instanced_geo)]
        else:
            instanced_geo = ['No source geometry selected']
        cmds.textScrollList('instanceList', allowMultiSelection=True,
                            append=instanced_geo, height=100)

        cmds.rowLayout(nc=2, adjustableColumn=2)
        cmds.button('addInstanceBtn', l='Add', c=pm.Callback(self.add_instance))
        cmds.button('removeInstanceBtn', l='Remove', c=pm.Callback(self.remove_instance))
        cmds.setParent('..')

    def update_instance_list(self, *args):

        instanced_geo = node_utils.get_instanced_geo(self._node)
        if instanced_geo:
            instanced_geo = ['[{}]: {}'.format(i, name.split('|')[-1]) for i, name in enumerate(instanced_geo)]
        else:
            instanced_geo = ['No source geometry selected']

        cmds.textScrollList('instanceList', e=1, removeAll=True)
        cmds.textScrollList('instanceList', e=1, append=instanced_geo)

    def add_instance(self):
        selection = cmds.ls(sl=True, l=True)
        spore_node = selection.pop(-1)

        num_items = cmds.textScrollList('instanceList', numberOfItems=True, q=True)
        #  items = cmds.textScrollList('instanceList', q=True, ai=True)
        for i, obj in enumerate(selection):
            # TODO - connect to instancer or continue if nothing to add
            item_str = '[{}]: {}'.format(i + num_items, obj)
            cmds.textScrollList('instanceList', e=1, append=item_str)

    def remove_instance(self):
        selection = cmds.textScrollList('instanceList', q=1, selectItem=True)
        print 'remove', selection


    # ------------------------------------------------------------------------ #
    # falloff control
    # ------------------------------------------------------------------------ #

    #  def add_falloff_ctrl(self):
    #      cmds.rowLayout('falloffLayou', nc=3)
    #      cmds.text(l='Falloff')
    #      rb_collection = cmds.radioCollection()
    #      cmds.radioButton('noFalloffRadio', l='None') #, onc=pm.Callback(self.set_falloff_ctrl, 0))
    #      cmds.radioButton('linearFalloffRadio', l='Linear') #, onc=pm.Callback(self.set_falloff_ctrl, 1))
    #      cmds.setParent('..')
    #      #  cmds.setParent('..')
    #
    #  def update_falloff_ctrl(self):
    #      print 'update falloff ctrl'
    #
    #  def set_falloff_ctrl(self, falloff):
    #      cmds.setAttr('{}.fallOff'.foramt(falloff))

    # ------------------------------------------------------------------------ #
    # emit button
    # ------------------------------------------------------------------------ #

    def add_emit_btn(self, attr):
        """ add button to trigger emit checkbox """

        cmd = 'cmds.setAttr("{}", 1)'.format(attr)
        cmds.button('emitButton', l='Emit', c=cmd )

    def update_emit_btn(self, attr):
        """ update button to trigger emit checkbox """

        cmd = 'cmds.setAttr("{}", 1)'.format(attr)
        cmds.button('emitButton', e=True, c=cmd)

    # ------------------------------------------------------------------------ #
    # context mode buttons
    # ------------------------------------------------------------------------ #

    def add_brush_btn(self, attr):
        """ replace the default combobox with a button for each entry """

        cmds.rowLayout('instanceLayout', nc=8 ) #, adjustableColumn=6) #, w=270 ) #, columnWidth3=(80, 75, 150),  columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)] )
        cmds.button('placeBtn', l='Place', c=pm.Callback(self.activateContext, 'place', attr, 0))
        cmds.button('sprayBtn', l='Spray', c=pm.Callback(self.activateContext, 'spray', attr, 1))
        cmds.button('scaleBtn', l='Scale', c=pm.Callback(self.activateContext, 'scale', attr, 2))
        cmds.button('alignBtn', l='Align', c=pm.Callback(self.activateContext, 'align', attr, 3))
        #  cmds.button('smoothBtn', l='Smooth', c=pm.Callback(self.activateContext, 'smooth', attr, 4))
        #  cmds.button('randomBtn', l='Randomize', c=pm.Callback(self.activateContext, 'random', attr, 5))
        cmds.button('moveBtn', l='Move', c=pm.Callback(self.activateContext, 'move', attr, 4))
        cmds.button('idBtn', l='Id', c=pm.Callback(self.activateContext, 'id', attr, 5))
        cmds.setParent('..')


    def update_brush_btn(self, attr):

        cmds.button('placeBtn', e=True, c=pm.Callback(self.activateContext, 'place', attr, 0))
        cmds.button('sprayBtn', e=True, c=pm.Callback(self.activateContext, 'spray', attr, 1))
        cmds.button('scaleBtn', e=True, c=pm.Callback(self.activateContext, 'scale', attr, 2))
        cmds.button('alignBtn', e=True, c=pm.Callback(self.activateContext, 'align', attr, 3))
        #  cmds.button('smoothBtn', e=True, c=pm.Callback(self.activateContext, 'smooth', attr, 4))
        #  cmds.button('randomBtn', e=True, c=pm.Callback(self.activateContext, 'random', attr, 5))
        cmds.button('moveBtn', e=True, c=pm.Callback(self.activateContext, 'move', attr, 4))
        cmds.button('idBtn', e=True, c=pm.Callback(self.activateContext, 'id', attr, 5))

        self._node = attr.split('.')[0]


    def activateContext(self, context_mode, attr, index):
        """ called whenever a brush button is clicked
        enable/disable context controls & activate tool context
        @param context_mode: indicates which button has been clicked
        @param attr: holds the current node and attribute name
        @param index: the index of the child attr in the combobox """

        cmds.setAttr(attr, index)
        attr_name = attr.split('.')[-1]
        node_name = attr.split('.')[0]

        # create a tuple of all controls and a dict that associates each control
        # to a specific context style
        brush_crtls = ('minDistance', 'fallOff', 'strength',
                       'numBrushSamples', 'alignTo', 'minRotation',
                       'maxRotation', 'uniformScale', 'minScale',
                       'maxScale', 'scaleFactor', 'scaleAmount',
                       'minOffset', 'maxOffset', 'minId', 'maxId',
                       'usePressureMapping', 'pressureMapping',
                       'minPressure', 'maxPressure')
        p_map = cmds.getAttr('{}.usePressureMapping'.format(self._node))
        dim_ctrl = {                #    minD,  foff,   stren,  numS,   aliTo   minR,   maxR,   uniS    minS,   maxS,   sFac,   sAmou,  minO,   maxO,   minI,   maxI,   pre,    map,    minP,   maxP
                    'place':            (True,  False,  True,   False,  True,   True,   True,   True,   True,   True,   False,  False,  True,   True,   True,   True,   True,   p_map,  p_map,  p_map),
                    'spray':            (True,  False,  True,   True,   True,   True,   True,   True,   True,   True,   False,  False,  True,   True,   True,   True,   True,   p_map,  p_map,  p_map),
                    'scale':            (False, True,   False,  False,  False,  False,  False,  False,  False,  False,  True,   True,   False,  False,  False,  False,  True,   False,  p_map,  p_map),
                    'align':            (False, True,   True,   False,  True,   False,  False,  False,  False,  False,  False,  False,  False,  False,  False,  False,  True,   False,  p_map,  p_map),
                    'move':             (False, False,  False,  False,  False,  False,  False,  False,  False,  False,  False,  False,  False,  False,  False,  False,  True,   False,  p_map,  p_map),
                    'id':               (False, False,  False,  False,  False,  False,  False,  False,  False,  False,  False,  False,  False,  False,  True,   True,   True,   False,  p_map,  p_map),
                    }

        #  dim controls
        for i, ctrl in enumerate(brush_crtls):
            self.dimControl(node_name, ctrl, not dim_ctrl[context_mode][i])

        #  print 'CONTEXT: ', self.context
        #  if self.context is None:
        self.context = cmds.sporeContext()

        cmds.select(self._node)
        cmds.setToolTo(self.context)

    # ------------------------------------------------------------------------ #
    # pen pressure checkbox
    # ------------------------------------------------------------------------ #

    def emit_type_cc(self, node):
        """ """
        emit_type = cmds.getAttr('{}.emitType'.format(node))

        if emit_type == 0:
            self.dimControl(node, 'minEmitDistance', True)
            self.dimControl(node, 'gridSize', True)
        elif emit_type == 1:
            self.dimControl(node, 'minEmitDistance', True)
            self.dimControl(node, 'gridSize', False)
        elif emit_type == 2:
            self.dimControl(node, 'minEmitDistance', False)
            self.dimControl(node, 'gridSize', True)


    def use_pressure_cc(self, node):
        """ use pen pressure change command is triggered when the "Use Pen Pressure"
        checkbox is toggled """
        use_pressure = not cmds.getAttr('{}.usePressureMapping'.format(node))

        self.dimControl(node, 'pressureMapping', use_pressure)
        self.dimControl(node, 'minPressure', use_pressure)
        self.dimControl(node, 'maxPressure', use_pressure)

        context_mode = cmds.getAttr('{}.contextMode'.format(node))
        if context_mode in (2, 3, 4): # disable for mode 2,3,4
            self.dimControl(node, 'pressureMapping', True)
        elif context_mode == 5:
            self.dimControl(node, 'minPressure', True)
            self.dimControl(node, 'maxPressure', True)


    def update_pressure_cbx(self, attr):
        pass

    # ------------------------------------------------------------------------ #
    # uniform scale toggle
    # ------------------------------------------------------------------------ #

    def uniform_scale_toggle(self, node):
        """ toggle between uniform and non-uniform scale
        :param node: the current node name """

        print 'toggle', node
        uniform_scale = not cmds.getAttr('{}.uniformScale'.format(node))
        print 'foo', cmds.getAttr('{}.minScaleX'.format(node))

        #  self.dimControl(node, 'minScaleX', uniform_scale)
        #  self.dimControl(node, 'maxScaleX', uniform_scale)
        #  self.dimControl(node, 'minScale', uniform_scale)
        #  self.dimControl(node, 'minScaleX', False)
        #  self.dimControl(node, 'minScaleY', False)

    def index_cc(self, typ):
        """ """
        min_id = cmds.getAttr('{}.minId'.format(self._node))
        max_id = cmds.getAttr('{}.maxId'.format(self._node))

        if typ == 'min' and min_id > max_id:
            cmds.setAttr('{}.maxId'.format(self._node), min_id)
        elif typ == 'max' and max_id < min_id:
            cmds.setAttr('{}.minId'.format(self._node), max_id)

        #  if min_id > max_id

    # ------------------------------------------------------------------------ #
    # utils
    # ------------------------------------------------------------------------ #

    #  def dim_controls(self, *args):
    #      """ dim / undim all brush controls
    #      :param dim: bool if we dim or undim the controls """
    #      dim = True
    #      print 'args', args
    #
    #      for crtl in self.brush_crtls:
    #          #  self.suppress(crtl)
    #          #  print 'dim: ', self._node, crtl, dim
    #          self.dimControl(self._node, crtl, dim)
    #
    #

def get_nav_layout():

    def find_first_frame_layout(layout):
        """ recursivley get all child layout until we find the first framelayout """

        children = cmds.layout(layout, ca=True, q=True)
        for child in children:

            if child.startswith('frameLayout'):
                return child

            else:
                return find_first_frame_layout(child)


    nav_layout = find_first_frame_layout('AttrEdsporeNodeFormLayout')
    return wrapInstance(long(omui.MQtUtil.findControl(nav_layout)), QWidget)



#
#  def get_nav_layout():
#      """ get the navigator frame layout and return and wrap it as qWidget """
#
#      def find_first_frame_layout(layout):
#          """ recursivley get all child layout until we find the first framelayout """
#
#          print layout
#          children = cmds.layout(layout, ca=True, q=True)
#          print children
#          if children is None:
#              return
#          for child in children:
#              if child.startswith('frameLayout'):
#                  return child
#              if child:
#                  return find_first_frame_layout(child)
#
#      print 'l', cmds.layout('AttrEdsporeNodeFormLayout', q=1, ex=1)
#      nav_layout = find_first_frame_layout('AttrEdsporeNodeFormLayout')
#      return wrapInstance(long(omui.MQtUtil.findControl(nav_layout)), qw.QWidget)
#
