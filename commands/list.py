from . import constants
import os


def commands():
    return [List]


class List(object):
    name = 'ls'

    @staticmethod
    def cmdline_switch(parserbuilder):
        # TODO ls verbose, should show environments description
        parserbuilder.add_command(List.name)

    def __init__(self, helper):
        self.helper = helper

    def run(self, args):
        active_environment = self.helper.active_environment

        for environment in self.helper.environments():
            print(
                f'{"*" if environment == active_environment else " "} {environment}'
            )

        if active_environment != constants.HERE_ENV and os.path.isdir('.xenv'):
            print(f'  constants.HERE ENV ({os.getcwd()})')
