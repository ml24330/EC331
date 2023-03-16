from scipy import stats, integrate, interpolate, optimize
import numpy as np
import sympy as sp
import json
import math
import time

with open("precomputed_2.json") as f_in:
    precomputed =  json.load(f_in)

def EBAY_INCREMENT(current):
    if current < 1:
        return current+0.05
    elif current < 5:
        return current+0.2
    elif current < 15:
        return current+0.5
    elif current < 60:
        return current+1
    elif current < 150:
        return current+2
    elif current < 300:
        return current+5
    elif current < 600:
        return current+10
    elif current < 1500:
        return current+20
    elif current < 3000:
        return current+50
    else:
        return current+100

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
    return lambda x: cdf(x, order_statistic_cdf, i, n)

class FastMean(stats.rv_continuous):
    """
    Subclass inheriting from scipy.stats.rv_continuous to speed up mean calculation

    Parameters (for __init__):
    -------
    discrete_cdf : list of values corresponding to the CDF of a random variable evaluated at certain points
    values : list of values corresponding to locations where discrete_cdf was evaluated
    -------


    Methods
    -------
    _cdf : callable of interpolated CDF that overrides the inherited _cdf method
    _ppf : callable of interpolated PPF that overrides the inherited _ppf method
    -------
    """
    
    def __init__(self, discrete_cdf, values):
        super().__init__()
        self.discrete_cdf = discrete_cdf
        self.values = values
        
    def _cdf(self, x):
        cdf = interpolate.interp1d(self.values, self.discrete_cdf, bounds_error=False, fill_value=(0,1))
        return cdf(x)
    
    def _ppf(self, y):
        ppf = interpolate.interp1d(self.discrete_cdf, self.values, bounds_error=False, fill_value="extrapolate")
        return ppf(y)

def get_conditional_pdf(y, x):
    """
    Returns a callable that produces a probability density function of y conditional on a fixed x.

    Parameters
    -------
    y : list of length N_OBSERVATIONS, which contains observed order statistics 
    x : list of length N_OBSERVATIONS, which contains observed covariates, each covariate being a list
    -------
    """
    
    N_OBSERVATIONS = len(x)

    data_pairs = [x[idx] + [y[idx]] for idx in range(N_OBSERVATIONS)]
    reflected_data = [[-v for v in x[idx]] + [y[idx]] for idx in range(N_OBSERVATIONS)]
    data_pairs = data_pairs + reflected_data

    joint_kde = stats.gaussian_kde(np.transpose(np.array(data_pairs)))
    
    marginal_kde = stats.gaussian_kde(np.transpose(np.array(x)))
    
    conditional_kde = lambda _x, _y: joint_kde.pdf(_x + [_y]) / marginal_kde.pdf(_x) 
    
    return lambda _x: (lambda _y: 2*conditional_kde(_x, _y))


def get_order_statistic_pdfs(bids, covariates):
    """
    Returns an array of callables which produces probability density functions.

    Parameters
    -------
    bids : list of length N_OBSERVATIONS, where each element is a list containing recorded bids
    covariates : list of length N_OBSERVATIONS, which contains observed covariates
    -------

    Returns
    -------
    pdfs : dictionary of length equal to the range of number of recorded bids per auction
    pdfs_delta : dictionary of length equal to the range of number of recorded bids per auction

    For any i inside this range and 0<j≤i, 
    pdfs["i"][j] is a callable with parameter x_val, which returns the probability density
        function of the j:i order statistic of bids conditional on x_val
    pdfs_delta["i"] is a callable with parameter x_val, which returns the probability density
        function of the i:i order statistic of bids conditional on x_val
    -------
    """

    BIDS_RANGE = set([len(auction) for auction in bids])

    pdfs = dict()
    pdfs_delta = dict()

    for N in BIDS_RANGE:

        pdfs[f"{N}"] = []
        pdfs_delta[f"{N}"] = []
        
        indices_with_n_bids = [idx for idx, auction in enumerate(bids) if len(auction) == N]
        auctions_with_n_bids = [bids[idx] for idx in indices_with_n_bids]
        covariates_with_n_bids = [covariates[idx] for idx in indices_with_n_bids]
        
        for i in range(N):
            auctions_i_n = [sorted(auction)[i] for auction in auctions_with_n_bids]
            
            conditional_pdf = get_conditional_pdf(auctions_i_n, covariates_with_n_bids)
            pdfs[f"{N}"].append(conditional_pdf)

            if i == N-1:
                auction_with_increment = [EBAY_INCREMENT(bid) for bid in auctions_i_n]
                conditional_pdf_delta = get_conditional_pdf(auction_with_increment, covariates_with_n_bids)
                pdfs_delta[f"{N}"] = conditional_pdf_delta

    return (pdfs, pdfs_delta)


