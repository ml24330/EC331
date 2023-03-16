clear all

import delimited "listings.csv"
save "listings.dta", replace
clear all

import delimited "bids.csv"
save "bids.dta", replace
clear all
