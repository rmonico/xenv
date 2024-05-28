import sys


def main():
    if sys.argv[1] == '--launch-script':
        with open('scripts/launch.sh') as launch_file:
            print(launch_file.read(), end='')


if __name__ == '__main__':
    main()
