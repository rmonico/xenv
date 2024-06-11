from . import XEnvException, _xenv_home, _environment_activate_script, \
    _xenv_environments_dir, _xenv_environment_dir, \
    _xenv_environment_config_file, _logger, _get_default_environment_or_active, \
    config
import argparse_decorations
from argparse_decorations import Command, SubCommand, Argument
from importlib import resources
import os
import yaml


argparse_decorations.init()

argparse_decorations.make_verbosity_argument()


def _get_script(script_name):
    return resources.files('xenv').joinpath('scripts').joinpath(script_name)


@Command('launch-zsh', help='Print the launch script for ZSH')
def launch_handler_handler():
    # TODO Autodetect shell
    launch_script_name = _get_script('launch.zsh')
    with open(launch_script_name) as launch_file:
        print(launch_file.read(), end='')

    print()
    print(f'[ -z "$XENV_HOME" ] && export XENV_HOME="{_xenv_home()}"')


def _check_xenv_launched():
    if 'XENV_UPDATE' not in os.environ:
        raise XEnvException(
                'xenv not launched. Run \'eval "$(xenv launch-zsh)"\'')

    global xenv_update

    xenv_update = os.environ['XENV_UPDATE']


def _path_extensions(environment):
    paths = [os.path.join(_xenv_home())]

    plugins = (config('.plugins', environment=environment) or {})
    for plugin_name, configs in plugins.items():
        bin_path = os.path.join(_xenv_home(), 'plugins', plugin_name, 'bin')

        if os.path.exists(bin_path):
            paths.append(bin_path)

    if len(paths) > 0:
        return ':'.join(paths)


@Command('load', help='Load a environment')
@Argument('environment', help='Environment name')
def load_handler(environment):
    _check_xenv_launched()

    with open(xenv_update, 'w') as update_file:
        update_file.write('# pre load script\n\n')
        pre_load_script_name = _get_script('pre_load.zsh')
        with open(pre_load_script_name) as pre_load_script:
            update_file.write(pre_load_script.read())

        update_file.write(f'export XENV_ENVIRONMENT="{environment}"\n')

        if path_extensions := _path_extensions(environment):
            update_file.write(f'export PATH="{path_extensions}:$PATH"\n')

        update_file.write('\n\n')

        update_file.write('# activation script\n\n')
        activate_script_name = _environment_activate_script(environment)
        with open(activate_script_name) as activate_script:
            update_file.write(activate_script.read())
        update_file.write('\n\n')


def _check_has_environment_loaded():
    _check_xenv_launched()

    if 'XENV_ENVIRONMENT' not in os.environ:
        raise XEnvException('No environment loaded')


@Command('unload', help='Unload the environment')
def unload_handler():
    _check_has_environment_loaded()

    with open(xenv_update, 'w') as update_file:
        update_file.write('# unload script\n\n')
        unload_script_name = _get_script('unload.zsh')
        with open(unload_script_name) as unload_script:
            update_file.write(unload_script.read())


def _xenv_environments():
    for entry in os.scandir(_xenv_environments_dir()):
        if entry.is_dir():
            yield entry.name


@Command('list', aliases=['ls'], help='List environments')
def list_handler():
    for environment in _xenv_environments():
        print(environment)


def _string_list(raw):
    return raw.split(',')


@Command('create', help='Create a environment')
@Argument('name', help='Environment name')
@Argument('path', help='Environment path')
@Argument('--plugins', '-p', type=_string_list, default=[],
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

    with open(_xenv_environment_config_file(name), 'w') as config_file:
        yaml.dump(config, config_file)

    # TODO Linkar os binários dos plugins


@Command('config', help='Configuration management')
@Argument('--environment', help='Override active environment')
@Argument('--global', '-g', dest='_global', action='store_true',
          help='Global property')
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

    config_file_name = _xenv_environment_config_file(environment, _global)

    print(config_file_name)


def main():
    argparse_decorations.parse_and_run()


if __name__ == '__main__':
    main()
