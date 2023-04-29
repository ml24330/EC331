import numpy as np
import sympy as sp
import math
import json
import os


with open(os.path.join(os.path.dirname(__file__), "precomputed_2.json")) as f_in:
    precomputed =  json.load(f_in)

def cdf(x, order_statistic_cdf, i, n):
    """
    Returns the CDF of the parent distribution evaluated at point x given the CDF of the i:n order distribution
        This function looks up a precomputed dictionary of input-output pairs
    
    Parameters
    -------
    x : scalar that is within the support of the parent (and thus the order statistic) distribution
    order_statistic_cdf : callable that corresponds to the CDF of an order statistic
    i : integer that indicates the ith largest order statistic
    n : integer that indicates the total number of observations
    -------
    """

    f_x = min(order_statistic_cdf(x),1)
    nearest = round(round(f_x / 0.0002) * 0.0002, -int(math.floor(math.log10(0.0002))))

    return precomputed[f"{i}_{n}_{nearest}"]

def _cdf(x, order_statistic_cdf, i, n):
    """
    Returns the CDF of the parent distribution evaluated at point x given the CDF of the i:n order distribution

    Parameters
    -------
    x : scalar that is within the support of the parent (and thus the order statistic) distribution
    order_statistic_cdf : callable that corresponds to the CDF of an order statistic
    i : integer that indicates the ith largest order statistic
    n : integer that indicates the total number of observations
    -------
    """
    t = sp.Symbol('t')
    f = sp.Symbol('f')
    outside = np.math.factorial(n)/(np.math.factorial(i-1)*np.math.factorial(n-i))
    integrand = (t**(i-1)) * ((1-t)**(n-i))

    func = sp.integrate(integrand, (t,0,f))
    exp = outside*func-order_statistic_cdf(x)
    try:
        ans = [s for s in sp.real_roots(exp) if 0<=s<=1][0]
    except:
        ans = 1

    return float(ans)

def get_cdf(order_statistic_cdf, i, n):
    """
    Wrapper function for cdf that returns a callable of the estimated CDF of the parent distribution

    Parameters
    -------
    order_statistic_cdf : callable that corresponds to the CDF of an order statistic
    i : integer that indicates the ith largest order statistic
    n : integer that indicates the total number of observations
    -------
    """
    print(f"called with i={i}")
    return lambda x: cdf(x, order_statistic_cdf, i, n)