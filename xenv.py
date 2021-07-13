#!/usr/bin/python3

import sys
import os
import shutil


XENV_HOME = os.environ['XENV_HOME']
XENV_ENVIRONMENTS = f'{XENV_HOME}/environments'
HERE_ENV = '__here_env__'


def shift(args, count=1):
    for i in range(count):
        if len(args) == 0:
            return

        args.pop(0)


def parse_args(args):
    parsed = {}

    while len(args) > 0:
        if args[0] == '--source-files-dir':
            parsed['output_files_dir'] = args[1]

            shift(args, 2)

        elif args[0] == 'ls':
            parsed['command'] = 'ls'

            args = {}
        elif args[0] == 'load':
            parsed['command'] = 'load'
            parsed['environment'] = args[1] if len(args) > 1 else HERE_ENV

            shift(args, 2)
        elif args[0] == 'off':
            parsed['command'] = 'off'

            shift(args, 1)
        elif args[0] == 'reload':
            parsed['command'] = 'reload'

            shift(args, 1)
        else:
            error('XENV: Command not found: "' + '" "'.join(args) + '"')

    return parsed


def error(message):
    print(message)
    sys.exit(1)


def environmentdir(environment):
    if environment == HERE_ENV:
        return os.path.join(os.getcwd(), '.xenv')
    else:
        return os.path.join(XENV_ENVIRONMENTS, environment)


def xenv_has_loaded_environment():
    return 'XENV_ACTIVE_ENVIRONMENT' in os.environ


def append_to_export_file(filename):
    if not 'output_files_dir' in args:
        error('--source-files-dir not informed')
    else:
        output_files_dir = args['output_files_dir']

    dest = os.path.join(output_files_dir, 'xenv.environment')

    with open(dest, 'a') as environmentfile:
        with open(filename, 'r') as source:
            while line := source.readline():
                environmentfile.write(line)


def load(environment, force, args):
    if not force and xenv_has_loaded_environment():
        error('Xenv environment already loaded')

    if not os.path.isdir(environmentdir(environment)):
        error(f'Environment "{environment}" not found')

    source = os.path.join(environmentdir(environment), 'load')

    if not os.path.exists(source):
        error(f'Environment "{environment}" has no load script, aborting')

    append_to_export_file(source)

    print(f'Environment "{environment}" loaded')

    return 0


def unload(args):
    if not xenv_has_loaded_environment():
        error('No xenv environment loaded')

    environment = os.environ['XENV_ACTIVE_ENVIRONMENT']

    source = os.path.join(environmentdir(environment), 'unload')

    if not os.path.exists(source):
        error(f'Environment "{environment}" has no unload script, aborting')

    append_to_export_file(source)

    print(f'Environment "{environment}" unloaded')

    return 0


def main(**args):
    if args['command'] == 'ls':
        trailing_chars = len(XENV_ENVIRONMENTS) + 1

        from glob import glob

        print('Available environments:')
        print()
        [ print(environment[trailing_chars:-1]) for environment in glob(f'{XENV_ENVIRONMENTS}/*/') ]


    if args['command'] == 'load':
        return load(args['environment'], force=False, args=args)


    elif args['command'] == 'off':
        return unload(args)


    elif args['command'] == 'reload':
        unload_status = unload(args)

        if unload_status == 0:
            return load(os.environ['XENV_ACTIVE_ENVIRONMENT'], force=True, args=args)
        else:
            return unload_status


args = parse_args(list(sys.argv[1:]))

sys.exit(main(**args))

