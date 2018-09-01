import maya.cmds as cmds
import maya.OpenMayaUI as omui

from shiboken2 import wrapInstance
from PySide2.QtWidgets import QWidget
from PySide2.QtCore import QObject, QEvent, Signal, Slot, QPoint, Qt
from PySide2.QtGui import QKeyEvent, QGuiApplication

import window_utils


class CanvasEventFilter(QObject):
    """ resize event
    object emits a resize_event when installed on widget """

    resize_event = Signal(QEvent)
    enter_event = Signal(QEvent)
    leave_event = Signal(QEvent)

    def __init__(self):
        super(CanvasEventFilter, self).__init__() #eventFilter(obj, event)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.resize_event.emit(event)

        if event.type() == QEvent.Enter:
            self.enter_event.emit(event)

        if event.type() == QEvent.Leave:
            self.leave_event.emit(event)

        return False

class KeyEventFilter(QObject):
    """ event filter for the brush context
    filter key events. the following singnals are emitted:
    meta_pressed / meta_released
    ctrl_pressed / ctrl_released
    ctrl_shift_pressed / shift_released"""

    # modifier
    meta_pressed = Signal() # ctrl on MacOs, windows ond win
    meta_released = Signal()
    ctrl_pressed = Signal()
    ctrl_released = Signal()
    shift_pressed = Signal()
    shift_released = Signal()
    ctrl_shift_pressed = Signal()
    ctrl_shift_released = Signal()
    meta_shift_preffed = Signal()
    mata_shift_released = Signal()

    # key event signals
    space_pressed = Signal()
    space_pressed = Signal()
    b_pressed = Signal()
    b_released = Signal()

    def __init__(self, parent):
        super(KeyEventFilter, self).__init__()
        self.parent = parent

    def eventFilter(self, source, event):
        if isinstance(event, QKeyEvent) and not event.isAutoRepeat():
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Control:
                    self.ctrl_pressed.emit()
                    return True

                if event.key() == Qt.Key_Shift:
                    self.shift_pressed.emit()
                    return True

                if event.key() == Qt.Key_Meta:
                    self.meta_pressed.emit()
                    return True

                if event.key() == Qt.Key_B:
                    self.b_pressed.emit()
                    return True

            if event.type() == QEvent.KeyRelease:
                if event.key() == Qt.Key_Control:
                    self.ctrl_released.emit()
                    return True

                if event.key() == Qt.Key_Shift:
                    self.shift_released.emit()
                    return True

                if event.key() == Qt.Key_Meta:
                    self.meta_released.emit()
                    return True

                if event.key() == Qt.Key_B:
                    self.b_released.emit()
                    return True

        return False


class MouseEventFilter(QObject):
    """ event filter for the brush context
    filter mouse and key events to trigger the user interaction """

    # mouse event signals
    mouse_moved = Signal(QPoint)
    clicked = Signal(QPoint)
    dragged = Signal(QPoint)
    released = Signal(QPoint)
    leave = Signal()

    def __init__(self, parent):
        super(MouseEventFilter, self).__init__()
        self.parent = parent
        self.is_clicked = False

    def eventFilter(self, source, event):

        modifier = QGuiApplication.queryKeyboardModifiers()

        if event.type() == QEvent.MouseMove:

            # emit mouse moved signal and the drag signal if the mouse
            # button is clicked
            position = event.pos()
            self.mouse_moved.emit(position)
            if self.is_clicked:
                self.dragged.emit(position)
            return False

        if event.type() == QEvent.Wheel:

            # emit the mouse moved signal when the mousewheel is used
            position = event.pos()
            self.mouse_moved.emit(position)

        if event.type() == QEvent.MouseButtonPress \
        or event.type() == QEvent.MouseButtonDblClick:

            # set the mouse button clicked state and emit the clicked signal
            # if neither control nor alt modifiers are pressed
            if not modifier == Qt.ControlModifier\
            and not modifier == Qt.AltModifier:
                self.is_clicked = True
                position = event.pos()
                self.clicked.emit(position)
                return False

        if event.type() == QEvent.MouseButtonRelease:

            # release the mouse button clicked state and emit the release
            # signal if neither ctontrol nor alt modifiers are pressed.
            self.is_clicked = False
            if not modifier == Qt.ControlModifier\
            and not modifier == Qt.AltModifier:
                position = event.pos()
                self.released.emit(position)
                return False

        if event.type() == QEvent.Leave:

            # emit a leave signal
            self.leave.emit()
            return False

        return False
