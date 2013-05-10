from setuptools import setup, find_packages
from os import path


def read(fname):
    return open(path.join(path.dirname(__file__), fname)).read()


setup(
    name='python-logging-proxy',
    package_data={'': ['*.md']},
    author='Alistair Broomhead',
    version='1.0.4',
    author_email='alistair.broomhead@gmail.com',
    description='Micro Interceptor Proxy - a simple MITM HTTP/S proxy with logging',
    license='GPL',
    url='https://github.com/alistair-broomhead/python-logging-proxy',
    download_url='https://github.com/alistair-broomhead/python-logging-proxy/zipball/master',
    long_description=read('README.md'),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'pyopenssl'
    ]
)
