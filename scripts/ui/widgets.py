from PySide2.QtWidgets import QWidget, QGridLayout, QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QSpacerItem, QLineEdit
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtCore import Signal, QObject, Qt
from PySide2.QtGui import QPalette, QColor, QPixmap, QIcon

class TreeItemWidget(QWidget):

    clicked = Signal(QObject)
    view_toggled = Signal(QObject)
    name_changed = Signal(QObject)

    def __init__(self, name, parent=None):
        super(TreeItemWidget, self).__init__(parent)

        self.name = name
        self.is_selected = False
        #  self.level = level
        self.children = []

        self.build_ui()

    def build_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.item_wdg = QFrame()
        self.layout.addWidget(self.item_wdg)
        self.item_lay = QGridLayout(self.item_wdg)
        self.item_lay.setContentsMargins(0, 0, 0, 0)
        #  self.item_lay.setSpacing(3)

        #  self.item_wdg.setFrameStyle(QFrame.Raised | QFrame.Panel)
        #  self.item_wdg.setStyleSheet("QFrame { background-color: rgb(55,55,55);}")
        #  self.item_wdg.setFixedHeight(30)

        # widget containing child widgets
        self.child_wdg = QWidget()
        self.layout.addWidget(self.child_wdg)
        self.child_lay = QVBoxLayout(self.child_wdg)
        self.child_lay.setContentsMargins(0, 0, 0, 0)
        self.child_lay.setSpacing(0)

        #  self.setLayout(layout)

    def add_child(self, widget):
        print 'addChild'
        self.children.append(widget)
        self.child_lay.addWidget(widget)

class GeoItem(TreeItemWidget):
    def __init__(self, name, parent=None):
        super(GeoItem, self).__init__(name, parent)

        self.build_geo_ui()

    def build_geo_ui(self):

        self.setMaximumHeight(85)
        self.item_wdg.setFrameStyle(QFrame.Raised | QFrame.StyledPanel)
        self.item_wdg.setStyleSheet("QFrame { background-color: rgb(55,55,55);}")

        icon = QIcon()
        icon.addPixmap(QPixmap(':/nudgeDown.png'), QIcon.Normal, QIcon.On);
        icon.addPixmap(QPixmap(':/nudgeRight.png'), QIcon.Normal, QIcon.Off);
        self.expand_btn = QPushButton()
        self.expand_btn.setStyleSheet("QPushButton#expand_btn:checked {background-color: green; border: none}")
        self.expand_btn.setStyleSheet("QPushButton { color:white; }\
                                        QPushButton:checked { background-color: rgb(55,55, 55); border: none; }\
                                        QPushButton:pressed { background-color: rgb(55,55, 55); border: none; }") #\
                                        #  QPushButton:hover{ background-color: grey; border-style: outset; }")
        self.expand_btn.setFlat(True)
        self.expand_btn.setIcon(icon)
        self.expand_btn.setCheckable(True)
        self.expand_btn.setFixedWidth(25)
        self.expand_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.item_lay.addWidget(self.expand_btn, 0, 0, 1, 1)

        pixmap = QPixmap(':/pickGeometryObj.png')
        icon_lbl = QLabel()
        icon_lbl.setMaximumWidth(18)
        icon_lbl.setPixmap(pixmap)
        self.item_lay.addWidget(icon_lbl, 0, 1, 1, 1)

        self.target_lbl = QLabel(self.name)
        self.item_lay.addWidget(self.target_lbl, 0, 2, 1, 1)
        #  self.target_edt = QLineEdit(item_wdg)
        #  self.target_edt.setMinimumWidth(180)
        #  self.target_edt.setVisible(False)

        self.item_lay.setColumnStretch(3, 1)

        self.view_buttons = DisplayButtons(self)
        self.item_lay.addWidget(self.view_buttons, 0, 4, 1, 1)

