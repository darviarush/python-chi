from setuptools import setup, find_packages
from os.path import join, dirname
import re

readme = open(join(dirname(__file__), 'README.md')).read()

def get(r, name):
    match = re.search(r, readme, re.S | re.M)
    if not match:
        raise Exception("В README.md не найден" + name)
    return match

version = get(r'^# VERSION\s*(\S+)', "а версия")
author = get(r'^# AUTHOR\s*([^<>#]+)\s+<([^<>]+)>', " автор")
description = get(r'^# NAME\s*([^\n]+?)\s*$', "о описание")
requirements = get(r'^# REQUIREMENTS\s*\n\*([^#]*?)\s*#', "ы зависимости")

requirements = requirements.group(1)
requirements = [] if requirements == 'Нет' else requirements.split('\n* ')

setup(
    name='python-perl-chi',
    version=version.group(1),
    description=description.group(1),
    long_description=readme,
    long_description_content_type="text/markdown",

    scripts=['script/chi'],
    platforms=['any'],
    python_requires='>=3.6',
    # The project's main homepage.
    url='https://github.com/darviarush/python-perl-chi',

    # Author details
    author=author.group(1),
    author_email=author.group(2),

    # Choose your license
    license='MIT',

    packages=find_packages(),
    install_requires=requirements,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        "Topic :: Text Processing",

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
        
        "Operating System :: OS Independent",

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
