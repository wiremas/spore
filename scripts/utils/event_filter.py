import maya.cmds as cmds
import maya.OpenMayaUI as omui

from shiboken2 import wrapInstance
from PySide2.QtWidgets import QWidget
from PySide2.QtCore import QObject, QEvent, Signal, Slot, QPoint, Qt
from PySide2.QtGui import QKeyEvent

import window_utils


class CanvasEventFilter(QObject):
    """ resize event
    object emits a resize_event when installed on widget """

    resize_event = Signal(QEvent)
    enter_event = Signal(QEvent)

    def __init__(self):
        super(CanvasEventFilter, self).__init__() #eventFilter(obj, event)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.resize_event.emit(event)

        if event.type() == QEvent.Enter:
            self.enter_event.emit(event)

        return False



class KeyEventFilter(QObject):

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
        self.is_modified = False

    def eventFilter(self, source, event):

        if isinstance(event, QKeyEvent) and not event.isAutoRepeat():
            if event.type() == QEvent.KeyPress and not self.is_clicked:
                if event.key() != Qt.Key_Shift and event.key() != Qt.Key_Meta:
                    self.is_modified = True
            if event.type() == QEvent.KeyRelease and not self.is_clicked:
                if event.key() != Qt.Key_Shift and event.key() != Qt.Key_Meta:
                    self.is_modified = False

        # Mouse Events
        if event.type() == QEvent.MouseMove:
            position = event.pos()
            self.mouse_moved.emit(position)
            if self.is_clicked and not self.is_modified:
                self.dragged.emit(position)
            return False

        if event.type() == QEvent.Wheel:
            position = event.pos()
            self.mouse_moved.emit(position)

        if event.type() == QEvent.MouseButtonPress:
            self.is_clicked = True
            if not self.is_modified:
                position = event.pos()
                self.clicked.emit(position)
                return False

        if event.type() == QEvent.MouseButtonRelease:
            self.is_clicked = False
            if not self.is_modified:
                position = event.pos()
                self.released.emit(position)
                return False

        if event.type() == QEvent.Leave:
            self.leave.emit()
            return False

        return False
