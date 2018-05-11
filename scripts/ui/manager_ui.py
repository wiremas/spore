from PySide2.QtWidgets import QWidget, QGridLayout, QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QSpacerItem, QLineEdit
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtCore import Signal, QObject, Qt
from PySide2.QtGui import QPalette, QColor, QPixmap, QIcon

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from maya import cmds

class NavigatorUI(QWidget):

    def __init__(self, parent=None):
        super(NavigatorUI, self).__init__(parent=parent)
        self.build_ui()

    def build_ui(self):
        layout = QGridLayout(self)
        self.setLayout(layout)

        self.add_btn = QPushButton()
        self.add_btn.setIcon(QIcon(QPixmap(':/teAdditive.png')))
        layout.addWidget(self.add_btn, 0, 0, 1, 1)
        remove_btn = QPushButton('-')
        layout.addWidget(remove_btn, 0, 1, 1, 1)
        remove_btn = QPushButton('refresh')
        layout.addWidget(remove_btn, 0, 2, 1, 1)

        scroll_wdg = QWidget(self)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { background-color: rgb(57,57,57);}");
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setWidget(scroll_wdg)

        self.spore_layout = QVBoxLayout()
        self.spore_layout.setContentsMargins(1, 1, 3, 1)
        self.spore_layout.setSpacing(0)
        self.spore_layout.addStretch()
        scroll_wdg.setLayout(self.spore_layout)
        layout.addWidget(scroll_area, 1, 0, 1, 3)



class ManagerWindow():
    def __init__(self):
        pass


class ManagerWindow(MayaQWidgetDockableMixin, QWidget):
    add_spore_clicked = Signal()

    def __init__(self, parent=None):
        super(ManagerWindow, self).__init__(parent=parent)

        self.setWindowTitle('Spore Manager')
        self.setGeometry(50, 50, 400, 550)
        #  self.setMinimumSize(350, 400)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred )

        self.items = [] # list of all item widgets

        self.build_ui()
        self.connect_signals()

    def build_ui(self):
        layout = QGridLayout(self)
        self.setLayout(layout)

        self.add_btn = QPushButton()
        self.add_btn.setIcon(QIcon(QPixmap(':/teAdditive.png')))
        layout.addWidget(self.add_btn, 0, 0, 1, 1)
        remove_btn = QPushButton('-')
        layout.addWidget(remove_btn, 0, 1, 1, 1)
        remove_btn = QPushButton('refresh')
        layout.addWidget(remove_btn, 0, 2, 1, 1)

        scroll_wdg = QWidget(self)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { background-color: rgb(57,57,57);}");
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setWidget(scroll_wdg)

        self.spore_layout = QVBoxLayout()
        self.spore_layout.setContentsMargins(1, 1, 3, 1)
        self.spore_layout.setSpacing(0)
        self.spore_layout.addStretch()
        scroll_wdg.setLayout(self.spore_layout)
        layout.addWidget(scroll_area, 1, 0, 1, 3)



        #  self.frame_lay.addWidget(ItemWidget())
        #  layout.addWidget(btn, 0, 0, 1, 1)

    def connect_signals(self):
        self.add_btn.clicked.connect(self.add_spore_clicked.emit)

    def append_item(self, item):
        #  item.setParent(self)
        self.items.append(item)
        self.spore_layout.insertWidget(0, item)

    def clear_items(self):
        for item in self.items:
            print 'widget: ', item
            item.setVisible(False)
            self.spore_layout.removeWidget(item)
            self.items.remove(item)
            del item
        #  del self.itmes
        #  self.spore_layout.clear()

        self.spore_layout.update()