def get_estimated_means(pdfs, pdfs_delta, x_val, interpolation_range):
    """
    Returns estimated upper and lower means given a covariate.

    Parameters
    -------
    pdfs : dictionary in the format as returned by get_order_statistic_pdfs
    pdfs_delta: dictionary in the format as returned by get_order_statistic_pdfs
    x_val : specific value of the covariate
    interpolation_range : tuple of form (x0, x1), which should cover most of the support of y
    -------

    Returns
    -------
    (upper, lower) : tuple where the first element is the estimated upper bound average,
        and the second element is the estimated lower bound average. The first element
        should be smaller than the second.
    -------
    """

    x0, x1 = interpolation_range

    conditional_pdfs = {key: [pdf(x_val) for pdf in value] for key, value in pdfs.items()}
    conditional_pdfs_delta = {key: pdf(x_val) for key, pdf in pdfs_delta.items()}

    parent_cdf_estimates_upper = []
    parent_cdf_estimates_lower = []

    for key in conditional_pdfs:
        
        N_BIDS = int(key)

        # weight = integrate.quad(conditional_pdfs[key][0], a=0, b=np.inf)[0]
        weight = 1

        conditional_pdf_N = [lambda y, pdf=pdf: pdf(y)/weight for pdf in conditional_pdfs[key]]
    

        for i in range(N_BIDS):
            
            conditional_pdf_i_N = conditional_pdf_N[i]
            conditional_cdf_i_N = lambda y, conditional_pdf_i_N=conditional_pdf_i_N: integrate.quad(conditional_pdf_i_N, a=0, b=y)[0]

            parent_conditional_cdf_from_i_N_ = get_cdf(conditional_cdf_i_N, i+1, N_BIDS)
            parent_conditional_cdf_from_i_N = lambda x: parent_conditional_cdf_from_i_N_(x)/parent_conditional_cdf_from_i_N_(x1)
            
            parent_cdf_estimates_upper.append(parent_conditional_cdf_from_i_N)
            
            if i == N_BIDS - 1:
                
                conditional_pdf_delta_N = conditional_pdfs_delta[key]
                conditional_cdf_delta_N = lambda y, conditional_pdf_delta_N=conditional_pdf_delta_N: integrate.quad(conditional_pdf_delta_N, a=0, b=y)[0]

                parent_conditional_cdf_delta_from_N_ = get_cdf(conditional_cdf_delta_N, i+1, N_BIDS)
                parent_conditional_cdf_delta_from_N = lambda x: parent_conditional_cdf_delta_from_N_(x)/parent_conditional_cdf_delta_from_N_(x1)

                parent_cdf_estimates_lower.append(parent_conditional_cdf_delta_from_N)


    def smooth_upper_bound_cdf(x, p):
        all_values = [cdf(x) for cdf in parent_cdf_estimates_upper]
        ans = sum([g*np.exp(g*p) for g in all_values])/sum([np.exp(g*p) for g in all_values])
        # print(f"smooth upper bound for {x}: {ans}")
        return ans
    
    def smooth_lower_bound_cdf(x, p):
        all_values = [cdf(x) for cdf in parent_cdf_estimates_lower]
        ans = sum([g*np.exp(g*p) for g in all_values])/sum([np.exp(g*p) for g in all_values])
        # print(f"smooth lower bound for {x}: {ans}")
        return ans

    values = np.linspace(x0,x1,num=100)
    discrete_upper_bound_cdf = [smooth_upper_bound_cdf(y, 0) for y in values]
    discrete_lower_bound_cdf = [smooth_lower_bound_cdf(y, 0) for y in values]
    upper_bound_rv = FastMean(discrete_upper_bound_cdf, values)
    lower_bound_rv = FastMean(discrete_lower_bound_cdf, values)
    
    return (upper_bound_rv.mean(), lower_bound_rv.mean(), discrete_upper_bound_cdf, discrete_lower_bound_cdf)


