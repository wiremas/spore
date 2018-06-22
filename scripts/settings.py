import os
import sys
import json
from logging import DEBUG, INFO, WARN, ERROR

import settings_ui
import logging_util

#  reload(settings_ui)

try:
    import requests
    REPORT_DEFAULT = True
except ImportError:
    REPORT_DEFAULT = False

class SporeGlobals(object):

    default_prefs = {
                     'INITIAL_STARTUP': True, # Indicates that spore starts up for the first time
                     'LOG_LEVEL': ERROR, # Set the log level for spore
                     'AUTOMATIC_REPORT': REPORT_DEFAULT, # Submit reports automatically
                     'REPORT': True, # Enable/Disabel reporting
                     'SENDER': ' ' # Store sender email address
                     }

    def __init__(self):

        self.ui = settings_ui.SettingsUI()
        self.spore_globals = self.parse_prefs()
        self.logger = logging_util.SporeLogger(__name__, self['LOG_LEVEL'])
        self.fill_prefs_ui()

    def __getitem__(self, attr):
        return self.spore_globals[attr]

    def __setitem__(self, attr, val):

        if attr in self.spore_globals.keys():
            if type(value) == type(self.spore_globals[pref]):
                self.logger.debug('Set prefs: {}={}'.format(pref, value))
                self.spore_globals[attr] = val
                self.dump_prefs()
            else:
                raise TypeError('{} must be of type {}'.format(pref, type(self.spore_globals[pref])))
        else:
            raise KeyError('{} is not a valid option'.format(pref))

    def __iter__(self):
        for attr, val in self.spore_globals.iteritems():
            yield attr, val

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

    def fill_prefs_ui(self):
        """ fill the settings ui with existing globals """

        for key, val in self.spore_globals.iteritems():
            print key, val
            self.ui.add_pref_wdg(key, val)

    def set_pref(self, pref, value):
        """ set the given pref option to the given value.
        :param pref: must match the a valid option
        :type pref: string
        :param value: type must match the required type
        :type value: any """

        if pref in self.spore_globals.keys():
            if type(value) == type(self.spore_globals[pref]):
                self.logger.debug('#DEPRECATED METHOD - USE __setitem__# Set prefs: {}={}'.format(pref, value))
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

    def show(self):
        self.ui.show()

