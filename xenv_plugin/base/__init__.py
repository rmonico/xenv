import os
from xenv import Loader, Unloader, config, updater, xenv_home, \
        _xenv_environments_dir


def _path_extensions(environment):
    paths = list()

    environment_bin = os.path.join(_xenv_environments_dir(), environment,
                                   'bin')

    if os.path.exists(environment_bin):
        paths.append(environment_bin)

    plugins = (config('.plugins') or {})
    for plugin_name, configs in plugins.items():
        bin_path = os.path.join(xenv_home(), 'plugins', 'xenv_plugin',
                                plugin_name, 'bin')

        if os.path.exists(bin_path):
            paths.append(bin_path)

    if len(paths) > 0:
        return ':'.join(paths)


@Loader
def load():
    updater._include('pre_load')

    environment = os.environ['XENV_ENVIRONMENT']
    updater.export('XENV_ENVIRONMENT', environment)

    if path_extensions := _path_extensions(environment):
        updater.export('PATH', f'{path_extensions}:{os.environ["PATH"]}')
        updater.export('PATH_EXTENSION_LENGTH', len(path_extensions))

    project_name = config('.project.name')
    project_path = config('.project.path')

    updater.cd(project_path)
    updater.print(f'Environment "{project_name}" loaded')


@Unloader
def unloader():
    updater.unset_function('preexec', 'precmd')

    path_extension_length = int(os.environ['PATH_EXTENSION_LENGTH'])

    updater.export('PATH', os.environ['PATH'][path_extension_length+1:])
    updater.unset('XENV_ENVIRONMENT', 'PATH_EXTENSION_LENGTH')

    project_name = config('.project.name')
    updater.print(f'\"{project_name}\" unloaded')
