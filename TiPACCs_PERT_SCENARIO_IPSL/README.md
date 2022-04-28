1 Get the CMIP data:
====================

- 1.1: register to the Climate Data Store provided by the EU: https://cds.climate.copernicus.eu/#!/home
- 1.2: test your access by downloading by hand a CMIP6 output: https://cds.climate.copernicus.eu/cdsapp#!/dataset/projections-cmip6?tab=form
- 1.3: setup CDS API: https://cds.climate.copernicus.eu/api-how-to

You can now try to download the data you are interested in => setup get_data_cmip6.py to fir your need. For an anomaly perturbation, you need runit twice to pick a reference period (IPSL CM6 historical 1974-2014) and then a target period (in my case IPSL CM6 SSP585 2260-2300).

2 Compute the anomaly:
======================

- 2.1: install the conda env needed for the various python script: conda env create -f TiPACCs_PERT_SCENARIO_IPSL.yml
- 2.2: setup and run Compute_IPSL_anomaly.ipynb to compute anomaly on your forcing grid (here JRA).
    - 2.2.1: setup the parameter section to fit your period / forcing / output grid (JRA here)
    - 2.2.2: get your output forcing grid (need lat/lon coordinates)
    - 2.2.3: run it (WARNING, it can take some times)
- 2.3: check ouptut by running plot_namoly.ipynb (need to be tuned to fit the forcing you used).

3 Create the full perturbed JRA forcing:
========================================
- 3.1: run ./Add_IPSLCM6_anomaly_to_JRA_data.py. You need to check hard coded file name prefix, directory name, source forcing ... are correct.
- 3.2: test it for a year.
- 3.2: prepare a script to run multiple sequencial script in parallel. In my case on Occigen, I book one node, and use X processors to run one year on each processor.

