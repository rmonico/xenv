def commands():
    return [Reload]


class Reload():
    name = 'reload'

    @staticmethod
    def cmdline_switch(parserbuilder):
        parserbuilder.add_command(Reload.name)

    def __init__(self, helper):
        self.helper = helper

    def run(self, args):
        unload_status = self._unload(args.source_files_dir)

        if unload_status == 0:
            return self._load(os.environ['XENV_ACTIVE_ENVIRONMENT'],
                              args.source_files_dir,
                              force=True)
        else:
            return unload_status
