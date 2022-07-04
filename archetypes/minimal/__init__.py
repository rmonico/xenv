import os
import shutil
import xenv
from xenv.pluggable import safecall
import yaml

_plugins = ['show_active_environment']


def initialize(configs):
    os.mkdir(xenv.environmentFolder(configs.environment))

    persistentConfigs = {
        'project': configs.environment,
        'description': configs.description,
        'archetype': 'minimal',
        'basepath': configs.basepath,
        'variables': {
            'project': configs.environment,
            'description': configs.description,
            'basepath': configs.basepath,
            },
        'plugins': _plugins,
    }

    destName = os.path.join(xenv.environmentFolder(configs.environment),
                            'configs.yaml')

    with open(destName, 'w') as dest:
        yaml.dump(persistentConfigs, dest)

    xenv.forEachPlugin(
        lambda p: safecall(p, 'initialize', configs.environment),
        plugins=_plugins)


def finalize(environment):
    xenv.forEachPlugin(lambda p: safecall(p, 'finalize', environment),
                       plugins=_plugins)

    # FIXME Não funciona com links
    shutil.rmtree(xenv.environmentFolder(environment))
