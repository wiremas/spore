import sys
import math
import traceback

import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
import maya.OpenMayaUI as omui
import maya.OpenMayaRender as omr

from shiboken2 import wrapInstance
from PySide2.QtCore import Qt, QObject, QEvent, Signal, Slot
from PySide2.QtWidgets import QWidget
from PySide2.QtGui import QKeyEvent

from asScatter.brush import context_ctrl



__author__ = 'Anno Schachner'
__version__ = '0.0.1'

context_cmd_name = 'brushCtxCmd'
context_name = 'brushCtx'
manip_name = 'brushManip'

k_node_id = om.MTypeId(0x00001)


def user_event(event):
    print 'user event', event

""" ####################################################################### """
""" Event Filter """
""" ####################################################################### """

class MouseEventFilter(QObject):

    def __init__(self, parent):
        super(MouseEventFilter, self).__init__()
        self.parent = parent

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseMove or event.type() == QEvent.Wheel:
            self.parent.mouse_move(event.pos().x(), event.pos().y())
            return False

        if event.type() == QEvent.Leave:
            self.parent.leave()
            return False

        return False

class KeyEventFilter(QObject):

    def __init__(self, parent):
        super(KeyEventFilter, self).__init__()
        self.parent = parent

    def eventFilter(self, source, event, ):
        if isinstance(event, QKeyEvent) and not event.isAutoRepeat():
            if event.type() == QEvent.KeyPress:
                if not event.isAutoRepeat():
                    if event.key() == Qt.Key_B:
                        #  print 'rep', event.isAutoRepeat()
                        self.parent.b_press()
                        return True

                if event.key() == Qt.Key_M:
                    return True

            if event.type() == QEvent.KeyRelease:
                if event.key() == Qt.Key_B:
                    self.parent.b_release()
                    return True

                if event.key() == Qt.Key_M:
                    return True

        return False

""" ####################################################################### """
""" Signal """
""" ####################################################################### """

class Sender(QObject):
    trigger = Signal(dict)

""" ####################################################################### """
""" Brush State """
""" ####################################################################### """

class BrushState(object):
    def __init__(self):
        self.radius = 3
        self.draw = False
        self.position = tuple()
        self.normal = tuple()
        self.tangent = tuple()
        self.modify_radius = False
        self.first_scale = True
        self.first_x = float()
        self.first_y = float()
        self.last_x = float()
        self.last_y = float()

""" ####################################################################### """
""" Context """
""" ####################################################################### """

