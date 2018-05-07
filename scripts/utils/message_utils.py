#   -----------------------------------------------------------------------------
#   This source file has been developed by Anno Schachner within the scope of the
#   Technical Director course at Filmakademie Baden-Wuerttemberg.
#   http://td.animationsinstitut.de/
#
#   Copyright (c) 2016 Filmakademie Baden-Wuerttemberg, Institute of Animation
#
#   -----------------------------------------------------------------------------

import maya.OpenMaya as om
import maya.OpenMayaUI as omui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import window_utils


class IOHandler(object):

    parent_wdg = window_utils.maya_main_window()

    def set_message(self, msg, lvl=0):
        """ sets an message in the status bar
        :param msg : the message to be displayed
        :param lvl : alters the message level:
                        0 = info message
                        1 = warning message
                        2 = error message """

        # self.status_bar.showMessage(msg, 6000)

        output = {0: om.MGlobal.displayInfo,
                  1: om.MGlobal.displayWarning,
                  2: om.MGlobal.displayError}

        output[lvl](msg)

    def confirm_dialog(self, msg, title='Title'):

        dialog = QtWidgets.QMessageBox()
        dialog.setIcon(QtWidgets.QMessageBox.Question)
        result = dialog.question(self.parent_wdg,
                                 title,
                                 msg,
                                 QtWidgets.QMessageBox.Yes,
                                 QtWidgets.QMessageBox.No
                                 )

        if result == QtWidgets.QMessageBox.Yes:
            return True
        else:
            return False

    def warn_dialog(self, msg, detail=None):
        dialog = QtWidgets.QMessageBox()
        dialog.setIcon(QtWidgets.QMessageBox.Warning)

        # dialog.setModal(1)
        dialog.setWindowTitle('Warning')
        dialog.setText(msg)
        if detail:
            dialog.setDetailedText(detail)

        dialog.exec_()

    def info_dialog(self, msg, title='Info'):
        dialog = QtWidgets.QMessageBox()
        dialog.setIcon(QtWidgets.QMessageBox.Information)

        dialog.setWindowTitle(title)
        dialog.setText(msg)

        dialog.exec_()


    def set_file_dialog(mode=0, file_mode=2):
        """ Set a file dialog
        :param mode : indicates whether to open or to save file
          0 - open
          2 - save
        :param file_mode : indicate what the user may select
          0 - AnyFile
          1 - ExistingFile
          2 - Directory
          3 - Existing Files """

        dialog = QtWidgets.QFileDialog()
        dialog.setFileMode(file_mode)
        # TODO - finish
