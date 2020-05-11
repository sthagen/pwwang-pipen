# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os.path

readme = ''
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, 'README.rst')
if os.path.exists(readme_path):
    with open(readme_path, 'rb') as stream:
        readme = stream.read().decode('utf8')

setup(
    long_description=readme,
    name='PyPPL',
    version='3.1.1',
    description='A Python PiPeLine framework',
    python_requires='==3.*,>=3.6.0',
    project_urls={
        "homepage": "https://github.com/pwwang/PyPPL",
        "repository": "https://github.com/pwwang/PyPPL"
    },
    author='pwwang',
    author_email='pwwang@pwwang.com',
    license='MIT',
    entry_points={"console_scripts": ["pyppl = pyppl.console:main"]},
    packages=['pyppl', 'pyppl.console'],
    package_dir={"": "."},
    package_data={"pyppl": ["*.bak"]},
    install_requires=[
        'attr-property', 'attrs==19.*,>=19.3.0', 'cmdy',
        'colorama==0.*,>=0.4.1', 'diot', 'filelock==3.*,>=3.0.0', 'liquidpy',
        'pluggy==0.*', 'psutil==5.*,>=5.6.0', 'pyparam', 'pyppl-echo',
        'pyppl-export', 'pyppl-lock', 'pyppl-rich', 'pyppl-runners',
        'pyppl-strict', 'python-simpleconf', 'python-varname',
        'toml==0.*,>=0.10.0', 'transitions==0.*,>=0.7.0'
    ],
    extras_require={
        "dev": [
            "faker==1.*,>=1.0.0", "jinja2==2.*,>=2.0.0", "pytest", "pytest-cov"
        ]
    },
)
