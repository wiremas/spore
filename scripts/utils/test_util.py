import os
import sys
import unittest
import __builtin__

import maya.cmds as cmds


class TestUtil(object):

    def __init__(self):

        self.test_dir = os.path.join(os.environ['SPORE_ROOT_DIR'], 'tests')
        sys.path.append(self.test_dir)

        self.runner = unittest.TextTestRunner()
        self.suite = None

    def run_tests(self):
        """ run the actual tests """

        self.suite = self.get_tests()
        self.runner.run(self.suite)

    def run_tests_from_commandline(self):
        """ run unittest from the command line with the mayapy interpreter """

        import maya.standalone as standalone
        standalone.initialize()

        sys_path = [os.path.realpath(p) for p in sys.path]
        python_path = os.environ.get('PYTHONPATH', '')
        for p in python_path.split(os.pathsep):
            p = os.path.realpath(p)
            if p not in sys_path:
                sys.path.append(p)

        self.run_tests()

        if hasattr(standalone, 'uninitialize'):
            standalone.uninitialize()


    def get_tests(self):

        suite = unittest.TestSuite()

        discovered_suite = unittest.TestLoader().discover(self.test_dir)
        if discovered_suite.countTestCases():
            suite.addTests(discovered_suite)

        return suite


class TestCase(unittest.TestCase):
    plugins = set()

    @classmethod
    def tearDownClass(cls):
        #  super(TestCase, cls).tearDownClass()
        cls.unload_plugins()

    @classmethod
    def load_plugin(cls, plugin):
        if cmds.pluginInfo(plugin, q=True, l=True):
            cmds.unloadPlugin(plugin)
        cmds.loadPlugin(plugin)
        cls.plugins.add(plugin)

    @classmethod
    def unload_plugins(cls):
        for plugin in cls.plugins:
            cmds.unloadPlugin(plugin)
        cls.plugins = set()


class RollbackImporter(object):
    """ the rollbacl importer overrides the global importer
    to roll back loaded modules for testing.
    credit goes to:
    http://pyunit.sourceforge.net/notes/reloading.html """

    def __init__(self):
        self.previous_modules = sys.modules.copy()
        self.real_import = __builtin__.__import__
        __builtin__.__import__ = self._import
        self.newModules = {}

    def _import(self, name, globals=None, locals=None, fromlist=[]):
        """ overwirte the builtin import functionality """
        result = apply(self.real_import, (name, globals, locals, fromlist))
        self.newModules[name] = 1
        return result

    def uninstall(self):
        for modname in self.newModules.keys():
            if not self.previousModules.has_key(modname):
                # Force reload when modname next imported
                del(sys.modules[modname])
        __builtin__.__import__ = self.real_import

if __name__ == '__main__':
    test_util = TestUtil()
    test_util.run_tests_from_commandline()
