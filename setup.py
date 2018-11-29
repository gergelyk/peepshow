from setuptools import setup, find_packages

setup(
    name = 'peepshow',
    version = '0.1.0',
    url = 'https://github.com/mypackage.git',
    author = 'Grzegorz Krason',
    author_email = 'grzegorz@krason.me',
    description = 'Data Explorer',
    packages = find_packages(),
    package_data={'': ['peepshow.1']},
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
