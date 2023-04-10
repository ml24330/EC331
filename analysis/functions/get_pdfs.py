from scipy import stats
import numpy as np

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
    # data_pairs = data_pairs + reflected_data

    joint_kde = stats.gaussian_kde(np.transpose(np.array(data_pairs)))
    
    marginal_kde = stats.gaussian_kde(np.transpose(np.array(x)))
    
    conditional_kde = lambda _x, _y: joint_kde.pdf(_x + [_y]) / marginal_kde.pdf(_x) 
    
    return lambda _x: (lambda _y: conditional_kde(_x, _y))
    # return lambda _x: (lambda _y: 2*conditional_kde(_x, _y))


def get_order_statistic_pdfs(bids, covariates, incremented):
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
        incremented_with_n_bids = [incremented[idx] for idx in indices_with_n_bids]

        for i in range(N):
            auctions_i_n = [sorted(auction)[i] for auction in auctions_with_n_bids]
            
            conditional_pdf = get_conditional_pdf(auctions_i_n, covariates_with_n_bids)
            pdfs[f"{N}"].append(conditional_pdf)

            if i == N-1:
                auction_with_increment = incremented_with_n_bids
                conditional_pdf_delta = get_conditional_pdf(auction_with_increment, covariates_with_n_bids)
                pdfs_delta[f"{N}"] = conditional_pdf_delta

    return (pdfs, pdfs_delta)

