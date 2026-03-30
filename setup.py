from pathlib import Path
from setuptools import setup


def _get_version():
    with open('xenv/__version__') as file:
        return file.readlines()[0].strip()


def _get_requirements():
    with open('requirements') as file:
        return [line for line in file.readlines() if line != '']


setup(name='xenvironment',
      version=_get_version(),
      description='Environments for any project',
      long_description_content_type="text/markdown",
      long_description=(Path(__file__).parent / 'README.md').read_text(),
      url='https://github.com/rmonico/xenv',
      author='Rafael Monico',
      author_email='rmonico1@gmail.com',
      license='GPL3',
      include_package_data=True,
      packages=['xenv', 'xenv_plugin.base'],
      entry_points={
          'console_scripts': ['xenv=xenv.__main__:main'],
      },
      zip_safe=False,
      install_requires=_get_requirements())
