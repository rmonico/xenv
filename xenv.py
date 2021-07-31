#!/usr/bin/python3

import argparse
from argparse_builder import ArgumentParserBuilder
import os
import shutil
import sys
import logger_wrapper

XENV_HOME = os.environ['XENV_HOME']
XENV_ENVIRONMENTS = f'{XENV_HOME}/environments'
HERE_ENV = '__here_env__'


class Main(object):
    def run(self):
        args = self._parse_args()

        if args.command == 'ls':
            trailing_chars = len(XENV_ENVIRONMENTS) + 1

            from glob import glob

            print('Available environments:')
            print()
            [
                print(environment[trailing_chars:-1])
                for environment in glob(f'{XENV_ENVIRONMENTS}/*/')
            ]
            # TODO Show a HERE_ENV if it exists in current directory

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

        else:
            self._error(f'Command not implemented yet: {args.command}')

    def _parse_args(self):
        '''
        reference: https://docs.python.org/3/library/argparse.html
        '''
        parser = argparse.ArgumentParser()

        parser.add_argument('--source-files-dir',
                            help='Source files directory (internal use only)')

        with ArgumentParserBuilder(parser) as b:
            b.add_command('ls')
            with b.add_command('load') as b:
                b.add_argument('environment', default=HERE_ENV)
            b.add_command('unload')  # alias: off (TODO)
            b.add_command('reload')

            # TODO
            # b.add_command('info')
        logger_wrapper.make_verbosity_argument(parser)

        return parser.parse_args()

    @staticmethod
    def _error(message):
        print(message)
        sys.exit(1)

    def _load(self, environment, source_files_dir, force):
        if not force and self._xenv_has_loaded_environment():
            self._error('Xenv environment already loaded')

        if not os.path.isdir(self._environmentdir(environment)):
            self._error(f'Environment "{environment}" not found')

        source = os.path.join(self._environmentdir(environment), 'load')

        if not os.path.exists(source):
            self._error(
                f'Environment "{environment}" has no load script, aborting')

        self._append_to_export_file(source_files_dir, source)

        print(f'Environment "{environment}" loaded')

        return 0

    def _unload(self, source_files_dir):
        if not self._xenv_has_loaded_environment():
            self._error('No xenv environment loaded')

        environment = os.environ['XENV_ACTIVE_ENVIRONMENT']

        source = os.path.join(self._environmentdir(environment), 'unload')

        if not os.path.exists(source):
            self._error(
                f'Environment "{environment}" has no unload script, aborting')

        self._append_to_export_file(source_files_dir, source)

        print(f'Environment "{environment}" unloaded')

        return 0

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
