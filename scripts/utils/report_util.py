import os
import sys
import time
import urllib
import urllib2

from PySide2.QtCore import QTimer

import maya.cmds as cmds

import logging_util


class MailWrapper(object):
    """ Wrapper class for anonymouse.org mail service """

    MAIL_URL = 'http://anonymouse.org/cgi-bin/anon-email.cgi'
    TARGET_ADD = 'anno.schachner@gmail.com'

    def __init__(self):
        self.logger = logging_util.SporeLogger(__name__)

        self.timer = QTimer()
        self.timer.timeout.connect(self.send_report)
        self.last_msg = 0.0
        self.msg_stack = []

    def submit_report(self, subject, msg):
        """ send a POST request to anonymouse.org to send a email with
        the given subject and message.
        :param subject: string containing the subject
        :type subject: str
        :param msg: string containing the message
        :type msg: str
        :return: True if the email was sent successfull else False
        :return type: bool """

        payload = {'to': self.TARGET_ADD,
                   'subject': subject,
                   'text': msg}

        current_time = time.time()

        if self.last_msg + 60 > current_time:
            self.msg_stack.append(payload)
            # add some extra seconds since the qtime is not 100% accurate
            self.timer.start(65000)
            self.logger.warn('Can only send one message per minute. Delivery postponed for {}sec.'.format(60 * len(self.msg_stack)))

        else:
            self.send_report(payload)

    def send_report(self, payload=None):

        if not payload:
            self.logger.debug('Timer triggered report')
            if self.msg_stack:
                payload = self.msg_stack.pop(-1)
                self.logger.debug('Timer triggered report')
            else:
                self.logger.debug('No more messages to send. Time stopped')
                self.timer.stop()
                return

        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)
        data = urllib.urlencode(payload)
        request = urllib2.Request(self.MAIL_URL, data=data)
        request.get_method = lambda: "POST"

        try:
            connection = opener.open(request)
        except urllib2.HTTPError, e:
            connection = e

        self.last_msg = time.time()

        # check. Substitute with appropriate HTTP code.
        if connection.code == 200:
            data = connection.read()
            self.logger.debug('Report {} delivered'.format(payload['subject']))
            print '=' * 40 + '\nThank you for submitting your report!\n' + '=' * 40
            return True
        else:
            self.logger.error('Could not send report, error code: {}'.format(connection))
            return False
