# About BaMM-suite
BaMM-suite is the motif finding suite developed by the Soedinglab.

This repository is the entry point to the BaMM universe. Here you can find documentation, common functionality and helper scripts and a clean interface into the BaMM world.

# Dependencies

## Build dependencies
- cmake
- python >= 3.3

## Building the documentation
- sphinx
- sphinx-argparse
- sphinx_rtd_theme
- sphinxcontrib-autoprogram

# Installing

## Cloning the repository
```bash
   git clone https://github.com/soedinglab/bamm-suite.git
```

## Python package
BaMM-suite is a python package and can be installed with pip.
```bash
    cd bamm-suite
    pip install bamm-suite-py
```

## Helper scripts
To install all helper scripts into `/user/bin`, you would do:
```bash
   mkdir build_cmake && cd build_cmake
   cmake -DCMAKE_INSTALL_PREFIX:PATH=/user ..
   make install
```

# Building the documentation
An html version of the documentation can be built by running following commands from the root of the repository.

    cd docs
    make html

# Usage of the commandline tools
BaMM-suite installs the command line script `bamm`. Run `bamm --help` for a list of available submodules.

# License
bamm-wrapper is licensed under the [GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/).
