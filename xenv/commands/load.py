from xenv import constants, _functions, _aliases, _variables
import os
from xenv import Plugin
import xenv
from xenv.pluggable import safecall


def commands():
    return [Load]


class Load():
    name = 'load'

    @staticmethod
    def cmdline_switch(parserbuilder):
        with parserbuilder.add_command(Load.name) as b:
            b.add_argument('environment', default=constants.hereEnvVariable)

    def run(self, environment, verbose=True):
        if env := xenv.environmentActive():
            xenv.error(f'Environment "{env}" is already loaded', 1)

        if not xenv.environmentExists(environment):
            xenv.error(f'Environment "{environment}" not found', 1)

        xenv.variable(constants.activeEnvironmentVariable, environment)

        self._load_environment()

        if verbose:
            print()
            print(f'Environment "{environment}" loaded')

    def functions_help(self):
        if len(_functions) > 0:
            print('Functions:')
            for function in _functions:
                print(f'  {function}')
        else:
            print('<No functions>')

    def aliases_help(self):
        print('Aliases:')
        if len(_aliases) > 0:
            for alias, value in zip(align(_aliases.keys()), _aliases.values()):
                print(f'  {alias} -> {value}')
        else:
            print('<No aliases>')

    def variables_help(self):
        print('Variables:')
        print()
        if len(_variables) == 0:
            print('<No variables>')
        else:
            columns = {
                'headers': {
                    'variables': 'Variable',
                    'rawValues': 'Raw Value',
                    'resolvedValues': 'Resolved Value',
                    'separatorLine': {
                        'enabled': True,
                        'fillCharacter': '-'
                    },
                },
                'variables':
                align(title='Variable', data=_variables.keys()),
                'rawValues':
                align(title='Raw Value', data=_variables.values()),
                'resolvedValues':
                align(title='Resolved Values', data=self._resolve(_variables.keys())),
                'headerSeparators': ['   ', '    '],
                'dataSeparators': [' = ', ' -> '],
            }

            for index, (variable, raw, resolved) in enumerate(
                    zip(columns['variables'], columns['rawValues'],
                        columns['resolvedValues'])):

                if index > 1:
                    dataSeparator0 = columns["dataSeparators"][0]
                    dataSeparator1 = columns["dataSeparators"][1]
                else:
                    dataSeparator0 = columns["headerSeparators"][0]
                    dataSeparator1 = columns["headerSeparators"][1]

                print(variable + dataSeparator0 + raw + dataSeparator1 +
                      resolved)

    def environment_help(self):
        self._load_environment()

        print()

        self.variables_help()
        print()
        print()

        self.aliases_help()
        print()
        print()

        self.functions_help()

    def _resolve(self, variables):
        return [os.environ.get(v, '<None>') for v in variables]

    def _load_environment(self):
        configs = xenv.environmentConfigs()

        if hasattr(configs, "dependencies"):
            for dependency in configs.dependencies:
                xenv.checkDependency(dependency)

        module = xenv.environmentModule()

        safecall(module, 'load')

        xenv.forEachPlugin(lambda p: safecall(p, 'load'))

        if hasattr(configs, "variables"):
            for variable, value in configs.variables.items():
                xenv.variable(variable, value)

        if hasattr(configs, "aliases"):
            for name, value in configs.aliases.items():
                xenv.alias(name, value)

        if hasattr(configs, "functions"):
            for name, body in configs.functions.items():
                xenv.function(name, body)

        # TODO Criar um parâmetro para isso
        if hasattr(configs, "variables") and (basepath :=
                                              configs.variables['basepath']):
            xenv.setcwd(basepath)


def largest(items):
    largest = 0

    for item in items:
        if (varLen := len(str(item))) > largest:
            largest = varLen

    return largest


def align(title=None,
          data=[],
          separatorLineChar='-',
          fieldSeparators=' | ',
          titleSeparators='   '):

    if not isinstance(data, list):
        data = list(data)

    if title:
        data.insert(0, title)

        if separatorLineChar:
            data.insert(1, separatorLineChar)

    largest_ = largest(data)

    lines = list()

    for idx, column in enumerate(data):
        if idx == 1:
            fillerChar = separatorLineChar if title and separatorLineChar else ' '
        else:
            fillerChar = ' '

        columnStr = str(column)
        line = columnStr + fillerChar * (largest_ - len(columnStr))

        lines.append(line)

    return lines
