import logger_wrapper
import os
import shutil
import xenv
from xenv.pluggable import safecall

logger = logger_wrapper.get(__name__)


def commands():
    return [Remove]


class Remove():
    name = 'remove'

    @staticmethod
    def cmdline_switch(parserbuilder):
        with parserbuilder.add_command(Remove.name) as parserbuilder:
            parserbuilder.add_argument('environment')

    def run(self, environment):
        if not xenv.environmentExists(environment):
            xenv.error(f'Environment "{environment}" doesnt exists')

        if xenv.environmentActive() == environment:
            xenv.error(
                f'Environment "{environment}" is active, unload it first')

        logger.info(f'Removing environment "{environment}"...')

        configs = xenv.environmentConfigs(environment)

        archetypeModule = xenv.archetypeModule(configs.archetype)

        safecall(archetypeModule, 'finalize', environment)

        print(f'Environment "{environment}" removed')
