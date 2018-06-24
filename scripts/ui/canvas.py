import math
from abc import ABCMeta, abstractmethod

import maya.cmds as cmds
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

        self.canvas_event_filter = event_filter.CanvasEventFilter()
        self.install_event_filter()
        self.resize()
        self.show()

    def install_event_filter(self):
        """ install the resize evenet filter """

        self.canvas_event_filter.enter_event.connect(self.enter_widget)
        self.canvas_event_filter.leave_event.connect(self.leave_widget)
        self.canvas_event_filter.resize_event.connect(self.resize)
        view_wdg = window_utils.active_view_wdg()
        view_wdg.installEventFilter(self.canvas_event_filter)

    def remove_event_filter(self):
        """ clean up the resize evenet filter """

        view_wdg = window_utils.active_view_wdg()
        view_wdg.removeEventFilter(self.canvas_event_filter)

    @Slot(QEvent)
    def resize(self):
        """ resize the widget to match the viewport """

        view_wdg = window_utils.active_view_wdg()
        wdg_size = view_wdg.rect()
        wdg_pos = view_wdg.pos()
        abs_pos = view_wdg.mapToGlobal(wdg_pos)
        self.setGeometry(abs_pos.x(), abs_pos.y(), wdg_size.width(), wdg_size.height())

    @Slot(QEvent)
    def enter_widget(self):
        """ set focuts to the panel under the cursor """

        panel = cmds.getPanel(underPointer=True)
        cmds.setFocus(panel)
        self.setFocus()

    @Slot(QEvent)
    def leave_widget(self):

        pass

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

            # get point at normal and tangent
            #  n_pnt = pnt + (nrm * self._state.radius * 0.75)
            #  t_str = pnt + (tan * self._state.radius * 0.75)
            #  t_end = pnt + (tan * self._state.radius)
            #  shape.append(window_utils.world_to_view(pnt))

            shape = []
            # get circle points
            theta = math.radians(360 / 20)
            for i in xrange(40 + 1):
                rot = om.MQuaternion(theta * i, nrm)
                rtan = tan.rotateBy(rot)
                pos = pnt + (rtan * self.brush_state.radius)

                pos_x, pos_y = window_utils.world_to_view(pos)
                shape.append((pos_x, pos_y))

            return [shape]


class HelpDisplay(Canvas):

    key_mapping = {'place': {'Shift': 'Drag',
                             'Ctrl': 'Align to Stroke'},
                   'spray': {'Shift': 'Drag',
                             'Ctrl': 'Align to Stroke',
                             'b': 'Mofify Radius'},
                   'scale': {'Shift': 'Smooth Scale',
                             'Ctrl': 'Randomize Scale'},
                   'align': {'Shift': 'Smooth Align (Not implemented yet)',
                             'Ctrl': 'Randomize Align'},
                   'id': {'Ctrl': 'Pick Random'},
                   'remove': {'Shift': 'Restore',
                              'Ctrl': 'Random Delete'}}

    def __init__(self, mode, parent=None):
        super(HelpDisplay, self).__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.SplashScreen | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)
        self.mapping = self.key_mapping[mode]
        self.mode = mode
        self.visible = True
        self.build()

    def build(self):

        self.setStyleSheet('QLabel {color: white}')

        layout = QGridLayout()
        self.setLayout(layout)

        layout.setRowStretch(0, 10)
        layout.setColumnStretch(3, 1)

        key_lbl = QLabel('{} Hotkeys:'.format(self.mode.title()))
        layout.addWidget(key_lbl, 1, 0, 1, 2)

        position = 2
        for key, op in self.mapping.iteritems():

            key_lbl = QLabel(key)
            layout.addWidget(key_lbl, position, 0, 1, 1)

            op_lbl = QLabel(op)
            layout.addWidget(op_lbl, position, 1, 1, 1)

            position += 1

        #  help_key_lbl = QLabel('h')
        #  layout.addWidget(help_key_lbl, position, 0, 1, 1)
        #
        #  help_lbl = QLabel('Toggle Help')
        #  layout.addWidget(help_lbl, position, 1, 1, 1)

        layout.setRowStretch(position, 1)

    def set_visible(self, visible):
        if self.visible is not visible:
            self.setVisible(visible)
            self.visible = visible
            self.update()
