from PySide2.QtWidgets import QWidget, QGridLayout, QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QSpacerItem, QLineEdit
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtCore import Signal, QObject, Qt
from PySide2.QtGui import QPalette, QColor, QPixmap, QIcon

from maya import cmds

from spore.ui import widgets

class NavigatorUI(QWidget):

    def __init__(self, parent=None):
        super(NavigatorUI, self).__init__(parent=parent)
        self.build_ui()

    def build_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
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
        scroll_area.setFixedHeight(150)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { background-color: rgb(50,50,50);}");
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setWidget(scroll_wdg)

        self.spore_layout = QVBoxLayout()
        self.spore_layout.setContentsMargins(1, 1, 1, 1)
        self.spore_layout.setSpacing(0)
        #  self.spore_layout.addStretch()
        scroll_wdg.setLayout(self.spore_layout)
        layout.addWidget(scroll_area, 1, 0, 1, 3)

    def add_item(self, spore_widget):
        self.spore_layout.addWidget(spore_widget)





