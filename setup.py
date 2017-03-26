from bamm_wrapper import __version__
from setuptools import setup, find_packages

setup(
    name='bamm_suite',
    version=__version__,
    description='bamm-suite for de-novo motif discovery',
    author='Christian Roth',
    license='GPLv3',
    entry_points={
        'console_scripts': [
            'bamm = bamm_wrapper.wrapper:main'
        ]
    },
    packages=find_packages(),
    test_suite='nose.collector',
)
