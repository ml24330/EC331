### Helper functions

- `__init__.py` exports the module.
- `bootstrap.py` contains functionalities relevant to bootstrapping and obtaining interval estimates & confidence intervals via minimising a loss function.
- `cdf_mapping.py` contains implementations of the implicit map taking the CDF of an order statistic to the CDF of its parent distribution.
- `dist.py` contains code for estimating joint distributions via kernels.
- `dump.py` implements code to dump calculated upper and lower bounds as `.json` files.
- `FastMean.py` contains a class intended to speed up mean calculation given an arbitrary CDF.
- `get_pdfs.py` contains code used to obtain kernel estimated densities of order statistics of observed bids.
- `mean.py` contains code used to implement the estimation of conditional expectation functions.
- `median.py` contains code used to implement the estimation of conditional median functions.
- `precomputation.py` pre-calculates input-output pairs associated with the implicit map taking the CDF of an order statistic to the CDF of its parent distribution and stores the results in `precomputated_2.json` as key-value pairs, which allows for faster calculation of this function by replacing the need for symbolic differentiation by looking up a hash table.
- `transform_covariates.py` contains code used to reduce the number of possible unique covariates for the purpose of speeding up estimation.