import argparse_decorations
from argparse_decorations import Command, Argument
from importlib import resources
import os
import sys


argparse_decorations.init()


def _xenv_home():
    config_home = os.environ.get(
            'XDG_CONFIG_HOME',
            os.path.join(os.environ['HOME'], '.config'))

    return os.path.join(config_home, 'xenv')


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


def _print_err(message):
    sys.stderr.write(message + '\n')


def _check_xenv_launched():
    if 'XENV_UPDATE' not in os.environ:
        _print_err('xenv not launched. Run \'eval "$(xenv launch-zsh)"\'')
        sys.exit(1)

    global xenv_update

    xenv_update = os.environ['XENV_UPDATE']


def _environment_activate_script(environment):
    xenv_home = os.environ['XENV_HOME']

    return os.path.join(xenv_home, 'environments', environment, 'activate.zsh')


@Command('load', help='Load a environment')
@Argument('environment', help='Environment name')
def load(environment):
    _check_xenv_launched()

    with open(xenv_update, 'w') as update_file:
        update_file.write('# pre load script\n\n')
        pre_load_script_name = _get_script('pre_load.zsh')
        with open(pre_load_script_name) as pre_load_script:
            update_file.write(pre_load_script.read())
        update_file.write('\n\n')

        update_file.write('# activation script\n\n')
        activate_script_name = _environment_activate_script(environment)
        with open(activate_script_name) as activate_script:
            update_file.write(activate_script.read())
        update_file.write('\n\n')


def _xenv_environments_dir():
    if 'XENV_ENVIRONMENTS' in os.environ:
        return os.environ['XENV_ENVIRONMENTS']

    return os.path.join(_xenv_home(), 'environments')


def _xenv_environments():
    for entry in os.scandir(_xenv_environments_dir()):
        if entry.is_dir():
            yield entry.name


@Command('list', aliases=['ls'], help='List environments')
def list():
    for environment in _xenv_environments():
        print(environment)


if __name__ == '__main__':
    argparse_decorations.parse_and_run()
