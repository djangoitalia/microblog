#!/usr/bin/env python

from distutils.core import setup

import os
import os.path

def recurse(path):
    B = 'microblog'
    output = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(B, path)):
        for f in filenames:
            output.append(os.path.join(dirpath, f)[len(B)+1:])
    return output

setup(name='microblog',
    version='0.1',
    description='django microblog',
    author='dvd',
    author_email='dvd@develer.com',
    packages=[
        'microblog',
        'microblog.management',
        'microblog.templatetags',
        'microblog.utils',
    ],
    package_data={
        'microblog': sum(map(recurse, ('deps', 'locale', 'static', 'templates')), []),
    }
)
