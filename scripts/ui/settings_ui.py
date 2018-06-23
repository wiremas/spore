import sys

from PySide2.QtWidgets import (QWidget, QGridLayout, QPushButton, QFrame,
                               QHBoxLayout, QVBoxLayout, QLabel, QScrollArea,
                               QSpacerItem, QLineEdit, QAction, QMenu,
                               QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox)
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtCore import Signal, QObject, Qt, QEvent
from PySide2.QtGui import QPalette, QColor, QPixmap, QIcon

from maya import cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

import logging_util


class SettingsUI(MayaQWidgetDockableMixin, QWidget):

    save_prefs = Signal(dict)

    def __init__(self, parent=None):
        super(SettingsUI, self).__init__(parent=parent)

        #  log_lvl = sys._global_spore_dispatcher.spore_globals['LOG_LEVEL']
        #  self.logger = logging_util.SporeLogger(__name__, log_lvl)
        self.build_ui()
        self.pref_tracking_dir = {}

    def build_ui(self):
        self.setWindowTitle('Spore Preferences')
        self.setGeometry(250, 250, 400, 150)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addStretch()

        self.save_btn = QPushButton('Save')
        self.layout.addWidget(self.save_btn)

        self.save_btn.clicked.connect(self.about_to_save)

    def add_pref_wdg(self, name, value):

        if isinstance(value, bool):
            wdg = BoolWidget(name, value)
            self.layout.insertWidget(0, wdg)
            self.pref_tracking_dir[wdg.name_lbl] = wdg.bool_cbx
        elif isinstance(value, str) or isinstance(value, unicode):
            wdg = StringWidget(name, value)
            self.layout.insertWidget(0, wdg)
            self.pref_tracking_dir[wdg.name_lbl] = wdg.line_edt
        elif isinstance(value, int):
            wdg = IntegerWidget(name, value)
            self.layout.insertWidget(0, wdg)
            self.pref_tracking_dir[wdg.name_lbl] = wdg.int_spn
        elif isinstance(value, float):
            wdg = FloatWidget(name, value)
            self.layout.insertWidget(0, wdg)
            self.pref_tracking_dir[wdg.name_lbl] = wdg.float_spn
        else:
            print 'no assignment for', name, value, type(value)
            pass

    def about_to_save(self):
        """ triggered by the save button.
        emit the save_prefs signal and send the resulting settings """

        #  self.logger.debug('About to emit save settings.')
        prefs = {}
        for attr_lbl, val_wdg in self.pref_tracking_dir.iteritems():
            attr = attr_lbl.text()

            val = None
            if isinstance(val_wdg, QCheckBox):
                val = val_wdg.isChecked()
            elif isinstance(val_wdg, QLineEdit):
                val = val_wdg.text()
            elif isinstance(val_wdg, QSpinBox)\
            or isinstance(val_wdg, QDoubleSpinBox):
                val = val_wdg.value()
            else:
                #  self.logger.error('Unknown widget type: {}'.format(val_wdg))
                raise RuntimeError('Impossible')

            prefs[attr] = val

        self.save_prefs.emit(prefs)
        self.close()

class BoolWidget(QWidget):
    def __init__(self, name, value):
        super(BoolWidget, self).__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.name_lbl = QLabel(name)
        self.name_lbl.setFixedWidth(150)
        layout.addWidget(self.name_lbl)

        self.bool_cbx = QCheckBox()
        self.bool_cbx.setChecked(value)
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

        self.int_spn = QSpinBox()
        self.int_spn.setValue(value)
        layout.addWidget(self.int_spn)

class FloatWidget(QWidget):
    def __init__(self, name, value):
        super(FloatWidget, self).__init__()

        self.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.name_lbl = QLabel(name)
        self.name_lbl.setFixedWidth(150)
        layout.addWidget(self.name_lbl)

        self.float_spn = QDoubleSpinBox()
        self.float_spn.setValue(value)
        layout.addWidget(self.float_spn)






