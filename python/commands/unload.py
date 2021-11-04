from xenv import constants
import os
import xenv
from xenv.pluggable import safecall


def commands():
    return [Unload]


class Unload():
    name = 'unload'

    @staticmethod
    def cmdline_switch(parserbuilder):
        parserbuilder.add_command(Unload.name)  # TODO alias:off

    def run(self, verbose=True):
        if not (env := xenv.environmentActive()):
            xenv.error('No xenv environment loaded', 1)

        self._unload_environment()

        xenv.variableUnset(constants.activeEnvironmentVariable)

        if verbose:
            print()
            print(f'Environment "{env}" unloaded')

    def _unload_environment(self):
        xenv.forEachPlugin(lambda p: safecall(p, 'unload'))

        module = xenv.environmentModule()

        safecall(module, 'unload')
