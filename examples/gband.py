from sklearn.datasets import load_boston
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_score
import numpy as np
import argparse

from hyperspace.hyperdrive import hyperband


boston = load_boston()
X, y = boston.data, boston.target
n_features = X.shape[1]

reg = GradientBoostingRegressor(n_estimators=50, random_state=0)


def objective(params):
    """
    Objective function to be minimized.

    Parameters
    ----------
    * params [list, len(params)=n_hyperparameters]
        Settings of each hyperparameter for a given optimization iteration.
        - Controlled by hyperspaces's hyperdrive function.
        - Order preserved from list passed to hyperdrive's hyperparameters argument.
    """
    max_depth, learning_rate, max_features, min_samples_split, min_samples_leaf = params

    reg.set_params(max_depth=max_depth,
                   learning_rate=learning_rate,
                   max_features=max_features,
                   min_samples_split=min_samples_split,
                   min_samples_leaf=min_samples_leaf)

    return -np.mean(cross_val_score(reg, X, y, cv=5, n_jobs=-1,
                                    scoring="neg_mean_absolute_error"))


def main():
    hparams = [(2, 10),             # max_depth
               (10.0**-2, 10.0**0), # learning_rate
               (1, 10),             # max_features
               (2, 100),            # min_samples_split
               (1, 100)]            # min_samples_leaf

    result = hyperband(objective=objective,
                      space=hparams,
                      max_iter=81,
                      eta=2,
                      verbose=True,
                      random_state=0)

    print('Number of models evaluated: {}'.format(len(result)))


if __name__ == '__main__':
    main()