import xenv
import os
import logger_wrapper
from xenv.pluggable import safecall

logger = logger_wrapper.get(__name__)


def commands():
    return [Create]


ARCHETYPE_MINIMAL = 'minimal'


def keyvalue(raw):
    sepIndex = raw.index('=') or raw.index(':')

    return raw[:sepIndex], raw[sepIndex + 1:]


class Create():
    name = 'create'

    @staticmethod
    def cmdline_switch(parserbuilder):
        with parserbuilder.add_command(Create.name) as b:
            b.add_argument('--archetype', default=ARCHETYPE_MINIMAL)
            b.add_argument('--param',
                           '-p',
                           type=keyvalue,
                           action='append',
                           default=[])
            b.add_argument('--description')
            b.add_argument('--base-folder')
            b.add_argument('name')

    def run(self, name, description, archetype, param, base_folder):
        if xenv.environmentExists(name):
            xenv.error(f'Environment already exists: {name}', 1)

        if not xenv.archetypeExists(archetype):
            xenv.error(f'Archetype not found: {archetype}')

        # TODO Check if environment is not __here_env__
        print(f'Creating environment "{name}"...')

        if description:
            print(f'With description "{description}"...')

        if archetype:
            print(f'With archetype "{archetype}"...')

        configs = {
            'environment': name,
            'description': description or f'Description of {name} project',
            'base_folder': base_folder or os.path.join(os.getcwd(), name),
            'archetype': archetype,
        }

        for key, value in param:
            configs[key] = value

        archetypeModule = xenv.archetypeModule(archetype)

        safecall(archetypeModule, 'initialize', xenv.AttrDict(configs))

        print()
        print(f'Environment "{name}" created')
