from . import XEnvException, xenv_home, _visit_environments, \
        _xenv_environment_dir, _xenv_config_file, \
        _get_default_environment_or_active, FileNotFoundException, \
        KeyNotObjectException, KeyNotFoundException, config, Updater, \
        _get_script, _visit_plugins, _invalid_plugin_visitor, \
        check_xenv_launched, check_environment_exists, \
        check_has_environment_not_loaded, has_environment_loaded
import argparse_decorations
from argparse_decorations import helpers, Command, SubCommand, Argument
import logging
import os
import subprocess
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


def _comma_separated_array(raw):
    return raw.split(',')


@Command('load', help='Load a environment')
@Argument('environment', help='Environment name')
@Argument('--flags', '-F', type=_comma_separated_array, default=[], help='Flags for plugins')
def load_handler(environment, flags):
    with Updater.create() as updater:
        check_environment_exists(environment)

        if 'XENV_ENVIRONMENT' in os.environ:
            _do_unload(os.environ['XENV_ENVIRONMENT'], updater)

        _do_load(environment, updater, flags)


def _do_load(environment, updater, flags):
    os.environ['XENV_ENVIRONMENT'] = environment

    from xenv_plugin import base
    base.load(environment, updater, {}, flags)

    _visit_plugins(
        visitor=lambda module, plugin_name, configs:
        _do_load_module(environment, updater, module, configs, flags),
        invalid_plugin_visitor=_invalid_plugin_visitor,
        reverse_plugins=False)


def _do_load_module(environment, updater, module, configs, flags):
    if hasattr(module, 'load'):
        module.load(environment, updater, configs, flags)

    return True


@Command('unload', help='Unload the environment')
def unload_handler():
    with Updater.create() as updater:
        check_has_environment_not_loaded()

        environment = os.environ['XENV_ENVIRONMENT']

        _do_unload(environment, updater)


def _do_unload(environment, updater):
    _visit_plugins(
        visitor=lambda module, name, configs:
        _do_unload_module(environment, updater, module, configs),
        invalid_plugin_visitor=_invalid_plugin_visitor,
        reverse_plugins=True)

    from xenv_plugin import base
    base.unload(environment, updater, {})


def _do_unload_module(environment, updater, module, configs):
    if hasattr(module, 'unload'):
        module.unload(environment, updater, configs)

    return True


@Command('reload', help='Reload current environment')
def reload_handler():
    with Updater.create() as updater:
        environment = os.environ['XENV_ENVIRONMENT']

        check_environment_exists(environment)

        check_has_environment_not_loaded()

        _do_unload(environment, updater)

        _do_load(environment, updater, [])


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
    def visit(env):
        name = env['project']['name']

        if filter in name:
            print(name)

        return True

    _visit_environments(visit)


def _list_complete(selected_columns, filter):
    def _remote_getter(data):
        path = os.path.expanduser(data['project']['path'])

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

    def visit(env_data):
        project_name = env_data['project']['name']
        if filter not in project_name:
            return True

        line = list()

        for column in columns:
            cell = column['getter'](env_data)
            line.append(cell)
            if (cell_len := len(cell)) > column['max_length']:
                column['max_length'] = cell_len

        data.append(line)

        return True

    _visit_environments(visit)

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
    check_xenv_launched()

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
    try:
        value = config(*args, **kwargs)
    except FileNotFoundException as e:
        sys.stderr.write(e.message() + '\n')
        return 1
    except KeyNotFoundException as e:
        sys.stderr.write(e.message() + '\n')
        return 2
    except KeyNotObjectException as e:
        sys.stderr.write(e.message() + '\n')
        return 3

    if isinstance(value, dict):
        print(yaml.dump(value), end='')
    elif isinstance(value, list):
        for item in value:
            print(f'- {item}')
    elif value is None:
        print('null')
    else:
        print(str(value), end='')


