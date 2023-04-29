from scipy import stats, interpolate

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
