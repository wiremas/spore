import shiboken2
import maya.OpenMaya as om
import maya.OpenMayaUI as omui

from PySide2.QtWidgets import QWidget
from PySide2.QtCore import QObject

def active_view():
    """ return the active 3d view """
    return omui.M3dView.active3dView()

def active_view_wdg():
    """ return the active 3d view wrapped in a QWidget """
    view = active_view()
    active_view_widget = shiboken2.wrapInstance(long(view.widget()), QWidget)
    return active_view_widget

def maya_main_window():
    """ return maya's main window wrapped in a QWidget """
    pointer_main_window = omui.MQtUtil.mainWindow()
    if pointer_main_window:
        return shiboken2.wrapInstance(long(pointer_main_window), QWidget)

def get_layout(layout):
    """ return a layout wraped as QObject """
    ptr = omui.MQtUtil.findLayout(layout)
    return shiboken2.wrapInstance(long(ptr), QWidget) #.layout()


def world_to_view(position, invert_y=True):
    """ convert the given 3d position to 2d viewpor coordinates
    :param invert_y bool: convert between qt and maya coordinane space """

    view = active_view()
    x_util = om.MScriptUtil()
    y_util = om.MScriptUtil()

    x_ptr = x_util.asShortPtr()
    y_ptr = y_util.asShortPtr()
    view.worldToView(position, x_ptr, y_ptr)
    x_pos = x_util.getShort(x_ptr)
    y_pos = y_util.getShort(y_ptr)

    if invert_y:
        y_pos = view.portHeight() - y_pos

    return (x_pos, y_pos)

