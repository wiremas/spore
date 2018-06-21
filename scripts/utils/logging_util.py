""" spore logggin module
instanciate the SporeLogger whenever we want to log to the spore.log in
the $SPORE_LOG_DIR location. """

import os, sys
import logging
from logging import handlers, DEBUG, INFO, ERROR

import maya.cmds as cmds
import maya.utils as utils

import reporter


class SporeLogger(object):
    """ spore's logging class
    primitive logger with no option to reconfigure once initialized. """

    LOGGERS = set()
    LOG_FORMAT = '[%(name)s] : [%(levelname)s] - %(message)s'

    def __init__(self, name, level=INFO):

        self.logger = logging.getLogger(name)
        if name not in self.LOGGERS:
            self.LOGGERS.add(name)
            self.logger.setLevel(level)

            if not self.logger.handlers:
                self.add_handler()

    def add_handler(self):
        log_file = os.path.join(os.environ['SPORE_LOG_DIR'], 'spore.log')
        file_hdlr = handlers.RotatingFileHandler(log_file, maxBytes=40000, backupCount=3)
        file_formatter = logging.Formatter(self.LOG_FORMAT)
        file_hdlr.setFormatter(file_formatter)
        self.logger.addHandler(file_hdlr)

    def debug(self, msg, extra=None):
        self.logger.debug(msg, extra=extra)

    def info(self, msg, extra=None):
        self.logger.info(msg, extra=extra)

    def warn(self, msg, extra=None):
        self.logger.warn(msg, extra=extra)

    def error(self, msg, extra=None):
        self.logger.error(msg, extra=extra)

    def except_hook(self, typ, value, traceback, detail):
        """ custom except hook
        when the exception is caused by a spore module forward it to the
        logger and run the bug reporter """

        err = utils._formatGuiException(typ, value, traceback, detail)
        if not cmds.about(batch=True) and 'spore' in err.splitlines()[0]:
            self.logger.critical('Uncaught exception:\n', exc_info=(typ, value, traceback))

            if sys._global_spore_dispatcher.get_pref('REPORT'):
                error_info = (typ, value, traceback, detail)
                if sys._global_spore_dispatcher.get_pref('AUTOMATIC_REPORT'):
                    rep = reporter.get_reporter()
                    rep.direct_submit()
                else:
                    reporter.show(error_info)

            return

        return utils._formatGuiException(typ, value, traceback, detail)


