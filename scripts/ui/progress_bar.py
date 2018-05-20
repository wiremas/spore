
import maya.cmds as cmds
import maya.mel as mel


class ProgressBar(object):
    def __init__(self, status='Busy...', start=0, end=100, interruptable=False):
        self._start = start
        self._end = end
        self._status = status
        self._interruptable = interruptable

        self._progress_bar = mel.eval('$tmp = $gMainProgressBar')

    def increment(self, val=1):
        cmds.progressBar(self._progress_bar, e=1, s=val)

    def status(self, msg):
        cmds.progressBar(self._progress_bar, e=1, st=msg)

    def interrupted(self):
        # cmds.waitCursor(state=False)
        return cmds.progressBar(self._progress_bar, q=1, ic=True)

    def run(self):
        # cmds.waitCursor(status=1)
        cmds.progressBar(self._progress_bar,
                         e=1,
                         bp=1,
                         ii=self._interruptable,
                         status=self._status,
                         min=self._start,
                         max=self._end
                         )
        cmds.refresh()

    def stop(self):
        # cmds.waitCursor(state=False)
        cmds.progressBar(self._progress_bar, e=1, ep=1)

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            self.run()
            result = func(*args, **kwargs)
            self.stop()
            return result

        wrapper.increment = self.increment
        wrapper.status = self.status
        wrapper.interrupt = self.interrupted

        return wrapper
