from . import XEnvException, xenv_home, _xenv_environments_dir, \
        _xenv_environment_dir, _xenv_config_file, _logger, \
        _get_default_environment_or_active, config, Updater, Loader, \
        Unloader, _get_script, _visit_plugins, _no_plugin_visitor
import xenv
import argparse_decorations
from argparse_decorations import Command, SubCommand, Argument
import logging
import os
import yaml


argparse_decorations.init()

argparse_decorations.make_verbosity_argument()


@Command('launch-zsh', help='Print the launch script for ZSH')
def launch_handler_handler():
    # TODO Autodetect shell
    launch_script_name = _get_script('launch.zsh')
    with open(launch_script_name) as launch_file:
        print(launch_file.read(), end='')

    if 'XENV_HOME' not in os.environ:
        print()
        print(f'export XENV_HOME="{xenv_home()}"')


def _check_xenv_launched():
    if 'XENV_UPDATE' not in os.environ:
        raise XEnvException(
                'xenv not launched. Run \'eval "$(xenv launch-zsh)"\'')

    global xenv_update

    xenv_update = os.environ['XENV_UPDATE']


def _load_plugin(plugin_name, configs):
    if len(Loader._handlers) == 0:
        logging.warning(f'Plugin "{plugin_name}" has no "loader" '
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


def _check_has_environment_loaded():
    _check_xenv_launched()

    if 'XENV_ENVIRONMENT' not in os.environ:
        raise XEnvException('No environment loaded')


def _unload_plugin(plugin_name, configs):
    if len(Unloader._handlers) == 0:
        logging.warning(f'Plugin "{plugin_name}" has no "unloader" '
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


def _xenv_environments():
    for entry in os.scandir(_xenv_environments_dir()):
        if entry.is_dir():
            yield entry.name


@Command('list', aliases=['ls'], help='List environments')
def list_handler():
    for environment in _xenv_environments():
        print(environment)


@Command('create', help='Create a environment')
@Argument('name', help='Environment name')
@Argument('path', help='Environment path')
@Argument('--plugins', '-p', type=lambda raw: raw.split(','), default=[],
          help='Plugin list to be installed')
def create_handler(name, path, plugins):
    _check_xenv_launched()

    import os

    env_dir = _xenv_environment_dir(name)
    env_bin = os.path.join(env_dir, 'bin')
    os.makedirs(env_bin, exist_ok=True)

    config = {
            'project': {
                'name': name,
                'path': path,
                }
            }

    with open(_xenv_config_file(name), 'w') as config_file:
        yaml.dump(config, config_file)


@Command('config', help='Configuration management')
@Argument('--source', help='Override active environment (if scope is '
          'environment) or define a plugin name (if scope is defined as), '
          'ignored for scope global')
@Argument('--scope', '-s', choices=['environment', 'plugin', 'global'], default='environment', help='Define scope, one of "environment", "plugin" '
          'or "global"')
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

    config_file_name = _xenv_config_file(environment, _global)

    print(config_file_name)


def main():
    argparse_decorations.parse_and_run()


if __name__ == '__main__':
    main()
