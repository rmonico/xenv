import xenv


def commands():
    return [List]


class List(object):
    name = 'ls'

    @staticmethod
    def cmdline_switch(parserbuilder):
        # TODO ls verbose, should show environments description
        parserbuilder.add_command(List.name)

    def run(self):
        for environment in xenv.environmentList():
            isActiveEnv = environment == xenv.environmentActive()

            prefix = "*" if isActiveEnv else " "

            envLine = f'{prefix} {environment}'

            print(envLine)
