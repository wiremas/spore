import sip

from PySide2.QtWidgets import QWidget, QGridLayout, QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QSpacerItem, QLineEdit, QAction, QMenu
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtCore import Signal, QObject, Qt, QEvent
from PySide2.QtGui import QPalette, QColor, QPixmap, QIcon

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from maya import cmds

"""
class NavigatorUI(QWidget):

    def __init__(self, parent=None):
        super(NavigatorUI, self).__init__(parent=parent)
        self.build_ui()

    def build_ui(self):
        #  layout = QHBoxLayout()
        layout = QGridLayout(self)
        self.setLayout(layout)

        self.add_btn = QPushButton()
        self.add_btn.setIcon(QIcon(QPixmap(':/teAdditive.png')))
        layout.addWidget(self.add_btn, 0, 0, 1, 1)
        remove_btn = QPushButton('-')
        layout.addWidget(remove_btn, 0, 1, 1, 1)
        refresh_btn = QPushButton('refresh')
        layout.addWidget(refresh_btn, 0, 2, 1, 1)

        scroll_wdg = QWidget(self)
        scroll_area = QScrollArea()
        #  scroll_area.setWidgetResizable(True)
        #  scroll_area.setStyleSheet("QScrollArea { background-color: rgb(57,57,57);}");
        #  scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        #  scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setWidget(scroll_wdg)

        self.spore_layout = QVBoxLayout()
        self.spore_layout.setContentsMargins(1, 1, 3, 1)
        self.spore_layout.setSpacing(0)
        self.spore_layout.addStretch()
        scroll_wdg.setLayout(self.spore_layout)
        layout.addWidget(scroll_area, 1, 0, 1, 3)
        """





class ManagerWindow(MayaQWidgetDockableMixin, QWidget):
    add_spore_clicked = Signal(str)
    remove_spore_clicked = Signal()
    refresh_spore_clicked = Signal()

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
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

        self.name_edt = QLineEdit()
        self.name_edt.setPlaceholderText('Create New Setup')
        self.name_edt.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        layout.addWidget(self.name_edt, 0, 0, 1, 1)

        self.add_btn = QPushButton()
        self.add_btn.setIcon(QIcon(QPixmap(':/teAdditive.png')))
        self.add_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        layout.addWidget(self.add_btn, 0, 1, 1, 1)

        self.refresh_btn = QPushButton()
        self.refresh_btn.setIcon(QIcon(QPixmap(':/teKeyRefresh.png')))
        self.refresh_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        layout.addWidget(self.refresh_btn, 0, 2, 1, 1)

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
        self.name_edt.returnPressed.connect(lambda: self.add_spore_clicked.emit(self.name_edt.text()))
        self.add_btn.clicked.connect(lambda: self.add_spore_clicked.emit(self.name_edt.text()))
        #  self.remove_btn.clicked.connect(self.remove_spore_clicked.emit)
        self.refresh_btn.clicked.connect(self.refresh_spore_clicked.emit)

    def append_item(self, item):
        #  item.setParent(self)
        self.items.append(item)
        self.spore_layout.insertWidget(0, item)

    def remove_item(self, item):
        pass

    def clear_items(self):
        for item in self.items:
            print 'widget: ', item
            # item.setVisible(False)
            self.spore_layout.removeWidget(item)
            self.items.remove(item)
            item.delateLater()
            del item
        #  del self.itmes
        #  self.spore_layout.clear()

        self.spore_layout.update()

    def clear_layout(self):
        del self.items[:]
        print 'items', self.items
        while self.spore_layout.count():
            child = self.spore_layout.takeAt(0)
            print child
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                clear_layout(child.layout())

        self.spore_layout.setSpacing(0)
        self.spore_layout.addStretch()



