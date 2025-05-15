import os
from xenv import config, updater, xenv_home, \
        _xenv_environments_dir


def _path_extensions(environment):
    paths = list()

    environment_bin = os.path.join(_xenv_environments_dir(), environment,
                                   'bin')

    if os.path.exists(environment_bin):
        paths.append(environment_bin)

    configs = config('plugins', default_getter=lambda e: {})

    plugins = list(configs.keys())
    plugins.insert(0, 'base')

    confs = list(configs.values())
    confs.insert(0, {})

    for plugin_name, configs in zip(plugins, confs):
        bin_path = os.path.join(xenv_home(), 'plugins', 'xenv_plugin',
                                plugin_name, 'bin')

        if os.path.exists(bin_path):
            paths.append(bin_path)

    if len(paths) > 0:
        return ':'.join(paths)


def load(environment, configs, flags):
    updater._include('pre_load')
    updater._include('cdhome')

    environment = os.environ['XENV_ENVIRONMENT']
    updater.export('XENV_ENVIRONMENT', environment)

    if path_extensions := _path_extensions(environment):
        updater.export('PATH', f'{path_extensions}:{os.environ["PATH"]}')
        updater.export('PATH_EXTENSION_LENGTH', len(path_extensions))

    project_name = config('project.name')
    project_path = config('project.path')

    updater.cd(project_path)
    updater.print(f'Environment "{project_name}" loaded')


def unload(environment, configs):
    project_name = config('project.name')

    updater.unset_function('preexec', 'precmd', 'cdhome')

    if 'PATH_EXTENSION_LENGTH' in os.environ:
        path_extension_length = int(os.environ['PATH_EXTENSION_LENGTH'])

        updater.export('PATH', os.environ['PATH'][path_extension_length+1:])
        updater.unset('PATH_EXTENSION_LENGTH')

    updater.unset('XENV_ENVIRONMENT')

    updater.print(f'\"{project_name}\" unloaded')
