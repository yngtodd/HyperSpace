import numbers
from enum import Enum
import numpy as np

from skopt.space import Dimension
from skopt.space import Space

from .space import HyperInteger
from .space import HyperReal
from .space import HyperCategorical


class SpaceType(Enum):
    INTEGER = 0
    REAL = 1
    CATEGORICAL = 2


class Factory:
    """
    Factory for building hyperspaces.

    Parameters
    ----------
    * `space_type` [`INTEGER`, `REAL`, or `CATEGORICAL`, SpaceType object]:

    * `**kwargs`
        keyword arguments to be passed to each of the HyperClasses.

    Returns
    -------
    * hyperspace_low, hyperspace_high [`Integer`, `Real`, or `Categorical` Scikit-Optimize object]:
    """
    def get_space(self, space_type, **kwargs):
        if space_type == SpaceType.INTEGER:
            hyper_int = HyperInteger(**kwargs)
            return hyper_int.get_hyperspace()
        elif space_type == SpaceType.REAL:
            hyper_real = HyperReal(**kwargs)
            return hyper_real.get_hyperspace()
        elif space_type == SpaceType.CATEGORICAL:
            hyper_cat = HyperCategorical(**kwargs)
            return hyper_cat.get_hyperspace()
        else:
            raise NotImplementedError("Unknown space type.")


def check_dimension(dimension, transform=None):
    """
    Turn a provided dimension description into a dimension object.
    Checks that the provided dimension falls into one of the
    supported types. For a list of supported types, look at
    the documentation of ``dimension`` below.
    If ``dimension`` is already a ``Dimension`` instance, return it.

    Parameters
    ----------
    * `dimension`:
        Search space Dimension.
        Each search dimension can be defined either as
        - a `(lower_bound, upper_bound)` tuple (for `Real` or `Integer`
          dimensions),
        - a `(lower_bound, upper_bound, "prior")` tuple (for `Real`
          dimensions),
        - as a list of categories (for `Categorical` dimensions), or
        - an instance of a `Dimension` object (`Real`, `Integer` or
          `Categorical`).

    * `transform` ["identity", "normalize", "onehot" optional]:
        - For `Categorical` dimensions, the following transformations are
          supported.
          - "onehot" (default) one-hot transformation of the original space.
          - "identity" same as the original space.
        - For `Real` and `Integer` dimensions, the following transformations
          are supported.
          - "identity", (default) the transformed space is the same as the
            original space.
          - "normalize", the transformed space is scaled to be between 0 and 1.

    Returns
    -------
    * `dimension`:
        Dimension instance.
    """
    if isinstance(dimension, Dimension):
        return dimension

    if not isinstance(dimension, (list, tuple, np.ndarray)):
        raise ValueError("Dimension has to be a list or tuple.")

    if len(dimension) == 2:
        if any([isinstance(d, (str, bool)) for d in dimension]):
            hyper_cat = HyperCategorical(dimension, transform=transform)
            return hyper_cat.get_hyperspace()
        elif all([isinstance(dim, numbers.Integral) for dim in dimension]):
            hyper_int = HyperInteger(*dimension, transform=transform)
            return hyper_int.get_hyperspace()
        elif any([isinstance(dim, numbers.Real) for dim in dimension]):
            hyper_real = HyperReal(*dimension, transform=transform)
            return hyper_real.get_hyperspace()
        else:
            raise ValueError("Invalid dimension {}. Read the documentation for"
                             " supported types.".format(dimension))

    if len(dimension) == 3:
        if (any([isinstance(dim, (float, int)) for dim in dimension[:2]]) and
            dimension[2] in ["uniform", "log-uniform"]):
            hyper_real = HyperReal(*dimension, transform=transform)
            return hyper_real.get_hyperspace()
        else:
            hyper_cat = HyperCategorical(dimension, transform=transform)
            return hyper_cat.get_hyperspace()

    if len(dimension) > 3:
        hyper_cat = HyperCategorical(dimension, transform=transform)
        return hyper_cat.get_hyperspace()

    raise ValueError("Invalid dimension {}. Read the documentation for "
                     "supported types.".format(dimension))


def fold_spaces(low_spaces, high_spaces):
    """
    Creates all possible combinations of hyperspaces.

    Parameters
    ----------
    * `low_spaces` [list, shape=(n_spaces,)]:
        lower spaces defined by hyperspace classes.

    * `high_spaces` [list, shape=(n_spaces,)]:
        lower spaces defined by hyperspace classes.

    Returns
    -------
    * `hyperspace` [`list of lists`, shape=(2**n_spaces, n_spaces)]:
        - All combinations of hyperspaces. Each list within hyperspace
          is a search space to be distributed across 2**n_spaces nodes.
    """
    if len(low_spaces)  != len(high_spaces):
        raise ValueError(("low_spaces and high_spaces must have the same length. "
                         "Got {} and {} respectively.".format(len(low_spaces), len(high_spaces))))

    indices = len(low_spaces)
    num_hyperspaces = 2**indices
    hyperspace = [[] for i in range(num_hyperspaces)]

    for space in range(num_hyperspaces):
        for index in range(indices):
            bit_tester = 1 << index
            if space & bit_tester:
                hyperspace[space].insert(index, low_spaces[index])
            else:
                hyperspace[space].insert(index, high_spaces[index])

    return hyperspace


def create_hyperspace(hyperparameters):
    """
    Converts hyperparameter lists to Scikit-Optimize Space instances.

    Parameters
    ----------
    * `hyperparameters` [list, shape=(n_hyperparameters,)]

    Returns
    -------
    * `hyperspace` [list of lists, shape(n_spaces, n_hyperparameters)]
        - All combinations of hyperspaces. Each list within hyperspace
          is a search space to be distributed across 2**n_spaces nodes.
    """
    hparams_low = []
    hparams_high = []
    for hparam in hyperparameters:
        low, high = check_dimension(hparam)
        hparams_low.append(low)
        hparams_high.append(high)

    all_spaces = fold_spaces(hparams_low, hparams_high)

    hyperspace = []
    for space in all_spaces:
        hyperspace.append(Space(space))

    return hyperspace
