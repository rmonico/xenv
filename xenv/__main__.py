import argparse_decorations
from argparse_decorations import Command


argparse_decorations.init()


@Command('launch-zsh', help='Print the launch script for ZSH')
def launch():
    # TODO Autodetect shell
    with open('scripts/launch.zsh') as launch_file:
        print(launch_file.read(), end='')


if __name__ == '__main__':
    argparse_decorations.parse_and_run()
