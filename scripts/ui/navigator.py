import maya.cmds as cmds
import maya.OpenMayaUI as omui

from PySide2.QtWidgets import (QWidget, QGridLayout, QLabel, QPushButton, QHBoxLayout)
from shiboken2 import wrapInstance


#  def load_ae_template(*args):
#      print 'load template'
#
#      navigator_wdg = get_nav_layout()
#      print navigator_wdg
#      #  navigator_lay = QGridLayout()
#      #
    #  l = QListWidget()

class Navigator(QWidget):

    def __init__(self, node_name, parent=None):
        super(Navigator, self).__init__(parent)
        self.node_name = node_name
        self.build_ui()

    def build_ui(self):
        layout = QGridLayout(self)

        lbl = QLabel(str(self))
        layout.addWidget(lbl)

    def update_ui(self):
        print 'update ui'

    def connect_signals(self):
        pass

def get_nav_layout():
    """ get the navigator frame layout and return and wrap it as qWidget """

    def find_first_frame_layout(layout):
        """ recursivley get all child layout until we find the first framelayout """

        children = cmds.layout(layout, ca=True, q=True)
        if children is None:
            return
        for child in children:
            if child.startswith('frameLayout'):
                return child
            if child:
                return find_first_frame_layout(child)

    nav_layout = find_first_frame_layout('AttrEdsporeNodeFormLayout')
    return wrapInstance(long(omui.MQtUtil.findControl(nav_layout)), qw.QWidget)

#  navigator_lay.addWidget(l)
