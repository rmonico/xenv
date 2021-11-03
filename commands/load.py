from . import constants
import os


def commands():
    return [Load]


class Load():
    name = 'load'

    @staticmethod
    def cmdline_switch(parserbuilder):
        with parserbuilder.add_command(Load.name) as b:
            b.add_argument('environment', default=constants.HERE_ENV)

    def __init__(self, helper):
        self.helper = helper

    def run(self, args, force=False):
        if not force and self.helper.is_some_enviroment_loaded():
            self.helper._error(
                f'Xenv environment "{os.environ["XENV_ACTIVE_ENVIRONMENT"]}" is already loaded'
            )

        environment_folder = self.helper.environmentfolder(args.environment)

        if not os.path.isdir(environment_folder):
            self.helper._error(f'Environment "{args.environment}" not found')

        self.helper.copy_to_export_folder('pythonbinder')

        if not self.helper.copy_to_export_folder('load', environment=args.environment):
            self.helper._error(
                f'Environment "{args.environment}" has no load script, aborting')

        configs = self.helper.configs(args.environment)

        # TODO Improve it: plugin should receive parameters, start and stop should be in different files. Should support abort during load.
        self._append_plugins(output_files_dir, configs.get('plugins', []))

        print(f'Environment "{environment}" loaded')

        return 0
