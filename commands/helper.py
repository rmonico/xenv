from . import constants
import os
import shutil
import sys


class Helper(object):
    def __init__(self, source_files_dir):
        self.source_files_dir = source_files_dir
        self.xenvhome = os.environ['XENV_HOME']
        self.environmentsfolder = f'{self.xenvhome}/environments'
        self.pluginsfolder = f'{self.xenvhome}/plugins'
        self.active_environment = os.environ.get('XENV_ACTIVE_ENVIRONMENT', '')

    def copy_to_export_folder(self, script, environment=None, plugin=None):
        if environment:
            folder = os.path.join(self.environmentsfolder, environment)
        elif plugin:
            folder = os.path.join(self.pluginsfolder, plugin)
        else:
            folder = self.xenvhome

        extension = os.path.basename(os.environ["SHELL"])

        source = os.path.join(folder, f'{script}.{extension}')

        if not os.path.exists(source):
            return False

        dest = os.path.join(self.source_files_dir, 'xenv.environment')

        shutil.copy(source, dest)

        return True

    def environmentfolder(self, environment):
        if environment == constants.HERE_ENV:
            return os.path.join(os.getcwd(), '.xenv')
        else:
            return os.path.join(self.environmentsfolder, environment)

    def archetypefolder(self, archetype):
        return os.path.join(self.environmentsfolder, archetype)

    def configs(self, environment):
        # TODO Load it once and store here
        yaml_file_name = os.path.join(self.environmentfolder(environment),
                                      'configs.yaml')

        if not os.path.exists(yaml_file_name):
            return {}

        with open(yaml_file_name, 'r') as yaml_file:
            import yaml
            return yaml.safe_load(yaml_file)

    def is_some_enviroment_loaded(self):
        return 'XENV_ACTIVE_ENVIRONMENT' in os.environ

    def environments(self):
        trailing_chars = len(self.environmentsfolder) + 1

        from glob import glob

        return [
            environment[trailing_chars:-1]
            for environment in glob(f'{self.environmentsfolder}/*/')
        ]

    @staticmethod
    def _error(message):
        print(message)
        sys.exit(1)