@Command('config')
@SubCommand('edit', help='Edit configuration file with default editor')
def config_edit_handler(source=None, scope='environment'):
    source = _get_default_environment_or_active(source)

    # FIXME Probably not working any more
    config_file_name = _xenv_config_file(source, scope)

    if 'EDITOR' not in os.environ:
        raise XEnvException('EDITOR variable doesnt exists')

    editor = os.environ['EDITOR']

    subprocess.run([editor, config_file_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@Command('config')
@SubCommand('path', help='Get configuration file path')
def config_file_path_handler(source=None, scope='environment'):
    _logger.info(f'Getting config file path for "{source}" '
                 f'({scope})')

    source = _get_default_environment_or_active(source)

    # FIXME Probably not working any more
    config_file_name = _xenv_config_file(source, scope)

    print(config_file_name)


def has_for_active():
    return 'XENV_FOR_PROJECT_LIST' in os.environ


def assure_has_no_for_active():
    if has_for_active():
        raise XEnvException('For loop already active')


def assure_has_for_active():
    if not has_for_active():
        raise XEnvException('No for loop active')


@Command('for', help='Loop commands')
@SubCommand('start', help='Start a for loop (nesting not allowed)')
# TODO
# @Argument('--names', '-n', type=_comma_separated_array,
#           help='Environment names to iterate over')
@Argument('--tags', '-t', type=_comma_separated_array, help='Iterate over ' +
          'all environments marked with one or more tags')
def for_start_handler(tags):
    assure_has_no_for_active()

    def _selected(env):
        env_tags = env['project'].get('tags', [])
        for tag in tags:
            if tag in env_tags:
                return True

        return False

    envs = list()

    def _visitor(env):
        if _selected(env):
            envs.append(env['project']['name'])

        return True

    _visit_environments(_visitor)

    if len(envs) == 0:
        raise XEnvException('No environments found matching criteria')

    with Updater.create() as updater:
        # FIXME Escape environment names
        updater.export('XENV_FOR_PROJECT_LIST', ' '.join(envs))
        updater.export('XENV_FOR_CURRENT_INDEX', 1)

        if has_environment_loaded():
            _do_unload(os.environ['XENV_ENVIRONMENT'], updater)

        _do_load(envs[0], updater, ['loop', 'quick'])


def for_has_next(envs, index):
    return index <= len(envs)


@Command('for')
@SubCommand('has-next', help='Check if there is more environments to loop on')
def for_has_next_handler():
    assure_has_for_active()

    envs = os.environ['XENV_FOR_PROJECT_LIST'].split(' ')
    index = int(os.environ['XENV_FOR_CURRENT_INDEX'])

    has_next = for_has_next(envs, index)

    if has_next:
        return 0
    else:
        return 1


@Command('for')
@SubCommand('next', help='Go to next project in loop')
def for_next_handler():
    assure_has_for_active()

    envs = os.environ['XENV_FOR_PROJECT_LIST'].split(' ')
    index = int(os.environ['XENV_FOR_CURRENT_INDEX'])

    if not for_has_next(envs, index):
        raise XEnvException('No next environment')

    index += 1

    with Updater.create() as updater:
        if has_environment_loaded():
            _do_unload(os.environ['XENV_ENVIRONMENT'], updater)

        updater.export('XENV_FOR_CURRENT_INDEX', index)

        _do_load(envs[index], updater, ['loop', 'quick'])


@Command('for')
@SubCommand('break', help='Stop for iteration')
def for_break_handler():
    assure_has_for_active()

    with Updater.create() as updater:
        if has_environment_loaded():
            _do_unload(os.environ['XENV_ENVIRONMENT'], updater)

        updater.unset('XENV_FOR_PROJECT_LIST', 'XENV_FOR_CURRENT_INDEX')


argparse_decorations.make_verbosity_argument()


metadata = helpers.Metadata(__package__)
argparse_decorations.make_version_command(metadata.load())


def main():
    return argparse_decorations.parse_and_run()


if __name__ == '__main__':
    import sys
    sys.exit(main())
