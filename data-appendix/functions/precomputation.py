import sympy as sp
import numpy as np
import time
import math
import json

def cdf(H, i, n):
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
    exp = outside*func-H
    
    try:
        ans = [s for s in sp.real_roots(exp) if 0<=s<=1][0]
    except:
        ans = 1

    return float(ans)


precomputed = {}

for n in range(1,19):
    for i in range(1,n+1):
        for H in np.linspace(0,1,num=5001):
            value = cdf(H, i, n)
            precomputed[f"{i}_{n}_{H}"] = value
            
            if H*100 % 5 == 0:
                print(f"calculated value for {i}_{n}_{H}, value is {value}")

_precomputed = dict()

for key in precomputed.keys():
    i, n, H = key.split("_")
    new_H = round(round(float(H) / 0.0002) * 0.0002, -int(math.floor(math.log10(0.0002))))
    _precomputed[f"{i}_{n}_{new_H}"] = precomputed[key]


with open('precomputed_2.json', 'w') as fp:
    json.dump(_precomputed, fp)