def _get_version():
    from importlib import resources
    return resources.files('xenv').joinpath('__version__').read_text()
