import xenv
import logger_wrapper

logger = logger_wrapper.get(__name__)


def commands():
    return [Configs]


class Configs(object):
    name = 'configs'

    @staticmethod
    def cmdline_switch(builder):
        builder.add_command(Configs.name)

    def run(self):
        env = xenv.environmentConfigsFilename()

        import subprocess
        import os

        subprocess.run(os.environ['EDITOR'].split(' ') + [env])
