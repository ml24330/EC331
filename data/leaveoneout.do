use "./bids.dta", clear

local N = _N
gen numbidscat = bidcount
replace numbidscat=5 if bidcount>5

gen e_bid = .

forvalues i = 1/`N' {
		disp `i'
		
		* Cash
		quietly xi: reg bids apple samsung amazon others screensize storage isnight returnsaccepted isused isbroken deliveryspeed i.numbidscat ///
			if id!=id[`i']

		sort id nobid
		quietly predict temp1 if id==id[`i']
		quietly replace e_bid=temp1 if id==id[`i']

		drop temp1
}	

gen residual = bids - e_bid
label variable residual "Deviation from expected bid"

drop numbidscat e_bid _*

save "../data/demeaned.dta", replace
export delimited using "../data/demeaned.csv", replace
