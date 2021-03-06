#!/usr/bin/env python

"""
Created in Feb 2017
@author: Markus Meier
"""

from collections import defaultdict
from enum import IntEnum
import numpy as np
import sys
import argparse
import glob
import os

IUPAC_ALPHABET_SIZE = 11

# an enum to encode the int representation of the iupac nucleotides


class IUPACNucleotide(IntEnum):
    A = 0
    C = 1
    G = 2
    T = 3
    S = 4
    W = 5
    R = 6
    Y = 7
    M = 8
    K = 9
    N = 10


# generates the map for the amiguous iupac nucleotides e.g.: N -> A, C, G, T
def init_representative_map():
    representative_iupac_nucleotides = defaultdict(list)
    representative_iupac_nucleotides[IUPACNucleotide.A].append(IUPACNucleotide.A)
    representative_iupac_nucleotides[IUPACNucleotide.C].append(IUPACNucleotide.C)
    representative_iupac_nucleotides[IUPACNucleotide.G].append(IUPACNucleotide.G)
    representative_iupac_nucleotides[IUPACNucleotide.T].append(IUPACNucleotide.T)
    representative_iupac_nucleotides[IUPACNucleotide.S].append(IUPACNucleotide.C)
    representative_iupac_nucleotides[IUPACNucleotide.S].append(IUPACNucleotide.G)
    representative_iupac_nucleotides[IUPACNucleotide.W].append(IUPACNucleotide.A)
    representative_iupac_nucleotides[IUPACNucleotide.W].append(IUPACNucleotide.T)
    representative_iupac_nucleotides[IUPACNucleotide.R].append(IUPACNucleotide.A)
    representative_iupac_nucleotides[IUPACNucleotide.R].append(IUPACNucleotide.G)
    representative_iupac_nucleotides[IUPACNucleotide.Y].append(IUPACNucleotide.C)
    representative_iupac_nucleotides[IUPACNucleotide.Y].append(IUPACNucleotide.T)
    representative_iupac_nucleotides[IUPACNucleotide.M].append(IUPACNucleotide.A)
    representative_iupac_nucleotides[IUPACNucleotide.M].append(IUPACNucleotide.C)
    representative_iupac_nucleotides[IUPACNucleotide.K].append(IUPACNucleotide.G)
    representative_iupac_nucleotides[IUPACNucleotide.K].append(IUPACNucleotide.T)
    representative_iupac_nucleotides[IUPACNucleotide.N].append(IUPACNucleotide.N)
    representative_iupac_nucleotides[IUPACNucleotide.N].append(IUPACNucleotide.N)
    representative_iupac_nucleotides[IUPACNucleotide.N].append(IUPACNucleotide.N)
    representative_iupac_nucleotides[IUPACNucleotide.N].append(IUPACNucleotide.N)
    return representative_iupac_nucleotides


# generates a map to translate the int representation of the iupac nucleotides to chars
def get_iupac_int2char():
    int2char = dict()
    int2char[IUPACNucleotide.A] = 'A'
    int2char[IUPACNucleotide.C] = 'C'
    int2char[IUPACNucleotide.G] = 'G'
    int2char[IUPACNucleotide.T] = 'T'
    int2char[IUPACNucleotide.S] = 'S'
    int2char[IUPACNucleotide.W] = 'W'
    int2char[IUPACNucleotide.R] = 'R'
    int2char[IUPACNucleotide.Y] = 'Y'
    int2char[IUPACNucleotide.M] = 'M'
    int2char[IUPACNucleotide.K] = 'K'
    int2char[IUPACNucleotide.N] = 'N'
    return int2char


# returns a sample bg model; mayhaps better to read from an external file?
def get_bg_model():
    bg_model = np.zeros(4)
    bg_model[IUPACNucleotide.A] = 0.2
    bg_model[IUPACNucleotide.C] = 0.3
    bg_model[IUPACNucleotide.G] = 0.3
    bg_model[IUPACNucleotide.T] = 0.2
    return bg_model


# init the profiles for the iupac nucleotides with the given bg_model
def init_iupac_profiles(representative_iupac_nucleotides, bg_model, c=0.2, t=0.7):
    iupac_profiles = np.zeros((IUPAC_ALPHABET_SIZE, 4), np.float)
    for iupac_c in range(IUPAC_ALPHABET_SIZE):
        rep = representative_iupac_nucleotides[iupac_c]
        for a in range(4):
            iupac_profiles[iupac_c][a] += c * bg_model[a]
            for r in rep:
                if a == r:
                    iupac_profiles[iupac_c][a] += t
    return iupac_profiles


