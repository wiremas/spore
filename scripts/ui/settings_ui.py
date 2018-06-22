
from PySide2.QtWidgets import (QWidget, QGridLayout, QPushButton, QFrame,
                               QHBoxLayout, QVBoxLayout, QLabel, QScrollArea,
                               QSpacerItem, QLineEdit, QAction, QMenu,
                               QComboBox, QSpinBox, QDoubleSpinBox)
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtCore import Signal, QObject, Qt, QEvent
from PySide2.QtGui import QPalette, QColor, QPixmap, QIcon

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from maya import cmds


class SettingsUI(MayaQWidgetDockableMixin, QWidget):

    def __init__(self, parent=None):
        super(SettingsUI, self).__init__(parent=parent)
        self.build_ui()

    def build_ui(self):
        self.setWindowTitle('Spore Preferences')
        self.setGeometry(50, 50, 400, 550)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addStretch()

        self.save_btn = QPushButton('Save')
        self.layout.addWidget(self.save_btn)

    def add_pref_wdg(self, name, value):

        if isinstance(value, bool):
            wdg = BoolWidget(name, value)
            self.layout.insertWidget(0, wdg)
        elif isinstance(value, str) or isinstance(value, unicode):
            wdg = StringWidget(name, value)
            self.layout.insertWidget(0, wdg)
        elif isinstance(value, int):
            wdg = IntegerWidget(name, value)
            self.layout.insertWidget(0, wdg)
        elif isinstance(value, float):
            wdg = FloatWidget(name, value)
            self.layout.insertWidget(0, wdg)
        else:
            print 'no assignment for', name, value, type(value)
            pass


class BoolWidget(QWidget):
    def __init__(self, name, value):
        super(BoolWidget, self).__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.name_lbl = QLabel(name)
        self.name_lbl.setFixedWidth(150)
        layout.addWidget(self.name_lbl)

        self.bool_cbx = QComboBox()
        self.bool_cbx.addItem('True')
        self.bool_cbx.addItem('False')
        self.bool_cbx.setCurrentIndex(1 if value else 0)
        layout.addWidget(self.bool_cbx)


class StringWidget(QWidget):
    def __init__(self, name, value):
        super(StringWidget, self).__init__()

        self.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.name_lbl = QLabel(name)
        self.name_lbl.setFixedWidth(150)
        layout.addWidget(self.name_lbl)

        self.line_edt = QLineEdit()
        self.line_edt.setText(value)
        layout.addWidget(self.line_edt)

class IntegerWidget(QWidget):
    def __init__(self, name, value):
        super(IntegerWidget, self).__init__()

        self.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.name_lbl = QLabel(name)
        self.name_lbl.setFixedWidth(150)
        layout.addWidget(self.name_lbl)

        self.inst_spn = QSpinBox()
        self.inst_spn.setValue(value)
        layout.addWidget(self.inst_spn)

class FloatWidget(QWidget):
    def __init__(self, name, value):
        super(FloatWidget, self).__init__()

        self.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.name_lbl = QLabel(name)
        self.name_lbl.setFixedWidth(150)
        layout.addWidget(self.name_lbl)

        self.inst_spn = QDoubleSpinBox()
        self.inst_spn.setValue(value)
        layout.addWidget(self.inst_spn)






