import os
from xenv import Loader, Unloader, config, updater, _xenv_home


def _path_extensions(environment):
    paths = [os.path.join(_xenv_home())]

    plugins = (config('.plugins') or {})
    for plugin_name, configs in plugins.items():
        bin_path = os.path.join(_xenv_home(), 'plugins', plugin_name, 'bin')

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

    project_name = config('.project.name')
    project_path = config('.project.path')

    updater.cd(project_path)
    updater.print(f'Environment "{project_name}" loaded')


@Unloader
def unloader():
    updater.unset_function('preexec', 'precmd')

    updater.unset('XENV_ENVIRONMENT')

    project_name = config('.project.name')
    updater.print(f'\"{project_name}\" unloaded')
