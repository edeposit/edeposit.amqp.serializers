#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path
import shutil

from setuptools import setup, find_packages
from distutils.command.sdist import sdist


version = '1.0.0'
long_description = "\n\n".join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read()
])


class BuildSphinx(sdist):
    """
    Generates sphinx documentation, puts it into html_docs/, packs it to
    package and removes unused directory.
    """
    def run(self):
        d = os.path.abspath('.')
        DOCS = d + "/" + "docs"
        DOCS_IN = DOCS + "/build/html"
        DOCS_OUT = d + "/html_docs"

        if not self.dry_run:
            print "Generating the documentation .."

            os.chdir(DOCS)
            os.system("make clean")
            os.system("make html")

            if os.path.exists(DOCS_OUT):
                shutil.rmtree(DOCS_OUT)

            shutil.copytree(DOCS_IN, DOCS_OUT)
            os.chdir(d)

        sdist.run(self)

        if os.path.exists(DOCS_OUT):
            shutil.rmtree(DOCS_OUT)


setup(
    name='edeposit.amqp.serializers',
    version=version,
    description="E-Deposit's AMQP definitions and common classes/patterns.",
    long_description=long_description,
    url='https://github.com/edeposit/edeposit.amqp.serializers/',

    author='Edeposit team',
    author_email='edeposit@email.cz',

    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    license='GPL2+',

    packages=find_packages("src"),
    package_dir={'': 'src'},

    namespace_packages=[
        'edeposit',
        'edeposit.amqp'
    ],
    include_package_data=True,

    zip_safe=False,
    install_requires=[
        'setuptools'
    ],

    extras_require={
        "test": [
            "unittest2",
            "robotsuite",
            "mock",
            "robotframework-httplibrary"
        ],
        "docs": [
            "sphinxcontrib-napoleon",
            "sphinx",
        ]
    },

    cmdclass={'sdist': BuildSphinx}
)
