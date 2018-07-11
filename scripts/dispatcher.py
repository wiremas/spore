""" The Spore Dispatcher is the global runtime class that monitors, maintains
and dispatches global processes like prefrence, environment and menu management,
loggin or bug reporting. It is instatiated at plugin load and lifes as long as
the spore plugin is loaded. The dispatcher object is globally available through
the sys._global_spore_dispatcher variable """

import os
import sys
import json
from logging import DEBUG, INFO, WARN, ERROR

import maya.mel as mel
import pymel.core as pm
import maya.cmds as cmds
import maya.utils as utils
import maya.OpenMaya as om

import logging_util
import manager
import settings
import reporter
import report_util
import reporter_ui


def global_reload():
    """ filter all loaded spore modules in the script dir and
    reload each of them. this is a convenience function for developing """

    import inspect

    windowed = mel.eval('$temp1=$gMainWindow')
    if windowed:
        scripts_dir = os.path.dirname(__file__)
        for key, module in sys.modules.iteritems():

            try:
                module_path = inspect.getfile(module)
            except TypeError:
                continue

            if module_path == __file__:
                continue

            if module_path.startswith(scripts_dir):
                reload(module)

if os.environ.get('SPORE_DEV_MODE', '0') == '1':
    global_reload()


class GlobalSporeDispatcher(object):

    def __init__(self):

        # set environment
        self.set_environment()

        # initialize global services
        self.spore_globals = settings.SporeGlobals()

        # initialize ui only in gui mode
        windowed = mel.eval('$temp1=$gMainWindow')
        if windowed:
            self.spore_manager = manager.SporeManager()
            self.spore_reporter = reporter.Reporter()

        #  self.spore_globals = self.parse_prefs()
        self.logger = self.get_logger()
        self.menu = self.build_menu()
        self.callbacks = self.add_callbacks()
        self.set_tracking_dir()

    def set_environment(self):
        """ set environment variable for spore root, log and pref folders.
        this is the first method that must be called to get everything going """

        spore_root_dir = os.path.dirname(os.path.dirname(__file__))

        spore_log_dir = os.path.join(spore_root_dir, 'log')
        spore_prefs_dir = os.path.join(spore_root_dir, 'prefs')

        os.environ['SPORE_ROOT_DIR'] = spore_root_dir
        os.environ['SPORE_LOG_DIR'] = spore_log_dir
        os.environ['SPORE_PREFS_DIR'] = spore_prefs_dir

    def get_logger(self):
        """ initialize the logger and hook all uncaught exception
        to our custom exception hook.
        :return: the SporeLogger object """

        logger = logging_util.SporeLogger(__name__, self.spore_globals['LOG_LEVEL'])
        utils.formatGuiException = logger.except_hook
        logger.debug('Create new logger')
        return logger

        #  sys._global_spore_logger = logger

    def build_menu(self):
        """ build spore main menu """

        self.logger.debug('Build menu...')
        main_wnd = pm.language.melGlobals['gMainWindow']
        menu = pm.menu('Spore', parent=main_wnd)
        pm.menuItem(l='Spore Manager', c='import sys;sys._global_spore_dispatcher.spore_manager.show()', parent=menu)
        pm.menuItem(divider=True)
        pm.menuItem(l='Create Spore', c='cmds.spore()', parent=menu)
        pm.menuItem(divider=True)
        pm.menuItem(l='Spore Globals', c='import sys;sys._global_spore_dispatcher.spore_globals.show()', parent=menu)
        pm.menuItem(l='Spore Reporter', c='import sys;sys._global_spore_dispatcher.spore_reporter.show()', parent=menu)
        pm.menuItem(l='Help', c='print help', parent=menu)

        if os.environ.get('SPORE_DEV_MODE', '0') == '1':
            pm.menuItem(l='Run tests', c='import test_util;test_util.run_tests_from_maya', parent=menu)

        return menu

    def remove_menu(self):
        """ remove the spore main menu """

        self.logger.debug('Delete menu...')
        pm.deleteUI(self.menu)

    def add_callbacks(self):
        """ add scene callbacks to reset the global tracking dir when a new
        scene is opened """

        self.logger.debug('Add global scene callbacks...')
        callbacks = om.MCallbackIdArray()
        callbacks.append(om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeOpen, self.set_tracking_dir))
        callbacks.append(om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeNew, self.set_tracking_dir))
        return callbacks

    def remove_callbacks(self):
        """ remove the scene callabacks """

        self.logger.debug('Remove callbacks...')
        for i in xrange(self.callbacks.length()):
            callback = self.callbacks[i]
            om.MSceneMessage.removeCallback(callback)

    def set_tracking_dir(self, *args):
        """ initialize the global spore tracking dir """

        self.logger.debug('Reset global tracking dir')
        sys._global_spore_tracking_dir = {}

    def set_pref(self, pref, value):
        """ set the given pref option to the given value.
        :param pref: must match the a valid option
        :type pref: string
        :param value: type must match the required type
        :type value: any """

        self.spore_globals.set_pref(pref, value)

    def get_pref(self, pref):
        """ get the value for the given pref option """

        return self.spore_globals.spore_globals[pref]

    def clean_up(self):
        del sys._global_spore_tracking_dir
        self.remove_callbacks()
        self.remove_menu()
        self.logger.debug('Unload Spore, Good bye!')



