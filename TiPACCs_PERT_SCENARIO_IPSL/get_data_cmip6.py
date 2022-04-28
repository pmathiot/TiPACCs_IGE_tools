import cdsapi

c = cdsapi.Client()

cvarin_lst=['eastward_near_surface_wind','northward_near_surface_wind','near_surface_air_temperature','near_surface_specific_humidity','precipitation','snowfall_flux','surface_downwelling_longwave_radiation','surface_downwelling_shortwave_radiation']

cperiod='1979-01-01/2019-01-01'

for cvar in cvarin_lst:

    c.retrieve(
        'projections-cmip6',
        {
            'temporal_resolution': 'monthly',
            'experiment': 'historical',
            'level': 'single_levels',
            'variable': cvar,
            'model': 'ipsl_cm6a_lr',
            'date': cperiod,
            'format': 'zip',
        },
        '{}.zip'.format(cvar))