class SporeItem(TreeItemWidget):
    def __init__(self, name, parent=None):
        super(SporeItem, self).__init__(name, parent)

        self.build_spore_ui()

    def build_spore_ui(self):

        self.item_wdg.setFrameStyle(QFrame.Raised | QFrame.StyledPanel)
        self.item_wdg.setStyleSheet("QFrame { background-color: rgb(75,75,75);}")

        #  icon = QIcon()
        #  icon.addPixmap(QPixmap(':/nudgeDown.png'), QIcon.Normal, QIcon.On);
        #  icon.addPixmap(QPixmap(':/nudgeRight.png'), QIcon.Normal, QIcon.Off);
        #  self.expand_btn = QPushButton()
        #  self.expand_btn.setStyleSheet("QPushButton#expand_btn:checked {background-color: green; border: none}")
        #  self.expand_btn.setStyleSheet("QPushButton { color:white; }\
        #                                  QPushButton:checked { background-color: rgb(55,55, 55); border: none; }\
        #                                  QPushButton:pressed { background-color: rgb(55,55, 55); border: none; }") #\
                                        #  QPushButton:hover{ background-color: grey; border-style: outset; }")
        #  self.expand_btn.setFlat(True)
        #  self.expand_btn.setIcon(icon)
        #  self.expand_btn.setCheckable(True)
        #  self.expand_btn.setFixedWidth(25)
        #  #  self.expand_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        #  self.item_lay.addWidget(self.expand_btn, 0, 0, 1, 1)

        pixmap = QPixmap(':/out_particle.png')
        icon_lbl = QLabel()
        icon_lbl.setMaximumWidth(18)
        icon_lbl.setPixmap(pixmap)
        self.item_lay.addWidget(icon_lbl, 0, 0, 1, 1)

        self.target_lbl = QLabel(self.name)
        self.item_lay.addWidget(self.target_lbl, 0, 1, 1, 1)
        #  self.target_edt = QLineEdit(item_wdg)
        #  self.target_edt.setMinimumWidth(180)
        #  self.target_edt.setVisible(False)

        self.item_lay.setColumnStretch(2, 1)

        self.view_buttons = DisplayButtons(self)
        self.item_lay.addWidget(self.view_buttons, 0, 3, 1, 1)


class DisplayButtons(QWidget):
    view_instancer = Signal()
    view_bounding_box = Signal()
    view_bounding_boxes = Signal()
    view_hide = Signal()

    def __init__(self, parent=None):
        super(DisplayButtons, self).__init__(parent)

        # view options widget
        self.setMinimumWidth(100)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

        view_btn_lay = QHBoxLayout(self)
        view_btn_lay.setContentsMargins(0, 0, 0, 0)
        view_btn_lay.setSpacing(1)

        self.instance_view_btn = QPushButton()
        self.instance_view_btn.setIcon(QIcon(QPixmap(':/eye.png')))
        self.instance_view_btn.setFlat(True)
        self.instance_view_btn.setFixedWidth(25)
        self.instance_view_btn.setCheckable(True)
        self.instance_view_btn.setChecked(True)
        self.instance_view_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        view_btn_lay.addWidget(self.instance_view_btn)

        self.bbs_view_btn = QPushButton()
        self.bbs_view_btn.setIcon(QIcon(QPixmap(':/out_timeEditorLayersFolder.png')))
        self.bbs_view_btn.setFlat(True)
        self.bbs_view_btn.setFixedWidth(25)
        self.bbs_view_btn.setCheckable(True)
        self.bbs_view_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        view_btn_lay.addWidget(self.bbs_view_btn)

        self.bb_view_btn = QPushButton()
        self.bb_view_btn.setIcon(QIcon(QPixmap(':/out_timeEditorLayer.png')))
        self.bb_view_btn.setFlat(True)
        self.bb_view_btn.setFixedWidth(25)
        self.bb_view_btn.setCheckable(True)
        self.bb_view_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        view_btn_lay.addWidget(self.bb_view_btn)

        self.disable_view_btn = QPushButton()
        self.disable_view_btn.setIcon(QIcon(QPixmap(':/error.png')))
        self.disable_view_btn.setFlat(True)
        self.disable_view_btn.setCheckable(True)
        self.disable_view_btn.setFixedWidth(25)
        self.disable_view_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        view_btn_lay.addWidget(self.disable_view_btn)

        self.connect_signals()

    def connect_signals(self):
        self.instance_view_btn.clicked.connect(lambda: self.toggle_view('instance'))
        self.bb_view_btn.clicked.connect(lambda: self.toggle_view('boundingbox'))
        self.bbs_view_btn.clicked.connect(lambda: self.toggle_view('boundingboxes'))
        self.disable_view_btn.clicked.connect(lambda: self.toggle_view('disable'))

    def toggle_view(self, mode):
        """ toggle between diffenrent view modes
        :param mode str: instance, boundingbox, boundingboxes, disable """

        self.viewmode = mode
        if mode == 'instance':
            self.view_bounding_boxes.emit()
            self.bb_view_btn.setChecked(False)
            self.bbs_view_btn.setChecked(False)
            self.view_instancer.emit()

        elif mode == 'boundingbox':
            self.instance_view_btn.setChecked(False)
            #  self.bb_view_btn.setChecked(True)
            self.bbs_view_btn.setChecked(False)
            self.view_bounding_box.emit()

        elif mode == 'boundingboxes':
            self.instance_view_btn.setChecked(False)
            self.view_bounding_boxes.emit()
            self.bb_view_btn.setChecked(False)
            #  self.bbs_view_btn.setChecked(False)

        elif mode == 'disable':
            self.view_hide.emit()


