import math
import random

import numpy as np

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
import node_state
import event_filter
import brush_utils

reload(canvas)
reload(mesh_utils)
reload(node_utils)
reload(message_utils)
reload(brush_utils)
reload(brush_state)
reload(node_state)
reload(event_filter)


""" -------------------------------------------------------------------- """
""" GLOBALS """
""" -------------------------------------------------------------------- """


K_TOOL_CMD_NAME="sporeToolCmd"
K_CONTEXT_NAME="sporeContext"

K_TRACKING_DICTIONARY = {}


""" -------------------------------------------------------------------- """
""" Sender """
""" -------------------------------------------------------------------- """


class Sender(QObject):
    press = Signal(QPoint)
    drag = Signal(QPoint)
    release = Signal(QPoint)


""" -------------------------------------------------------------------- """
""" TOOL COMMAND """
""" -------------------------------------------------------------------- """


class SporeToolCmd(ompx.MPxToolCommand):
    """ spore base tool command - abstract tool command class ment to be
    subclassed in order to create new spore tool commands """
    k_click, k_drag, k_release = 0, 1, 2

    def __init__(self):
        ompx.MPxToolCommand.__init__(self)
        self.setCommandString(K_TOOL_CMD_NAME)
        K_TRACKING_DICTIONARY[ompx.asHashable(self)] = self

        self.brush_state = None
        self.node_state = None
        self.last_brush_position = None

        self.last_undo_journal = ''

        self.position = om.MVectorArray()
        self.scale = om.MVectorArray()
        self.rotation = om.MVectorArray()
        self.instance_id = om.MIntArray()
        self.normal = om.MVectorArray()
        self.tangent = om.MVectorArray()
        self.u_coord = om.MDoubleArray()
        self.v_coord = om.MDoubleArray()
        self.poly_id = om.MIntArray()
        self.color = om.MVectorArray()
        self.point_id = om.MIntArray()

        self.initial_rotation = om.MVectorArray()
        self.initial_scale = om.MVectorArray()
        self.initial_offset = om.MDoubleArray()
        self.initial_id = om.MIntArray()
        self.spray_coords = []

    def __del__(self):
        try:
            del K_TRACKING_DICTIONARY[ompx.asHashable(self)]
        except KeyError:
            pass

    @staticmethod
    def creator():
        return ompx.asMPxPtr(SporeToolCmd())

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
        self.displayInfo('Calling {} from the script editor is not supported\
                         '.format(K_TOOL_CMD_NAME))

        return

    def redoIt(self):
        flag = self.brush_state.action

        if self.node_state.state['mode'] == 'place'\
        or self.node_state.state['mode'] == 'spray': #'place':
            self.place_action(flag)

        elif self.node_state.state['mode'] == 'scale': #'scale'
            if self.brush_state.shift_mod: # smooth
                self.smooth_scale_action(flag)
            elif self.brush_state.meta_mod: # randomize
                self.random_scale_action(flag)
            else: # scale
                self.scale_action(flag)

        elif self.node_state.state['mode'] == 'align': #'align'
            if self.brush_state.shift_mod:
                self.smooth_align_action(flag)
            elif self.brush_state.meta_mod:
                self.random_align_action(flag)
            else:
                self.align_action(flag)

        elif self.node_state.state['mode'] == 'move': #'move':
            self.move_action(flag)

        elif self.node_state.state['mode'] == 'id': #'index':
            self.index_action(flag)

    def undoIt(self):
        print 'undoIt', self.last_undo_journal
        self.last_undo_journal = cmds.undoInfo(q=True, un=True)

    def isUndoable(self):
        return True

    def finalize(self):
        """ Command is finished, construct a string
        for the command for journalling. """

        command = om.MArgList()
        command.addArg(self.commandString())

        if self.node_state.state['mode'] == 'place': #'place':
            command.addArg('place')
            for i in xrange(self.position.length()):
                command.addArg(self.position[i])

        if self.node_state.state['mode'] == 'spray': #'place':
            command.addArg('spray')
            command.addArg(self.position.length())

        # This call adds the command to the undo queue and sets
        # the journal string for the command.
        ompx.MPxToolCommand._doFinalize(self, command)

        for i in xrange(command.length()):
            self.last_undo_journal += ' {}'.format(command.asString(i))

        # reset command variables
        self.position = om.MVectorArray()
        self.scale = om.MVectorArray()
        self.rotation = om.MVectorArray()
        self.instance_id = om.MIntArray()
        self.normal = om.MVectorArray()
        self.tangent = om.MVectorArray()
        self.u_coord = om.MDoubleArray()
        self.v_coord = om.MDoubleArray()
        self.poly_id = om.MIntArray()
        self.color = om.MVectorArray()
        self.point_id = om.MIntArray()

        self.initial_rotation = om.MVectorArray()
        self.initial_scale = om.MVectorArray()
        self.initial_offset = om.MDoubleArray()
        self.initial_id = om.MIntArray()
        self.spray_coords = []

    """ -------------------------------------------------------------------- """
    """ place """
    """ -------------------------------------------------------------------- """

    def place_action(self, flag):
        position, normal, tangent = self.get_brush_coords()

        # return if we under min_distance threashold
        if not self.brush_state.shift_mod and self.last_brush_position:
            min_distance = self.node_state.state['min_distance']
            if position.distanceTo(self.last_brush_position) < min_distance:
                return

        self.last_brush_position = position

        # set number of samples or default to 1 in place mode
        if self.node_state.state['mode'] == 'spray': # spray mode
            num_samples = self.node_state.state['num_samples']
        else:
            num_samples = 1

        # set last placed points "cache" and begin to sample
        self.set_cache_length(num_samples)
        for i in xrange(num_samples):

            # if in spay mode get random coords on the brush dist or get last values
            if self.node_state.state['mode'] == 'spray': # spray mode
                if self.brush_state.shift_mod and flag != SporeToolCmd.k_click:
                    angle, distance = self.spray_coords[i]
                else:
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.uniform(0, self.brush_state.radius)
                    self.spray_coords.append((angle, distance))

                # place point on brush disk
                rotation = om.MQuaternion(angle, normal)
                tangential_vector = tangent.rotateBy(rotation)
                rand_pos =  position + tangential_vector * distance
                position, normal = mesh_utils.get_closest_point_and_normal(rand_pos, self.brush_state.target)
                tangent = mesh_utils.get_tangent(normal)

            # get point data
            rotation = self.get_rotation(flag, normal, i)
            scale = self.get_scale(flag, i)
            position = self.get_offset(position, normal, flag, i)
            instance_id = self.get_instance_id(flag, i)
            u_coord, v_coord = mesh_utils.get_uv_at_point(self.brush_state.target, position)
            color = om.MVector(0, 0, 0)

            # set internal cached points
            self.position.set(om.MVector(position), i)
            self.rotation.set(rotation, i)
            self.scale.set(scale, i)
            self.instance_id.set(instance_id, i)
            self.normal.set(normal, i)
            self.tangent.set(tangent, i)
            self.u_coord.set(u_coord, i)
            self.v_coord.set(v_coord, i)
            # TODO - not yet implemented
            self.poly_id.set(0, i)

        # set or append data
        if self.brush_state.shift_mod and flag != SporeToolCmd.k_click:
            self.node_state.set_points(self.point_id,
                                    self.position,
                                    self.scale,
                                    self.rotation,
                                    self.instance_id,
                                    self.normal,
                                    self.tangent,
                                    self.u_coord,
                                    self.v_coord,
                                    self.poly_id,
                                    self.color)

        else:
            self.point_id = self.node_state.append_points(self.position,
                                        self.scale,
                                        self.rotation,
                                        self.instance_id,
                                        self.normal,
                                        self.tangent,
                                        self.u_coord,
                                        self.v_coord,
                                        self.poly_id,
                                        self.color)

        # refresh set plug data and update view
        self.node_state.set_state()

    """ ------------------------------------------------------- """
    """ align """
    """ ------------------------------------------------------- """

    def align_action(self, flag):
        position, normal, tangent = self.get_brush_coords()
        radius = self.brush_state.radius

        neighbour = self.node_state.get_closest_points(position, radius)
        self.set_cache_length(len(neighbour))
        for i, index in enumerate(neighbour):
            rotation = self.node_state.rotation[index]
            print 'init rotation', rotation.x, rotation.y, rotation.z
            normal = self.node_state.normal[index]
            direction = self.get_alignment(normal)
            rotation = self.rotate_into(direction, rotation)

            #  print self.node_state.position[index], i, self.position.length()
            self.position.set(self.node_state.position[index], i)
            self.scale.set(self.node_state.scale[index], i)
            self.rotation.set(rotation, i)
            self.instance_id.set(self.node_state.instance_id[index], i)
            self.normal.set(normal, i)
            self.tangent.set(self.node_state.tangent[index], i)
            self.u_coord.set(self.node_state.u_coord[index], i)
            self.v_coord.set(self.node_state.v_coord[index], i)
            self.poly_id.set(self.node_state.poly_id[index], i)

        self.node_state.set_points(neighbour,
                                self.position,
                                self.scale,
                                self.rotation,
                                self.instance_id,
                                self.normal,
                                self.tangent,
                                self.u_coord,
                                self.v_coord,
                                self.poly_id,
                                self.color)

        self.node_state.set_state()

    def smooth_align_action(self, flag):
        """ """

        print 'Smooth align. Not implemented yet'

    def random_align_action(self, flag):
        """ """

        print 'Randomize align. Not implemented yet'

    """ ------------------------------------------------------- """
    """ scale """
    """ ------------------------------------------------------- """

    def scale_action(self, flag):
        position, normal, tangent = self.get_brush_coords()
        radius = self.brush_state.radius

        neighbour = self.node_state.get_closest_points(position, radius)
        self.set_cache_length(len(neighbour))

        scale = []
        for i, index in enumerate(neighbour):
            value = self.node_state.scale[index]
            factor = self.node_state.state['scale_factor']
            scale.append((index, value * factor))

        self.set_scale_values(scale)

    def smooth_scale_action(self, flag):
        """ """

        position, normal, tangent = self.get_brush_coords()
        radius = self.brush_state.radius
        neighbour = self.node_state.get_closest_points(position, radius)
        self.set_cache_length(len(neighbour))
        average = self.node_state.get_scale_average(neighbour)
        amount = self.node_state.state['scale_amount']

        scale = []
        for i, index in enumerate(neighbour):
            value = self.node_state.scale[index]
            value = [value.x, value.y, value.z]
            delta = np.subtract(average, value)
            step = np.multiply(delta, amount)
            new_scale = np.add(value, step)
            # TODO - uniform scale
            value = om.MVector(new_scale[0], new_scale[1], new_scale[2])
            scale.append((index, value))

        self.node_state.set_points(neighbour, scale=self.scale)
        self.node_state.set_state()

    def random_scale_action(self, flag):
        position, normal, tangent = self.get_brush_coords()
        radius = self.brush_state.radius
        neighbour = self.node_state.get_closest_points(position, radius)
        self.set_cache_length(len(neighbour))
        amount = self.node_state.state['scale_amount']

        for i, index in enumerate(neighbour):
            value = self.node_state.scale[index]
            value = [value.x, value.y, value.z]
            # get rand scale, rand * 2 -1 to distribute evenly between -1 and +1
            if self.node_state.state['uni_scale']:
                step = np.multiply(np.multiply(np.ones(3), np.random.rand() * 2 - 1), amount)
            else:
                step = np.multiply(np.minus(np.multiply(np.sample(3), 2), 1), amount)
            new_scale = np.add(value, step)
            value = om.MVector(new_scale[0], new_scale[1], new_scale[2])
            self.scale.set(value, i)

        self.node_state.set_points(neighbour, scale=self.scale)
        self.node_state.set_state()

    """ ------------------------------------------------------- """
    """ move """
    """ ------------------------------------------------------- """

    def move_action(self, flag):
        print 'move'

    """ ------------------------------------------------------- """
    """ index """
    """ ------------------------------------------------------- """

    def index_action(self, flag):
        position, normal, tangent = self.get_brush_coords()
        radius = self.brush_state.radius
        neighbour = self.node_state.get_closest_points(position, radius)
        self.set_cache_length(len(neighbour))
        min_id = self.node_state.state['min_id']
        max_id = self.node_state.state['max_id']

        for i, index in enumerate(neighbour):
            if min_id == max_id:
                new_id = min_id
            else:
                new_id = np.random.randint(min_id, max_id)
            self.instance_id.set(new_id, i)

        self.node_state.set_points(neighbour, instance_id=self.instance_id)
        self.node_state.set_state()


    """ -------------------------------------------------------------------- """
    """ utils """
    """ -------------------------------------------------------------------- """

    def get_brush_coords(self):
        """ get current brush position, normal and tangent """

        position = om.MPoint(self.brush_state.position[0],
                             self.brush_state.position[1],
                             self.brush_state.position[2])
        normal = om.MVector(self.brush_state.normal[0],
                            self.brush_state.normal[1],
                            self.brush_state.normal[2])
        tangent = om.MVector(self.brush_state.tangent[0],
                             self.brush_state.tangent[1],
                             self.brush_state.tangent[2])

        return position, normal, tangent

    def get_alignment(self, normal):
        """ get the alignment vector """
        print 'metamod', self.brush_state.meta_mod

        if self.node_state.state['align_to'] == 'world': # align to world
            direction = om.MVector(0, 1, 0)

        elif self.node_state.state['align_to'] == 'object': # align to obj's local
            # TODO - get object up vector
            pass

        elif self.node_state.state['align_to'] == 'stroke'\
        or self.brush_state.meta_mod: # align to stroke
            direction = om.MVector(self.brush_state.stroke_direction[0],
                                    self.brush_state.stroke_direction[1],
                                    self.brush_state.stroke_direction[2])

        else:
            direction = normal

        return direction


    def rotate_into(self, direction, rotation, index=0):
        """ slerp the given rotation values into the direction given
        by the brush_state
        @param direction MVector: the target direction
        @param rotation MVector: current euler rotation """

        vector_weight = self.node_state.state['strength']
        up_vector = om.MVector(0, 1, 0)
        local_up = up_vector.rotateBy(om.MEulerRotation(math.radians(rotation.x),
                                                        math.radians(rotation.y),
                                                        math.radians(rotation.z)))

        if math.degrees(direction.angle(local_up)) <= 4: # 1 degree of rotation threashold
            #  print 'localUp:', local_up.x, local_up.y, local_up.z
            #  print 'retun:', direction.x, direction.y, direction.z, direction.angle(local_up)
            return rotation

        util = om.MScriptUtil()
        util.createFromDouble(rotation.x, rotation.y, rotation.z)
        rotation_ptr = util.asDoublePtr()
        mat = om.MTransformationMatrix()
        mat.setRotation(rotation_ptr, om.MTransformationMatrix.kXYZ)

        rotation = om.MQuaternion(local_up, direction, vector_weight)

        rotation = om.MQuaternion.slerp(mat.rotation, rotation, 1)
        #  mat.rotateBy(rotation, om.MSpace.kWorld)
        mat.rotateTo(rotation) #, om.MSpace.kWorld)

        #  mat = mat.asMatrix() * rotation.asMatrix()
        #  rotation = mat.rotation()
        rotation = om.MTransformationMatrix(mat).rotation()

        return om.MVector(math.degrees(rotation.asEulerRotation().x),
                        math.degrees(rotation.asEulerRotation().y),
                        math.degrees(rotation.asEulerRotation().z))

    def set_cache_length(self, length=0):
        """ set the length of the point arrays """
        if length == 0:
            length = self.node_state.state['num_samples']

        self.position.setLength(length)
        self.scale.setLength(length)
        self.rotation.setLength(length)
        self.instance_id.setLength(length)
        self.normal.setLength(length)
        self.tangent.setLength(length)
        self.u_coord.setLength(length)
        self.v_coord.setLength(length)
        self.poly_id.setLength(length)
        self.color.setLength(length)

        self.initial_scale.setLength(length)
        self.initial_rotation.setLength(length)
        self.initial_offset.setLength(length)
        self.initial_id.setLength(length)

    def get_rotation(self, flag, normal, index=0):
        """ generate new rotation values based on the brush state
        if we are in drag mode we maintain old rotation values and adjust
        rotation to the new normal. we can use the index arg to set a
        specific index for the last placed objects """

        dir_vector = self.get_alignment(normal)
        vector_weight = self.node_state.state['strength']
        world_up = om.MVector(0, 1, 0)
        rotation = om.MQuaternion(world_up, dir_vector, vector_weight)

        # when we in drag mode we want to maintain old rotation values
        if self.brush_state.shift_mod and flag != SporeToolCmd.k_click:
            initial_rotation = self.initial_rotation[index]

        # otherwise we generate new values
        else:
            # get random rotation
            min_rotation = self.node_state.state['min_rot']
            max_rotation = self.node_state.state['max_rot']
            r_x = math.radians(random.uniform(min_rotation[0], max_rotation[0]))
            r_y = math.radians(random.uniform(min_rotation[1], max_rotation[1]))
            r_z = math.radians(random.uniform(min_rotation[2], max_rotation[2]))
            self.initial_rotation.set(om.MVector(r_x, r_y, r_z), index)
            initial_rotation = self.initial_rotation[index]
            #  rotation = brush_utils.get_rotation(self.initial_rotation, direction,

        mat = om.MTransformationMatrix()

        util = om.MScriptUtil()
        util.createFromDouble(initial_rotation.x,
                              initial_rotation.y,
                              initial_rotation.z)
        rotation_ptr = util.asDoublePtr()
        mat.setRotation(rotation_ptr, om.MTransformationMatrix.kXYZ)

        mat = mat.asMatrix() * rotation.asMatrix()
        rotation = om.MTransformationMatrix(mat).rotation()

        return om.MVector(math.degrees(rotation.asEulerRotation().x),
                        math.degrees(rotation.asEulerRotation().y),
                        math.degrees(rotation.asEulerRotation().z))

    def get_scale(self, flag, index=0):
        """ get scale values for the currently saved point at the given index """

        # when we in drag mode we want to maintain old scale values
        if self.brush_state.shift_mod and flag != SporeToolCmd.k_click:
            scale = self.initial_scale[index]

        # otherweise we generate new values
        else:
            min_scale = self.node_state.state['min_scale']
            max_scale = self.node_state.state['max_scale']
            uniform = self.node_state.state['uni_scale']
            if uniform:
                scale_x = scale_y = scale_z = random.uniform(min_scale[0], max_scale[0])
            else:
                scale_x = random.uniform(min_scale[0], max_scale[0])
                scale_y = random.uniform(min_scale[1], max_scale[1])
                scale_z = random.uniform(min_scale[2], max_scale[2])

            scale = om.MVector(scale_x, scale_y, scale_z)
            self.initial_scale.set(scale, index)

        return scale

    def get_offset(self, position, normal, flag, index=0):
        """ offset the given position along the given normal """

        min_offset = self.node_state.state['min_offset']
        max_offset = self.node_state.state['max_offset']
        if self.brush_state.shift_mod and flag != SporeToolCmd.k_click:
            initial_offset = self.initial_offset[index]
        else:
            initial_offset = random.uniform(min_offset, max_offset)
            self.initial_offset.set(initial_offset, index)

        return position + normal * initial_offset

    def get_instance_id(self, flag, index=0):
        """ the the instance id for the point at the given index """

        # when we in drag mode we want to maintain old instance id value
        if self.brush_state.shift_mod and flag != SporeToolCmd.k_click:
            instance_id = self.initial_id[index]

        else:
            instance_id = random.randint(self.node_state.state['min_id'],
                                         self.node_state.state['max_id'])
            self.initial_id.set(instance_id, index)
        print 'inst_id', instance_id

        return instance_id

    def initialize_tool_cmd(self, brush_state, node_state):
        """ must be called from the context setup method to
        initialize the tool command with the current brush and node state. """

        self.brush_state = brush_state
        self.node_state = node_state


