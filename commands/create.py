from . import constants
import os
import logger_wrapper

logger = logger_wrapper.get(__name__)


def commands():
    return [Create]


ARCHETYPE_MINIMAL = 'minimal'


class Create():
    name = 'create'

    @staticmethod
    def cmdline_switch(parserbuilder):
        with parserbuilder.add_command(Create.name) as b:
            b.add_argument('--archetype', default=ARCHETYPE_MINIMAL)
            b.add_argument('--description')
            b.add_argument('--base-folder', default=os.getcwd())
            b.add_argument('name')

    def __init__(self, helper):
        self.helper = helper

    def run(self, args):
        # TODO Check if environment is not __here_env__
        logger.info(f'Creating environment "{args.name}"')
        logger.info(f'With description "{args.description}"')
        logger.info(f'With archetype "{args.archetype}"')

        environment_folder = self.helper.environmentfolder(args.name)
        archetype_folder = self.helper.archetypefolder(args.archetype)

        # TODO Check if environment_folder already exists
        os.mkdir(environment_folder)

        # TODO Check if archetype exists

        variables = {
            'name': args.name,
            'description': args.description
            or f'Description of {args.name} project',
            'base_folder': args.base_folder,
        }

        from glob import glob

        for archetype_file_name in glob(archetype_folder + '/*',
                                        recursive=True):
            with open(archetype_file_name, 'r') as archetype_file:
                file_name = os.path.join(environment_folder,
                                         os.path.basename(archetype_file_name))
                # FIXME When archetype has some subfolder it will not create corresponding environment subfolder
                with open(file_name, 'w') as file:
                    while archetype_line := archetype_file.readline():
                        line = archetype_line.format(**variables)

                        file.write(line)

        print(f'Environment "{args.name}" created')
