from PySide2.QtGui import QPainter, QPen
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QLabel, QGridLayout

import canvas

class DrawOverride(canvas.Canvas):
    """ Draw custom 2d shapes on top of the maya viewport """

    def __init__(self, parent=None):
        super(DrawOverride, self).__init__()

    def build(self):
        layout = QGridLayout()
        self.setLayout(layout)

        lbl - QLabel('FOOOOOOO')
        layout.addWidget(lbl)

    def paintEvent(self, event):
        painter = QPainter()
        painter.setRenderHint(painter.Antialiasing)
        #  painter.setRenderHint(painter.HighQualityAnti)

        painter.begin(self)

        print 'paint something', event
        #  path = QPainterPath()
        painter.setPen(QPen(Qt.yellow, 5))
        painter.drawEllipse(50, 50, 50, 50)



        painter.end()