""" -------------------------------------------------------------------- """
""" CONTEXT """
""" -------------------------------------------------------------------- """


class SporeContext(ompx.MPxContext):

    def __init__(self):
        ompx.MPxContext.__init__(self)
        self._setTitleString('sporeContext')
        self.setImage("moveTool.xpm", ompx.MPxContext.kImage1)

        self.state = brush_state.BrushState()
        self.node_state = None
        self.msg_io = message_utils.IOHandler()
        self.canvas = None
        self.sender = Sender()
        self.tool_cmd = None

        self.mouse_event_filter = event_filter.MouseEventFilter(self)
        self.key_event_filter = event_filter.KeyEventFilter(self)

        self.connect_signals()

    def connect_signals(self):
        # mouse event signals
        self.mouse_event_filter.clicked.connect(self.clicked)
        self.mouse_event_filter.released.connect(self.released)
        self.mouse_event_filter.dragged.connect(self.dragged)
        self.mouse_event_filter.mouse_moved.connect(self.mouse_moved)
        self.mouse_event_filter.leave.connect(self.leave)

        # key event signals
        self.key_event_filter.ctrl_pressed.connect(self.ctrl_pressed)
        self.key_event_filter.ctrl_released.connect(self.ctrl_released)
        self.key_event_filter.meta_pressed.connect(self.meta_pressed)
        self.key_event_filter.meta_released.connect(self.meta_released)
        self.key_event_filter.shift_pressed.connect(self.shift_pressed)
        self.key_event_filter.shift_released.connect(self.shift_released)
        self.key_event_filter.b_pressed.connect(self.b_pressed)
        self.key_event_filter.b_released.connect(self.b_released)

    def toolOnSetup(self, event):
        """ tool setup:
        - get the node's inMesh and set it as target for the tool
        - update the context controller
        - install mouse & key events
        - build the canvas frot drawing """

        # get spore_node's inMesh and set it as target
        # note: we expect the target node to be selected when we setup the tool
        # if no sporeNode is selected we try to use the last target as fallback
        # if there is no fallback, tool initialization will fail and display a
        # warning
        try: # try to get selection of type sporeNode
            node_name = cmds.ls(sl=True, l=True, type='sporeNode')[0]
        except IndexError:
            node_name = None

        # try to get inMesh of selected spore node
        if node_name:
            self.state.target = node_utils.get_connected_in_mesh(node_name)
            self.state.node = node_name

            if not self.state.target or not self.state.node:
                raise RuntimeError('Failed initializing sporeTool')

        # fallback to old target, just pass since target is already set
        elif self.state.target and self.state.node:
            pass

        # if we neither have a sporeNode selected nor have a fallback, tool init fails
        else:
            self.msg_io.set_message('No sporeNode selected: Can\'t operate on: {}'.format(cmds.ls(sl=1), 1))
            return

        # get node state & cache points for editing
        self.node_state = node_state.SporeState(self.state.node)
        self.node_state.get_node_state()
        if self.node_state.state['mode'] == 'scale'\
        or self.node_state.state['mode'] == 'align'\
        or self.node_state.state['mode'] == 'smooth'\
        or self.node_state.state['mode'] == 'move' \
        or self.node_state.state['mode'] == 'id':
            self.node_state.build_kd_tree()

        # install event filter
        view = window_utils.active_view_wdg()
        view.installEventFilter(self.mouse_event_filter)
        window = window_utils.maya_main_window()
        window.installEventFilter(self.key_event_filter)

        # set up canvas for drawing
        if self.node_state.state['mode'] == 'place': #'place':
            self.canvas = canvas.DotBrush(self.state)
        else:
            self.canvas = canvas.CircularBrush(self.state)



    def toolOffCleanup(self):
        view = window_utils.active_view_wdg()
        view.removeEventFilter(self.mouse_event_filter)
        window = window_utils.maya_main_window()
        window.removeEventFilter(self.key_event_filter)

        self.state.draw = False

        if self.canvas:
            self.canvas.update()
            del self.canvas


    """ -------------------------------------------------------------------- """
    """ mouse events """
    """ -------------------------------------------------------------------- """


    @Slot(QPoint)
    def mouse_moved(self, position):
        """ update the brush as soon as the mouse moves """

        self.state.cursor_x = position.x()
        self.state.cursor_y = position.y()

        result = None
        if not self.state.first_scale:
            result = mesh_utils.hit_test(self.state.target,
                                         self.state.first_x,
                                         self.state.first_y)

        else:
            result = mesh_utils.hit_test(self.state.target,
                                         position.x(),
                                         position.y())

        if result:
            position, normal, tangent = result
            self.state.position = position
            self.state.normal = normal
            self.state.tangent = tangent
            self.state.draw = True

            if not self.state.last_position:
                self.state.last_position = position
            else:
                pos = om.MPoint(position[0], position[1], position[2])
                last_pos = om.MPoint(self.state.last_position[0],
                                     self.state.last_position[1],
                                     self.state.last_position[2])
                stroke_dir = pos - last_pos

                self.state.stroke_direction = (stroke_dir[0],
                                               stroke_dir[1],
                                               stroke_dir[2])

                self.state.last_position = position

        else:
            self.state.draw = False

        #  redraw after coursor has been move
        self.canvas.update()

    @Slot(QPoint)
    def clicked(self, position):
        """ clicked event """

        self.state.action = SporeToolCmd.k_click

        if self.state.draw and not self.state.modify_radius:
            state = self._get_state()
            self.sender.press.emit(state)

            self.node_state.get_node_state()

            #  instanciate the tool command
            self.create_tool_command()
            if not self.state.meta_mod:
                self.tool_cmd.redoIt()


    @Slot(QPoint)
    def dragged(self, position):
        """ dragged event """

        self.state.action = SporeToolCmd.k_drag

        if not self.tool_cmd:
            self.create_tool_command()

        if self.state.draw:
            if self.state.modify_radius:
                if self.state.first_scale:
                    self.state.first_x = position.x()
                    self.state.first_y = position.y()
                    self.state.last_x = position.x()
                    self.state.last_y = position.y()
                    self.state.first_scale = False

                self.modify_radius()
                self.state.last_x = position.x()
                self.state.last_y = position.y()

            else:
                state = self._get_state()
                self.sender.drag.emit(state)
                self.tool_cmd.redoIt()


    @Slot(QPoint)
    def released(self, position):
        """ released event """

        self.state.action = SporeToolCmd.k_release

        if not self.tool_cmd:
            self.create_tool_command()

        if self.state.draw and not self.state.modify_radius:
            state = self._get_state()
            self.sender.release.emit(state)

        # finalize tool command
        if self.tool_cmd:
            #  self.tool_cmd.redoIt()
            self.tool_cmd.finalize()
            self.tool_cmd = None

    @Slot()
    def leave(self):
        self.state.draw = False
        self.canvas.update()


    """ -------------------------------------------------------------------- """
    """ key events """
    """ -------------------------------------------------------------------- """

    @Slot()
    def ctrl_pressed(self):
        print 'ctrl on'
        self.state.ctrl_mod = True
        self.canvas.update()

    @Slot()
    def ctrl_released(self):
        print 'ctrl off'
        self.state.ctrl_mod = False
        self.canvas.update()

    @Slot()
    def meta_pressed(self):
        print 'meta on'
        self.state.meta_mod = True
        self.canvas.update()

    @Slot()
    def meta_released(self):
        print 'meta off'
        self.state.meta_mod = False
        self.canvas.update()

    @Slot()
    def shift_pressed(self):
        self.state.shift_mod = True
        self.canvas.update()

    @Slot()
    def shift_released(self):
        self.state.shift_mod = False
        self.canvas.update()


    @Slot()
    def b_pressed(self):
        self.state.modify_radius = True

    @Slot()
    def b_released(self):
        self.state.modify_radius = False
        self.state.first_scale = True

    """ -------------------------------------------------------------------- """
    """ utils """
    """ -------------------------------------------------------------------- """

    def _get_state(self):
        """ get the current state and return it as a dictionary """

        state = {'position': self.state.position,
                 'normal': self.state.normal,
                 'tangent': self.state.tangent,
                 'radius': self.state.radius}

        return state

    def modify_radius(self):
        """ modify the brush radius """

        delta_x = self.state.last_x - self.state.cursor_x

        view = window_utils.active_view()
        cam_dag = om.MDagPath()
        view.getCamera(cam_dag)
        cam_node_fn = node_utils.get_dgfn_from_dagpath(cam_dag.fullPathName())
        cam_coi = cam_node_fn.findPlug('centerOfInterest').asDouble()

        step = delta_x * (cam_coi * -0.025) # TODO - finetune static factor for different scene sizes!
        if (self.state.radius + step) >= 0.01:
            self.state.radius += step

        else:
            self.state.radius = 0.01

    def create_tool_command(self):
        """ create a new instance of the command associated with the context """

        tool_cmd = self._newToolCommand()
        #  print 'toolcmd: ', tool_cmd # spore_tool_cmd.SporeToolCmd.tracking_dir # .get(ompx.asHashable(tool_cmd))
        self.tool_cmd = K_TRACKING_DICTIONARY.get(ompx.asHashable(tool_cmd))
        self.tool_cmd.initialize_tool_cmd(self.state, self.node_state)


""" -------------------------------------------------------------------- """
""" CONTEXT COMMAND """
""" -------------------------------------------------------------------- """


class SporeContextCommand(ompx.MPxContextCommand):
    def __init__(self):
        ompx.MPxContextCommand.__init__(self)

    def makeObj(self):
        return ompx.asMPxPtr(SporeContext())

    @staticmethod
    def creator():
        return ompx.asMPxPtr(SporeContextCommand())


