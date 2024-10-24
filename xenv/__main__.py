from . import XEnvException, xenv_home, _xenv_environments, \
        _xenv_environment_dir, _xenv_config_file, \
        _get_default_environment_or_active, config, Updater, Loader, \
        Unloader, _get_script, _visit_plugins, _no_plugin_visitor
import xenv
import argparse_decorations
from argparse_decorations import Command, SubCommand, Argument
import logging
import os
import yaml


argparse_decorations.init()


_logger = logging.getLogger(__name__)
# _logger.setLevel(logging.DEBUG)


@Command('launch-zsh', help='Print the launch script for ZSH')
def launch_handler_handler():
    # TODO Autodetect shell
    launch_script_name = _get_script('launch.zsh')
    with open(launch_script_name) as launch_file:
        print(launch_file.read(), end='')

    if 'XENV_HOME' not in os.environ:
        print()
        print(f'export XENV_HOME="{xenv_home()}"')


# TODO Move to init
def _check_xenv_launched():
    if 'XENV_UPDATE' not in os.environ:
        raise XEnvException(
                'xenv not launched. Run \'eval "$(xenv launch-zsh)"\'')

    global xenv_update

    xenv_update = os.environ['XENV_UPDATE']


# TODO Move this method and next one to init
def _load_plugin(plugin_name, configs):
    if len(Loader._handlers) == 0:
        _logger.debug(f'Plugin "{plugin_name}" has no "loader" '
                      'defined')

    for loader in Loader._handlers:
        loader()


@Command('load', help='Load a environment')
@Argument('environment', help='Environment name')
def load_handler(environment):
    _check_xenv_launched()

    with open(xenv_update, 'w') as update_file:
        xenv.updater = Updater(update_file)

        os.environ['XENV_ENVIRONMENT'] = environment

        _visit_plugins(
            pre_visitor=lambda *args: Loader._reset(),
            visitor=_load_plugin,
            no_plugin_visitor=_no_plugin_visitor)


# TODO Move to init
def _check_has_environment_loaded():
    _check_xenv_launched()

    if 'XENV_ENVIRONMENT' not in os.environ:
        raise XEnvException('No environment loaded')


# TODO Move this method and next one to init
def _unload_plugin(plugin_name, configs):
    if len(Unloader._handlers) == 0:
        _logger.debug(f'Plugin "{plugin_name}" has no "unloader" '
                      'defined')

    for unloader in Unloader._handlers:
        unloader()


@Command('unload', help='Unload the environment')
def unload_handler():
    _check_has_environment_loaded()

    with open(xenv_update, 'w') as update_file:
        xenv.updater = Updater(update_file)

        _visit_plugins(
            pre_visitor=lambda *args: Unloader._reset(),
            visitor=_unload_plugin,
            no_plugin_visitor=_no_plugin_visitor)


def _columns(raw):
    choices = ['name', 'description', 'path', 'tags', 'plugins', 'remote']

    parsed = raw.split(',')

    for col in parsed:
        if col not in choices:
            from argparse import ArgumentTypeError
            raise ArgumentTypeError(f'"{col}" must be in: {", ".join(choices)}')

    return parsed


@Command('list', aliases=['ls'], help='List environments')
@Argument('--raw', '-r', action='store_true', help='Print just the environment'
          ' names')
@Argument('--columns', type=_columns, default=['name', 'description', 'path'],
          # choices=['name', 'description', 'path', 'tags', 'plugins', 'remote'],
          help='Select columns to print (default: name,description,path other '
          'possible columns: tags,plugins,remote)')
@Argument('filter', default='', nargs='?', help='Filter projects by name')
def list_handler(raw, columns, filter):
    if raw:
        _list_raw(filter)
    else:
        _list_complete(columns, filter)


def _list_raw(filter):
    for environment in _xenv_environments():
        project_name = environment['project']['name']
        if filter in project_name:
            print(project_name)


