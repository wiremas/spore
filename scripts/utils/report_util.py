import os
import sys
import urllib
import urllib2

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

        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)
        data = urllib.urlencode(payload)
        request = urllib2.Request(self.MAIL_URL, data=data)
        request.get_method = lambda: "POST"

        try:
            connection = opener.open(request)
        except urllib2.HTTPError, e:
            connection = e

        # check. Substitute with appropriate HTTP code.
        if connection.code == 200:
            data = connection.read()
            print '=' * 40 + '\nThank you for submitting your report!\n' + '=' * 40
            return True
        else:
            self.logger.error('Could not send report, error code: {}'.format(connection))
            return False
