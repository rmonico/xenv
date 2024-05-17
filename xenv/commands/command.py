from abc import abstractmethod
'''
Modules should have a commands callable with should return a Command class with the method above
'''
# def commands():
#     pass


class Command(object):
    '''
    '''
    name = 'command model'
    '''
    Should register the command line arguments and options for the command
    '''
    @staticmethod
    def cmdline_argument(parsebuilder):
        pass

    '''
    Called when command is ran
    '''

    @abstractmethod
    def run(self, args):
        pass
