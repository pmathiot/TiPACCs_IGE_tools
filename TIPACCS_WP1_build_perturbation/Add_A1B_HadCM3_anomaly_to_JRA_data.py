#!/usr/bin/env python
# coding: utf-8

# In[1]:

print('import modules ...')
import xarray as xr
import numpy  as np
import pandas as pd
from datetime import datetime
import calendar
import copy
import argparse

print('end import modules ...')

def get_argument():
    # define argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", metavar='start year YYYY', help="start year", type=int, nargs=1, required=True)
    parser.add_argument("--yeare", metavar='end year YYYY', help="end year", type=int, nargs=1, required=True)
    parser.add_argument("--fileext", metavar='file extension', help="file extension 20602100-19792019 or 21602200-19792019", \
                                     type=str, nargs=1, required=True)
    return parser.parse_args()

args = get_argument()

# data dir path
cdir='./'

# list of file variables to process and the corresponding infile variables
#fvarlst_ano=['SNOW' ,'Q_1_5M','LW_TOTAL_DOWNWARD_SURFACE','P_SURF','SW_TOTAL_DOWNWARD_SURFACE','TOTAL_PRECIP','T_AIR_1_5M','U_10M','V_10M']
#cvarlst_ano=['dsnow','dq'    ,'dilr'                     ,'dp'    ,'dfield203'                ,'dprecip'     ,'dtemp'     ,'du'   ,   'dv']
#
#fvarlst_JRA=['prsn', 'huss'  ,'rlds'                     ,'psl'   ,'rsds'                     ,'tprecip'     ,'tas'       ,'uas'  ,'vas'  ]
#cvarlst_JRA=['prsn', 'huss'  ,'rlds'                     ,'psl'   ,'rsds'                     ,'tprecip'     ,'tas'       ,'uas'  ,'vas'  ]

fvarlst_ano=['T_AIR_1_5M']
cvarlst_ano=['dtemp'     ]

fvarlst_JRA=['tas']
cvarlst_JRA=['tas']

# input file name extension
cfin_ext=args.fileext[0]

yJRAs=args.years[0]
yJRAe=args.yeare[0]


# ## Add HadCM3 anomaly data to JRA data

# In[3]:


for ivar,fvar in enumerate(fvarlst_ano[0:1]):
    cvar_ano=cvarlst_ano[ivar]
    cvar_JRA=cvarlst_JRA[ivar]

   
    for year in range(yJRAs,yJRAe+1):
        year_out=year
        print('YEAR = ',year)
        print(datetime.now())
        # load data anomaly
        print('    load HadCM3 data ...')
        cfin_ano='./A1B_{}_3h_ano_{}_on_JRA_grid.NC'.format(fvar,cfin_ext)
        print('        file : {}'.format(cfin_ano))
        ds_ano = xr.open_dataset('./DATA_out/'+cfin_ano)
        
        # load JRA data
        print('    load JRA data '+str(year)+' ...')
        cfin_JRA='drowned_{}_JRA55_y{}.nc'.format(cvar_JRA,year)
        print('        file : {}'.format(cfin_JRA))
        ds_JRA = xr.open_dataset('./DATA_in/JRA/'+cfin_JRA)

        # if leap year repeat last frame 8 times (ie one day)
        if calendar.isleap(year):
            print('    year {} is a leap year, repeat last frame over 1 day ...'.format(year))
            ds_tmp=ds_ano.isel(time=slice(-1,None,1))
            ds_tmp['time']=ds_tmp['time']+pd.Timedelta(hours=3)
            ds_leap=copy.deepcopy(ds_tmp)
            for ih in range(7):
                ds_tmp['time']=ds_tmp['time']+pd.Timedelta(hours=3)
                ds_leap = xr.concat([ds_leap,ds_tmp],dim='time')

            ds_ano=xr.concat([ds_ano,ds_leap],dim='time')

        # add dataset
        print('    add anomaly to JRA data ...')
        ds_out = copy.deepcopy(ds_JRA)
        ds_out[cvar_JRA].values = ds_JRA[cvar_JRA].values + ds_ano[cvar_ano].values

        # correct attributes
        print('    update global attributes ...')
        ds_out.attrs['Description']='JRA data plus A1B HadCM3 {} anomaly ({}) creating by {}'.format(cfin_ext, cfin_ano, 'Add_A1B_HadCM3_anomaly_to_JRA_data.py')
        ds_out.attrs['Contact']='P. Mathiot (IGE)'
        ds_out.attrs['Creation date'] = '{}'.format(datetime.now())
        
        # write dataset
        cfout='drowned_{}_JRA55_perturbed_A1B_HadCM3_{}_anomaly_y{:d}.nc'.format(cvar_JRA,cfin_ext,year_out)
        print('    write output file ...')
        print('        file : ',cfout)
        ds_out.to_netcdf('DATA_out/JRA55_perturb/'+cfout)
        print()
        print()

print('DONE')