class TreeItemWidget(QWidget):

    clicked = Signal(QObject)
    view_toggled = Signal(QObject)
    name_changed = Signal(QObject)

    def __init__(self, name, parent=None):
        """ primitive tree item widget for navigator
        :param name: full dag path name of the item """
        super(TreeItemWidget, self).__init__(parent)

        self.long_name = name
        self.name = name.split('|')[-1]
        self.is_selected = False
        #  self.level = level

        self.parent_elem = None
        self.child_elem = []

        self.build_ui()

    def build_ui(self):
        #  self.setFixedHeight(30)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.item_wdg = QFrame()
        self.layout.addWidget(self.item_wdg)
        self.item_lay = QGridLayout(self.item_wdg)
        self.item_lay.setContentsMargins(0, 0, 0, 0)
        #  self.item_lay.setSpacing(3)

        #  self.item_wdg.setFrameStyle(QFrame.Raised | QFrame.Panel)
        #  self.item_wdg.setStyleSheet("QFrame {background-color: rgb(55,55,55);}")
        #  self.item_wdg.setFixedHeight(30)

        # widget containing child widgets
        self.child_wdg = QWidget()
        self.layout.addWidget(self.child_wdg)
        self.child_lay = QVBoxLayout(self.child_wdg)
        self.child_lay.setContentsMargins(0, 0, 0, 0)
        self.child_lay.setSpacing(0)

        #  self.setLayout(layout)


    #  def mouseReleaseEvent(self, event):
    #
    #      self.is_selected = not self.is_selected
    #
    #      if self.is_selected:
    #          pal = QPalette()
    #          pal.setColor(self.backgroundRole(), Qt.black)
    #          #  pal.setColor(QPalette.Background, Qt.black)
    #
    #          self.setAutoFillBackground(True)
    #          self.setPalette(pal)
    #          #  self.setStyleSheet("background-color: rgb(55,55,155);")
    #      else:
    #          pass
    #          #  self.setStyleSheet("background-color: rgb(55,55,55);")
    #
    #      print 'pressed', event, self.is_selected
    def add_child(self, widget):
        widget.parent_elem = self
        self.child_elem.append(widget)
        self.child_lay.addWidget(widget)

class GeoItem(TreeItemWidget):
    def __init__(self, name, parent=None):
        super(GeoItem, self).__init__(name, parent)

        self.build_geo_ui()
        self.connect_signals()

    def build_geo_ui(self):

        #  self.setMaximumHeight(85)
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
        self.expand_btn.setChecked(True)
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

        #  self.view_buttons = DisplayButtons(self)
        #  self.item_lay.addWidget(self.view_buttons, 0, 4, 1, 1)

    def connect_signals(self):
        self.expand_btn.toggled.connect(self.toggle_children)

    def toggle_children(self):
        state = self.expand_btn.isChecked()
        print 'toggle', state
        self.child_wdg.setVisible(state)



