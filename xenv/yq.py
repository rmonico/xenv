from subprocess import run, PIPE


class YqException(Exception):

    def __init__(self, process, filename):
        self._process = process
        self._filename = filename

    def __str__(self):
        if self._process.stderr:
            return self._process.stderr.decode()
        else:
            return f'Erro loading yaml file \"{self._filename}\"'


def yq(filter, input_file_name):
    process = run(['yq', '-y', filter, input_file_name], stdout=PIPE)

    if process.returncode == 0:
        import yaml
        return yaml.safe_load(process.stdout.decode())
    else:
        raise YqException(process, input_file_name)
