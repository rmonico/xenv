from pathlib import Path
from setuptools import setup
from xenv import _get_version


_version = _get_version()

setup(name='xenvironment',
      version=_version,
      description='Environments for any project',
      long_description_content_type="text/markdown",
      long_description=(Path(__file__).parent / 'README.md').read_text(),
      url='https://github.com/rmonico/xenv',
      author='Rafael Monico',
      author_email='rmonico1@gmail.com',
      license='GPL3',
      include_package_data=True,
      packages=['xenv'],
      entry_points={
          'console_scripts': ['xenv=xenv.__main__:main'],
      },
      zip_safe=False,
      install_requires=[''])
