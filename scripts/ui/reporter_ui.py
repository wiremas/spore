
from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit, QTextEdit, QPushButton, QLabel, QFrame

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

import logging_util


class ReporterUI(MayaQWidgetDockableMixin, QWidget):
    submit_report = Signal()
    cancel_report = Signal()
    disable_report = Signal()
    automatic_report = Signal()

    def __init__(self, parent=None):
        super(ReporterUI, self).__init__(parent=parent)

        self.build_ui()
        self.connect_signals()

    def build_ui(self):
        self.setGeometry(50, 50, 450, 300)
        self.setMinimumSize(400, 300)
        self.setWindowTitle('Spore Reporter')

        layout = QVBoxLayout()

        #  self.err_wdg = QWidget()
        #  err_layout = QHBoxLayout(self.err_wdg)
        #  layout.addWidget(err_wdg)
        #
        #  err_lbl = 'Ops..\nSpore seems to have caused an error.\n'

        info_msg = 'Help to improve Spore by anonymously submitting your logs'
        self.info_lbl = QLabel(info_msg)
        layout.addWidget(self.info_lbl)

        self.address_edt = QLineEdit()
        self.address_edt.setPlaceholderText('E-Mail Address (optional)')
        layout.addWidget(self.address_edt)

        self.subject_edt = QLineEdit()
        self.subject_edt.setPlaceholderText('Subject (optional)')
        layout.addWidget(self.subject_edt)

        self.msg_edt = QTextEdit()
        self.msg_edt.setPlaceholderText('Message (optional)')
        self.msg_edt.setFixedHeight(60)
        layout.addWidget(self.msg_edt)

        self.log_edt = QTextEdit()
        self.log_edt.setReadOnly(True)
        self.log_edt.setLineWrapMode(QTextEdit.NoWrap)
        layout.addWidget(self.log_edt)

        ctrl_layout = QGridLayout()
        layout.addLayout(ctrl_layout)

        self.submit_btn = QPushButton('Submit')
        ctrl_layout.addWidget(self.submit_btn, 0, 0, 1, 1)

        self.cancel_btn = QPushButton('Cancel')
        ctrl_layout.addWidget(self.cancel_btn, 0, 1, 1, 1)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        ctrl_layout.addWidget(line, 1, 0, 1, 2)

        self.disable_btn = QPushButton('Disable Reporter')
        ctrl_layout.addWidget(self.disable_btn, 2, 0, 1, 1)

        self.auto_btn = QPushButton('Send Reports Automatically')
        ctrl_layout.addWidget(self.auto_btn, 2, 1, 1, 1)

        self.setLayout(layout)

    def connect_signals(self):
        self.submit_btn.clicked.connect(self.submit_report.emit)
        self.cancel_btn.clicked.connect(self.cancel_report.emit)
        self.disable_btn.clicked.connect(self.disable_report.emit)
        self.auto_btn.clicked.connect(self.automatic_report.emit)

    def set_log_text(self, text):
        self.log_edt.setText(text)

    def get_user_input(self):
        address = self.address_edt.text()
        subject = self.subject_edt.text()
        msg = self.msg_edt.toPlainText()
        return address, subject, msg

    def show(self):
        super(ReporterUI, self).show()


