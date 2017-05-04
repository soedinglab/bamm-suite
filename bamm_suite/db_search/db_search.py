import argparse
import json
import numpy as np

from bamm_suite.db_search.utils import calculate_H_model_bg, calculate_H_model, model_sim


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_models')
    parser.add_argument('model_db')
    parser.add_argument('--n_neg_perm', type=int, default=10)
    parser.add_argument('--highscore_fraction', type=float, default=0.1)
    parser.add_argument('--evalue_threshold', type=float, default=0.1)
    parser.add_argument('--seed', type=int, default=42)
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    np.random.seed(args.seed)

    highscore_fraction = args.highscore_fraction
    evalue_thresh = args.evalue_threshold

    def update_models(models):
        for model in models:
            model['pwm'] = np.array(model['pwm'], dtype=float)
            model['bg_freq'] = np.array(model['bg_freq'], dtype=float)
            if 'H_model_bg' not in model or 'H_model' not in model:
                model['H_model_bg'] = calculate_H_model_bg(model['pwm'], model['bg_freq'])
                model['H_model'] = calculate_H_model(model['pwm'])
            else:
                model['H_model_bg'] = np.array(model['H_model_bg'], dtype=float)
                model['H_model'] = np.array(model['H_model'], dtype=float)
        return models

    with open(args.input_models) as in_models:
        models = update_models(json.load(in_models))

    with open(args.model_db) as model_db:
        db_models = update_models(json.load(model_db))
        db_size = len(db_models)

    rev_models = []
    for model in models:
        rev_model = dict(model)
        rev_model['model_id'] = model['model_id'] + '_rev'
        # reverse complement the pwm
        rev_model['pwm'] = model['pwm'][::-1, ::-1]

        # entropy calculations simply reverse
        rev_model['H_model_bg'] = model['H_model_bg'][::-1]
        rev_model['H_model'] = model['H_model'][::-1]
        rev_models.append(rev_model)

    # intertwine models and rev. complemented models
    models = [model for pair in zip(models, rev_models) for model in pair]

    print('model_id', 'db_id', 'simscore', 'e-value', sep='\t')
    for model in models:
        pwm = model['pwm']
        model_id = model['model_id']
        bg_freq = model['bg_freq']
        model_len = len(pwm)
        H_model = model['H_model']
        H_model_bg = model['H_model_bg']

        # step 1: use shuffled pwms to estimate the p-value under the null.
        shuffled_dists = []
        for _ in range(args.n_neg_perm):
            # calculate a locality preserving permutation
            assert model_len > 1
            Z = np.random.normal(0, 1, model_len)
            shuffle_ind = np.argsort(2 * Z - np.arange(model_len))

            shuffle_pwm = pwm[shuffle_ind]
            H_shuffle_bg = calculate_H_model_bg(shuffle_pwm, bg_freq)
            H_shuffle = calculate_H_model(shuffle_pwm)

            for db_model in db_models:
                shuf_sim = model_sim(
                    shuffle_pwm, db_model['pwm'],
                    H_shuffle_bg, db_model['H_model_bg'],
                    H_shuffle, db_model['H_model']
                )
                shuffled_dists.append(shuf_sim)

        # we are fitting only the tail of the null scores with an exponential
        # distribution
        sorted_null = np.sort(shuffled_dists)
        N_neg = len(sorted_null)
        high_scores = sorted_null[-int(N_neg * highscore_fraction):]
        high_score = high_scores[0]
        exp_lambda = 1 / np.mean(high_scores - high_score)

        # TODO remove debug code
        #with open('/tmp/data.pkl', 'wb') as data:
        #    import pickle
        #    pickle.dump([sorted_null, high_score, exp_lambda], data)

        # run pwm against the database
        for db_model in db_models:
            sim = model_sim(
                pwm, db_model['pwm'],
                H_model_bg, db_model['H_model_bg'],
                H_model, db_model['H_model']
            )
            if sim < high_score:
                # the score is not in the top scores of the background model
                # this is surely not a significant hit
                continue

            pvalue = highscore_fraction * np.exp(- exp_lambda * (sim - high_score))
            evalue = db_size * pvalue
            if evalue < evalue_thresh:
                print(model_id, db_model['model_id'], sim, evalue, sep='\t')


if __name__ == '__main__':
    main()
