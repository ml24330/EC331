from scipy import integrate, optimize
import time
from .FastMean import *
from .cdf_mapping import *
from .get_pdfs import *

def get_estimated_distributions(pdfs, pdfs_delta, x_val, interpolation_range):

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


    return (smooth_upper_bound_cdf, smooth_lower_bound_cdf)