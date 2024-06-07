from subprocess import run, PIPE


class YqException(Exception):

    def __init__(self, process):
        self._process = process

    def __str__(self):
        return self._process.stderr.decode()


def yq(filter, input_file_name):
    process = run(['yq', '-y', filter, input_file_name], stdout=PIPE)

    if process.returncode == 0:
        import yaml
        return yaml.safe_load(process.stdout.decode())
    else:
        raise YqException(process)
