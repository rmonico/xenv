import sys


def main():
    # TODO Autodetect shell
    if sys.argv[1] == '--launch-zsh':
        with open('scripts/launch.zsh') as launch_file:
            print(launch_file.read(), end='')


if __name__ == '__main__':
    main()
