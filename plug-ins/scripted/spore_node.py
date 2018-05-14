import maya.cmds as cmds

import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
import maya.OpenMayaUI as omui
import maya.OpenMayaRender as omr

#  from spore.data import point_cache

class SporeNode(ompx.MPxLocatorNode):
    name = 'sporeNode'
    id = om.MTypeId(0x88805)

    # node attributes
    a_instance_data = om.MObject() # point output attr

    # input attributes
    in_mesh = om.MObject() # input mesh
    a_emit_texture  = om.MObject() # emit texture

    # node attributes
    a_context_mode = om.MObject() # current mode of the context
    a_num_brush_samples = om.MObject()
    a_falloff = om.MObject()
    a_min_distance = om.MObject()
    a_min_rotation = om.MObject()
    a_max_rotation =  om.MObject()
    a_min_scale = om.MObject()
    a_max_scale = om.MObject()
    a_scale_factor = om.MObject()
    a_uniform_scale = om.MObject()
    a_scale_amount = om.MObject()
    a_min_offset = om.MObject()
    a_max_offset = om.MObject()
    a_min_id = om.MObject()
    a_max_id = om.MObject()
    a_strength = om.MObject()
    a_relative = om.MObject()
    a_emit_type = om.MObject()
    a_emit = om.MObject()
    a_num_samples = om.MObject()
    a_min_radius = om.MObject()
    a_pressure = om.MObject()
    a_pressure_mapping = om.MObject()
    a_min_pressure = om.MObject()
    a_max_pressure = om.MObject()
    a_cached = om.MObject()
    a_num_spores = om.MObject()

    context = None

    @classmethod
    def attach_context(cls, context):
        cls.context = context

    @classmethod
    def remove_context(cls):
        cls.context = None

    @staticmethod
    def creator():
        return SporeNode()

    @classmethod
    def initialize(cls):
        generic_attr_fn = om.MFnGenericAttribute()
        typed_attr_fn = om.MFnTypedAttribute()
        enum_attr_fn = om.MFnEnumAttribute()
        numeric_attr_fn = om.MFnNumericAttribute()

        # output attributes
        cls.a_instance_data = generic_attr_fn.create('instanceData', 'instanceData')
        generic_attr_fn.addDataAccept(om.MFnArrayAttrsData.kDynArrayAttrs)
        generic_attr_fn.setKeyable(False)
        generic_attr_fn.setWritable(False)
        generic_attr_fn.setReadable(True)
        generic_attr_fn.setStorable(True)
        generic_attr_fn.setHidden(False)
        cls.addAttribute(cls.a_instance_data)

        # input attribute
        cls.in_mesh = typed_attr_fn.create('inMesh', 'inMesh', om.MFnMeshData.kMesh)
        typed_attr_fn.setWritable(True)
        typed_attr_fn.setKeyable(False)
        typed_attr_fn.setReadable(False)
        typed_attr_fn.setStorable(False)
        typed_attr_fn.setHidden(True)
        cls.addAttribute(cls.in_mesh)

        # brush attributes
        cls.context_mode = enum_attr_fn.create('contextMode', 'contextMode', 0)
        enum_attr_fn.addField('place', 0)
        enum_attr_fn.addField('spray', 1)
        enum_attr_fn.addField('scale', 2)
        enum_attr_fn.addField('align', 3)
        #  enum_attr_fn.addField('smooth', 4)
        #  enum_attr_fn.addField('random', 5)
        enum_attr_fn.addField('move', 4)
        enum_attr_fn.addField('id', 5)
        enum_attr_fn.addField('remove', 6)
        enum_attr_fn.setStorable(False)
        enum_attr_fn.setKeyable(False)
        enum_attr_fn.setConnectable(False)
        cls.addAttribute(cls.context_mode)

        cls.a_num_brush_samples = numeric_attr_fn.create('numBrushSamples', 'numBrushSamples', om.MFnNumericData.kInt, 1)
        numeric_attr_fn.setMin(1)
        numeric_attr_fn.setSoftMax(10)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        enum_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_num_brush_samples)

        cls.a_falloff = enum_attr_fn.create('fallOff', 'fallOff', 1)
        enum_attr_fn.addField('None', 0)
        enum_attr_fn.addField('Linear', 1)
        enum_attr_fn.setStorable(False)
        enum_attr_fn.setKeyable(False)
        cls.addAttribute(cls.a_falloff)

        cls.a_min_distance = numeric_attr_fn.create('minDistance', 'minDistance', om.MFnNumericData.kDouble, 0.1)
        numeric_attr_fn.setMin(0.001)
        numeric_attr_fn.setSoftMax(10)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_min_distance )

        cls.a_uniform_scale = numeric_attr_fn.create('uniformScale', 'uniformScale', om.MFnNumericData.kBoolean, 1)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_uniform_scale)

        cls.a_min_scale = numeric_attr_fn.createPoint('minScale', 'minScale')
        numeric_attr_fn.setDefault(0.9, 0.9, 0.9)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_min_scale)

        cls.a_max_scale = numeric_attr_fn.createPoint('maxScale', 'maxScale')
        numeric_attr_fn.setDefault(1.1, 1.1, 1.1)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_max_scale)

        cls.a_scale_factor = numeric_attr_fn.create('scaleFactor', 'scaleFactor', om.MFnNumericData.kDouble, 1)
        numeric_attr_fn.setMin(0.001)
        numeric_attr_fn.setSoftMin(0.8)
        numeric_attr_fn.setSoftMax(1.2)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_scale_factor)

        cls.a_scale_amount = numeric_attr_fn.create('scaleAmount', 'scaleAmount', om.MFnNumericData.kDouble, 0.1)
        numeric_attr_fn.setMin(0)
        numeric_attr_fn.setMax(1)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_scale_amount)

        cls.a_min_rotation = numeric_attr_fn.createPoint('minRotation', 'minRotation')
        numeric_attr_fn.setMin(-360, -360, -360)
        numeric_attr_fn.setMax(360, 360, 360)
        numeric_attr_fn.setDefault(-3.0, -180.0, -3.0)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_min_rotation )

        cls.a_max_rotation = numeric_attr_fn.createPoint('maxRotation', 'maxRotation')
        numeric_attr_fn.setMin(-360, -360, -360)
        numeric_attr_fn.setMax(360, 360, 360)
        numeric_attr_fn.setDefault(3.0, 180.0, 3.0)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_max_rotation )

        cls.a_min_offset = numeric_attr_fn.create('minOffset', 'minOffset', om.MFnNumericData.kInt, 0)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_min_offset )

        cls.a_max_offset = numeric_attr_fn.create('maxOffset', 'maxOffset', om.MFnNumericData.kInt, 0)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_max_offset )

        cls.a_min_id = numeric_attr_fn.create('minId', 'minId', om.MFnNumericData.kInt, 0)
        numeric_attr_fn.setMin(0)
        numeric_attr_fn.setSoftMax(10)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_min_id)

        cls.a_max_id = numeric_attr_fn.create('maxId', 'maxId', om.MFnNumericData.kInt, 1)
        numeric_attr_fn.setMin(0)
        numeric_attr_fn.setSoftMax(10)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_max_id)

        cls.a_strength = numeric_attr_fn.create('strength', 'strength', om.MFnNumericData.kDouble, 1.0)
        numeric_attr_fn.setMin(0)
        numeric_attr_fn.setMax(1)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_strength )

        cls.a_alig_space = enum_attr_fn.create('alignTo', 'alignTo', 0)
        enum_attr_fn.addField('Normal', 0)
        enum_attr_fn.addField('World', 1)
        enum_attr_fn.addField('Object', 2)
        enum_attr_fn.addField('Stroke', 3)
        enum_attr_fn.setStorable(False)
        enum_attr_fn.setKeyable(False)
        enum_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_alig_space)

        cls.a_pressure = numeric_attr_fn.create('usePressureMapping', 'usePressureMapping', om.MFnNumericData.kBoolean, 0)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_pressure)

        cls.a_pressure_mapping = enum_attr_fn.create('pressureMapping', 'pressureMapping', 0)
        enum_attr_fn.addField('Number Of Samples', 0)
        enum_attr_fn.addField('Min Distance', 1)
        enum_attr_fn.addField('Weigth', 2)
        enum_attr_fn.addField('Rotation', 3)
        enum_attr_fn.addField('Scale', 4)
        enum_attr_fn.addField('Offset', 5)
        enum_attr_fn.addField('Id', 6)
        enum_attr_fn.setStorable(False)
        enum_attr_fn.setKeyable(False)
        enum_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_pressure_mapping)

        cls.a_min_pressure = numeric_attr_fn.create('minPressure', 'minPressure', om.MFnNumericData.kDouble, 0.0)
        numeric_attr_fn.setMin(0)
        numeric_attr_fn.setMax(1)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_min_pressure )

        cls.a_max_pressure = numeric_attr_fn.create('maxPressure', 'maxPressure', om.MFnNumericData.kDouble, 1.0)
        numeric_attr_fn.setMin(0)
        numeric_attr_fn.setMax(1)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_max_pressure )

        # node attributes - emit attributes
        cls.a_emit_type = enum_attr_fn.create('emitType', 'emitType', 0)
        enum_attr_fn.addField('random', 0)
        enum_attr_fn.addField('jitter grid', 1)
        enum_attr_fn.addField('poisson', 2)
        enum_attr_fn.setStorable(False)
        enum_attr_fn.setKeyable(False)
        enum_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_emit_type)

        cls.a_emit = numeric_attr_fn.create('emit', 'emit', om.MFnNumericData.kBoolean, 0)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_emit)

        cls.a_emit_from_texture = numeric_attr_fn.create('emitFromTexture', 'emitFromTexture', om.MFnNumericData.kBoolean, 1)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setReadable(False)
        numeric_attr_fn.setKeyable(False)
        cls.addAttribute(cls.a_emit_from_texture)

        cls.a_emit_texture  = numeric_attr_fn.createColor('emitTexture', 'emitTexture')
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_emit_texture )

        cls.a_num_samples = numeric_attr_fn.create('numSamples', 'numSamples', om.MFnNumericData.kInt, 1)
        numeric_attr_fn.setMin(0)
        numeric_attr_fn.setSoftMax(10000)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_num_samples)

        cls.a_min_radius = numeric_attr_fn.create('minRadius', 'minRadius', om.MFnNumericData.kDouble , 1.0)
        numeric_attr_fn.setMin(0.001)
        numeric_attr_fn.setSoftMax(100)
        numeric_attr_fn.setSoftMax(10000)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_min_radius)

        # node attribute - dummy attributes
        cls.a_cached = numeric_attr_fn.create('cached', 'cached', om.MFnNumericData.kBoolean, 0)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_cached)

        cls.a_num_spores = numeric_attr_fn.create('numSpores', 'numSpores', om.MFnNumericData.kInt, 1)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_num_spores)

        cls.attributeAffects(cls.a_emit, cls.a_instance_data)

    def __init__(self):
        ompx.MPxLocatorNode.__init__(self)

    def postConstructor(self):

        # initialize point cache
        #  self.cache = point_cache.PointCloud()

        # write point cache to node attributes before saving the scene
        #  self.save_callback = om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeSave, self.write_cache)
        # kBeforeNew, kBeforeOpen kMayaExiting
        #  callback = om.MNodeMessage.addNodePreRemovalCallback(self.thisMObject(), self.event)
        self.callbacks = om.MCallbackIdArray()
        self.callbacks.append(om.MNodeMessage.addNodePreRemovalCallback(self.thisMObject(), self.pre_destructor))
        self.callbacks.append(om.MDGMessage.addConnectionCallback(self.connection_callback))
        self.callbacks.append(om.MDGMessage.addNodeAddedCallback(self.node_added_callback, 'sporeNode'))
        #  self.callbacks.append(om.MDGMessage.addNodeAddedCallback(self.thisMObject(), self.node_added))

    def pre_destructor(self, *args):
        print '__del__', args
        for i in xrange(self.callbacks.length()):
            om.MMessage().removeCallback(self.callbacks[i])

    def connection_callback(self, *args):
        #  print 'connection callback', args
        pass

    def node_added_callback(self, *args):
        #  print 'node added ', args
        pass

    def write_cache(self, *args, **kwargs):
        """ write the in-memory point cache to the node's attributes to
        make sure we save all our points with the maya file """

        print "WRITE CACHE", args, kwargs

    def compute(self, plug, data):
        #  return None
        print 'compute'

        this_node = self.thisMObject()

        is_cached = data.inputValue(self.a_cached).asBool()
        if not is_cached:
            #  print 'CACHE!'
            pass

        if plug == self.a_instance_data:

            output = data.outputValue(plug)

            #  if output.isGeneric(True, ):
            array_attr_fn = om.MFnArrayAttrsData()
            attr_array_obj = array_attr_fn.create()

            out_position = array_attr_fn.vectorArray('position')
            out_scale = array_attr_fn.vectorArray('scale')
            out_rotation = array_attr_fn.vectorArray('rotation')
            out_id = array_attr_fn.intArray('objectIndex')
            out_id = array_attr_fn.intArray('visibility')

            normal = array_attr_fn.vectorArray('normal')
            tangent = array_attr_fn.vectorArray('tangent')
            u_coord = array_attr_fn.doubleArray('u_coord')
            v_coord = array_attr_fn.doubleArray('v_coord')
            poly_id = array_attr_fn.intArray('poly_id')
            color = array_attr_fn.vectorArray('color')
            unique_id = array_attr_fn.intArray('unique_id')

            #  for i in xrange(10):
            #      out_position.append(om.MVector(0, i, 0))

            output.setMObject(attr_array_obj)



