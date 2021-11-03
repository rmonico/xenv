#!/usr/bin/python3

import argparse
from argparse_builder import ArgumentParserBuilder
from commands.helper import Helper
import os
import shutil
import sys
import logger_wrapper


class Main(object):
    def run(self):
        self._load_modules()

        args = self._parse_args()

        logger_wrapper.configure(args.verbosity)

        global logger
        logger = logger_wrapper.get(__name__)

        command_class = self.commands.get(args.command)

        instance = command_class(Helper(args.source_files_dir))

        if instance:
            status_code = instance.run(args)
        else:
            Helper._error(f'Command not found: {args.command}')
            status_code = 1

        return status_code

    def _load_modules(self):
        from importlib import import_module
        import re

        self.commands = dict()

        import commands
        commands_folder = os.path.dirname(commands.__file__)

        for node in os.scandir(commands_folder):
            if re.match('^(?!:__).*\.py$', node.name):
                module = import_module('commands.' + node.name[:-3])

                if hasattr(module, 'commands'):
                    commands = module.commands()
                    for command in commands:
                        if command.name in self.commands:
                            raise Exception(
                                f'Command registered twice: "{command.name}"')
                        self.commands[command.name] = command

    def _parse_args(self):
        '''
        reference: https://docs.python.org/3/library/argparse.html
        '''
        parser = argparse.ArgumentParser()

        parser.add_argument('--source-files-dir',
                            help='Source files directory (internal use only)')

        with ArgumentParserBuilder(parser) as b:
            for command in self.commands.values():
                command.cmdline_switch(b)

        logger_wrapper.make_verbosity_argument(parser)

        return parser.parse_args()

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


main = Main()

sys.exit(main.run())
