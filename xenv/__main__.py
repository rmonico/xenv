from . import XEnvException, _xenv_home, _environment_activate_script, \
    _xenv_environments_dir, _xenv_environment_dir, \
    _xenv_environment_config_file, _logger, _get_default_environment_or_active
import argparse_decorations
from argparse_decorations import Command, SubCommand, Argument
from importlib import resources
import os


argparse_decorations.init()


def _get_script(script_name):
    return resources.files('xenv').joinpath('scripts').joinpath(script_name)


@Command('launch-zsh', help='Print the launch script for ZSH')
def launch():
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


@Command('load', help='Load a environment')
@Argument('environment', help='Environment name')
def load(environment):
    _check_xenv_launched()

    with open(xenv_update, 'w') as update_file:
        update_file.write('# pre load script\n\n')
        pre_load_script_name = _get_script('pre_load.zsh')
        with open(pre_load_script_name) as pre_load_script:
            data = pre_load_script.read()
            data = data.replace('--environment--', environment)
            update_file.write(data)
        update_file.write('\n\n')

        update_file.write('# activation script\n\n')
        activate_script_name = _environment_activate_script(environment)
        with open(activate_script_name) as activate_script:
            update_file.write(activate_script.read())
        update_file.write('\n\n')


def _xenv_environments():
    for entry in os.scandir(_xenv_environments_dir()):
        if entry.is_dir():
            yield entry.name


@Command('list', aliases=['ls'], help='List environments')
def list():
    for environment in _xenv_environments():
        print(environment)


def _string_list(raw):
    return raw.split(',')


@Command('create', help='Create a environment')
@Argument('name', help='Environment name')
@Argument('path', help='Environment path')
@Argument('--plugins', '-p', type=_string_list, default=[],
          help='Plugin list to be installed')
def create(name, path, plugins):
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
        import yaml
        yaml.dump(config, config_file)

    # TODO Linkar os binários dos plugins


def _get_default_environment_or_active(default_environment):
    if default_environment:
        return default_environment

    if 'XENV_ENVIRONMENT' not in os.environ:
        raise XEnvException(
                'Environment not loaded and --environment specified')

    return os.environ['XENV_ENVIRONMENT']


@Command('config', help='Configuration management')
@Argument('--environment', help='Override active environment')
@Argument('--global', '-g', dest='_global', action='store_true',
          help='Global property')
@SubCommand('path', help='Get configuration file path')
def config_file_path(environment, _global=False):
    _logger.info(f'Getting config file path for environment "{environment}" '
                 f'({"" if _global else "non "}globally)')

    environment = _get_default_environment_or_active(environment)

    config_file_name = _xenv_environment_config_file(environment, _global)

    print(config_file_name)


def main():
    argparse_decorations.parse_and_run()


if __name__ == '__main__':
    main()
