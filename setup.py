"""Setup for badgr XBlock."""

import os
from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='badgr-xblock',
    version='0.2.3',
    description='badgr XBlock',
    license='MIT',  
    packages=[
        'badgr',
    ],
    install_requires=[
        'XBlock==1.0.0',
    ],
    entry_points={
        'xblock.v1': [
            'badgr = badgr:BadgrXBlock',
        ]
    },
    package_data=package_data("badgr", ["static", "public"]),
)
