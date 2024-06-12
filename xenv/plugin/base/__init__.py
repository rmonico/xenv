import xenv


class Loader:

    def load(self):
        project_name = xenv.config('.project.name')
        project_path = xenv.config('.project.path')

        updater = xenv.Updater.instance()
        updater.cd(project_path)
        updater.print(f'Environment "{project_name}" loaded')
