import argparse
import multiprocessing
import sys

from .utils import assert_binary_presence, execute_command
from . import argparse_helper as aph


N_CORES = multiprocessing.cpu_count()
PY2 = sys.version_info[0] == 2


class BaMMModule(object):

    subcommand = None
    aliases = []

    def __init__(self, parser, description=None, help=None):
        if PY2:
            subcommand_parser = parser.add_parser(
                self.subcommand,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                description=description,
                help=help
            )
        else:
            subcommand_parser = parser.add_parser(
                self.subcommand,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                description=description,
                help=help,
                aliases=self.aliases
            )

        subcommand_parser.set_defaults(subcommand_func=self)
        subcommand_parser.add_argument('--debug', action='store_true',
                                       help='print additional information for debugging')
        self.subcommand_parser = subcommand_parser

    def __call__(self, args):
        pass


class EvalModule(BaMMModule):
    subcommand = 'eval'

    def __init__(self, parser):
        help_msg = 'evaluate model performance'
        description = 'evaluate a crossvalidated model performance'
        super(EvalModule, self).__init__(parser, help=help_msg, description=description)
        scp = self.subcommand_parser
        scp.add_argument('some_file')

    def __call__(self, args):
        print('run evaluation module')


class PEnGModule(BaMMModule):
    subcommand = 'peng'

    def __init__(self, parser):
        help_msg = 'find overrepresented patterns'
        description = 'Finding overrepresented patterns in large sequence sets with PEnGmotif'
        super(PEnGModule, self).__init__(parser, help=help_msg, description=description)
        scp = self.subcommand_parser
        scp.add_argument('fasta_file', help='file with input sequences in fasta format',
                         type=aph.file_r)
        scp.add_argument('output_file', help='file output is written to',
                         type=aph.file_rw)

        basic_grp = scp.add_argument_group('basic options')
        basic_grp.add_argument('--pattern_length', '-w', default=8, type=aph.positive_integer,
                               help='length of patterns in bp')
        basic_grp.add_argument('--threads', '-t', type=aph.positive_integer, default=N_CORES,
                               help='set number of parallel threads')
        basic_grp.add_argument('--pos_strand_only', '-s', action='store_true',
                               help='do not scan the reverse complement for patterns')
        basic_grp.add_argument('--output_format', '-f', choices=['meme', 'json'], default='meme',
                               help='file format of the output file')
        basic_grp.add_argument('--bg_order', default=1, type=aph.non_negative_integer,
                               help='order of the background model')
        basic_grp.add_argument('--no_em', action='store_true',
                               help='do not optimize PWMs with em')

        tune_grp = scp.add_argument_group('tuning parameters')
        tune_grp.add_argument('--zscore_thresh', '-z', default=100, type=float,
                              help='set zscore threshold')
        tune_grp.add_argument('--bit_factor_thresh', '-b', default=0.75, type=float,
                              help='set bit factor threshold')
        tune_grp.add_argument('--em_dampening_factor', '-a', default=1000, type=float,
                              help='set the dampening factor of the em')
        tune_grp.add_argument('--em-convergence_thresh', default=0.08, type=float,
                              help='set convergence threshold of the em')
        tune_grp.add_argument('--em_max_iterations', default=100, type=aph.positive_integer,
                              help='set maximum number of em iterations')

    def __call__(self, args):
        assert_binary_presence('peng_motif')

        cmd = [
            'peng_motif',
            '%r' % args.fasta_file,
            '-t %s' % args.zscore_thresh,
            '-w %s' % args.pattern_length,
            '-bg-model-order %s' % args.bg_order,
            '-b %s' % args.bit_factor_thresh,
            '-a %s' % args.em_dampening_factor,
            '-em-threshold %s' % args.em_convergence_thresh,
            '-em-max-iterations %s' % args.em_max_iterations,
            '-threads %s' % args.threads,
        ]
        if args.output_format == 'json':
            cmd.append('-j %r' % args.output_file)
        else:
            cmd.append('-o %r' % args.output_file)

        if args.pos_strand_only:
            cmd.append('-strand PLUS')

        execute_command(cmd, debug=args.debug)
