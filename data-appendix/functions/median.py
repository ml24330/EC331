from scipy import integrate, optimize
import time
from .FastMean import *
from .cdf_mapping import *
from .get_pdfs import *
import traceback

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
                # print(f"error occurred for one cdf while calculating upper bound for {x}")
                # print(traceback.format_exc())
                # print(e)
                pass

        ans = sum([g*np.exp(g*p) for g in all_values])/sum([np.exp(g*p) for g in all_values])
        return ans
    
    def smooth_lower_bound_cdf(x, p):

        all_values = []
        for cdf in parent_cdf_estimates_lower:
            try:
                all_values.append(cdf(x))
            except Exception as e:
                # print(f"error occurred while calculating lower bound for {x}!")
                # print(traceback.format_exc())
                # print(e)
                pass

        ans = sum([g*np.exp(g*p) for g in all_values])/sum([np.exp(g*p) for g in all_values])
        return ans

    
    upper_bound_median = optimize.bisect(lambda x: smooth_upper_bound_cdf(x,-1)-0.5, x0, x1, xtol=0.001)
    lower_bound_median = optimize.bisect(lambda x: smooth_lower_bound_cdf(x,1)-0.5, x0, x1, xtol=0.001)
    
    return (upper_bound_median, lower_bound_median)



def estimate_median(bids, covariates, incremented, _range):
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

    pdfs, pdfs_delta = get_order_statistic_pdfs(bids, covariates, incremented)

    median_upper = {}
    median_lower = {}

    unique_covariates = [list(x) for x in set(tuple(x) for x in covariates)]

    start = time.perf_counter()

    for idx, covariate in enumerate(unique_covariates):
        print(f"calculating values for covariate: {covariate} ({idx+1}/{len(unique_covariates)})")
        print(f"total time elapsed: {time.perf_counter()-start}s")
        lower, upper = get_estimated_medians(pdfs, pdfs_delta, covariate, _range)
        median_upper[f"{covariate}"] = upper
        median_lower[f"{covariate}"] = lower

    return (median_upper, median_lower)

