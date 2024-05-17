#!/usr/bin/python3

from .attrdict import AttrDict
from . import constants
from .plugin import Plugin
import argparse
from argparse_builder import ArgumentParserBuilder
from importlib import import_module
import yaml
import logger_wrapper
import os
import shutil
import sys


class Main(object):
    def run(self):
        self._loadModules()

        args = self._parseArgs()

        logger_wrapper.configure(args.verbosity)

        global logger
        logger = logger_wrapper.get(__name__)

        command_class = self.commands.get(args.command)

        instance = command_class()

        if not instance:
            error(f'Command not found: {args.command}')

        params = dict(args.__dict__)

        params.pop('command')
        params.pop('callback')
        # TODO Não sei se o verbosity deve sair aqui....
        params.pop('verbosity')

        try:
            statusCode = instance.run(**params)
        except XENVCommandException as e:
            print()
            print(e.format())

            return e.errorCode

        if statusCode not in [0, None]:
            return statusCode

        # FIXME Este arquivo deve ser gravado conforme as chamadas forem sendo feitas
        with open(exportScriptFileName(), 'w') as exportFile:
            self._exportVariables(exportFile)
            self._exportUnsetVariables(exportFile)

            self._exportAliases(exportFile)
            self._exportUnaliases(exportFile)

            self._exportFunctions(exportFile)
            self._exportUnsetFunctions(exportFile)

            if newwd:
                exportFile.write(f'cd "{newwd}"\n')

        return 0

    def _loadModules(self):
        from importlib import import_module
        import re

        self.commands = dict()

        from . import commands
        commands_folder = os.path.dirname(commands.__file__)

        for node in os.scandir(commands_folder):
            if re.match(r'^(?!:__).*\.py$', node.name):
                module = import_module('xenv.commands.' + node.name[:-3])

                if hasattr(module, 'commands'):
                    commands = module.commands()
                    for command in commands:
                        if command.name in self.commands:
                            raise Exception(
                                f'Command registered twice: "{command.name}"')
                        self.commands[command.name] = command

    def _parseArgs(self):
        progname = os.path.basename(os.path.dirname(__file__))
        parser = argparse.ArgumentParser(prog=progname)

        with ArgumentParserBuilder(parser) as b:
            for command in self.commands.values():
                command.cmdline_switch(b)

        logger_wrapper.make_verbosity_argument(parser)

        return parser.parse_args()

    def _exportVariables(self, exportFile):
        for name, value in _variables.items():
            exportFile.write(f'export {name}="{value}"\n')

    def _exportUnsetVariables(self, exportFile):
        for variable in _variables_unset:
            exportFile.write(f'unset {variable}\n')

    def _exportAliases(self, exportFile):
        for name, value in _aliases.items():
            exportFile.write(f'alias {name}="{value}"\n')

    def _exportUnaliases(self, exportFile):
        for alias in _unaliases:
            exportFile.write(f'unalias {alias}\n')

    def _exportFunctions(self, exportFile):
        for name, body in _functions.items():
            exportFile.write(self._format_function(name, body))

    def _format_function(self, name, body):
        return '''\
{name}() {{
{body}
}}

'''.format(name=name, body=body)

    def _exportUnsetFunctions(self, exportFile):
        for function in _functions_unset:
            exportFile.write(f'unset -f {function}\n')


def exportScriptFileName():
    return os.environ[constants.exportScriptVariable]


def homeFolder():
    return os.environ[constants.homeVariable]


_variables = dict()
_variables_unset = list()


def variable(name, value):
    _variables[name] = value

    if name in _variables_unset:
        _variables_unset.remove(name)


def variableUnset(name):
    if name in _variables:
        _variables.pop(name)

    _variables_unset.append(name)


_functions = dict()
_functions_unset = list()


def function(name, body):
    _functions[name] = body

    if name in _functions_unset:
        _functions_unset.remove(name)


def functionUnset(name, body=None):
    if name in _functions:
        _functions.pop(name)

    _functions_unset.append(name)


