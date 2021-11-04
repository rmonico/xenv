import xenv


def load():
    environment = xenv.environmentActive()

    xenv.function(
        'precmd', '''\
echo
echo "XENV: {environment}"
        '''.format(environment=environment))


def unload():
    xenv.functionUnset('precmd')


def initialize(environment):
    print(f'Setting up environment {environment}')


def finalize(environment):
    print(f'Destroying environment {environment}')