def get_estimated_medians(pdfs, pdfs_delta, x_val, interpolation_range):
    """
    Returns estimated upper and lower medians given a covariate.

    Parameters
    -------
    pdfs : dictionary in the format as returned by get_order_statistic_pdfs
    pdfs_delta: dictionary in the format as returned by get_order_statistic_pdfs
    x_val : specific value of the covariate
    interpolation_range : tuple of form (x0, x1), which should cover most of the support of y
    -------

    Returns
    -------
    (upper, lower) : tuple where the first element is the estimated upper bound median,
        and the second element is the estimated lower bound median. The first element
        should be smaller than the second.
    -------
    """

    x0, x1 = interpolation_range

    conditional_pdfs = {key: [pdf(x_val) for pdf in value] for key, value in pdfs.items()}
    conditional_pdfs_delta = {key: pdf(x_val) for key, pdf in pdfs_delta.items()}

    parent_cdf_estimates_upper = []
    parent_cdf_estimates_lower = []

    for key in conditional_pdfs:
        
        N_BIDS = int(key)

        # weight = integrate.quad(conditional_pdfs[key][0], a=0, b=np.inf)[0]
        weight = 1

        conditional_pdf_N = [lambda y, pdf=pdf: pdf(y)/weight for pdf in conditional_pdfs[key]]
    

        for i in range(N_BIDS):
            
            conditional_pdf_i_N = conditional_pdf_N[i]
            conditional_cdf_i_N = lambda y, conditional_pdf_i_N=conditional_pdf_i_N: integrate.quad(conditional_pdf_i_N, a=0, b=y)[0]

            parent_conditional_cdf_from_i_N_ = get_cdf(conditional_cdf_i_N, i+1, N_BIDS)
            parent_conditional_cdf_from_i_N = lambda x: parent_conditional_cdf_from_i_N_(x)/parent_conditional_cdf_from_i_N_(x1)
            
            parent_cdf_estimates_upper.append(parent_conditional_cdf_from_i_N)
            
            if i == N_BIDS - 1:
                
                conditional_pdf_delta_N = conditional_pdfs_delta[key]
                conditional_cdf_delta_N = lambda y, conditional_pdf_delta_N=conditional_pdf_delta_N: integrate.quad(conditional_pdf_delta_N, a=0, b=y)[0]

                parent_conditional_cdf_delta_from_N_ = get_cdf(conditional_cdf_delta_N, i+1, N_BIDS)
                parent_conditional_cdf_delta_from_N = lambda x: parent_conditional_cdf_delta_from_N_(x)/parent_conditional_cdf_delta_from_N_(x1)

                parent_cdf_estimates_lower.append(parent_conditional_cdf_delta_from_N)


    def smooth_upper_bound_cdf(x, p):
        all_values = [cdf(x) for cdf in parent_cdf_estimates_upper]
        ans = sum([g*np.exp(g*p) for g in all_values])/sum([np.exp(g*p) for g in all_values])
        # print(f"smooth upper bound for {x}: {ans}")
        return ans
    
    def smooth_lower_bound_cdf(x, p):
        all_values = [cdf(x) for cdf in parent_cdf_estimates_lower]
        ans = sum([g*np.exp(g*p) for g in all_values])/sum([np.exp(g*p) for g in all_values])
        # print(f"smooth lower bound for {x}: {ans}")
        return ans

    upper_bound_median = optimize.bisect(lambda x: smooth_upper_bound_cdf(x,0)-0.5, x0, x1, xtol=0.001)
    lower_bound_median = optimize.bisect(lambda x: smooth_lower_bound_cdf(x,0)-0.5, x0, x1, xtol=0.001)

    
    return (upper_bound_median, lower_bound_median)


