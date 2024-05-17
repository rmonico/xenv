from .pluggable import Pluggable


class Plugin(Pluggable):
    def load(self, *args, **kwargs):
        return self.safecall('load', *args, **kwargs)

    def unload(self, *args, **kwargs):
        return self.safecall('unload', *args, **kwargs)
