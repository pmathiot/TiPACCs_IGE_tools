## Load module
import xarray as xr
import numpy  as np
import pandas as pd
from datetime import datetime
import copy as copy
from dask.diagnostics import ProgressBar
import argparse

cdir_JRA   ='DATA_in/JRA'

cvar_snow_JRA='prsn'
cvar_tprecip_JRA='tprecip'

idateout = 1951 # use a non leap year (0001 is out of bound for date_range pandas function )

def get_argument():
    # define argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", metavar='start year YYYY', help="start year", type=int, nargs=1, required=True)
    parser.add_argument("--yeare", metavar='end year YYYY', help="end year", type=int, nargs=1, required=True)
    return parser.parse_args()

args = get_argument()

years=args.years[0]
yeare=args.yeare[0]

# for each variable
for year in range(years,yeare+1):
    print(year)
    yrefs=year; yrefe=year+1
    slc_ref=slice('{:d}-01-01'.format(yrefs), '{:d}-01-01'.format(yrefe))

    # load data reference
    print('    load reference data ...')
    cfJRAsnow='{}/drowned_{}_JRA55_y{}.nc'.format(cdir_JRA,cvar_snow_JRA,year)
    print('        file : {}'.format(cfJRAsnow))
    ds_JRA_snow    = xr.open_mfdataset(cfJRAsnow,chunks={'time':2920}, parallel=True)

    cfJRAtprecip='{}/drowned_{}_JRA55_y{}.nc'.format(cdir_JRA,cvar_tprecip_JRA,year)
    print('        file : {}'.format(cfJRAtprecip))
    ds_JRA_tprecip = xr.open_mfdataset(cfJRAtprecip,chunks={'time':2920}, parallel=True)

    # compute climato
    print('    build monthly climato ...')
    ds_JRA_snow_clim   =ds_JRA_snow.sel(time=slc_ref).groupby('time.month').mean(dim='time').rename({'month': 'time'})
    ds_JRA_tprecip_clim=ds_JRA_tprecip.sel(time=slc_ref).groupby('time.month').mean(dim='time').rename({'month': 'time'})

    # update month dimension (use idateout as dummy date 0001 was not possible (out of bound))
    ds_JRA_snow_clim['time']   =pd.date_range("{:d}/01/15".format(year),periods=12,freq=pd.DateOffset(months=1))
    ds_JRA_tprecip_clim['time']=pd.date_range("{:d}/01/15".format(year),periods=12,freq=pd.DateOffset(months=1))

    delayed_obj=ds_JRA_snow_clim.to_netcdf('DATA_in/JRA/JRA_monthly_{}_y{:d}.nc'.format(cvar_snow_JRA,year),unlimited_dims='time',encoding={'time' : {'dtype': 'float64'}}, compute=False)
    results = delayed_obj.compute()

    delayed_obj=ds_JRA_tprecip_clim.to_netcdf('DATA_in/JRA/JRA_monthly_{}_y{:d}.nc'.format(cvar_tprecip_JRA,year),unlimited_dims='time',encoding={'time' : {'dtype': 'float64'}}, compute=False)
    results = delayed_obj.compute()
