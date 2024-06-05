import argparse_decorations
from argparse_decorations import Command


argparse_decorations.init()


def _xenv_home():
    import os

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
    print(f'export XENV_HOME="{_xenv_home()}"')


if __name__ == '__main__':
    argparse_decorations.parse_and_run()