class BrushContext(ompx.MPxContext):
    def __init__(self):
        super(BrushContext, self).__init__()

        self._state = BrushState()
        self._cursor_x = int
        self._cursor_y = int

        self.view = omui.M3dView().active3dView()
        self.view_wdg = self.get_view_wdg()
        self.main_win = self.get_main_win()
        self.moues_event_filter = MouseEventFilter(self)
        self.key_event_filter = KeyEventFilter(self)

        self.brush_event = Sender()
        self.brush_event.trigger.connect(context_ctrl.brush_event)

        gl_renderer = omr.MHardwareRenderer.theRenderer()
        self.glft = gl_renderer.glFunctionTable()

    """---------------------------------------------------------------------"""
    """ setup / cleanup """
    """---------------------------------------------------------------------"""

    def toolOnSetup(self, event):
        """ enter context """
        self._setCursor(omui.MCursor.pencilCursor)

        obj = om.MObject()
        BrushManip.newManipulator('brushManip', obj)
        self.addManipulator(obj)

        node = om.MFnDependencyNode(obj)
        if node:
            BrushManip.set_context(self)

        glRenderer = omr.MHardwareRenderer.theRenderer()
        self.glFT = glRenderer.glFunctionTable()

        self.view_wdg.installEventFilter(self.moues_event_filter)
        self.main_win.installEventFilter(self.key_event_filter)

        # TODO - temp
        self.targets = cmds.ls(sl=1, l=1)

    def toolOffCleanup(self):
        """ leave context """
        self.deleteManipulators()

        self.view_wdg.removeEventFilter(self.moues_event_filter)
        self.main_win.removeEventFilter(self.key_event_filter)

        self.brush_event.trigger.emit({'event': 'cleanup'})

    """---------------------------------------------------------------------"""
    """ qt events """
    """---------------------------------------------------------------------"""

    def mouse_move(self, x, y):
        """ check for intersections and refesh the view
        :param x: x position of the cursor
        :param y: y position of the cursor """
        self._cursor_x = x
        self._cursor_y = self.view.portHeight() - y

        if not self._state.first_scale:
            self.check_draw_state(self._state.first_x, self._state.first_y)
        else:
            self.check_draw_state(self._cursor_x, self._cursor_y)
        self.view.refresh(True, False)

    def leave(self):
        """ hide the brush when the curour leaves the widget boundaries"""
        self.check_draw_state(0, 0)
        self._state.draw = False
        self.view.refresh(True, False)

    def b_press(self):
        """ enter brush modify mode """
        self._state.modify_radius = True
        #  self._state.first_scale = True
        print 'is first scale', self._state.first_scale


    def b_release(self):
        """ leave brush modify mode """
        self._state.modify_radius = False
        self._state.first_scale = True
        print self._state.first_scale

    """---------------------------------------------------------------------"""
    """ maya events """
    """---------------------------------------------------------------------"""

    def doPress(self, event):

        if self._state.draw and not self._state.modify_radius:
            state = self.get_state('click')
            self.brush_event.trigger.emit(state)


    def doDrag(self, event):
        # modify radius
        if self._state.draw:
            if self._state.modify_radius:
                if self._state.first_scale:
                    self._state.first_x = self._cursor_x
                    self._state.first_y = self._cursor_y
                    self._state.last_x = self._cursor_x
                    self._state.last_y = self._cursor_y
                    self._state.first_scale = False

                self.modify_radius()
                self._state.last_x = self._cursor_x
                self._state.last_y = self._cursor_y


            else:
                state = self.get_state('drag')
                self.brush_event.trigger.emit(state)

    def doRelease(self, event):
        if self._state.draw and not self._state.modify_radius:
            state = self.get_state('release')
            self.brush_event.trigger.emit(state)

    def get_state(self, event):

        event_types = ['click', 'drag', 'release', 'radius_update',
                       'initialize', 'cleanup']

        #  assert event not in event_types

        state = {'point': self._state.position,
                'normal': self._state.normal,
                'tangent': self._state.tangent,
                'radius': self._state.radius,
                'event': event}
        return state

    """---------------------------------------------------------------------"""
    """ brush radius """
    """---------------------------------------------------------------------"""

    def modify_radius(self):
        """ modify brush radius """
        dx = self._state.last_x - self._cursor_x

        step = dx * -0.1
        print self._state.radius + step
        if (self._state.radius + step) >= 0.01:
            self._state.radius += step
        else:
            self._state.radius = 0.01

        state = self.get_state('radius_update')
        self.brush_event.trigger.emit(state)

    """---------------------------------------------------------------------"""
    """ brush draw """
    """---------------------------------------------------------------------"""

    def draw_brush(self):
        """ draw a circular brush with a normal indicating it's up-direction"""
        if self._state.draw:
            view = omui.M3dView.active3dView()

            # fetch point and normal
            pnt = om.MPoint(self._state.position[0],
                            self._state.position[1],
                            self._state.position[2])
            nrm = om.MVector(self._state.normal[0],
                             self._state.normal[1],
                             self._state.normal[2])
            tan = om.MVector(self._state.tangent[0],
                             self._state.tangent[1],
                             self._state.tangent[2])

            # get point at normal and tangent
            n_pnt = pnt + (nrm * self._state.radius * 0.75)
            t_str = pnt + (tan * self._state.radius * 0.75)
            t_end = pnt + (tan * self._state.radius)

            # get circle points
            theta = math.radians(360 / 40)
            circ_pnts = []
            for i in xrange(40 + 1):
                rot = om.MQuaternion(theta * i, nrm)
                rtan = tan.rotateBy(rot)
                pos = pnt + (rtan * self._state.radius)
                circ_pnts.append((pos.x, pos.y, pos.z))

            # draw normal
            self.draw_vertex_line((pnt.x, pnt.y, pnt.z),
                                  (n_pnt.x, n_pnt.y, n_pnt.z))

            # draw tangent
            self.draw_vertex_line((t_str.x, t_str.y, t_str.z),
                                  (t_end.x, t_end.y, t_end.z))

            # draw circle
            for i, pnt in enumerate(circ_pnts):
                try: self.draw_vertex_line((pnt[0], pnt[1], pnt[2]),
                                          (circ_pnts[i+1][0],
                                          circ_pnts[i+1][1],
                                          circ_pnts[i+1][2]))
                except IndexError: pass

    """---------------------------------------------------------------------"""
    """ gl drawing """
    """---------------------------------------------------------------------"""

    def draw_vertex_line(self, v1, v2, color=(1,0,0), width=3.0):
        """ draw a line between two vertices
        :param v1: first vertex
        :param v2: sectond vertex
        :param color: line color
        :param width: line width """
        self.view.beginGL()
        self.glFT.glPushAttrib(omr.MGL_LINE_BIT)
        self.glFT.glLineWidth(width)
        self.glFT.glBegin(omr.MGL_LINES)

        self.glFT.glColor3f(color[0], color[1], color[2])
        self.glFT.glVertex3f(v1[0], v1[1], v1[2])
        self.glFT.glVertex3f(v2[0], v2[1], v2[2])

        self.glFT.glEnd()
        self.glFT.glPopAttrib()
        self.view.endGL()

    """---------------------------------------------------------------------"""
    """ brush state / intersection testing """
    """---------------------------------------------------------------------"""

    def check_draw_state(self, x, y):
        """ check current cursor position for any
        intersection with target shapes if an intersection
        was found set _draw state and intersection point, normal and tangent
        :param x: x position of the cursor
        :param y: y position of the cursor"""

        origin = om.MPoint()
        direction = om.MVector()

        self.view.viewToWorld(x, y, origin, direction)

        pnt = None
        closest_target = None
        closest_isect = 10000 # TODO - set this to far clip plane

        # collect intersections
        for i, target in enumerate(self.targets):
            mesh_fn = self.get_mesh_fn(target)

            if mesh_fn:
                points = om.MPointArray()
                found = mesh_fn.intersect(origin, direction, points,
                                          1.0e-5, om.MSpace.kWorld)

                if (not found or points.length() == 0):
                    self._state.draw = False

                else:
                    distance = points[0].distanceTo(origin)
                    if distance < closest_isect:
                        pnt = points[0].x, points[0].y, points[0].z
                        closest_isect = distance
                        closest_target = target

        # set point, normal, tangent and draw state if found
        if pnt:
            mesh_fn = self.get_mesh_fn(closest_target)
            m_nrm = om.MVector()
            pnt = om.MPoint(pnt[0], pnt[1], pnt[2])
            mesh_fn.getClosestNormal(pnt, m_nrm, om.MSpace.kWorld)

            # get tangent
            nrm = m_nrm.x, m_nrm.y, m_nrm.z
            if m_nrm.x >= m_nrm.y:
                u = om.MVector(nrm[2], 0, -nrm[1])
            else:
                u = om.MVector(0, nrm[2], -nrm[1])
            tan = m_nrm ^ u
            tan.normalize()

            self._state.position = pnt.x, pnt.y, pnt.z
            self._state.normal = m_nrm.x, m_nrm.y, m_nrm.z
            self._state.tangent = tan.x, tan.y, tan.z
            self._state.draw = True

    """---------------------------------------------------------------------"""
    """ utils """
    """---------------------------------------------------------------------"""

    def get_view_wdg(self):
        """ return a qObject of the active 3d view """
        ptr = self.view.widget()
        return wrapInstance(long(ptr), QObject)

    def get_main_win(self):
        """ return a qObject of the active 3d view """
        ptr = omui.MQtUtil().mainWindow()
        return wrapInstance(long(ptr), QObject)

    def get_mesh_fn(self, target):
        """ get mesh function set for the closest target
        :param target: dag path of the mesh """
        slls = om.MSelectionList()
        slls.add(target)

        ground_path = om.MDagPath()
        slls.getDagPath(0, ground_path)
        ground_path.extendToShapeDirectlyBelow(0)
        ground_node = ground_path.node()

        if ground_node.hasFn(om.MFn.kMesh):
            return om.MFnMesh(ground_path)
        else:
            return False


