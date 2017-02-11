from bamm_wrapper import __version__
from setuptools import setup

setup(
    name='bamm_wrapper',
    version=__version__,
    description='wrapper script for the bamm-suite',
    author='Christian Roth',
    license='GPLv3',
    entry_points={
        'console_scripts': [
            'bamm = bamm_wrapper.wrapper:main'
        ]
    },
    packages=['bamm_wrapper'],
    test_suite='nose.collector',
)
