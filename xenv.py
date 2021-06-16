#!/usr/bin/python3

import sys
import os
import shutil


def shift(args, count=1):
    for i in range(count):
        args.pop(0)


def parse_args(args):
    parsed = {}

    while len(args) > 0:
        if args[0] == '--source-files-dir':
            parsed['output_files_dir'] = args[1]

            shift(args, 2)

        elif args[0] == 'activate':
            parsed['command'] = 'activate'
            parsed['environment'] = args[1]

            shift(args, 2)
        elif args[0] == 'deactivate':
            parsed['command'] = 'deactivate'

            shift(args, 1)

    return parsed


def error(message):
    print(message)
    sys.exit(1)


def environmentdir(environment):
    return os.path.join(os.environ['HOME'], '.config/xenv/', environment)


def main(**args):
    if args['command'] == 'activate':
        environment = args['environment']
        source = os.path.join(environmentdir(environment), 'activate')

        if not os.path.exists(source):
            print(f'Environment "{environment}" activated')
            return 0

        if not 'output_files_dir' in args:
            error('--source-files-dir not informed')
        else:
            output_files_dir = args['output_files_dir']

        dest = os.path.join(output_files_dir, 'activate')

        shutil.copyfile(source, dest)

        print(f'Environment "{environment}" activated')

    elif args['command'] == 'deactivate':
        environment = os.environ['XENV_ACTIVE_ENVIRONMENT']

        source = os.path.join(environmentdir(environment), 'deactivate')

        if not os.path.exists(source):
            print(f'Environment "{environment}" deactivated')
            return 0

        if not 'output_files_dir' in args:
            error('--source-files-dir not informed')
        else:
            output_files_dir = args['output_files_dir']

        dest = os.path.join(output_files_dir, 'deactivate')

        shutil.copyfile(source, dest)

        print(f'Environment "{environment}" deactivated')

args = parse_args(list(sys.argv[1:]))

sys.exit(main(**args))
