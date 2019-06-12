#!/usr/bin/env python

"""main_validation.py: Start AnalogMethod Validation for specified reanalysis"""

__author__ = "Georg Seyerl"
__copyright__ = "Copyright 2019"
__license__ = "MIT"
__maintainer__ = "Georg Seyerl"
__email__ = "g.seyerl@posteo.net"
__status__ = "Development"

import xarray as xr
from eofs.multivariate.standard import MultivariateEof

from utils import calc_normalized_anomalies

# TODO:
# Add test data
# Comments and tests for anomaly calculation
# Create AnalogMethod class:
#   - prepare method with anomalie calculation function as argument (e.g from utils calc_normalized_anomalies)
#   - loop in new classMethod
#   - EOF loop for explained variance

#           --------------------------------------------
# ----------------------------------------------------------------
#                     VALIDATION SETTINGS
# ----------------------------------------------------------------
#           --------------------------------------------

# "era", "ncep" or "jra"
rea_selection = "ncep"

# TODO maybe choose variable combination for validation later in this dict
rea_info = {
    "era": {'path':'../data/ERA5/*',
            'vars':['r', 'q']},
    "ncep": {'path':'/Users/jana/Desktop/EOF/Klima_Data/Test/*',
            'vars':['slp', 'rhum', 'shum']},
    "jra": {'path':'../data/JRA55/*/*.nc',
            'vars':['PRMSL_GDS0_MSL', 'RH_GDS0_ISBL', 'SPFH_GDS0_ISBL']},
}


# Usefull for debugging
# .sel(lat=48, lon=16, method="nearest").plot()

#           --------------------------------------------
# ----------------------------------------------------------------
#                        MAIN TERRITORY
# ----------------------------------------------------------------
#           --------------------------------------------

try:
    ds_rea = xr.open_mfdataset(rea_info[rea_selection]['path'], decode_cf=True)
except KeyError:
    print("Choose a valid reanalysis from these options: {}".format(', '.join(rea_info.keys())))
    raise
except:
    print("Unexpected error")
    raise

print ('hallo')

# Prepare NCEP1 -------------------------------------------------------------------------------------
if rea_selection == 'ncep':
    #ds_rea = xr.open_mfdataset("../data/NCEP1/slp.*", decode_cf=True)
    # Rotate longitude to be able to use slice (0 - 360  ->  -180 - 180)
    ds_rea.coords['lon'].data = (ds_rea.coords['lon'] + 180) % 360 - 180
    ds_rea = ds_rea.sortby(ds_rea.lon)
    ds_rea = ds_rea.sel(lon=slice(-10, 25), lat=slice(67.5, 32.5))
    
    ds_rea['rhum'] = ds_rea['rhum'].squeeze(dim='level')
    ds_rea['shum'] = ds_rea['shum'].squeeze(dim='level')
    ds_rea = ds_rea.drop('level')

    print(ds_rea)
    
# Prepare ERA   -------------------------------------------------------------------------------------
if rea_selection == 'era':
    #ds_rea = xr.open_mfdataset("../data/ERA5/*", decode_cf=True).chunk({'time':-1})
    ds_rea = ds_rea.rename({'latitude': 'lat', 'longitude': 'lon'})
    pass

# Prepare JRA-55  -----------------------------------------------------------------------------------
if rea_selection == 'jra':
    #ds_rea = xr.open_mfdataset(rea_info[rea_selection]['path'], decode_cf=True)
    ds_rea = ds_rea.rename({'initial_time0_hours': 'time',
                            'g0_lat_1': 'lat',
                            'g0_lon_2': 'lon'}).drop(['initial_time0_encoded','initial_time0'])

    # Rotate longitude to be able to use slice (0 - 360  ->  -180 - 180)
    ds_rea.coords['lon'].data = (ds_rea.coords['lon'] + 180) % 360 - 180
    ds_rea = ds_rea.sortby(ds_rea.lon)


# Calculate normalized anomalies and construct rolled dimension
ds_rea = calc_normalized_anomalies(ds_rea)
ds_rea_roll = ds_rea.rolling(time=21, center=True).construct('window_dim')

# Loop over dayofyear   ---------------------------------------------------------------------------------------------------------
for _, ds_test in ds_rea_roll.groupby("time.dayofyear"):

    # TODO
    ds_test = ds_test.rename({"time":"time_old"})
    #ds_test = ds_test.stack(time=('time_old', 'window_dim')).transpose('time_eof', 'lat', 'lon', 'nbnds')
    ds_test = ds_test.stack(time=('time_old', 'window_dim')).transpose('time', 'lat', 'lon')
    # Add attribute axis for EOF package to find new time dimension
    ds_test.coords['time'].attrs['axis'] = 'T'

    # Rename time dimension to avoid conflict if pcs are computed

    # Create an EOF solver to do the EOF analysis. Square-root of cosine of
    # latitude weights are applied before the computation of EOFs.
    # coslat = np.cos(np.deg2rad(z_djf.coords['latitude'].values)).clip(0., 1.)
    # wgts = np.sqrt(coslat)[..., np.newaxis]
    #solver = Eof(ds_test.pres.dropna('time'))
    
    SLP = ds_test.slp.dropna('time').values
    RHUM = ds_test.rhum.dropna('time').values
    SHUM = ds_test.shum.dropna('time').values
    
    msolver = MultivariateEof([SLP, RHUM, SHUM])
    eofs_slp, eofs_rhum, eofs_shum = msolver.eofs(neofs=5)
    pc = msolver.pcs(npcs=5)


    break
