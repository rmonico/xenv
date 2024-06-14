from xenv import Loader, Unloader, config, updater


@Loader
def load():
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