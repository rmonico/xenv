from .command import Command
import logger_wrapper
import os

logger = logger_wrapper.get(__name__)


def commands():
    return [Remove]


class Remove(Command):
    name = 'remove'

    @staticmethod
    def cmdline_switch(parserbuilder):
        with parserbuilder.add_command(Remove.name) as parserbuilder:
            parserbuilder.add_argument('name')

    def __init__(self, helper):
        self.helper = helper

    def run(self, args):
        logger.info(f'Removing environment "{args.name}"')

        # FIXME Não funciona com links
        import shutil
        shutil.rmtree(self.helper.environmentfolder(args.name))

        print(f'Environment "{args.name}" removed')