def environmentActive():
    if constants.activeEnvironmentVariable in _variables_unset:
        return None

    return _variables.get(constants.activeEnvironmentVariable,
                          os.environ.get(constants.activeEnvironmentVariable))


def environmentList():
    envFolderLen = len(environmentsFolder()) + 1

    from glob import glob

    globExpr = glob(f'{environmentsFolder()}/*/')

    return [env[envFolderLen:-1] for env in globExpr]


def environmentsFolder():
    return os.path.join(homeFolder(), 'environments')


def environmentFolder(environment=None):
    environment = environment or environmentActive()

    if environment == constants.hereEnvVariable:
        return os.path.join(os.getcwd(), '.xenv')
    else:
        return os.path.join(environmentsFolder(), environment)


def environmentExists(environment=None):
    environment = environment or environmentActive()

    envFolder = environmentFolder(environment)

    return os.path.isdir(envFolder)


def environmentConfigsFilename(environment=None):
    environment = environment or environmentActive()

    return os.path.join(environmentFolder(environment), 'configs.yaml')


def environmentConfigs(environment=None):
    configsFileName = environmentConfigsFilename(environment)

    if os.path.isfile(configsFileName):
        with open(configsFileName) as f:
            return AttrDict(yaml.load(f, Loader=yaml.Loader))
    else:
        return dict()


def forEachPlugin(action, environment=None, plugins=None):
    if plugins:
        pluginList = plugins
    else:
        environment = environment or environmentActive()

        configs = environmentConfigs(environment)

        pluginList = configs.get('plugins', {})

    for pluginName in pluginList:
        plugin = getPlugin(pluginName)

        action(plugin)


def environmentModule(environment=None):
    environment = environment or environmentActive()

    return _loadModule(environmentsFolder(), environment)


_pluginCache = dict()


def getPlugin(pluginName):
    """
    Plugins should always be get from here, they are SingleTones
    """
    return _pluginCache.get(pluginName, _loadPlugin(pluginName))


def _loadPlugin(pluginName):
    return Plugin(_pluginModule(pluginName))


def _pluginModule(pluginName):
    return _loadModule(_pluginsFolder(), pluginName)


def _pluginsFolder():
    return os.path.join(homeFolder(), 'plugins')


def archetypesFolder():
    return os.path.join(homeFolder(), 'archetypes')


def archetypeFolder(archetype):
    return os.path.join(archetypesFolder(), archetype)


def archetypeExists(archetype):
    return os.path.exists(archetypeFolder(archetype))


def archetypeModule(archetype):
    return _loadModule(archetypesFolder(), archetype)


def _loadModule(folder, moduleName):
    sys.path.append(folder)
    module = import_module(moduleName)
    sys.path.pop()

    return module


class XENVCommandException(Exception):
    def __init__(self, message, errorCode):
        super().__init__(message)
        self.message = message
        self.errorCode = errorCode

    def format(self):
        return f'ERROR: {self.message}'


class XENVDependencyNotFoundException(Exception):
    def __init__(self, dependency):
        super().__init__(f'Dependency "{dependency}" not found')


def error(*args, **kwargs):
    raise XENVCommandException(*args, **kwargs)


newwd = None


def setcwd(_newwd):
    global newwd
    newwd = _newwd


_aliases = dict()
_unaliases = list()


def alias(name, value):
    _aliases[name] = value


def unalias(name):
    _unaliases.append(name)


def checkDependency(dependency):
    if not shutil.which(dependency):
        raise XENVDependencyNotFoundException(dependency)


def registerHelp():
    body = f'''
        export initial_pythonpath="$PYTHONPATH"
        export PYTHONPATH="$PYTHONPATH:{os.path.join(homeFolder(), 'python')}"
        python -c "from commands.load import Load; Load().environment_help()"
        export PYTHONPATH="$initial_pythonpath"'''

    function('help', body)


registerHelp()
