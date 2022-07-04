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
            print(f'Environment "{env}" unloaded')
            print()

    def _unload_environment(self):
        xenv.forEachPlugin(lambda p: safecall(p, 'unload'))

        module = xenv.environmentModule()

        safecall(module, 'unload')

        configs = xenv.environmentConfigs()

        if hasattr(configs, 'variables'):
            for variable in configs.variables.keys():
                xenv.variableUnset(variable)

        if hasattr(configs, 'aliases'):
            for name in configs.aliases.keys():
                xenv.unalias(name)

        if hasattr(configs, 'functions'):
            for name in configs.functions.keys():
                xenv.functionUnset(name)
