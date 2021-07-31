#!/usr/bin/python3

import argparse
from argparse_builder import ArgumentParserBuilder
import os
import shutil
import sys
import logger_wrapper

XENV_HOME = os.environ['XENV_HOME']
XENV_ENVIRONMENTS = f'{XENV_HOME}/environments'
# If a folder has a .xenv subfolder its considered a xenv "HERE_ENV" environment
HERE_ENV = '__here_env__'
ARCHETYPE_MINIMAL = 'minimal'
XENV_ARCHETYPES = f'{XENV_HOME}/archetypes'


class Main(object):
    def _parse_args(self):
        '''
        reference: https://docs.python.org/3/library/argparse.html
        '''
        parser = argparse.ArgumentParser()

        parser.add_argument('--source-files-dir',
                            help='Source files directory (internal use only)')

        with ArgumentParserBuilder(parser) as b:
            # TODO ls verbose, should show environments description
            b.add_command('ls')
            with b.add_command('load') as b:
                b.add_argument('environment', default=HERE_ENV)
            b.add_command('unload')  # alias: off (TODO)
            b.add_command('reload')
            with b.add_command('create') as b:
                b.add_argument('--archetype', default=ARCHETYPE_MINIMAL)
                b.add_argument('--description')
                b.add_argument('--base_folder', default=os.getcwd())
                b.add_argument('name')
            with b.add_command('remove') as b:
                b.add_argument('name')

        logger_wrapper.make_verbosity_argument(parser)

        return parser.parse_args()

    def run(self):
        args = self._parse_args()

        logger_wrapper.configure(args)

        global logger
        logger = logger_wrapper.get(__name__)

        if args.command == 'ls':
            trailing_chars = len(XENV_ENVIRONMENTS) + 1

            from glob import glob

            environments = [
                environment[trailing_chars:-1]
                for environment in glob(f'{XENV_ENVIRONMENTS}/*/')
            ]

            active_environment = os.environ.get('XENV_ACTIVE_ENVIRONMENT', '')

            for environment in environments:
                print(f'{"*" if environment == active_environment else " "} {environment}')

            if active_environment != HERE_ENV and os.path.isdir('.xenv'):
                print(f'  HERE ENV ({os.getcwd()})')

        elif args.command == 'load':
            return self._load(args.environment,
                              args.source_files_dir,
                              force=False)

        elif args.command == 'unload':
            return self._unload(args.source_files_dir)

        elif args.command == 'reload':
            unload_status = self._unload(args.source_files_dir)

            if unload_status == 0:
                return self._load(os.environ['XENV_ACTIVE_ENVIRONMENT'],
                                  args.source_files_dir,
                                  force=True)
            else:
                return unload_status

        elif args.command == 'create':
            # TODO Check if environment is not __here_env__
            logger.info(f'Creating environment "{args.name}"')
            logger.info(f'With description "{args.description}"')
            logger.info(f'With archetype "{args.archetype}"')

            environment_folder = os.path.join(XENV_ENVIRONMENTS, args.name)
            archetype_folder = os.path.join(XENV_ARCHETYPES, args.archetype)

            # TODO Check if environment_folder already exists
            os.mkdir(environment_folder)

            # TODO Check if archetype exists

            variables = {
                'name': args.name,
                'description': args.description or f'Description of {args.name} project',
                'base_folder': args.base_folder,
            }

            from glob import glob

            for archetype_file_name in glob(archetype_folder + '/*', recursive=True):
                with open(archetype_file_name, 'r') as archetype_file:
                    file_name = os.path.join(environment_folder, os.path.basename(archetype_file_name))
                    # FIXME When archetype has some subfolder it will not create corresponding environment subfolder
                    with open(file_name, 'w') as file:
                        while archetype_line := archetype_file.readline():
                            line = archetype_line.format(**variables)

                            file.write(line)

            print(f'Environment "{args.name}" created')

        elif args.command == 'remove':
            logger.info(f'Removing environment "{args.name}"')
            environment_folder = os.path.join(XENV_ENVIRONMENTS, args.name)

            import shutil
            shutil.rmtree(environment_folder)

            print(f'Environment "{args.name}" removed')

        else:
            self._error(f'Command not implemented yet: {args.command}')

    @staticmethod
    def _error(message):
        print(message)
        sys.exit(1)

    def _load(self, environment, output_files_dir, force):
        if not force and self._xenv_has_loaded_environment():
            self._error(
                f'Xenv environment "{os.environ["XENV_ACTIVE_ENVIRONMENT"]}" is already loaded'
            )

        if not os.path.isdir(self._environmentdir(environment)):
            self._error(f'Environment "{environment}" not found')

        source = os.path.join(self._environmentdir(environment), 'load')

        if not os.path.exists(source):
            self._error(
                f'Environment "{environment}" has no load script, aborting')

        self._append_to_export_file(output_files_dir, source)

        configs = self._load_configs(environment)

        self._append_plugins(output_files_dir, configs.get('plugins', []))

        print(f'Environment "{environment}" loaded')

        return 0

    def _unload(self, output_files_dir):
        if not self._xenv_has_loaded_environment():
            self._error('No xenv environment loaded')

        environment = os.environ['XENV_ACTIVE_ENVIRONMENT']

        source = os.path.join(self._environmentdir(environment), 'unload')

        if not os.path.exists(source):
            self._error(
                f'Environment "{environment}" has no unload script, aborting')

        self._append_to_export_file(output_files_dir, source)

        configs = self._load_configs(environment)

        self._append_plugins(output_files_dir, configs.get('plugins', []))

        print(f'Environment "{environment}" unloaded')

        return 0

    def _append_plugins(self, output_files_dir, plugins):
        scripts_extension = os.path.basename(os.environ['SHELL'])

        for plugin in plugins:
            self._append_plugin(output_files_dir, plugin, scripts_extension)

    def _append_plugin(self, output_files_dir, plugin_name, scripts_extension):
        global logger

        logger.info(f'Appending plugin {plugin_name}')

        source = os.path.join(XENV_HOME, 'plugins',
                              f'{plugin_name}.{scripts_extension}')

        if not os.path.exists(source):
            logger.warning(f'Plugin "{plugin_name}" not found')

            return

        logger.debug(f'Appending plugin on file: {source}')

        self._append_to_export_file(output_files_dir, source)

    def _load_configs(self, environment):
        yaml_file_name = os.path.join(self._environmentdir(environment),
                                      'configs.yaml')

        if not os.path.exists(yaml_file_name):
            return {}

        with open(yaml_file_name, 'r') as yaml_file:
            import yaml
            return yaml.safe_load(yaml_file)

    def _xenv_has_loaded_environment(self):
        return 'XENV_ACTIVE_ENVIRONMENT' in os.environ

    def _environmentdir(self, environment):
        if environment == HERE_ENV:
            return os.path.join(os.getcwd(), '.xenv')
        else:
            return os.path.join(XENV_ENVIRONMENTS, environment)

    def _append_to_export_file(self, output_files_dir, filename):
        dest = os.path.join(output_files_dir, 'xenv.environment')

        with open(dest, 'a') as environmentfile:
            with open(filename, 'r') as source:
                while line := source.readline():
                    environmentfile.write(line)


main = Main()

sys.exit(main.run())
