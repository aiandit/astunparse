#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import re
from setuptools import setup, find_packages

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


def read_reqs(name):
    with open(os.path.join(os.path.dirname(__file__), name)) as f:
        return [line for line in f.read().split('\n') if line and not line.strip().startswith('#')]

tests_require = []  # mostly handled by tox
if sys.version_info < (2, 7):
    tests_require.append("unittest2 == 0.5.1")  # except this

def read_version():
    with open(os.path.join('lib', 'astunparse', '__init__.py')) as f:
        m = re.search(r'''__version__\s*=\s*['"]([^'"]*)['"]''', f.read())
        if m:
            return m.group(1)
        raise ValueError("couldn't find version")


setup(
    name='astunparse-aiandit',
    version=read_version(),
    description='An AST unparser for Python (AI&IT fork)',
    long_description=readme + '\n\n' + history,
    maintainer='Simon Percivall',
    maintainer_email='jwillkomm@ai-and-it.de',
    url='https://github.com/aiandit/astunparse',
    project_urls={
        'AI&IT Home': 'https://ai-and-it.de',
        'Original Project': 'https://github.com/simonpercivall/astunparse',
    },
    packages=find_packages('lib'),
    package_dir={'': 'lib'},
    include_package_data=True,
    package_data={'astunparse': ['xsl/xml2json.xsl']},
    install_requires=read_reqs('requirements.txt'),
    entry_points={
        'console_scripts': [
            'py2py=astunparse.cmdline:unparse2pyrun',
            'pydump=astunparse.cmdline:pydumprun',
            'py2json=astunparse.cmdline:unparse2jrun',
            'json2py=astunparse.cmdline:loadastjrun',
            'json2xml=astunparse.cmdline:json2xmlrun',
            'xml2json=astunparse.cmdline:xml2jsonrun',
            'py2xml=astunparse.cmdline:unparse2xrun',
            'xml2py=astunparse.cmdline:loadastxrun',
            'py2json2xml=astunparse.cmdline:py2json2xmlrun'
        ]
    },
    license="BSD",
    zip_safe=False,
    keywords='astunparse',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Code Generators',
    ],
    test_suite='tests',
    tests_require=tests_require,
)
