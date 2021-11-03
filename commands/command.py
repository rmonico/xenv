from abc import abstractmethod


class Command(object):
    @staticmethod
    def cmdline_argument(parser):
        pass

    @staticmethod
    def name():
        pass

    @staticmethod
    def create_instance():
        pass

    @abstractmethod
    def run(self, args):
        pass

