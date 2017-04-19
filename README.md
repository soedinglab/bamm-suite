About BaMM-suite
================

BaMM-suite is the motif finding suite developed by the Soedinglab

Dependencies
============

Running the commandline tools
-----------------------------

- backports.shutil_which (python2)


Building the documentation
-----------------
- sphinx
- sphinx-argparse
- sphinx_rtd_theme
- sphinxcontrib-autoprogram

Installing
==========

BaMM-suite is a python package and can be installed with pip.

    git clone https://github.com/soedinglab/bamm-wrapper.git
    cd bamm-wrapper
    pip install .


Building the documentation
==========================

An html version of the documentation can be built by running following commands from the root of the repository.

    cd docs
    make html

Usage of the commandline tools
==============================

BaMM-suite installs the command line script `bamm`. Run `bamm --help` for a list of available submodules.

License
=======

bamm-wrapper is licensed under the [GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/).
