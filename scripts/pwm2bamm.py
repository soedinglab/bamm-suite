#!/usr/bin/env python

'''
This is a script to convert PWMs from a MEME-formated file to BaMM-formated files.
The only input is a MEME-formated file (version 4)
Written by Wanwan Ge
'''

import argparse
import os
import re
import numpy as np

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('meme_file')
    parser.add_argument('-o', default=None)
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    ipath = args.meme_file
    if args.o is None:
        dir = os.path.dirname(ipath)
    else:
        dir = args.o
        if not os.path.exists(dir):
            os.makedirs(dir)
    basename = os.path.splitext(os.path.basename(ipath))[0]
    motifset = parse_meme(ipath)
    models = motifset['models']
    for num in range(len(models)):
        filepath_v = os.path.join(dir, basename + "_motif_" + str(num+1) + ".ihbcp")
        filepath_p = os.path.join(dir, basename + "_motif_" + str(num+1) + ".ihbp")
        write_bamm(models[num]['pwm'], filepath_v )
        write_bamm(models[num]['pwm'], filepath_p )

def parse_meme(meme_input_file):
    dataset = {}
    with open(meme_input_file) as handle:
        line = handle.readline()
        if line.strip() != 'MEME version 4':
            raise ValueError('requires MEME minimal file format version 4')
        else:
            dataset['version'] = line.strip()
        # skip the blank line
        line = handle.readline()
        # read in the ALPHABET info
        dataset['alphabet'] = handle.readline().split()[1]
        # skip the blank line
        line = handle.readline()
        # read in the background letter frequencies
        line = handle.readline()
        if line != 'Background letter frequencies\n':
            # if not given, assign 0.25 to each letter
            dataset['bg_freq'] = [0.25,0.25,0.25,0.25]
            bg_freqs = dataset['bg_freq']
        else:
            bg_toks = handle.readline().split()[1::2]
            bg_freqs = [float(f) for f in bg_toks]
            dataset['bg_freq'] = bg_freqs
        # parse pwms
        width_pat = re.compile('w= (\d+)')
        models = []
        for line in handle:
            if line.startswith('MOTIF'):
                model = {}
                model['model_id'] = line.split()[1]
                model['bg_freq'] = bg_freqs
                info_line = handle.readline().rstrip('\n')
                model['info'] = info_line
                width_hit = width_pat.search(info_line)
                if not width_hit:
                    raise MalformattedMemeError('could not read motif width')
                pwm_length = int(width_hit.group(1))
                pwm = []
                for i in range(pwm_length):
                    pwm.append([float(p) for p in handle.readline().split()])
                pwm_arr = np.array(pwm, dtype=float)
                bg_arr = np.array(bg_freqs, dtype=float)
                model['pwm'] = pwm
                models.append(model)
        dataset['models'] = models
    return dataset


def write_bamm(pwm, ofile):
    eps = 1e-16
    with open(ofile, "w") as fh:
        for i in range(len(pwm)):
            print(' '.join(['{:.4e}'.format(x+eps) for x in pwm[i]]) + ' \n', file=fh)
 

if __name__ == '__main__':
    main()