""" ####################################################################### """
""" Manipulator """
""" ####################################################################### """

class BrushManip(ompx.MPxManipContainer):
    ctx = None
    def __init__(self):
        super(BrushManip, self).__init__()

    def preDrawUI(self, view):
        print 'predraw', view

    def draw(self, view, path, stype, status):
        self.ctx.draw_brush()

    def drawUI(self, drawManager, frameContext):
        self.ctx.draw_brush()

    @classmethod
    def set_context(cls, context):
        cls.ctx = context

def manipCreator():
    return ompx.asMPxPtr(BrushManip())

def manipInitializer():
    ompx.MPxManipContainer.initialize()

""" ####################################################################### """
""" Command """
""" ####################################################################### """

class BrushCmd(ompx.MPxContextCommand):
    def __init__(self, *args):
        super(BrushCmd, self).__init__(*args)

    def makeObj(self):
        return ompx.asMPxPtr(BrushContext())

def cmdCreator():
    return ompx.asMPxPtr(BrushCmd())

""" ####################################################################### """
""" Init / Uninit """
""" ####################################################################### """

def initializePlugin(mobject):
    mplugin = ompx.MFnPlugin(mobject)
    try:
        mplugin.registerNode(manip_name,
                             k_node_id,
                             manipCreator,
                             manipInitializer,
                             ompx.MPxNode.kManipContainer)
        mplugin.registerContextCommand(context_cmd_name, cmdCreator)
    except:
        raise

def uninitializePlugin(mobject):
    mplugin = ompx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(k_node_id)
        mplugin.deregisterContextCommand(context_cmd_name)
    except:
        raise

