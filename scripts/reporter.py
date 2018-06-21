"""" a wrapper for http://anonymouse.org, a free web service for sending
anonymous emails.
The module provides a simple maya ui to report bugs and issues.
If the reporter finds a valid spore.log it will also be includeded in the
report """

import os
import sys

import maya.cmds as cmds

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLineEdit, QTextEdit, QPushButton, QLabel, QFrame

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

import logging_util
import report_util
import reporter_ui

reload(report_util)
reload(reporter_ui)

REPORTER = None


class Reporter(object):
    """ Bug/issue report util """

    def __init__(self):
        super(Reporter, self).__init__()

        self.logger = logging_util.SporeLogger(__name__)

        self.ui = reporter_ui.ReporterUI()
        self.ui.submit_report.connect(self.submit_report)
        self.ui.cancel_report.connect(self.cancel_report)
        self.ui.disable_report.connect(self.disable_report)
        self.ui.automatic_report.connect(self.automatic_report)

    def get_log_content(self):
        """ get the content of all log files """

        if os.environ.has_key('SPORE_LOG_DIR'):
            log_content = ''

            log_file = os.path.join(os.environ['SPORE_LOG_DIR'], 'spore.log')
            with open(log_file, 'r') as f:
                log_content += '#' * 20 + ' Spore Log ' + '#' * 20 + '\n'
                log_content += f.read()
                log_content += '#' * 51 + '\n'

            return log_content

    def format_report(self, sender, subject, message, log):
        """ format the given payload to the actual report message """

        report = 'Report submitted from: {}\n'.format(sender)
        report += 'Subject: {}\n'.format(subject)
        report += 'Message: {}\n'.format(message)
        report += 'Log:\n{}\n'.format(log)
        return report

    @Slot()
    def submit_report(self):
        """ submit the report """

        log = self.get_log_content()
        address, subject, msg = self.ui.get_user_input()
        if address:
            sys._global_spore_dispatcher.set_pref('SENDER', address)

        report = self.format_report(address, subject, msg, log)

        mail = report_util.MailWrapper()
        mail.submit_report(subject, report)

        self.ui.close()

    @Slot()
    def cancel_report(self):
        """ close the reporter ui """

        self.ui.close()

    @Slot()
    def disable_report(self):
        """ disable the bug reporter """

        self.logger.debug('User disabled submitting reports')
        sys._global_spore_dispatcher.set_pref('REPORT', False)
        self.ui.close()

    @Slot()
    def automatic_report(self):
        """ opt in to automatically submitting all unhandled exceptions """

        self.logger.debug('User opted in to submitting reports automatically')
        sys._global_spore_dispatcher.set_pref('AUTOMATIC_REPORT', True)
        self.submit_report()

    def direct_submit(self):
        """ directly submit a bug report without opening up the ui """

        self.logger.debug('Automatic bug report')
        log = self.get_log_content()
        subject = 'SPORE - Automatic Bug Report'
        address = sys._global_spore_dispatcher.get_pref('SENDER')
        report = self.format_report(address, subject, '', log)

        mail = report_util.MailWrapper()
        mail.submit_report(subject, report)

    def show(self, err=None):

        self.logger.debug('Show Spore Reporter')
        self.ui.show()
        log = self.get_log_content()
        self.ui.set_log_text(log)



def show(err=None):
    """ show the Reporter window.
    the given payload must be a tuple of:
        (exc_typ, exc_value, exc_traceback, exec_detail)
    when a certain payload is given the for will be filled automatically """

    global REPORTER
    if not REPORTER:
        REPORTER = Reporter()

    REPORTER.show(err)

    return REPORTER

def get_reporter():
    global REPORTER
    if not REPORTER:
        REPORTER = Reporter()
    return REPORTER