class ItemWidget(QWidget):
    clicked = Signal(QObject)
    view_toggled = Signal(QObject)
    name_changed = Signal(QObject)
    #  instance_request = Signal(QObject)

    def __init__(self, name, is_root=True, parent=None):
        super(ItemWidget , self).__init__(parent)
        self.name = name
        self.is_root = is_root
        self._children = []
        self._parent = None

        self.is_highlighted = False

        self.build_ui()
        self.connect_signals()

    def build_ui(self):
        self.setMinimumHeight(25)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        # target frame widget
        item_wdg = QFrame()
        layout.addWidget(item_wdg)
        self.itme_lay = QGridLayout(item_wdg)
        self.itme_lay.setContentsMargins(9, 0, 9, 0)
        if self.is_root:
            item_wdg.setFrameStyle(QFrame.Raised | QFrame.StyledPanel)
            item_wdg.setStyleSheet("QFrame { background-color: rgb(75,75,75);}")

            icon = QIcon()
            icon.addPixmap(QPixmap(':/nudgeDown.png'), QIcon.Normal, QIcon.On);
            icon.addPixmap(QPixmap(':/nudgeRight.png'), QIcon.Normal, QIcon.Off);
            self.expand_btn = QPushButton()
            #  pushbutton Objectname->setStylesheet{ QPushButton:flat {   border: none; }}
            self.expand_btn.setStyleSheet("QPushButton#expand_btn:checked {background-color: green; border: none}")
            self.expand_btn.setStyleSheet("QPushButton { color:white; }\
                                           QPushButton:checked { background-color: rgb(75,75, 75); border: none; }\
                                           QPushButton:pressed { background-color: rgb(75,75, 75); border: none; }") #\
                                           #  QPushButton:hover{ background-color: grey; border-style: outset; }")
            #  self.expand_btn.setStyleSheet("QPushButton:checked{ background-color: rgb(175,175,175);}")
            self.expand_btn.setFlat(True)
            self.expand_btn.setIcon(icon)
            self.expand_btn.setCheckable(True)
            self.expand_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
            self.itme_lay.addWidget(self.expand_btn, 0, 0, 1, 1)

        else:
            item_wdg.setFrameStyle(QFrame.Raised | QFrame.Panel)
            item_wdg.setStyleSheet("QFrame { background-color: rgb(55,55,55);}")
            item_wdg.setFixedHeight(30)

            pixmap = QPixmap(':/out_particle.png')
            icon_lbl = QLabel()
            icon_lbl.setMaximumWidth(18)
            icon_lbl.setPixmap(pixmap)
            self.itme_lay.addWidget(icon_lbl, 0, 0, 1, 1)

        self.target_lbl = QLabel(self.name)
        self.itme_lay.addWidget(self.target_lbl, 0, 1, 1, 1)
        self.target_edt = QLineEdit(item_wdg)
        self.target_edt.setMinimumWidth(180)
        self.target_edt.setVisible(False)

        # view options widget
        view_btn_wdg = QWidget(self)
        view_btn_wdg.setMinimumWidth(100)
        view_btn_wdg.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.itme_lay.addWidget(view_btn_wdg, 0, 3, 1, 1)

        view_btn_lay = QHBoxLayout(view_btn_wdg)
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


        # create clayout for child nodes
        self.child_wdg = QWidget()
        self.child_wdg.setVisible(False)
        layout.addWidget(self.child_wdg)
        self.child_lay = QVBoxLayout(self.child_wdg)
        self.child_lay.setContentsMargins(0, 0, 0, 0)
        self.child_lay.setSpacing(0)
        #  self.child_lay.addStretch()

        #  lbl = QLabel('lbl')
        #  self.child_lay.addWidget(lbl)

        self.setLayout(layout)

    def connect_signals(self):
        if self.is_root:
            self.expand_btn.toggled.connect(lambda: self.child_wdg.setVisible(self.expand_btn.isChecked()))

        self.instance_view_btn.clicked.connect(lambda: self.toggle_view('instance'))
        self.bb_view_btn.clicked.connect(lambda: self.toggle_view('boundingbox'))
        self.bbs_view_btn.clicked.connect(lambda: self.toggle_view('boundingboxes'))
        self.disable_view_btn.clicked.connect(lambda: self.toggle_view('disable'))

        self.target_edt.editingFinished.connect(self.finish_edit_name)
        self.target_edt.returnPressed.connect(self.finish_edit_name)

    def toggle_view(self, mode):
        """ toggle between diffenrent view modes
        :param mode str: instance, boundingbox, boundingboxes, disable """

        self.viewmode = mode
        if mode == 'instance':
            self.bb_view_btn.setChecked(False)
            self.bbs_view_btn.setChecked(False)
            self.disable_view_btn.setChecked(False)
            self.instance_view_btn.setChecked(True)

        elif mode == 'boundingbox':
            self.instance_view_btn.setChecked(False)
            self.bbs_view_btn.setChecked(False)
            self.bb_view_btn.setChecked(True)
            self.disable_view_btn.setChecked(False)

        elif mode == 'boundingboxes':
            self.instance_view_btn.setChecked(False)
            self.bb_view_btn.setChecked(False)
            self.disable_view_btn.setChecked(False)
            self.bbs_view_btn.setChecked(True)

        elif mode == 'disable':
            self.instance_view_btn.setChecked(False)
            self.bb_view_btn.setChecked(False)
            self.bbs_view_btn.setChecked(False)
            self.disable_view_btn.setChecked(True)

        else: return

        self.view_toggled.emit(self)


    def mousePressEvent(self, event):
        # toggle highlight
        self.is_highlighted = not self.is_highlighted
        if self.is_highlighted:
            pal = QPalette()
            pal.setColor(QPalette.Background, Qt.black)
            self.autoFillBackground()
            self.setPalette(pal)

        self.clicked.emit(self)
        print 'mouse'

    def mouseDoubleClickEvent(self, event):
        #  self.target_lbl.setVisible(False)
        if not self.is_root:
            self.target_edt.setVisible(True)
            self.target_edt.setFocus()
            self.itme_lay.addWidget(self.target_lbl, 0, 1, 1, 1)
            self.target_edt.setText(self.name)

        #  else:
        #      instance_request.emit(self)

    def finish_edit_name(self):
        #  self.target_lbl.setVisible(True)
        self.target_edt.setVisible(False)
        self.name = self.target_edt.text()
        self.target_lbl.setText(self.name)

        self.name_changed.emit(self)

    def add_child(self, widget):
        self._children.append(widget)
        self.child_lay.insertWidget(0, widget)


class SporeWidget(QWidget):
    def __init__(self, parent=None):
        super(SporeWodget, self).__init__(parent)

class SourceWidget(QWidget):
    def __init__(self, parent=None):
        super(SourceWidget, self).__init__(parent)
