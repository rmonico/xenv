#!/usr/bin/python3

import sys
import os
import shutil

XENV_HOME = os.environ['XENV_HOME']
XENV_ENVIRONMENTS = f'{XENV_HOME}/environments'
HERE_ENV = '__here_env__'


class Main(object):
    def __init__(self, args):
        self.args = self._parse_args(args)

    def _parse_args(self, args):
        parsed = {}

        while len(args) > 0:
            if args[0] == '--source-files-dir':
                parsed['output_files_dir'] = args[1]

                self._shift(args, 2)

            elif args[0] == 'ls':
                parsed['command'] = 'ls'

                args = {}
            elif args[0] == 'load':
                parsed['command'] = 'load'
                parsed['environment'] = args[1] if len(args) > 1 else HERE_ENV

                self._shift(args, 2)
            elif args[0] == 'off':
                parsed['command'] = 'off'

                self._shift(args, 1)
            elif args[0] == 'reload':
                parsed['command'] = 'reload'

                self._shift(args, 1)
            else:
                self._error('XENV: Command not found: "' + '" "'.join(args) + '"')

        return parsed

    @staticmethod
    def _shift(args, count=1):
        for i in range(count):
            if len(args) == 0:
                return

            args.pop(0)

    @staticmethod
    def _error(message):
        print(message)
        sys.exit(1)

    def run(self):
        if self.args['command'] == 'ls':
            trailing_chars = len(XENV_ENVIRONMENTS) + 1

            from glob import glob

            print('Available environments:')
            print()
            [
                print(environment[trailing_chars:-1])
                for environment in glob(f'{XENV_ENVIRONMENTS}/*/')
            ]
            # TODO Show a HERE_ENV if it exists in current directory

        if self.args['command'] == 'load':
            return self._load(self.args['environment'], force=False)

        elif self.args['command'] == 'off':
            return self._unload()

        elif self.args['command'] == 'reload':
            unload_status = self._unload()

            if unload_status == 0:
                return self._load(os.environ['XENV_ACTIVE_ENVIRONMENT'],
                            force=True)
            else:
                return unload_status

    def _load(self, environment, force):
        if not force and self._xenv_has_loaded_environment():
            self._error('Xenv environment already loaded')

        if not os.path.isdir(self._environmentdir(environment)):
            self._error(f'Environment "{environment}" not found')

        source = os.path.join(self._environmentdir(environment), 'load')

        if not os.path.exists(source):
            self._error(f'Environment "{environment}" has no load script, aborting')

        self._append_to_export_file(source)

        print(f'Environment "{environment}" loaded')

        return 0

    def _unload(self):
        if not self._xenv_has_loaded_environment():
            self._error('No xenv environment loaded')

        environment = os.environ['XENV_ACTIVE_ENVIRONMENT']

        source = os.path.join(self._environmentdir(environment), 'unload')

        if not os.path.exists(source):
            self._error(
                f'Environment "{environment}" has no unload script, aborting')

        self._append_to_export_file(source)

        print(f'Environment "{environment}" unloaded')

        return 0

    def _xenv_has_loaded_environment(self):
        return 'XENV_ACTIVE_ENVIRONMENT' in os.environ

    def _environmentdir(self, environment):
        if environment == HERE_ENV:
            return os.path.join(os.getcwd(), '.xenv')
        else:
            return os.path.join(XENV_ENVIRONMENTS, environment)

    def _append_to_export_file(self, filename):
        if not 'output_files_dir' in args:
            error('--source-files-dir not informed')
        else:
            output_files_dir = args['output_files_dir']

        dest = os.path.join(output_files_dir, 'xenv.environment')

        with open(dest, 'a') as environmentfile:
            with open(filename, 'r') as source:
                while line := source.readline():
                    environmentfile.write(line)


main = Main(sys.argv[1:])

sys.exit(main.run())

