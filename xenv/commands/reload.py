import xenv


def commands():
    return [Reload]


class Reload():
    name = 'reload'

    @staticmethod
    def cmdline_switch(parserbuilder):
        parserbuilder.add_command(Reload.name)

    def run(self):
        module = xenv.environmentModule()

        if hasattr(module, 'reload'):
            module.reload()
        else:
            environment = xenv.environmentActive()

            self._unload()

            self._load(environment)

            print()
            print(f'Environment {environment} reloaded')

    def _unload(self):
        from .unload import Unload

        unloader = Unload()

        unloader.run(verbose=False)

    def _load(self, environment):
        from .load import Load

        loader = Load()

        loader.run(environment, verbose=False)