# calculates the distance between two profiles; based on the Shannon Entropy?
def calculate_d(profile1, profile2):
    d = 0.0
    for a in range(4):
        d += (profile1[a] - profile2[a]) * (np.log2(profile1[a]) - np.log2(profile2[a]))
    return d


# finds for each profile in the pwm the closest iupac profile
def get_iupac_string(pwm, iupac_profiles, int2char):
    res = []
    pattern_length = len(pwm)
    for i in range(pattern_length):
        min_dist = np.inf
        min_iupac = 0
        for m in range(IUPAC_ALPHABET_SIZE):
            dist = calculate_d(pwm[i], iupac_profiles[m])
            if dist < min_dist:
                min_dist = dist
                min_iupac = m
        res.append(int2char[min_iupac])
    return "".join(res)


# extracts iupacs from meme file
def get_iupac_list(file):
    iupac_list = []
    with open(file) as fh:
        for line in fh:
            tokens = line.split()
            if len(tokens)>0:
                if tokens[0] == "MOTIF":
                    iupac_list.append(tokens[1])
    return iupac_list


# read the pwm from an external file
def read_pwm(filename, order):
    # for IUPAC presentation of 0th order contribution of a higher order model input file, only read every other order+1 line
    skipper = order+1
    pwm = []
    with open(filename) as fh:
        for line in fh:
            if skipper == order + 1:
                profile = np.zeros(4)
                tokens = line.split()
                if len(tokens) != 4:
                    print("ERROR: line does not seem to be part of a valid pwm, more than 4 nucleotides!!!", file=sys.stderr)
                    print("\t{}".format(line), file=sys.stderr)
                    exit(1)
                for i, token in enumerate(tokens):
                    profile[i] = float(token)
                EPSILON = 0.4
                if np.sum(profile) >= 1.0 + EPSILON or np.sum(profile) <= 1.0 - EPSILON:
                    print("ERROR: line does not seem to be part of a valid pwm, probabilities dont add up to 1!!!", file=sys.stderr)
                    print("\t{}".format(line), file=sys.stderr)
                    exit(1)
                pwm.append(profile)
            if skipper == 0:
                skipper = order + 1
            else:
                skipper = skipper - 1
    return pwm


# THE main ;)
def main():
    parser = argparse.ArgumentParser(description='Translates a PWM into an IUPAC identifier and prints it')
    parser.add_argument(metavar='MAIN_DIR', dest='maindir', type=str,
                        help='directory with motif files')
    parser.add_argument(metavar='PREFIX', dest='prefix', type=str,
                        help='prefix used to name output files')
    parser.add_argument(metavar='ORDER', dest='order', type=int,
                        help='order of the models represented in the motif files')
    parser.add_argument(metavar='MODE', dest='mode', type=str, 
                        default="BaMM", nargs='?',
                        help='define if input is meme or bamm format')

    args = parser.parse_args()

    maindir = args.maindir
    prefix = args.prefix
    order = args.order
    mode = args.mode

    # preparation
    representative_iupac_nucleotides = init_representative_map()
    int2char = get_iupac_int2char()
    bg_model = get_bg_model()
    iupac_profiles = init_iupac_profiles(representative_iupac_nucleotides, bg_model)

    outfile = ''.join([prefix, '.iupac'])
    os.chdir(maindir)
    with open(outfile, 'w') as fh:
        if mode == "BaMM":
            # get all motif file in the folder
            for file in glob.glob("*.ihbcp"):
                print(file)
                # read motif file
                end = file.split('_')[-1]
                motif_num = end.split('.')[0]
                pwm = read_pwm(file, order)
                iupac = get_iupac_string(pwm, iupac_profiles, int2char)
                line = ' '.join([prefix, motif_num, iupac, str(len(iupac)), '\n'])
                fh.write(line)
        else:
            if mode == "PWM":
                # get all motif file in the folder
                for file in glob.glob("*.meme"):
                    iupac_list = get_iupac_list(file)
                    motif_num = 1
                    for iupac in iupac_list:
                        line = ' '.join([prefix, str(motif_num), iupac, str(len(iupac)), '\n'])
                        motif_num = motif_num + 1
                        fh.write(line)


# if called as a script; calls the main method
if __name__ == '__main__':
    main()
