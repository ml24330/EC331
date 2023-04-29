use "./bids.dta", clear

local N = _N
gen numbidscat = bidcount
replace numbidscat=10 if bidcount>10
replace deliveryspeed = 0 if deliveryspeed == .
replace screensize = 5 if screensize == .

gen e_bid = .
gen e_bid2 = .

tempname results

postfile `results' idx apple samsung amazon others screensize storage isnight returnsaccepted isused isbroken deliveryspeed se_apple se_samsung se_amazon se_others se_screensize se_storage se_isnight se_returnsaccepted se_isused se_isbroken se_deliveryspeed r_squared using results.dta

forvalues i = 1/`N' {
		disp `i'
		
		quietly xi: reg bids apple samsung amazon others screensize storage isnight returnsaccepted isused isbroken deliveryspeed i.numbidscat ///
			if id!=id[`i'], nocons

		post `results' (`i') (`=_b[apple]') (`=_b[samsung]') (`=_b[amazon]') (`=_b[others]') (`=_b[screensize]') (`=_b[storage]') (`=_b[isnight]') (`=_b[returnsaccepted]') (`=_b[isused]') (`=_b[isbroken]') (`=_b[deliveryspeed]') (`=_se[apple]') (`=_se[samsung]') (`=_se[amazon]') (`=_se[others]') (`=_se[screensize]') (`=_se[storage]') (`=_se[isnight]') (`=_se[returnsaccepted]') (`=_se[isused]') (`=_se[isbroken]') (`=_se[deliveryspeed]') (`=e(r2_a)')
			
		sort id nobid
		quietly predict temp1 if id==id[`i']
		quietly replace e_bid=temp1 if id==id[`i']
		
		drop temp1
}
postclose `results'


forvalues i = 1/`N' {
		disp `i'
		
		quietly xi: reg bids apple samsung amazon others screensize storage isnight returnsaccepted isused isbroken deliveryspeed i.numbidscat sellerfeedbackscore ///
			if id!=id[`i']

		sort id nobid
		quietly predict temp2 if id==id[`i']
		quietly replace e_bid2=temp2 if id==id[`i']
		
		drop temp2
}	


gen residual = bids - e_bid
gen residual2 = bids - e_bid2

label variable residual "Deviation from expected bid"
label variable residual2 "Deviation from expected bid (conditioning on feedback)"

gen increment_residual = increment - e_bid

drop numbidscat e_bid e_bid2 _*

save "../data/demeaned.dta", replace
export delimited using "../data/demeaned.csv", replace
clear all

use results
export delimited using "../analysis/output.csv", replace
clear all
