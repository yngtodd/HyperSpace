import argparse
import numpy as np

from hyperspace import hyperbelt 
from hyperspace.benchmarks import StyblinskiTang 


def main():
    parser = argparse.ArgumentParser(description='Setup experiment.')
    parser.add_argument('--ndims', type=int, help='Number of dimensions for Styblinski-Tang function')
    parser.add_argument('--results_dir', type=str, help='Path to results directory.')
    args = parser.parse_args()

    stybtang = StyblinskiTang(args.ndims)
    bounds = np.tile((-5., 5.), (args.ndims, 1))

    hyperbelt(objective=stybtang,
              hyperparameters=bounds,
              results_path=args.results_dir,
              model="RAND",
              n_iterations=50,
              sampler='lhs',
              n_samples=2,
              model_verbose=False,
              hyperband_verbose=True,
              random_state=0)


if __name__ == '__main__':
    main()

