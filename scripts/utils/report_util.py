
import os
import sys

try:
    import requests
except ImportError:
    import message_utils
    message_utils.IOHandler().warn_dialog('No module named request\nBug reporting will be disabled\nI\'d still appreciate if you send your log files to anno.schachner@gmail.com\nThis helps to improve later version. Thank you!')

import maya.cmds as cmds

import logging_util


class MailWrapper(object):
    """ Wrapper class for anonymouse.org mail service """

    MAIL_URL = 'http://anonymouse.org/cgi-bin/anon-email.cgi'
    TARGET_ADD = 'anno.schachner@gmail.com'

    def __init__(self):
        log_lvl = sys._global_spore_dispatcher.spore_globals['LOG_LEVEL']
        self.logger = logging_util.SporeLogger(__name__, log_lvl)

    def submit_report(self, subject, msg):
        """ submit the report with the given subject and message
        :param subject:
        :param msg: """

        payload = {'to': self.TARGET_ADD,
                   'subject': subject,
                   'text': msg}

        r = requests.post(self.MAIL_URL, payload)

        if r.status_code == requests.codes.ok:
            self.logger.debug('Submitted report')
            print '=' * 40
            print 'Thank you for submitting your report!'
            print '=' * 40

        else:
            #  self.logger.warn('Could not set report, status code: {}'.format(r.status_code)))
            cmds.warning('Could not set report, status code: {}'.format(r.status_code))



