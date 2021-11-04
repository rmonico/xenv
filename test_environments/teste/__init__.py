# vim: filetype=python
import xenv


def load():
    xenv.variable('VARIABLE_DEFINED_BY_ENV', 'teste')


def unload():
    xenv.variableUnset('VARIABLE_DEFINED_BY_ENV')
