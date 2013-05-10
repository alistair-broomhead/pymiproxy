from setuptools import setup, find_packages
from os import path


def read(fname):
    return open(path.join(path.dirname(__file__), fname)).read()


setup(
    name='python-logging-proxy',
    package_data={'': ['*.md']},
    author='Alistair Broomhead',
    version='1.0.6',
    author_email='alistair.broomhead@gmail.com',
    description='Logging Proxy adapting pymiproxy',
    license='MIT',
    url='https://github.com/alistair-broomhead/python-logging-proxy',
    download_url='https://github.com/alistair-broomhead/python-logging-proxy/zipball/master',
    long_description=read('README.md'),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['pyopenssl', 'pymiproxy']
)
