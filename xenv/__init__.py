import logging
import os


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


def _xenv_plugins_dir():
    return os.path.join(_xenv_home(), 'plugins')


def _xenv_plugin_dir(plugin):
    return os.path.join(_xenv_plugins_dir(), plugin)


def _xenv_config_file(environment, scope):
    match scope:
        case 'global':
            config_dir = _xenv_home()

        case 'plugin':
            config_dir = _xenv_plugin_dir(environment)

        case 'environment':
            config_dir = _xenv_environment_dir(environment)

    config_file = os.path.join(config_dir, 'config.yaml')

    return config_file if os.path.exists(config_file) else None


def config(entry_path, source=None, scope='environment'):
    _logger.info(f'Getting {entry_path} for scope "{scope}"'
                 f'and source "{source}"')

    source = _get_default_environment_or_active(source)

    config_file_name = _xenv_config_file(source, scope)

    if not config_file_name:
        return None

    from .yq import yq
    value = yq(entry_path, config_file_name)

    if isinstance(value, str):
        value = os.path.expanduser(value)
        value = os.path.expandvars(value)

        return value

    # TODO Expand vars inside dictionaries, recursively
    return value
