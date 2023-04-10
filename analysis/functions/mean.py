from scipy import integrate
import time
from .FastMean import *
from .cdf_mapping import *
from .get_pdfs import *


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
            conditional_cdf_i_N = lambda y, conditional_pdf_i_N=conditional_pdf_i_N: integrate.quad(conditional_pdf_i_N, a=x0, b=y)[0]

            parent_conditional_cdf_from_i_N = lambda x, i=i, conditional_cdf_i_N=conditional_cdf_i_N: cdf(x, conditional_cdf_i_N, i+1, N_BIDS)/cdf(x1, conditional_cdf_i_N, i+1, N_BIDS)

            parent_cdf_estimates_upper.append(parent_conditional_cdf_from_i_N)
            
            if i == N_BIDS - 1:
                
                conditional_pdf_delta_N = conditional_pdfs_delta[key]
                conditional_cdf_delta_N = lambda y, conditional_pdf_delta_N=conditional_pdf_delta_N: integrate.quad(conditional_pdf_delta_N, a=x0, b=y)[0]

                parent_conditional_cdf_delta_from_N = lambda x, i=i, conditional_cdf_delta_N=conditional_cdf_delta_N: cdf(x, conditional_cdf_delta_N, i, N_BIDS)/cdf(x1, conditional_cdf_delta_N, i, N_BIDS)

                parent_cdf_estimates_lower.append(parent_conditional_cdf_delta_from_N)


    def smooth_upper_bound_cdf(x, p):

        all_values = []
        for cdf in parent_cdf_estimates_upper:
            try:
                all_values.append(cdf(x))
            except Exception as e:
                print(f"error occurred for one cdf while calculating upper bound for {x}")
                print(e)

        ans = sum([g*np.exp(g*p) for g in all_values])/sum([np.exp(g*p) for g in all_values])
        return ans
    
    def smooth_lower_bound_cdf(x, p):

        all_values = []
        for cdf in parent_cdf_estimates_lower:
            try:
                all_values.append(cdf(x))
            except Exception as e:
                print(f"error occurred while calculating lower bound for {x}!")
                print(e)

        ans = sum([g*np.exp(g*p) for g in all_values])/sum([np.exp(g*p) for g in all_values])
        return ans

    values = np.linspace(x0,x1,num=100)
    discrete_upper_bound_cdf = [smooth_upper_bound_cdf(y, -1) for y in values]
    discrete_lower_bound_cdf = [smooth_lower_bound_cdf(y, 1) for y in values]
    upper_bound_rv = FastMean(discrete_upper_bound_cdf, values)
    lower_bound_rv = FastMean(discrete_lower_bound_cdf, values)
    
    return (upper_bound_rv.mean(), lower_bound_rv.mean(), discrete_upper_bound_cdf, discrete_lower_bound_cdf)



def estimate_mean(bids, covariates, incremented, _range):
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

    pdfs, pdfs_delta = get_order_statistic_pdfs(bids, covariates, incremented)

    expected_upper = {}
    expected_lower = {}
    u_cdfs = {}
    l_cdfs = {}

    unique_covariates = [list(x) for x in set(tuple(x) for x in covariates)]

    start = time.perf_counter()

    for idx, covariate in enumerate(unique_covariates):
        print(f"calculating values for covariate: {covariate} ({idx+1}/{len(unique_covariates)})")
        print(f"total time elapsed: {time.perf_counter()-start}s")
        lower, upper, u_cdf, l_cdf = get_estimated_means(pdfs, pdfs_delta, covariate, _range)
        expected_upper[f"{covariate}"] = upper
        expected_lower[f"{covariate}"] = lower
        u_cdfs[f"{covariate}"] = u_cdf
        l_cdfs[f"{covariate}"] = l_cdf

    return (expected_upper, expected_lower, u_cdfs, l_cdfs)
