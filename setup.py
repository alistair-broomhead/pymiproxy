from setuptools import setup, find_packages
from os import path


def open_(fname):
    return open(path.join(path.dirname(__file__), fname))


def read(fname):
    return open_(fname).read()


def readlines(fname):
    return open_(fname).readlines()


def read_json(fname):
    from json import load
    return load(open_(fname))


def read_version():
    return '.'.join([str(i) for i in
                     read_json("src/python_logging_proxy/version.txt")])


setup(
    name='python-logging-proxy',
    package_data={'': ['*.md', '*.txt']},
    author='Alistair Broomhead',
    version=read_version(),
    author_email='alistair.broomhead@gmail.com',
    description='Logging Proxy adapting pymiproxy',
    license='MIT',
    url='https://github.com/alistair-broomhead/python-logging-proxy',
    download_url='https://github.com/alistair-broomhead/python-logging-proxy/zipball/master',
    long_description=read('README.md'),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=readlines("requirements.txt")
)