def _list_complete(selected_columns, filter):
    def _remote_getter(data):
        path = os.path.expanduser(data['project']['path'])

        import subprocess
        process = subprocess.run('git remote -v'.split(' '), cwd=path,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

        stdout = process.stdout.decode()
        import re
        match = re.search(r'[a-z]+\t(.*) \(fetch\)', stdout)

        if not match:
            return ''

        remote = match.groups()[0]

        return remote

    available_columns = [
            {
                'title': 'Name',
                'name': 'name',
                'getter': lambda data: data['project']['name'],
                'max_length': 4
            },
            {
                'title': 'Description',
                'name': 'description',
                'getter': lambda data: data['project'].get('description', ''),
                'max_length': 11
            },
            {
                'title': 'Path',
                'name': 'path',
                'getter': lambda data: data['project']['path'],
                'max_length': 4
            },
            {
                'title': 'Tags',
                'name': 'tags',
                'getter': lambda data: ', '.join(data['project'].get('tags', [])),
                'max_length': 4
            },
            {
                'title': 'Plugins',
                'name': 'plugins',
                'getter': lambda data: ', '.join(data.get('plugins', {}).keys()),
                'max_length': 7
            },
            {
                'title': 'Remote',
                'name': 'remote',
                'getter': _remote_getter,
                'max_length': 6
            },
        ]

    columns = list()

    for sel_column in selected_columns:
        for avail_column in available_columns:
            if sel_column == avail_column['name']:
                columns.append(avail_column)

    data = list()
    data.append([column['title'] for column in columns])

    for env_data in _xenv_environments():
        project_name = env_data['project']['name']
        if filter not in project_name:
            continue
        line = list()
        for column in columns:
            cell = column['getter'](env_data)
            line.append(cell)
            if (cell_len := len(cell)) > column['max_length']:
                column['max_length'] = cell_len

        data.append(line)

    for data_line in data:
        line = ''
        for i, column in enumerate(columns):
            line += data_line[i]
            line += ' ' * (column['max_length'] - len(data_line[i]))
            line += '    '

        print(line)


@Command('create', help='Create a environment')
@Argument('name', help='Environment name')
@Argument('path', help='Environment path')
@Argument('--description', '-d', help='Environment description')
@Argument('--tags', '-t', type=lambda raw: raw.split(','),
          help='Tag list (comma separated)')
@Argument('--plugins', '-p', type=lambda raw: raw.split(','),
          help='Plugin list to be installed')
def create_handler(name, path, description, tags, plugins):
    _check_xenv_launched()

    # TODO Move this logic to init
    import os

    env_dir = _xenv_environment_dir(name)
    _logger.debug('Creating environment dir at "%s"', env_dir)
    os.makedirs(env_dir, exist_ok=True)

    config = {
            'project': {
                'name': name,
                'path': path,
                },
            }

    if description:
        config['project']['description'] = description

    if tags:
        config['project']['tags'] = tags

    if plugins:
        _plugins = dict()
        for plugin in plugins:
            _plugins[plugin] = True

        config['plugins'] = _plugins

    config_file_name = _xenv_config_file(name, 'environment')
    _logger.debug('Creating config file at "%s"', config_file_name)

    with open(config_file_name, 'w') as config_file:
        yaml.dump(config, config_file)

    _logger.debug('Creating project dir at "%s"', path)

    os.makedirs(path, exist_ok=True)

    print(f'Environment "{name}" created successfully!')


@Command('config', help='Configuration management')
@Argument('--source', help='Override active environment (if scope is '
          'environment) or define a plugin name (if scope is defined as), '
          'ignored for scope global')
@Argument('--scope', '-s', choices=['environment', 'plugin', 'global'],
          default='environment', help='Define scope, one of "environment", '
          '"plugin" or "global"')
@SubCommand('get', help='Get a configuration entry')
@Argument('entry_path', help='Entry to get')
def config_handler(*args, **kwargs):
    value = config(*args, **kwargs)

    if isinstance(value, dict):
        print(yaml.dump(value), end='')
    else:
        if value:
            print(str(value), end='')


@Command('config')
@SubCommand('path', help='Get configuration file path')
def config_file_path_handler(environment=None, _global=False):
    _logger.info(f'Getting config file path for environment "{environment}" '
                 f'({"" if _global else "non "}globally)')

    environment = _get_default_environment_or_active(environment)

    # FIXME Probably not working any more
    config_file_name = _xenv_config_file(environment, _global)

    print(config_file_name)


argparse_decorations.make_verbosity_argument()


def _get_version():
    from importlib import resources
    return resources.files('xenv').joinpath('__version__').read_text()


argparse_decorations.make_version_command(_get_version())


def main():
    argparse_decorations.parse_and_run()


if __name__ == '__main__':
    main()
