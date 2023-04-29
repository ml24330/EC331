clear all

import delimited "../data/listings.csv"
save "../data/listings.dta", replace
clear all

import delimited "../data/bids.csv"
save "../data/bids.dta", replace
clear all
