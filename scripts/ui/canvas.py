import math
from abc import ABCMeta, abstractmethod

import maya.OpenMaya as om

from PySide2.QtGui import QPainter, QPen, QPainterPath
from PySide2.QtCore import Qt, QObject, Signal, Slot, QEvent, QPointF, QPoint
from PySide2.QtWidgets import QWidget, QLabel, QGridLayout

import window_utils
import event_filter
reload(event_filter)
reload(window_utils)

class Canvas(QWidget):
    """ Canvas widget to draw on top of the viewport """
    def __init__(self, parent=None):
        super(Canvas, self).__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.SplashScreen | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        #  self.setAttribute(Qt.WA_PaintOnScreen)
        #  self.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.resize_event_filter = event_filter.CanvasEventFilter()
        self.install_event_filter()
        self.resize()
        self.show()

    def install_event_filter(self):
        """ install the resize evenet filter """
        self.resize_event_filter.resize_event.connect(self.resize)
        view_wdg = window_utils.active_view_wdg()
        view_wdg.installEventFilter(self.resize_event_filter)

    def remove_event_filter(self):
        """ clean up the resize evenet filter """
        view_wdg = window_utils.active_view_wdg()
        view_wdg.removeEventFilter(self.resize_event_filter)

    @Slot(QEvent)
    def resize(self):
        """ resize the widget to match the viewport """
        view_wdg = window_utils.active_view_wdg()
        wdg_size = view_wdg.rect()
        wdg_pos = view_wdg.pos()
        abs_pos = view_wdg.mapToGlobal(wdg_pos)
        self.setGeometry(abs_pos.x(), abs_pos.y(), wdg_size.width(), wdg_size.height())

    @Slot(QEvent)
    def set_focus(self):
        """ set focuts to the panel under the cursor """

        panel = cmds.getPanel(underPointer=True)
        cmds.setFocus(panel)

    def __del__(self):
        """ remove event filter when the canvas is deleted """
        self.remove_event_filter()


""" -------------------------------------------------------------------- """
""" Brushes """
""" -------------------------------------------------------------------- """


class CircularBrush(Canvas):
    """ Draw a circular brush around the coursor
    based on the given brush state """

    def __init__(self, brush_state):
        super(CircularBrush, self).__init__()

        self.brush_state = brush_state

    def paintEvent(self, event):

        super(CircularBrush, self).paintEvent(event)

        # draw brush
        if hasattr(self, 'brush_state') and self.brush_state.draw:
            painter = QPainter()
            shapes = self.create_brush_shape()
            for shape in shapes:
                shape = [QPointF(point[0], point[1]) for point in shape]

                path = QPainterPath()
                start_pos = shape.pop(0)
                path.moveTo(start_pos)
                [path.lineTo(point) for point in shape]

                painter.setRenderHint(painter.Antialiasing)
                #  painter.setRenderHint(painter.HighQualityAnti)
                painter.begin(self)

                painter.setPen(QPen(Qt.red, 1))
                painter.drawPath(path)

            painter.end()


    def create_brush_shape(self):
        """ generate the shape of the brush based on the brush state """

        if self.brush_state.draw:
            # fetch point and normal
            pnt = om.MPoint(self.brush_state.position[0],
                            self.brush_state.position[1],
                            self.brush_state.position[2])
            nrm = om.MVector(self.brush_state.normal[0],
                            self.brush_state.normal[1],
                            self.brush_state.normal[2])
            tan = om.MVector(self.brush_state.tangent[0],
                            self.brush_state.tangent[1],
                            self.brush_state.tangent[2])

            # draw dragger shapes
            #  if self.brush_state.drag_mode:
            #      pos_x, pos_y = window_utils.world_to_view(pnt)
            #
            #      shapes = []
            #      shapes.append([(pos_x - 15, pos_y - 15), (pos_x + 15, pos_y + 15)])
            #      shapes.append([(pos_x - 15, pos_y + 15), (pos_x + 15, pos_y - 15)])
            #      return shapes
            #

            # get point at normal and tangent
            #  n_pnt = pnt + (nrm * self._state.radius * 0.75)
            #  t_str = pnt + (tan * self._state.radius * 0.75)
            #  t_end = pnt + (tan * self._state.radius)

            # get circle points
            theta = math.radians(360 / 20)
            shape = []
            for i in xrange(40 + 1):
                rot = om.MQuaternion(theta * i, nrm)
                rtan = tan.rotateBy(rot)
                pos = pnt + (rtan * self.brush_state.radius)

                pos_x, pos_y = window_utils.world_to_view(pos)
                shape.append((pos_x, pos_y))

            return [shape]

class DotBrush(Canvas):
    """ Draw a circular brush around the coursor
    based on the given brush state """

    def __init__(self, brush_state):
        super(DotBrush, self).__init__()
        self.brush_state = brush_state

    def paintEvent(self, event):
        if hasattr(self, 'brush_state') and self.brush_state.draw:
            painter = QPainter()
            position = self.create_brush_dots()
            painter.drawPoint(position)
            #  for shape in shapes:
            #      shape = [QPointF(point[0], point[1]) for point in shape]
            #
            #      path = QPainterPath()
            #      start_pos = shape.pop(0)
            #      path.moveTo(start_pos)
            #      [path.lineTo(point) for point in shape]
            #
            #      painter.setRenderHint(painter.Antialiasing)
            #      #  painter.setRenderHint(painter.HighQualityAnti)
            #      painter.begin(self)
            #
            #      painter.setPen(QPen(Qt.yellow, 1))
            #      painter.drawPath(path)

            painter.end()

    def create_brush_dots(self):
        """ generate the shape of the brush based on the brush state """

        if self.brush_state.draw:
            # fetch point and normal
            pnt = om.MPoint(self.brush_state.position[0],
                            self.brush_state.position[1],
                            self.brush_state.position[2])
            nrm = om.MVector(self.brush_state.normal[0],
                            self.brush_state.normal[1],
                            self.brush_state.normal[2])
            tan = om.MVector(self.brush_state.tangent[0],
                            self.brush_state.tangent[1],
                            self.brush_state.tangent[2])

            # draw dragger shapes
            #  if self.brush_state.drag_mode:
            pos_x, pos_y = window_utils.world_to_view(pnt)

            #shapes = []
            #shapes.append([(pos_x - 15, pos_y - 15), (pos_x + 15, pos_y + 15)])
            #shapes.append([(pos_x - 15, pos_y + 15), (pos_x + 15, pos_y - 15)])
            return QPoint(pos_x, pos_y) #shapes


            # get point at normal and tangent
            #  n_pnt = pnt + (nrm * self._state.radius * 0.75)
            #  t_str = pnt + (tan * self._state.radius * 0.75)
            #  t_end = pnt + (tan * self._state.radius)

            # get circle points
            #  theta = math.radians(360 / 20)
            #  shape = []
            #  for i in xrange(20 + 1):
            #      rot = om.MQuaternion(theta * i, nrm)
            #      rtan = tan.rotateBy(rot)
            #      pos = pnt + (rtan * self.radius)
            #
            #      pos_x, pos_y = window_utils.world_to_view(pos)
            #      shape.append((pos_x, pos_y))
            #
            #  return [shape]

