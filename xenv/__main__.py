import argparse_decorations
from argparse_decorations import Command, Argument
import os
import sys


argparse_decorations.init()


def _xenv_home():
    config_home = os.environ.get(
            'XDG_CONFIG_HOME',
            os.path.join(os.environ['HOME'], '.config'))

    return os.path.join(config_home, 'xenv')


@Command('launch-zsh', help='Print the launch script for ZSH')
def launch():
    # TODO Autodetect shell
    with open('scripts/launch.zsh') as launch_file:
        print(launch_file.read(), end='')

    print()
    print(f'[ -z "$XENV_HOME" ] && export XENV_HOME="{_xenv_home()}"')


def _print_err(message):
    sys.stderr.write(message + '\n')


def _environment_activate_script(environment):
    xenv_home = os.environ['XENV_HOME']

    return os.path.join(xenv_home, 'environments', environment, 'activate.zsh')


@Command('load', help='Load a environment')
@Argument('environment', help='Environment name')
def load(environment):
    breakpoint()
    if 'XENV_UPDATE' not in os.environ:
        _print_err('xenv not launched. Run "source `xenv launch-zsh`"')
        sys.exit(1)

    xenv_update = os.environ['XENV_UPDATE']

    import shutil
    activate_script = _environment_activate_script(environment)
    shutil.copy(activate_script, xenv_update)


if __name__ == '__main__':
    argparse_decorations.parse_and_run()
