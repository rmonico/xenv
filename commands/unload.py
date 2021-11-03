def commands():
    return [Unload]


class Unload():
    name = 'unload'

    @staticmethod
    def cmdline_switch(parserbuilder):
        parserbuilder.add_command(Unload.name)  # alias: off (TODO)

    def __init__(self, helper):
        self.helper = helper

    def run(self, args):
        return self._unload(args.source_files_dir)

    def _unload(self, output_files_dir):
        if not self._xenv_has_loaded_environment():
            self._error('No xenv environment loaded')

        environment = os.environ['XENV_ACTIVE_ENVIRONMENT']

        source = os.path.join(self._environmentdir(environment), 'unload')

        if not os.path.exists(source):
            self._error(
                f'Environment "{environment}" has no unload script, aborting')

        self._append_to_export_file(output_files_dir, source)

        configs = self._load_configs(environment)

        self._append_plugins(output_files_dir, configs.get('plugins', []))

        print(f'Environment "{environment}" unloaded')

        return 0
