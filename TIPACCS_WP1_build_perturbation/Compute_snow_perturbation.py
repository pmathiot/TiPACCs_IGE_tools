## Load module
import xarray as xr
import numpy  as np
import pandas as pd
from datetime import datetime
import copy as copy
from dask.diagnostics import ProgressBar

## Core functions
### compute 3h anomaly (with and without leap year)
def compute_1m_to_3h(ds_month):
    """
    Purpose: compute 3h dataset based on a monthly file
    
    Args:
        ds_month_ano : monthly data set [xarray dataset]
        
    Return: 
        ds_3h_ano : 3hourly data set [xarray dataset]
    """
    
    # Concat last 3 months at the beginning and first 3 month at the end
    # It is needed for a coorect interpolation as the end (31st december should match the 1st January minus 1 day)
    # 3 month as depending of the stencil of the interpolation scheme it could be needed
    m0=ds_month.isel(time=[9,10,11])
    m0['time']=m0['time']-pd.Timedelta(days=365)
    m13=ds_month.isel(time=[0,1,2])
    m13['time']=m13['time']+pd.Timedelta(days=365)
    ds_3h=xr.concat([m0,ds_month,m13],dim='time')

    # resampling with quadratic interpolation
    ds_3h=ds_3h.resample(time="3H").interpolate("quadratic")

    # select data only between 1st January to 31st december
    ds_3h=ds_3h.sel(time=slice('{:d}-01-01'.format(idateout), '{:d}-12-31'.format(idateout))).chunk({'time':1})

    return ds_3h


def modify_attributes_anomaly(cvar,dattrs,ds):
    """
    Purpose: modify variable reference attributes
    
    Args:
        dattrs : old attributes [dict]
        cvar   : variable name used to extract min and max [ string ]
        ds     : dataset from where min and max are extracted [ xarray dataset ]
        
    Return: 
        dattrs : new attributes [dict]
    """
    
    # get rid of non sense attributes
    if 'time' in list(dattrs.keys()):
        del dattrs["time"]
    if 'date' in list(dattrs.keys()):
        del dattrs["date"]
    
    # modify existing attributes
    dattrs["name"]      = 'snow_anomaly'
    dattrs["title"]     = 'SNOW PRECIPITATION RATE     KG/M2/S anomaly'
    dattrs["long_name"] = 'SNOW PRECIPITATION RATE     KG/M2/S anomaly'
    
    # compute new valid range
    print('    compute new range ...')
    print(ds[cvar])
    #dattrs["valid_min"] = ds[cvar].min().values
    #dattrs["valid_max"] = ds[cvar].max().values
    
    return dattrs

## Parameters
# data dir path
cdir_HadCM3='DATA_out/'
cdir_JRA   ='DATA_in/JRA'

# list of file variables to process and the corresponding infile variables
fvar_tprecip_HadCM3='TOTAL_PRECIP'
cvar_tprecip_HadCM3='precip'

fvar_snow_HadCM3='SNOW'
cvar_snow_HadCM3='snow'

cdvar_tprecip_HadCM3='dprecip'
cdvar_snow_HadCM3='dsnow'

cvar_snow_JRA='prsn'
cvar_tprecip_JRA='tprecip'

# reference period
yrefs=1979; yrefe=2019
ytrgs=2160; ytrge=2200
cfext='{:d}{:d}-{:d}{:d}'.format(ytrgs,ytrge,yrefs,yrefe)

idateout = 1951 # use a non leap year (0001 is out of bound for date_range pandas function )

# slice definition
slc_ref=slice('{:d}-01-01'.format(yrefs), '{:d}-01-01'.format(yrefe))

# for each variable
print('Processing of {} ({}) in progress ...'.format(fvar_snow_HadCM3,cvar_snow_HadCM3))
    
# load data reference
print('    load reference data ...')
cfJRAsnow='{}/JRA_monthly_{}_y{}.nc'.format(cdir_JRA,cvar_snow_JRA,'*')
print('        file : {}'.format(cfJRAsnow))
ds_JRA_snow=xr.open_mfdataset(cfJRAsnow)

cfJRAtprecip='{}/JRA_monthly_{}_y{}.nc'.format(cdir_JRA,cvar_tprecip_JRA,'*')
print('        file : {}'.format(cfJRAtprecip))
ds_JRA_tprecip=xr.open_mfdataset(cfJRAtprecip)

# compute climato
print('    build monthly climato ...')
ds_JRA_snow_clim   =ds_JRA_snow.sel(time=slc_ref).groupby('time.month').mean(dim='time').rename({'month': 'time'})
ds_JRA_tprecip_clim=ds_JRA_tprecip.sel(time=slc_ref).groupby('time.month').mean(dim='time').rename({'month': 'time'})

