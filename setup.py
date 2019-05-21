#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    """Retrieves the version from quartet_vrs/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("quartet_vrs", "__init__.py")


if sys.argv[-1] == 'publish':
    try:
        import wheel
        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='quartet_vrs',
    version=version,
    description="""A GS1-compliant VRS interface for the open-source EPCIS QU4RTET platform.""",
    long_description=readme,
    author='SerialLab',
    author_email='slab@serial-lab.com',
    url='https://gitlab.com/serial-lab/quartet_vrs',
    packages=[
        'quartet_vrs',
    ],
    include_package_data=True,
    install_requires=[
        'django',
        'djangorestframework',
        'mixer',
        'recommonmark',
        'sphinx_rtd_theme',
        'quartet_capture',
        'quartet_masterdata',
        'quartet_epcis',
        'EPCPyYes',
        'EParseCIS'
    ],
    license="GPLv3",
    zip_safe=False,
    keywords='quartet_vrs',
    classifiers=[
        'Development Status :: 1 - Release',
        'Framework :: Django :: 2.15',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
)
