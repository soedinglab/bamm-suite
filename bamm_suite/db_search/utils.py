import numpy as np
from scipy.special import xlogy

loge2 = np.log(2)


def calculate_H_model_bg(model, bg):
    H = xlogy(model, model).sum(axis=1) / loge2
    H += xlogy(bg, bg).sum() / loge2
    H *= 0.5
    p_bar = 0.5 * (model + bg)
    H -= xlogy(p_bar, p_bar).sum(axis=1) / loge2
    return H


def calculate_H_model(model):
    H = 0.5 * xlogy(model, model).sum(axis=1) / loge2
    return H


def create_slices(m, n, min_overlap):

    # m, n are the lengths of the patterns
    # we demand that n is not longer than m
    assert m >= n

    # obviously it's not possible to overlap in this case
    if n < min_overlap:
        return

    # the shorter pattern can be shifted m - n + 1 inside the longer pattern
    for i in range(m - n + 1):
        yield slice(i, i + n), slice(0, n)

    # these are the patterns overlapping the edges with at least min_overlap
    # nucleotides
    for ov in range(min_overlap, n):
        yield slice(0, ov), slice(-ov, None)
        yield slice(-ov, None), slice(0, ov)


def model_sim(model1, model2, H_model1_bg, H_model2_bg, H_model1, H_model2, min_overlap=2):

    # my design model2 cannot be longer than model1
    if len(model1) < len(model2):
        model1, model2 = model2, model1

    scores = []
    for sl1, sl2 in create_slices(len(model1), len(model2), min_overlap):
        total_score = 0
        # so we want the contributions of the background
        total_score += H_model1_bg[sl1].sum()
        total_score += H_model2_bg[sl2].sum()

        # and the contributions of model1 vs. model2
        total_score -= H_model1[sl1].sum()  # entropy of model1
        total_score -= H_model2[sl2].sum()  # entropy of model2

        # cross entropy part
        p_bar = 0.5 * (model1[sl1, :] + model2[sl2, :])
        p_bar_entropy = xlogy(p_bar, p_bar) / loge2
        total_score += p_bar_entropy.sum()

        scores.append(total_score)

    return max(scores)
