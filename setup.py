from bamm_suite import __version__
from setuptools import setup, find_packages

setup(
    name='bamm_suite',
    version=__version__,
    description='bamm-suite for de-novo motif discovery',
    author='Christian Roth',
    license='GPLv3',
    entry_points={
        'console_scripts': [
            'bamm = bamm_suite.bamm_wrapper.wrapper:main',

            # standalone scripts
            'db_search = bamm_suite.db_search.db_search:main',
            'meme2models = bamm_suite.db_search.meme2models:main',
        ]
    },
    packages=find_packages(),
    test_suite='nose.collector',
)
