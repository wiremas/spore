from maya import OpenMaya
from maya import OpenMayaMPx
import sys




class SprayCommand(OpenMayaMPx.MPxCommand):
    kPluginCmdName = "spraySpores"
    kVerboseFlag = "-v"
    kVerboseLongFlag = "-verbose"

    def __init__(self):
        super(SamplePyCmd, self).__init__()

        self.verbose = False
        self.cmdArg = "Initial arg"

    def doIt(self, args):

        # Parse the arguments.
        argData = OpenMaya.MArgDatabase(self.syntax(), args)
        try:
            self.cmdArg = argData.commandArgumentString(0)
        except RuntimeError:
            pass
        if argData.isFlagSet(kVerboseFlag):
            self.verbose = argData.flagArgumentBool(kVerboseFlag, 0)

        # Do something
        print "Hello world"

        self.undoIt

    def undoIt(self):

        if self.verbose:
            print 'verbose mode'
            print self.cmdArg

    def redoIt(self):
        pass

    def isUndoable(self):
        return True


# Creator
def cmdCreator():
    # Create the command
    """

    Return:
        pointer to the command

    """
    ptr = OpenMayaMPx.asMPxPtr(SamplePyCmd())
    return ptr


def syntaxCreator():
    """ Syntax creator

    Return:
        syntax (OpenMaya.MSyntax): return value

    """
    syntax = OpenMaya.MSyntax()
    syntax.addArg(OpenMaya.MSyntax.kString)
    syntax.addFlag(kVerboseFlag, kVerboseLongFlag, OpenMaya.MSyntax.kBoolean)
return syntax
