from setuptools import setup, find_packages
from setuptools.command.install import install
from pathlib import Path
import site

customize_code = """
###############################################################################
# Add peepshow to built-ins
###############################################################################

try:
    import peepshow
    import builtins
    builtins.peep = peepshow.peep
    builtins.show = peepshow.show
    builtins.peep_ = peepshow.peep_
    builtins.show_ = peepshow.show_
except:
    print("peepshow seems to be uninstalled, please manually remove " \\
          "corresponding entry form " + __file__)

###############################################################################
"""

class CustomInstallCommand(install):

    user_options = install.user_options + [
        ('add-builtins', None, 'Add "peep" and "show" keywords to builtins'),
    ]

    def initialize_options(self):
        install.initialize_options(self)
        self.add_builtins = 0

    def do_add_builtins(self):
        if self.user:
            customize_path = Path(site.getusersitepackages()) / 'usercustomize.py'
        else:
            customize_path = Path(site.getsitepackages()[0]) / 'sitecustomize.py'

        with open(customize_path, 'a') as fh:
            fh.write(customize_code)

        print('PeepShow utils added to builtins through: ', customize_path)

    def run(self):
        super().run()
        if self.add_builtins:
            self.do_add_builtins()

readme_path = Path(__file__).parent / 'README.rst'

with open(readme_path) as fh:
    long_description = fh.read()

setup(
    name = 'peepshow',
    version = '0.1.6',
    url = 'https://github.com/gergelyk/peepshow',
    author = 'Grzegorz Krason',
    author_email = 'grzegorz@krason.me',
    description = 'Data Explorer',
    packages = find_packages(),
    keywords = 'debug data explore programming'.split(),
    long_description = long_description,
    python_requires = '>=3.6,<3.9',
    package_data = {'': ['peepshow.1']},
    cmdclass = {
        'install': CustomInstallCommand,
    },
    classifiers = [
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Utilities',
    ],
    install_requires = [
        'astor~=0.7',
        'astunparse~=1.6',
        'colorama~=0.4',
        'getch~=1.0',
        'miscutils~=1.1',
        'pprintpp~=0.4',
        'pygments~=2.2',
        ],
)
