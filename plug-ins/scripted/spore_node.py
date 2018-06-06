import sys
import math

import maya.cmds as cmds

import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
import maya.OpenMayaUI as omui
import maya.OpenMayaRender as omr

#  from spore.data import point_cache

import node_utils
import instance_data
#  import ptc_sampler
import geo_cache
import progress_bar
#  import grd_sampler
#  import dsk_sampler

reload(geo_cache)

class SporeNode(ompx.MPxNode):
    name = 'sporeNode'
    id = om.MTypeId(0x88805)

    # output attributes
    a_instance_data = om.MObject()
    # input attributes
    in_mesh = om.MObject()
    # paint / place attributes
    a_context_mode = om.MObject()
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
    a_pressure = om.MObject()
    a_pressure_mapping = om.MObject()
    a_min_pressure = om.MObject()
    a_max_pressure = om.MObject()
    # emit attributes
    a_emit_type = om.MObject()
    a_emit = om.MObject()
    a_emit_from_texture = om.MObject()
    a_evaluate_shader = om.MObject()
    a_num_samples = om.MObject()
    a_min_radius = om.MObject()
    a_min_radius_2d = om.MObject()
    # filter attributes
    a_emit_texture  = om.MObject()
    a_min_altitude = om.MObject()
    a_max_altitude = om.MObject()
    a_min_altitude_fuzz = om.MObject()
    a_max_altitude_fuzz = om.MObject()
    a_min_slope = om.MObject()
    a_max_slope = om.MObject()
    a_min_slope_fuzz = om.MObject()
    a_max_slope_fuzz = om.MObject()
    a_geo_cached = om.MObject()
    a_points_cached = om.MObject()
    a_brush_radius = om.MObject()
    # count
    a_num_spores = om.MObject()
    a_clear = om.MObject()
    a_seed = om.MObject()
    # storage attributes
    a_position = om.MObject()
    a_rotation = om.MObject()
    a_scale = om.MObject()
    a_instance_id = om.MObject()
    a_visibility = om.MObject()
    a_normal = om.MObject()
    a_tangnet = om.MObject()
    a_u_coord = om.MObject()
    a_v_coord = om.MObject()
    a_poly_id = om.MObject()
    a_color = om.MObject()
    a_unique_id = om.MObject()

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
        vect_array_attr = om.MFnVectorArrayData()
        int_array_attr = om.MFnIntArrayData()
        double_array_attr = om.MFnDoubleArrayData()

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
        typed_attr_fn.setKeyable(False)
        cls.addAttribute(cls.in_mesh)

        # input attribute
        #  cls.a_out_mesh = typed_attr_fn.create('outMesh', 'outMesh', om.MFnMeshData.kMesh)
        #  typed_attr_fn.setKeyable(False)
        #  typed_attr_fn.setWritable(False)
        #  #  typed_attr_fn.setKeyable(False)
        #  #  typed_attr_fn.setReadable(False)
        #  typed_attr_fn.setReadable(True)
        #  typed_attr_fn.setStorable(True)
        #  cls.addAttribute(cls.a_out_mesh)

        # brush attributes
        cls.context_mode = enum_attr_fn.create('contextMode', 'contextMode', 0)
        enum_attr_fn.addField('place', 0)
        enum_attr_fn.addField('spray', 1)
        enum_attr_fn.addField('scale', 2)
        enum_attr_fn.addField('align', 3)
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

        cls.a_scale_factor = numeric_attr_fn.create('scaleFactor', 'scaleFactor', om.MFnNumericData.kDouble, 1.05)
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

        cls.a_min_offset = numeric_attr_fn.create('minOffset', 'minOffset', om.MFnNumericData.kDouble, 0.0)
        numeric_attr_fn.setSoftMin(-10)
        numeric_attr_fn.setSoftMax(10)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_min_offset )

        cls.a_max_offset = numeric_attr_fn.create('maxOffset', 'maxOffset', om.MFnNumericData.kDouble, 0.0)
        numeric_attr_fn.setSoftMin(-10)
        numeric_attr_fn.setSoftMax(10)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_max_offset )

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
        enum_attr_fn.addField('poisson 3d', 2)
        enum_attr_fn.addField('poisson 2d', 3)
        enum_attr_fn.setStorable(False)
        enum_attr_fn.setKeyable(False)
        enum_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_emit_type)

        cls.a_emit = numeric_attr_fn.create('emit', 'emit', om.MFnNumericData.kBoolean, 0)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_emit)

        cls.a_emit_from_texture = numeric_attr_fn.create('emitFromTexture', 'emitFromTexture', om.MFnNumericData.kBoolean, 0)
        numeric_attr_fn.setStorable(True)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setReadable(False)
        numeric_attr_fn.setKeyable(False)
        cls.addAttribute(cls.a_emit_from_texture)

        cls.a_evaluate_shader = numeric_attr_fn.create('evalShader', 'evalShader', om.MFnNumericData.kBoolean, 0)
        numeric_attr_fn.setStorable(True)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setReadable(False)
        numeric_attr_fn.setKeyable(False)
        cls.addAttribute(cls.a_evaluate_shader)

        cls.a_emit_texture  = numeric_attr_fn.createColor('emitTexture', 'emitTexture')
        numeric_attr_fn.setStorable(True)
        numeric_attr_fn.setKeyable(False)
        cls.addAttribute(cls.a_emit_texture )

        cls.a_min_altitude = numeric_attr_fn.create('minAltitude', 'minAltitude', om.MFnNumericData.kDouble, 0.0)
        numeric_attr_fn.setMin(0)
        numeric_attr_fn.setMax(1)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_min_altitude)

        cls.a_max_altitude = numeric_attr_fn.create('maxAltitude', 'maxAltitude', om.MFnNumericData.kDouble, 1.0)
        numeric_attr_fn.setMin(0)
        numeric_attr_fn.setMax(1)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_max_altitude)

        cls.a_min_altitude_fuzz = numeric_attr_fn.create('minAltitudeFuzz', 'minAltitudeFuzz', om.MFnNumericData.kDouble, 0.0)
        numeric_attr_fn.setMin(0)
        numeric_attr_fn.setMax(1)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_min_altitude_fuzz)

        cls.a_max_altitude_fuzz = numeric_attr_fn.create('maxAltitudeFuzz', 'maxAltitudeFuzz', om.MFnNumericData.kDouble, 0.0)
        numeric_attr_fn.setMin(0)
        numeric_attr_fn.setMax(1)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_max_altitude_fuzz)

        cls.a_min_slope = numeric_attr_fn.create('minSlope', 'minSlope', om.MFnNumericData.kDouble, 0.0)
        numeric_attr_fn.setMin(0)
        numeric_attr_fn.setMax(180)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_min_slope)

        cls.a_max_slope = numeric_attr_fn.create('maxSlope', 'maxSlope', om.MFnNumericData.kDouble, 180.0)
        numeric_attr_fn.setMin(0)
        numeric_attr_fn.setMax(180)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_max_slope)

        cls.a_min_slope_fuzz = numeric_attr_fn.create('slopeFuzz', 'slopeFuzz', om.MFnNumericData.kDouble, 0.0)
        numeric_attr_fn.setMin(0)
        numeric_attr_fn.setMax(1)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_min_slope_fuzz)

        cls.a_num_samples = numeric_attr_fn.create('numSamples', 'numSamples', om.MFnNumericData.kInt, 1000)
        numeric_attr_fn.setMin(0)
        numeric_attr_fn.setSoftMax(10000)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_num_samples)

        cls.a_min_radius = numeric_attr_fn.create('minRadius', 'minRadius', om.MFnNumericData.kDouble , 1.0)
        numeric_attr_fn.setMin(0.001)
        numeric_attr_fn.setSoftMax(100)
        numeric_attr_fn.setStorable(True)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_min_radius)

        cls.a_min_radius_2d = numeric_attr_fn.create('minRadius2d', 'minRadius2d', om.MFnNumericData.kDouble , 0.1)
        numeric_attr_fn.setMin(0.0001)
        numeric_attr_fn.setMax(1)
        numeric_attr_fn.setStorable(True)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_min_radius_2d)

        cls.a_cell_size = numeric_attr_fn.create('cellSize', 'cellSize', om.MFnNumericData.kDouble , 1.0)
        numeric_attr_fn.setMin(0.001)
        numeric_attr_fn.setSoftMax(100)
        numeric_attr_fn.setStorable(True)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_cell_size)

        # node attribute - dummy attributes
        cls.a_geo_cached = numeric_attr_fn.create('geoCached', 'geoCached', om.MFnNumericData.kBoolean, 0)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_geo_cached)

        cls.a_points_cached = numeric_attr_fn.create('pointsChached', 'pointsChached', om.MFnNumericData.kBoolean, 0)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_points_cached)

        cls.a_brush_radius = numeric_attr_fn.create('brushRadius', 'brushRadius', om.MFnNumericData.kDouble, 1)
        numeric_attr_fn.setMin(0.001)
        numeric_attr_fn.setSoftMax(10)
        numeric_attr_fn.setStorable(True)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        #  numeric_attr_fn.setHidden(True)
        cls.addAttribute(cls.a_brush_radius)

        cls.a_num_spores = numeric_attr_fn.create('numSpores', 'numSpores', om.MFnNumericData.kInt, 1)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_num_spores)

        cls.a_clear = numeric_attr_fn.create('clear', 'clear', om.MFnNumericData.kBoolean, 0)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_clear)

        cls.a_seed = numeric_attr_fn.create('seed', 'seed', om.MFnNumericData.kInt, -1)
        numeric_attr_fn.setMin(-1)
        numeric_attr_fn.setStorable(False)
        numeric_attr_fn.setKeyable(False)
        numeric_attr_fn.setConnectable(False)
        cls.addAttribute(cls.a_seed)

        # node storage attributes
        cls.a_position = typed_attr_fn.create('position', 'position', om.MFnData.kVectorArray, vect_array_attr.create())
        typed_attr_fn.setHidden(True)
        typed_attr_fn.setStorable(True)
        cls.addAttribute(cls.a_position)

        cls.a_rotation = typed_attr_fn.create('rotation', 'rotation', om.MFnData.kVectorArray, vect_array_attr.create())
        typed_attr_fn.setHidden(True)
        typed_attr_fn.setStorable(True)
        cls.addAttribute(cls.a_rotation)

        cls.a_scale = typed_attr_fn.create('scale', 'scale', om.MFnData.kVectorArray, vect_array_attr.create())
        typed_attr_fn.setHidden(True)
        typed_attr_fn.setStorable(True)
        cls.addAttribute(cls.a_scale)

        cls.a_instance_id = typed_attr_fn.create('instanceId', 'instanceId', om.MFnData.kIntArray, int_array_attr.create())
        typed_attr_fn.setHidden(True)
        typed_attr_fn.setStorable(True)
        cls.addAttribute(cls.a_instance_id)

        cls.a_visibility = typed_attr_fn.create('instanceVisibility', 'instanceVisibility', om.MFnData.kIntArray, int_array_attr.create())
        typed_attr_fn.setHidden(True)
        typed_attr_fn.setStorable(True)
        cls.addAttribute(cls.a_visibility)

        cls.a_normal = typed_attr_fn.create('normal', 'normal', om.MFnData.kVectorArray, vect_array_attr.create())
        typed_attr_fn.setHidden(True)
        typed_attr_fn.setStorable(True)
        cls.addAttribute(cls.a_normal)

        cls.a_tangent = typed_attr_fn.create('tangent', 'tangent', om.MFnData.kVectorArray, vect_array_attr.create())
        typed_attr_fn.setHidden(True)
        typed_attr_fn.setStorable(True)
        cls.addAttribute(cls.a_tangent)

        cls.a_u_coord = typed_attr_fn.create('uCoord', 'uCoord', om.MFnData.kDoubleArray, double_array_attr.create())
        typed_attr_fn.setHidden(True)
        typed_attr_fn.setStorable(True)
        cls.addAttribute(cls.a_u_coord)

        cls.a_v_coord = typed_attr_fn.create('vCoord', 'vCoord', om.MFnData.kDoubleArray, double_array_attr.create())
        typed_attr_fn.setHidden(True)
        typed_attr_fn.setStorable(True)
        cls.addAttribute(cls.a_v_coord)

        cls.a_poly_id = typed_attr_fn.create('polyId', 'polyId', om.MFnData.kIntArray, int_array_attr.create())
        typed_attr_fn.setHidden(True)
        typed_attr_fn.setStorable(True)
        cls.addAttribute(cls.a_poly_id)

        cls.a_color = typed_attr_fn.create('color', 'color', om.MFnData.kVectorArray, vect_array_attr.create())
        typed_attr_fn.setHidden(True)
        typed_attr_fn.setStorable(True)
        cls.addAttribute(cls.a_color)

        cls.a_unique_id = typed_attr_fn.create('uniqueId', 'uniqueId', om.MFnData.kIntArray, int_array_attr.create())
        typed_attr_fn.setHidden(True)
        typed_attr_fn.setStorable(True)
        cls.addAttribute(cls.a_unique_id)

        cls.attributeAffects(cls.a_geo_cached, cls.a_instance_data)
        cls.attributeAffects(cls.a_clear, cls.a_instance_data)

    def __init__(self):
        ompx.MPxNode.__init__(self)

    #  def isBounded(self):
    #      return True

    def boundingBox(self):
        in_mesh = node_utils.get_connected_in_mesh(self.thisMObject(), False)
        mesh_fn = om.MFnDagNode(in_mesh)
        return mesh_fn.boundingBox()

    def postConstructor(self):
        """ called after node has been constructed. used to set things up """

        self._state = None
        self.geo_cache = geo_cache.GeoCache()

        obj_handle = om.MObjectHandle(self.thisMObject())
        sys._global_spore_tracking_dir[obj_handle.hashCode()] = self
        #  print 'node hashcode', obj_handle.hashCode(), self

        self.callbacks = om.MCallbackIdArray()
        self.callbacks.append(om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeSave, self.write_points))
        self.callbacks.append(om.MNodeMessage.addNodePreRemovalCallback(self.thisMObject(), self.pre_destructor))
        #  callback = om.MNodeMessage.addNodePreRemovalCallback(self.thisMObject(), self.event)
        #  self.callbacks.append(om.MDGMessage.addConnectionCallback(self.connection_callback))
        #  self.callbacks.append(om.MDGMessage.addNodeAddedCallback(self.node_added_callback, 'sporeNode'))
        #  self.callbacks.append(om.MDGMessage.addNodeAddedCallback(self.thisMObject(), self.node_added))

    def pre_destructor(self, *args):
        """ called before node is deleted. used to clean stuff up """

        for i in xrange(self.callbacks.length()):
            om.MMessage().removeCallback(self.callbacks[i])

    def compute(self, plug, data):

        this_node = self.thisMObject()
        print 'compute', plug.info()

        if plug == self.a_instance_data:

            # if the node has yet not been in initialized create the instance
            # data attribute and read all point if some exist
            if not self._state:
                self.initialize_state(plug, data)


            # cache geometry
            is_cached = data.inputValue(self.a_geo_cached).asBool()
            if not is_cached:

                # check if there is another spore node that already has a cache
                # object for the current inmesh
                # note: this does not ensureis the cache is up to date!
                found = False
                for key, node in sys._global_spore_tracking_dir.iteritems():
                    other_in_mesh = node_utils.get_connected_in_mesh(node.thisMObject())
                    in_mesh = node_utils.get_connected_in_mesh(self.thisMObject())
                    if in_mesh == other_in_mesh and node != self:
                        self.geo_cache = node.geo_cache
                        found = True
                        break

                # if no cache was found start creating a new one
                if not found:
                    in_mesh = node_utils.get_connected_in_mesh(self.thisMObject(), False)
                    self.geo_cache.cache_geometry(in_mesh)

                # set cached to true
                is_geo_cached_handle = data.outputValue(self.a_geo_cached)
                is_geo_cached_handle.setBool(True)

        #  if plug == self.a_emit_dummy:
        #      emit_type = data.inputValue(self.a_emit_type).asShort()
        #      print 'emit type', emit_type
        #      #  print 'emit type', emit_type.type(), emit_type.asInt() #, emit_t,ype.asInt(), emit_type.asString()
        #      if emit_type == 0:
        #          print 'random'
        #      elif emit_type == 2:
        #          print 'jitter'
        #      elif emit_type == 3:
        #          print 'dsok'


    def initialize_state(self, plug, data):
        """ initialize the instance data attribute by
        creating all arrays needed. read data from the storage attributes
        and add it the instance data """

        # create array attr
        output = data.outputValue(plug)
        array_attr_fn = om.MFnArrayAttrsData()
        attr_array_obj = array_attr_fn.create()

        out_position = array_attr_fn.vectorArray('position')
        out_scale = array_attr_fn.vectorArray('scale')
        out_rotation = array_attr_fn.vectorArray('rotation')
        out_id = array_attr_fn.intArray('objectIndex')
        out_visibility = array_attr_fn.intArray('visibility')
        normal = array_attr_fn.vectorArray('normal')
        tangent = array_attr_fn.vectorArray('tangent')
        u_coord = array_attr_fn.doubleArray('u_coord')
        v_coord = array_attr_fn.doubleArray('v_coord')
        poly_id = array_attr_fn.intArray('poly_id')
        color = array_attr_fn.vectorArray('color')
        unique_id = array_attr_fn.intArray('unique_id')

        # load points from stored attributes oand copy to instance data attr
        # this should happen only once when the scene is loaded
        is_point_cached = data.inputValue(self.a_points_cached).asBool()
        if not is_point_cached:

            vect_array_fn = om.MFnVectorArrayData()
            int_array_fn = om.MFnIntArrayData()
            double_array_fn = om.MFnDoubleArrayData()

            position_data = data.outputValue(self.a_position).data()
            vect_array_fn.setObject(position_data)
            vect_array_fn.copyTo(out_position)

            rotation_data = data.outputValue(self.a_rotation).data()
            vect_array_fn.setObject(rotation_data)
            vect_array_fn.copyTo(out_rotation)

            scale_data = data.outputValue(self.a_scale).data()
            vect_array_fn.setObject(scale_data)
            vect_array_fn.copyTo(out_scale)

            instance_id_data = data.outputValue(self.a_instance_id).data()
            int_array_fn.setObject(instance_id_data)
            int_array_fn.copyTo(out_id)

            visibility_data = data.outputValue(self.a_visibility).data()
            int_array_fn.setObject(visibility_data)
            int_array_fn.copyTo(out_visibility)

            normal_data = data.outputValue(self.a_normal).data()
            vect_array_fn.setObject(normal_data)
            vect_array_fn.copyTo(normal)

            tangent_data = data.outputValue(self.a_tangent).data()
            vect_array_fn.setObject(tangent_data)
            vect_array_fn.copyTo(tangent)

            u_cood_data = data.outputValue(self.a_u_coord).data()
            double_array_fn.setObject(u_cood_data)
            double_array_fn.copyTo(u_coord)

            v_cood_data = data.outputValue(self.a_v_coord).data()
            double_array_fn.setObject(v_cood_data)
            double_array_fn.copyTo(v_coord)

            poly_id_data = data.outputValue(self.a_poly_id).data()
            int_array_fn.setObject(poly_id_data)
            int_array_fn.copyTo(poly_id)

            color_data = data.outputValue(self.a_color).data()
            vect_array_fn.setObject(color_data)
            vect_array_fn.copyTo(color)

            unique_id_data = data.outputValue(self.a_unique_id).data()
            int_array_fn.setObject(unique_id_data)
            int_array_fn.copyTo(unique_id)

            # set points cached to true
            is_point_cached_handle = data.outputValue(self.a_points_cached)
            is_point_cached_handle.setBool(True)

        # set the instance data attribute
        output.setMObject(attr_array_obj)

        self._state = instance_data.InstanceData(self.thisMObject())
        self._state.initialize_data()

    def write_points(self, *args, **kwargs):
        """ write the instanceData attribute, that can't be saved with the
        maya scene, to the node's storage attributes to make sure all points
        are svaed with the maya file """

        #  state = instance_data.SporeState(self.thisMObject())
        node_fn = om.MFnDependencyNode(self.thisMObject())
        data_plug = node_fn.findPlug('instanceData')
        data_obj = data_plug.asMObject()

        array_attr_fn = om.MFnArrayAttrsData(data_obj)
        vect_array_fn = om.MFnVectorArrayData()
        int_array_fn = om.MFnIntArrayData()
        double_array_fn = om.MFnDoubleArrayData()

        # store position
        position = array_attr_fn.vectorArray('position')
        position_obj = vect_array_fn.create(position)
        position_plug = node_fn.findPlug('position')
        position_plug.setMObject(position_obj)

        # store scale
        scale = array_attr_fn.vectorArray('scale')
        scale_obj = vect_array_fn.create(scale)
        scale_plug = node_fn.findPlug('scale')
        scale_plug.setMObject(scale_obj)

        #store rotation
        rotation = array_attr_fn.vectorArray('rotation')
        rotation_obj = vect_array_fn.create(rotation)
        rotation_plug = node_fn.findPlug('rotation')
        rotation_plug.setMObject(rotation_obj)

        # store instance id
        instance_id = array_attr_fn.intArray('objectIndex')
        instance_id_obj = int_array_fn.create(instance_id)
        instance_id_plug = node_fn.findPlug('instanceId')
        instance_id_plug.setMObject(instance_id_obj)

        # store visibility
        visibility = array_attr_fn.intArray('visibility')
        visibility_obj = int_array_fn.create(visibility)
        visibility_plug = node_fn.findPlug('visibility')
        visibility_plug.setMObject(visibility_obj)

        normal = array_attr_fn.vectorArray('normal')
        normal_obj = vect_array_fn.create(normal)
        normal_plug = node_fn.findPlug('normal')
        normal_plug.setMObject(normal_obj)

        tangent = array_attr_fn.vectorArray('tangent')
        tangent_obj = vect_array_fn.create(tangent)
        tangent_plug = node_fn.findPlug('tangent')
        tangent_plug.setMObject(tangent_obj)

        u_coord = array_attr_fn.doubleArray('u_coord')
        u_coord_obj = double_array_fn.create(u_coord)
        u_coord_plug = node_fn.findPlug('uCoord')
        u_coord_plug.setMObject(u_coord_obj)

        v_coord = array_attr_fn.doubleArray('v_coord')
        v_coord_obj = double_array_fn.create(v_coord)
        v_coord_plug = node_fn.findPlug('vCoord')
        v_coord_plug.setMObject(v_coord_obj)

        poly_id = array_attr_fn.intArray('poly_id')
        poly_id_obj = int_array_fn.create(poly_id)
        poly_id_plug = node_fn.findPlug('polyId')
        poly_id_plug.setMObject(poly_id_obj)

        color = array_attr_fn.vectorArray('color')
        color_obj = vect_array_fn.create(color)
        color_plug = node_fn.findPlug('color')
        color_plug.setMObject(color_obj)

        unique_id = array_attr_fn.intArray('unique_id')
        unique_id_obj = int_array_fn.create(unique_id)
        unique_id_plug = node_fn.findPlug('uniqueId')
        unique_id_plug.setMObject(unique_id_obj)


