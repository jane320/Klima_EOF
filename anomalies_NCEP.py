#!/usr/bin/env python

import xarray as xr

from utils import calc_normalized_anomalies

### ----------------------- Open NCEP1-Dataset ---------------------------- ###
rea_selection = "ncep"

rea_info = {
    "ncep": {'path':'/Users/jana/Desktop/EOF/Klima_Data/NCEP/*/*',
            'vars':['slp', 'rhum', 'shum']},
}


try:
    ds_rea = xr.open_mfdataset(rea_info[rea_selection]['path'], decode_cf=True)
except KeyError:
    print("Choose a valid reanalysis from these options: {}".format(', '.join(rea_info.keys())))
    raise
except:
    print("Unexpected error")
    raise


### ------------------------ Prepare NCEP1 -------------------------------- ###
# Cut out specific geographical area
ds_rea.coords['lon'].data = (ds_rea.coords['lon'] + 180) % 360 - 180
ds_rea = ds_rea.sortby(ds_rea.lon)
ds_rea = ds_rea.sel(lon=slice(-10, 25), lat=slice(67.5, 32.5))

# Get rid of demension 'level'    
ds_rea['rhum'] = ds_rea['rhum'].squeeze(dim='level')
ds_rea['shum'] = ds_rea['shum'].squeeze(dim='level')
ds_rea = ds_rea.drop('level')
    
# In some later files there is a variable time_bnds. Needs to be removed!!
try:
    ds_rea = ds_rea.drop('time_bnds')
except:
    pass

print(ds_rea)

### --------------------------- Anomalies --------------------------------- ###
# Calculate normalized anomalies and construct rolled dimension
ds_rea = calc_normalized_anomalies(ds_rea)
#ds_rea_roll = ds_rea.rolling(time=21, center=True).construct('window_dim')

print(ds_rea)

# Save anomalies
ds_rea.to_netcdf(path="normalized_animaliies_NCEP.nc")
