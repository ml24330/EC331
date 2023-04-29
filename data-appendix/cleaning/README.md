### Data cleaning

- `main.py` cleans the data, including transforming columns, imputing missing values, reformatting & encoding variables, and more. This file produces two data files in the `../data` folder, `listings.csv` and `bids.csv`.
- `main.do` carries out leave-one-out demeaning regressions. Coefficients reported in these regressions are stored in `../output/reg_output.csv`, and homogenised bids are stored in `../data/demeaned.csv`. This file also copies these `.csv` file into `.dta`.
- `listings.db` is contains data used and is copied from the `../collection` directory.
- `db_utils.py` is a file containing helper functions also copied from the `../collection` directory. 