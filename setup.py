from argparse_decorations import helpers
from pathlib import Path
from setuptools import setup


_main_package = 'xenv'

helper = helpers.BuildHelper(_main_package)

helper.update_dynamic_metadata()


def _load_requirements():
    with open('requirements') as file:
        return [line for line in file.readlines() if line != '']


def _load_readme():
    return (Path(__file__).parent / 'README.md').read_text()


setup(name='xenvironment',
      version=helper.get_version(),
      description='Environments for any project',
      long_description_content_type="text/markdown",
      long_description=_load_readme(),
      url='https://github.com/rmonico/xenv',
      author='Rafael Monico',
      author_email='rmonico1@gmail.com',
      license='GPL3',
      include_package_data=True,
      data_files=helper.get_metadata_files(),
      packages=[_main_package, 'xenv_plugin.base'],
      entry_points={
          'console_scripts': ['xenv=xenv.__main__:main'],
      },
      zip_safe=False,
      install_requires=_load_requirements())