def transform_covariates(covariates, n_bins):
    """
    Returns a transformed version of covariates where each value is replaced by the mean of 
        their respective binned group

    Parameters
    -------
    covariates : list of covariates to be transformed, currently being continuous
    n_bins : the number of ordinal variables the covariates are to be transformed into
    -------

    Returns
    -------
    transformed_covariates : list of transformed covariates, where each value is generated by
        first sorting the covariates input, binning everything into n_bins and replacing each
        value by the mean within the bin.
    -------
    """

    covariates = np.array(covariates)
    argsort = np.argsort(covariates)
    orders = np.array_split(argsort, n_bins)
    
    for order in orders:
        covariates[order] = covariates[order].mean()
    
    return covariates


def estimate_mean(bids, covariates, _range):
    """
    Estimates the lower and upper bounds to the conditional mean for each covariate.

    Parameters
    --------
    bids : list containing individual bids
    covariates : list containing auction covariates corresponding to each bid
    _range : tuple of the form (x0, x1) that indicates the region where the CDF is interpolated
    --------

    Returns
    --------
    (expected_upper, expected_lower) : tuple of dictionaries containing upper and lower
        bounds of the conditional mean, where each key is a covariate as a string
    --------
    """

    pdfs, pdfs_delta = get_order_statistic_pdfs(bids, covariates)

    expected_upper = {}
    expected_lower = {}

    unique_covariates = [list(x) for x in set(tuple(x) for x in covariates)]

    start = time.perf_counter()

    for idx, covariate in enumerate(unique_covariates):
        print(f"calculating values for covariate: {covariate} ({idx+1}/{len(unique_covariates)})")
        print(f"total time elapsed: {time.perf_counter()-start}s")
        lower, upper, u_cdf, l_cdf = get_estimated_means(pdfs, pdfs_delta, covariate, _range)
        expected_upper[f"{covariate}"] = upper
        expected_lower[f"{covariate}"] = lower

    return (expected_upper, expected_lower)


def estimate_median(bids, covariates, _range):
    """
    Estimates the lower and upper bounds to the conditional median for each covariate.

    Parameters
    --------
    bids : list containing individual bids
    covariates : list containing auction covariates corresponding to each bid
    --------

    Returns
    --------
    (expected_upper, expected_lower) : tuple of dictionaries containing upper and lower
        bounds of the conditional median, where each key is a covariate as a string
    --------
    """

    pdfs, pdfs_delta = get_order_statistic_pdfs(bids, covariates)

    median_upper = {}
    median_lower = {}

    unique_covariates = [list(x) for x in set(tuple(x) for x in covariates)]

    start = time.perf_counter()

    for idx, covariate in enumerate(unique_covariates):
        print(f"calculating values for covariate: {covariate} ({idx+1}/{len(unique_covariates)})")
        print(f"total time elapsed: {time.perf_counter()-start}s")
        lower, upper = get_estimated_medians(pdfs, pdfs_delta, covariate, (0,9))
        median_upper[f"{covariate}"] = upper
        median_lower[f"{covariate}"] = lower

    return (median_upper, median_lower)


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

