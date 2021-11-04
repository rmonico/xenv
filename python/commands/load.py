from xenv import constants
import os
from xenv import Plugin
import xenv
from xenv.pluggable import safecall


def commands():
    return [Load]


class Load():
    name = 'load'

    @staticmethod
    def cmdline_switch(parserbuilder):
        with parserbuilder.add_command(Load.name) as b:
            b.add_argument('environment', default=constants.hereEnvVariable)

    def run(self, environment, verbose=True):
        if env := xenv.environmentActive():
            xenv.error(f'Environment "{env}" is already loaded', 1)

        if not xenv.environmentExists(environment):
            xenv.error(f'Environment "{environment}" not found', 1)

        xenv.variable(constants.activeEnvironmentVariable, environment)

        self._load_environment()

        if verbose:
            print()
            print(f'Environment "{environment}" loaded')

    def _load_environment(self):
        xenv.forEachPlugin(lambda p: safecall(p, 'load'))

        module = xenv.environmentModule()

        safecall(module, 'load')
