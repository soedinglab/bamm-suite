import numpy as np
from itertools import permutations


def read_BaMM(handle, max_order=100):
    positions = []
    for line in handle:
        model = {}
        cur_order = 0
        if line.startswith('#'):
            continue
        while line != '\n' and line != '':
            if cur_order <= max_order:
                model[cur_order] = np.array(line.split(), dtype=float)
            cur_order += 1
            line = handle.readline()
        positions.append(model)
    return BaMM(positions)

def ind(s):
    """
    Computes the index.
    """
    indict = {"A" : 0, "C" : 1, "G" : 2, "T": 3}
    ind = 0
    e = 0
    for c in s:
        ind += indict[c] << e
        e += 1
    return ind

def kld_bamm_order(p_cp, p_j, p_bg, position=0, order=0):
    """
    Computes the Kullback-Leibler Divergence for a given order.
    : param p_cp : Conditional probabilities as dict
    : param p_j  : Joint probabilities as dict
    : param p_bg : Background probabilities as dict
    : param order: Order for which the KLB is computed.
    """
    alphabet = "ACGT"
    H = 0
    if order == 0:
        for letter in alphabet:
            index = ind(letter)
            H += p_j.get_data(position,order)[index] * np.log2(p_j.get_data(position, order)[index] / p_bg.get_data(position, order)[index])
        return H
    indices = permutations(alphabet, order)
    for index in indices:
        # Usually the index needs to be inverted, but since we are going over allpossible outcomes, it doesn't matter.
        index = "".join(index)
        prev_ind = ind(index[1:])
        index = ind(index)
        p_joint = p_j.get_data(position, order)[index]
        p_cond_current = p_cp.get_data(position, order)[index]
        p_cond_prev = p_cp.get_data(position, order - 1)[prev_ind]
        p_back_current =  p_bg.get_data(position, order)[index]
        p_back_prev = p_bg.get_data(position, order - 1)[prev_ind] 
        H += p_joint * np.log2(p_cond_current * p_back_prev / (p_cond_prev * p_back_current))
    return H

def kld_bamm(bw_p_cp, bw_p_j, bw_p_bg, position=0, order=0):
    """
    Computes the Kullback-Leibler-Divergence up to the specified order.
    : param p_cp : Conditional probabilities
    : param p_j  : Joint probabilities
    : param p_bg : Background probabilities
    : param order: Order for which the KLB is computed
    """
    H = 0
    (maxorder, stuff_at_end) = (bw_p_cp.max_order(), True) if bw_p_cp.max_order() < order else (order, False)
    H += sum([kld_bamm_order(bw_p_cp, bw_p_j, bw_p_bg, position, x) for x in range(maxorder + 1)])
    if stuff_at_end:
        H += (order - bw_p_cp.max_order()) * kld_bamm_order(bw_p_cp, bw_p_j, bw_p_bg, position, maxorder)
    return H


class BaMM:
    def __init__(self, data):
        self._data = data

    def __getitem__(self, key):
        if key in self._data.keys():
            return self._data[key]
        return None

    def toPWM(self):
        zero_order_list = [p[0] for p in self._data]
        return np.vstack(zero_order_list)

    def get_data(self, position=0, order=0):
        return self._data[position][order]

    def max_order(self):
        return len(self._data[0]) - 1



