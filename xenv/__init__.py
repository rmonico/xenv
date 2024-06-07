from argparse_decorations import Command, SubCommand, Argument
import logging
import os
import yaml


_logger = logging.getLogger(__name__)


def _get_version():
    from importlib import resources
    return resources.files('xenv').joinpath('__version__').read_text()


class XEnvException(Exception):

    def __init__(self, message):
        super().__init__(message)


def _get_default_environment_or_active(default_environment):
    if default_environment:
        return default_environment

    if 'XENV_ENVIRONMENT' not in os.environ:
        raise XEnvException(
                'Environment not loaded and --environment specified')

    return os.environ['XENV_ENVIRONMENT']


def _xenv_home():
    config_home = os.environ.get(
            'XDG_CONFIG_HOME',
            os.path.join(os.environ['HOME'], '.config'))

    return os.path.join(config_home, 'xenv')


def _xenv_environments_dir():
    if 'XENV_ENVIRONMENTS' in os.environ:
        return os.environ['XENV_ENVIRONMENTS']

    return os.path.join(_xenv_home(), 'environments')


def _xenv_environment_dir(environment):
    return os.path.join(_xenv_environments_dir(), environment)


def _environment_activate_script(environment):
    return os.path.join(_xenv_environment_dir(environment), 'activate.zsh')


def _xenv_environment_config_file(environment, _global=False):
    if _global:
        config_dir = _xenv_home()
    else:
        config_dir = _xenv_environment_dir(environment)

    return os.path.join(config_dir, 'config.yaml')


@Command('config')
@SubCommand('get', help='Get a configuration entry')
@Argument('entry_path', help='Entry to get')
def _config(*args, **kwargs):
    value = config(*args, **kwargs)

    if isinstance(value, dict):
        print(yaml.dump(value), end='')
    else:
        print(str(value), end='')


def config(entry_path, environment=None, _global=False):
    _logger.info(f'Getting {entry_path} ({"" if _global else "non "}globally) '
                 f'for environment "{environment}"')

    environment = _get_default_environment_or_active(environment)

    config_file_name = _xenv_environment_config_file(environment, _global)

    from .yq import yq
    value = yq(entry_path, config_file_name)

    return value
