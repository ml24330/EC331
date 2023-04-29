from scipy import optimize
import numpy as np
from random import choices
from copy import deepcopy
from .median import *
import traceback
from .dump import *



def get_loss_function(covariates, upper_dict, lower_dict, cef):
    """
    Loss function according to Haile & Tamer 2003

    Parameters
    --------
    covariates : list of auction covariates corresponding to each bid
    upper_dict : dictionary containing upper bounds of conditional mean/median
    lower_dict : dictionary containing lower bounds of conditional mean/median
    cef : callable that resembles a conditional mean/median function in bidder valuation
    --------

    Returns
    --------
    _sum : total loss of input parameters, weighted as quadratic violations to estimated bounds
    --------
    """
    _sum = 0
    for covariate in covariates:
        upper = upper_dict[f"{covariate}"]
        lower = lower_dict[f"{covariate}"]
        if cef(covariate) > upper:
            _sum += (cef(covariate)-upper)**2
        if cef(covariate) < lower:
            _sum += (cef(covariate)-lower)**2
    return _sum



def get_estimates(loss_function, n_cov, x0):
                
    b_hat = optimize.minimize(loss_function, x0).x
    
    estimates = []

    for j in range(n_cov):

        def obj(b):
            _b = deepcopy(b_hat)
            _b[j] = b
            return loss_function(_b)-loss_function(b_hat)-0.1
        
        interval_lower = optimize.newton(obj, b_hat[j]-5)
        interval_upper = optimize.newton(obj, b_hat[j]+5)

        estimates.append(interval_lower)
        estimates.append(interval_upper)

    return (b_hat, estimates)


def bootstrap(bids, covariates, incremented, n_covs, cefs, repetition, name):
    
    estimated_intervals = []
    
    data_pairs = [(bid, covariate, increment) for bid, covariate, increment in zip(bids, covariates, incremented)]

    for i in range(repetition):
        
        resampled = choices(data_pairs, k=len(bids))
        
        for n in set([len(b) for b in bids]):
        
            police_listing_n = [(b,c,i) for b,c,i in zip(bids, covariates, incremented) if c[0] == 1.0 and len(b) == n][0]

            covariates_n = set([listing[1][0] for listing in resampled if len(listing[0]) == n])
            if not 1 in covariates_n:
                resampled.append(police_listing_n)
        
        _bids = [r[0] for r in resampled]
        _covariates = [r[1] for r in resampled]
        _incremented = [r[2] for r in resampled]

        try:

            median_upper, median_lower = estimate_median(_bids, _covariates, _incremented, (-4,6))

            dump(_covariates, median_lower, median_upper, f"bootstrap_{name}_{i}")

            results = []

            for cef, n_cov in zip(cefs, n_covs):
            
                loss_function = lambda c: get_loss_function(_covariates, median_upper, median_lower, lambda cov: cef(c, cov))
                
                _, estimates = get_estimates(loss_function, n_cov)

                results.append(estimates)
            
            estimated_intervals.append(results)

        except Exception as e:
            print(f"An error occurred while calculating intervals on iteration {i}")
            print(e)
            # print(traceback.format_exc())


    return (estimated_intervals)



def bootstrap2(bids, covariates, incremented, _range, n_covs, cefs, repetition, name):
    
    estimated_intervals = []
    
    data_pairs = [(bid, covariate, increment) for bid, covariate, increment in zip(bids, covariates, incremented)]

    for i in range(repetition):
        
        resampled = choices(data_pairs, k=len(bids))
                
        _bids = [r[0] for r in resampled]
        _covariates = [r[1] for r in resampled]
        _incremented = [r[2] for r in resampled]

        try:

            median_upper, median_lower = estimate_median(_bids, _covariates, _incremented, _range)

            dump(_covariates, median_lower, median_upper, f"bootstrap_{name}_{i}")

            results = []

            for cef, n_cov in zip(cefs, n_covs):
            
                loss_function = lambda c: get_loss_function(_covariates, median_upper, median_lower, lambda cov: cef(c, cov))
                
                _, estimates = get_estimates(loss_function, n_cov)

                results.append(estimates)
            
            estimated_intervals.append(results)

        except Exception as e:
            print(f"An error occurred while calculating intervals on iteration {i}")
            print(e)
            # print(traceback.format_exc())


    return (estimated_intervals)


def report_intervals(estimates, cv):

    conf_intervals = []

    n_cov = len(estimates[0])

    for i in range(int(n_cov/2)):

        lower = [e[2*i+0] for e in estimates]
        upper = [e[2*i+1] for e in estimates]

        print(f"{cv}% confidence interval for variable {i}:")
        print(f"[{np.percentile(lower, (100-cv)/2)}, {np.percentile(upper, 100-(100-cv)/2)}]")
        conf_intervals.append([np.percentile(lower, (100-cv)/2), np.percentile(upper, 100-(100-cv)/2)])

    return conf_intervals