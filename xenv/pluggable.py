def safecall(obj, methodName, *args, **kwargs):
    if attr := getattr(obj, methodName, None):
        return attr(*args, **kwargs)


class Pluggable(object):
    def __init__(self, module):
        self.module = module

    def safecall(self, methodName, *args, **kwargs):
        return safecall(self.module, methodName, *args, **kwargs)

    def initialize(self, *args, **kwargs):
        return self.safecall('initialize', *args, **kwargs)

    def finalize(self, *args, **kwargs):
        return self.safecall('finalize', *args, **kwargs)
