### Notes to replicators

This data appendix is structured as seven directories. Below I describe the use of each directory and steps to reproduce relevant results in my paper.

#### Description of Directories

In addition to these descriptions, each folder contains a `README.md` briefly describing the use of each file inside.

- The `/collection` folder contains code used during data collection, including scraping and labelling;
- The `/cleaning` folder contains code used to clean and transform the data, including the first stage demeaning regressions;
- The `/estimation` folder contains code relevant to my main analysis, including simulating synthetic police data, estimating coefficients of conditional median function specifications, and conducting power analysis using generated data;
- The `/output` folder takes calculated estimates as given and reports results used to fill in tables;
- The `/figures` folder contains code used to produce graphic figures;
- The `/functions` folder contains helper functions that are used during estimation and output;
- The `/data` folder stores all intermediate data files in both `.csv` and `.dta` format. 

### Instructions for Replication

As hand labelling the data takes around 10 hours and and producing bootstrap intervals of interval estimates can take hundreds of hours, it is not recommended to replicate all codes in this data appendix in one sitting. Instead, I provide replication guidance for three separate parts: __(1) Collection of data__, __(2) Cleaning and estimation__, __(3) Producing outputs and figures__.

### Prerequisites of Replication

- Python 3.8+ with an appropriate package manager, e.g. `pip` or `conda`;
- Jupyter Notebook;
- Stata 17;
- Sufficient computing power.

#### Replication of Data Collection

Detailed instructions on doing this is provided in the `README.md` file in the `/collection` folder.


#### Replication of Cleaning and Estimation

1. Navigate to `/cleaning`. 
2. Run `main.py` in Python. (<5s)
3. Run `main.do` in Stata. (~3m)
4. Navigate to `/estimation`.
5. Run `main.py` in Python. (>50h)

This populates the `/estimation/dumps` folder with estimated results of conditional upper and lower bounds, which should be the same as the `/output/final dumps` folder. Power analysis results will also be stored in this folder, and should be qualitatively similar to what is inside the `/output/power dumps` folder.


#### Replication of Outputs and Figures

1. Navigate to `/output`.
2. To get a specific output, follow instructions in `/output/README.md` and run the relevant `.ipynb` notebook. (~5m each)
3. Navigate to `/figures`.
4. To produce a specific figure, follow instructions in `/figures/README.md` and run the relevant `.py` script. (~10s each)

Note: Figure 4 is generated as part of `/estimation/s_CMF.py`.