class SporeItem(TreeItemWidget):
    clicked = Signal(QObject, QEvent)
    double_clicked = Signal()
    context_requested = Signal(QObject, QAction)
    view_toggled = Signal(QObject, int)
    name_changed = Signal(QObject, str)

    def __init__(self, name, parent=None):
        super(SporeItem, self).__init__(name, parent)

        self.build_spore_ui()
        self.connect_signals()

    def build_spore_ui(self):

        self.item_wdg.setFrameStyle(QFrame.Raised | QFrame.StyledPanel)
        self.setStyleSheet("background-color: rgb(68,68,68);")

        pixmap = QPixmap(':/out_particle.png')
        icon_lbl = QLabel()
        icon_lbl.setMaximumWidth(18)
        icon_lbl.setPixmap(pixmap)
        self.item_lay.addWidget(icon_lbl, 0, 1, 1, 1)

        self.target_lbl = QLabel(self.name)
        self.item_lay.addWidget(self.target_lbl, 0, 2, 1, 1)

        self.target_edt = QLineEdit(self.item_wdg)
        self.target_edt.setStyleSheet("background-color: rgb(68,68,68);")
        self.target_edt.setMinimumWidth(180)
        self.target_edt.setVisible(False)
        self.item_lay.addWidget(self.target_edt, 0, 2, 1, 1)

        self.item_lay.setColumnStretch(2, 1)

        self.view_buttons = DisplayButtons(self)
        self.item_lay.addWidget(self.view_buttons, 0, 3, 1, 1)

    def connect_signals(self):
        self.view_buttons.view_instancer.connect(lambda: self.toggle_view(0))
        self.view_buttons.view_bounding_box.connect(lambda: self.toggle_view(2))
        self.view_buttons.view_bounding_boxes.connect(lambda: self.toggle_view(1))
        #  self.view_buttons.view_hide.connect(self.view_hide.emit(self))

        #  self.target_edt.returnPressed.connect(self.change_name)
        self.target_edt.editingFinished.connect(self.change_name)

    def mousePressEvent(self, event):
        """ click event to select / deselect widgets """

        if event.button() == Qt.LeftButton:
            if self.is_selected:
                self.deselect()
            else:
                self.select()
            self.clicked.emit(self, event)

    def mouseDoubleClickEvent(self, event):
        """ double click event to enter rename context """

        self.target_lbl.setVisible(False)
        self.target_edt.setVisible(True)
        self.target_edt.setFocus()

    def contextMenuEvent(self, event):

        if not self.is_selected:
            self.select()

        # build context menu
        menu = QMenu(self)
        menu.setStyleSheet("background-color: rgb(68,68,68);")
        instance_displ_act = menu.addAction("Display Instances")
        bb_displ_act = menu.addAction("Display Bounding Box")
        bbs_displ_act = menu.addAction("Display Bounding Boxes")
        hide_act = menu.addAction("Hide Selected Setup(s)")
        #  menu.addSeparator()
        #  convert_particle_act = menu.addAction("Convert to Particles")
        #  convert_particle_act = menu.addAction("Write to Alembic")
        #  convert_particle_act = menu.addAction("Write to Katana Live Group")
        #  convert_particle_act = menu.addAction("Combine Selected Setups")
        menu.addSeparator()
        remove_act = menu.addAction("Remove Selected Setup(s)")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        self.context_requested.emit(self, action)

    def deselect(self):
        """ deselect widget """

        self.is_selected = False
        self.setStyleSheet("background-color: rgb(68,68,68);")

    def select(self):
        """ select widget """

        self.is_selected = True
        self.setStyleSheet("background-color: rgb(21,60,97);")

    def set_select(self, select=False):

        if select:
            self.select()
        else:
            self.deselect()

        return self.is_selected

    def toggle_view(self, state):
        self.view_toggled.emit(self, state)

    def change_name(self):
        """ trigger for name changed event """

        name = self.target_edt.text()
        if name:
            self.name_changed.emit(self, name)

        self.target_edt.setVisible(False)
        self.target_lbl.setVisible(True)


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

        #  self.disable_view_btn = QPushButton()
        #  self.disable_view_btn.setIcon(QIcon(QPixmap(':/error.png')))
        #  self.disable_view_btn.setFlat(True)
        #  self.disable_view_btn.setCheckable(True)
        #  self.disable_view_btn.setFixedWidth(25)
        #  self.disable_view_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        #  view_btn_lay.addWidget(self.disable_view_btn)

        self.connect_signals()

    def connect_signals(self):
        self.instance_view_btn.clicked.connect(lambda: self.toggle_view('instance'))
        self.bb_view_btn.clicked.connect(lambda: self.toggle_view('boundingbox'))
        self.bbs_view_btn.clicked.connect(lambda: self.toggle_view('boundingboxes'))
        #  self.disable_view_btn.clicked.connect(lambda: self.toggle_view('disable'))

    def toggle_view(self, mode):
        """ toggle between diffenrent view modes
        :param mode str: instance, boundingbox, boundingboxes, disable """

        self.viewmode = mode
        if mode == 'instance':
            #  self.view_bounding_boxes.emit()
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

