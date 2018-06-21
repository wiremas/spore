""" The Spore Dispatcher is the global runtime class that monitors, maintains
and dispatches global processes like prefrence, environment and menu management,
loggin or bug reporting. It is instatiated at plugin load and lifes as long as
the spore plugin is loaded. The dispatcher object is globally available through
the sys._global_spore_dispatcher variable """

import os
import sys
import json
from logging import DEBUG, INFO, WARN, ERROR

import pymel.core as pm
import maya.cmds as cmds
import maya.utils as utils
import maya.OpenMaya as om

import logging_util

import reporter
import report_util
import reporter_ui

reload(report_util)
reload(reporter_ui)
reload(reporter)

reload(logging_util)

class SporeDispatcher(object):

    default_prefs = {
                     'INITIAL_STARTUP': True, # Indicates that spore starts up for the first time
                     'LOG_LEVEL': DEBUG, # Set the log level for spore
                     'AUTOMATIC_REPORT': False, # Submit reports automatically
                     'REPORT': True, # Enable/Disabel reporting
                     'SENDER': '' # Store sender email address
                     }

    def __init__(self):

        # set environment
        self.set_environment()

        # initialize global services
        self.spore_globals = self.parse_prefs()
        self.logger = self.get_logger()
        self.menu = self.build_menu()
        self.callbacks = self.add_callbacks()
        self.set_tracking_dir()



    def set_environment(self):
        """ set environment variable for spore root, log and pref folders.
        this is the first method that must be called to get everything going """

        spore_root_dir = os.path.dirname(__file__).replace('/scripts', '')

        spore_log_dir = os.path.join(spore_root_dir, 'log')
        spore_prefs_dir = os.path.join(spore_root_dir, 'prefs')

        os.environ['SPORE_ROOT_DIR'] = spore_root_dir
        os.environ['SPORE_LOG_DIR'] = spore_log_dir
        os.environ['SPORE_PREFS_DIR'] = spore_prefs_dir

    def parse_prefs(self):
        """ parse the global spore preferences found in the SPORE_PREFS_DIR.
        if the file does not exist, create it with the default prefs. """

        pref_file = os.path.join(os.environ['SPORE_PREFS_DIR'], 'spore_prefs.json')

        if not os.path.isfile(pref_file):
            with open(pref_file, 'w') as f:
                json.dump(self.default_prefs, f)

        with open(pref_file, 'r') as f:
            try:
                spore_globals = json.load(f)
            except ValueError:
                msg = 'Could not load preference file from: {}\nMaybe badly formatted. Try to delete it...'.format(pref_file)
                raise RuntimeError(msg)

        return spore_globals

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

        pm.menuItem(l='Spore Manager', c='import manager;reload(manager)', parent=menu)
        pm.menuItem(divider=True)
        pm.menuItem(l='Create Spore', c='cmds.spore()', parent=menu)
        pm.menuItem(divider=True)
        pm.menuItem(l='Spore Reporter', c='import reporter;reporter.show()', parent=menu)
        pm.menuItem(l='Help', c='print help', parent=menu)

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

        if pref in self.spore_globals.keys():
            if type(value) == type(self.spore_globals[pref]):
                self.logger.debug('Set prefs: {}={}'.format(pref, value))
                self.spore_globals[pref] = value
                self.dump_prefs()
            else:
                raise TypeError('{} must be of type {}'.format(pref, type(self.spore_globals[pref])))
        else:
            raise KeyError('{} is not a valid option'.format(pref))

    def get_pref(self, pref):
        """ get the value for the given pref option """

        return self.spore_globals[pref]

    def dump_prefs(self):
        """ dump the current setting to file """

        pref_file = os.path.join(os.environ['SPORE_PREFS_DIR'], 'spore_prefs.json')

        with open(pref_file, 'w') as f:
            json.dump(self.default_prefs, f)


    def clean_up(self):
        del sys._global_spore_tracking_dir
        self.remove_callbacks()
        self.remove_menu()
        self.logger.debug('Unload Spore, Good bye!')



