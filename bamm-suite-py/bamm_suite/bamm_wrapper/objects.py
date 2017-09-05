import numpy as np


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


class BaMM:
    def __init__(self, data):
        self._data = data

    def toPWM(self):
        zero_order_list = [p[0] for p in self._data]
        return np.vstack(zero_order_list)

    def get_data(self, position=0, order=0):
        return self._data[position][order]
