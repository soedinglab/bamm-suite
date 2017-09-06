import argparse
import sys

from . import modules
from bamm_suite import __version__


def create_parser():
    parser = argparse.ArgumentParser(
        'bamm',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    subparser = parser.add_subparsers(title='subcommands')
    module_classes = [
        modules.PEnGModule,
        modules.BaMMModule,
        modules.SearchModule,
        modules.DBSearchModule,
        modules.EvalModule,
        modules.LogoModule,
        modules.PrecomputeModule,
        modules.PostprocessModule,
    ]

    for mod_cls in module_classes:
        mod_cls(subparser)
    parser.add_argument('--version', action='version',
                        version=__version__)
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if not sys.argv[1:]:
        args = parser.parse_args(['--help'])
    else:
        args = parser.parse_args()

    args.subcommand_func(args)

if __name__ == '__main__':
    main()