# update month dimension (use idateout as dummy date 0001 was not possible (out of bound))
ds_JRA_snow_clim['time']   =pd.date_range("{:d}/01/15".format(idateout),periods=12,freq=pd.DateOffset(months=1))
ds_JRA_tprecip_clim['time']=pd.date_range("{:d}/01/15".format(idateout),periods=12,freq=pd.DateOffset(months=1))

delayed_obj=ds_JRA_snow_clim.to_netcdf('snow.nc',unlimited_dims='time',encoding={'time' : {'dtype': 'float64'}}, compute=False)
with ProgressBar():
    results = delayed_obj.compute()

delayed_obj=ds_JRA_tprecip_clim.to_netcdf('precip.nc',unlimited_dims='time',encoding={'time' : {'dtype': 'float64'}}, compute=False)
with ProgressBar():
    results = delayed_obj.compute()

cfHadCM3tprecip_ano='{}/A1B_{}_3h_ano_{}_on_JRA_grid.NC'.format(cdir_HadCM3,fvar_tprecip_HadCM3,cfext)
print('        file : {}'.format(cfHadCM3tprecip_ano))
ds_HadCM3_tprecip_ano = xr.open_dataset(cfHadCM3tprecip_ano,chunks={'time':1}).drop('surface')
print('')
# create empty snow data set
print('compute empty data set')
ds_HadCM3_snow_ano = ds_HadCM3_tprecip_ano.drop(cdvar_tprecip_HadCM3)

# compute snow anomaly based on Hadcm3 tprecip and JRA ratio snow/tprecip  
print('ratio')
da_ratio = ds_JRA_snow_clim[cvar_snow_JRA] # / ds_JRA_tprecip_clim[cvar_tprecip_JRA]
precip=ds_JRA_tprecip_clim[cvar_tprecip_JRA].values
snow=ds_JRA_snow_clim[cvar_snow_JRA].values
ratio=copy.deepcopy(snow)
ratio[precip > 0.0] = snow[precip > 0.0] / precip[precip > 0.0] 
ratio[precip == 0.0] = 0.0
da_ratio.values=ratio

delayed_obj=da_ratio.to_dataset(name='JRA_snow_over_precip').to_netcdf('ratio.nc',unlimited_dims='time',encoding={'time' : {'dtype': 'float64'}}, compute=False)
with ProgressBar():
    results = delayed_obj.compute()

# compute 3h ratio (with and without leap year)
print('ratio 3h')
ds_ratio_3h = compute_1m_to_3h(da_ratio.to_dataset(name='JRA_snow_over_precip'))

# compute snow anoamlie
print('compute snow anomaly')
ds_HadCM3_snow_ano[cdvar_snow_HadCM3]=ds_HadCM3_tprecip_ano[cdvar_tprecip_HadCM3] * ds_ratio_3h['JRA_snow_over_precip']

# add variable attributes
print('modify attributes ...')
ds_HadCM3_snow_ano[cdvar_snow_HadCM3].attrs = modify_attributes_anomaly(cdvar_snow_HadCM3,ds_HadCM3_tprecip_ano[cdvar_tprecip_HadCM3].attrs,ds_HadCM3_snow_ano)
  
# add global attributes
print('    write global att ...')
ds_HadCM3_snow_ano.attrs =  { 'Description' : 'The above anomaly file is the differences between a specific period and a reference period',
                     'Specific Period' : '{:d} - {:d}'.format(ytrge, ytrgs),
                     'Reference period' : '{:d} - {:d}'.format(yrefe, yrefs),
                     'Method' : 'snow_ano = tprecip_HadCM3_ano * JRA_snow_clim/JRA_tprecip_clim, in other word, we assum, ratio precip / snow is the same. We need such approximation as A1B HadCM3 dataset do not have snow as variable.',
                     'Model' : 'HadCM3',
                     'Scenario'   : 'A1B',
                     'Contact':'P. Mathiot (IGE)',
                     'Creation date':'{}'.format(datetime.now()),
                    }

# write data
print('    write data ...')
cfout="A1B_{}_3h_ano_{}_on_JRA_grid.NC".format(fvar_snow_HadCM3,cfext)
print('        file : {} ...'.format(cfout))
delayed_obj=ds_HadCM3_snow_ano.to_netcdf('DATA_out/'+cfout,unlimited_dims='time',encoding={'time' : {'dtype': 'float64'}}, compute=False)
with ProgressBar():
    results = delayed_obj.compute()
print('')
print('')
