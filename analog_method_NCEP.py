# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 15:04:00 2019

@author: nikta
"""

#!/usr/bin/env python
import xarray as xr
from eofs.multivariate.standard import MultivariateEof
import pickle 
import numpy as np
import datetime

start_year= 1979
end_year= 2017

def get_Date_from_index(index, TD_Date, start_year=start_year):
    day = TD_Date.time.dt.day.values
    month = TD_Date.time.dt.month.values

    year_from_index = int(index/21) + start_year

    #day - 1 becouse of 29th of february. Becouse we are using a different year to create date. to solve inconsistencies 
    #gets added below again
    if month==2 and day==29:
        analog_date = datetime.datetime(year_from_index, month, day-1)
    
        analog_date = analog_date + datetime.timedelta(days=int(index%21 - 10 + 1))
    else:
        analog_date = datetime.datetime(year_from_index, month, day)
    
        analog_date = analog_date + datetime.timedelta(days=int(index%21 - 10))
    
    return np.datetime64(analog_date)


try:
    ds_rea = xr.open_mfdataset('./normalized_anomalies_NCEP.nc', decode_cf=True)
except:
    print("Unexpected error")
    raise

ds_rea = ds_rea.sel(time=slice(str(start_year) + '-01-01', str(end_year) + '-12-31'))

ds_rea_roll = ds_rea.rolling(time=21, center=True).construct('window_dim')
print(ds_rea_roll) 

solver_list = []
    
for _, ds_doy in ds_rea_roll.groupby("time.dayofyear"):

    ds_doy = ds_doy.rename({"time":"time_old"})
    #ds_test = ds_test.stack(time=('time_old', 'window_dim')).transpose('time_eof', 'lat', 'lon', 'nbnds')
    ds_doy = ds_doy.stack(time=('time_old', 'window_dim')).transpose('time', 'lat', 'lon')
    # Add attribute axis for EOF package to find new time dimension
    ds_doy.coords['time'].attrs['axis'] = 'T'
    
    #create multivariate Eof
    msolver = MultivariateEof([ds_doy.slp.dropna('time').values, ds_doy.rhum.dropna('time').values, ds_doy.shum.dropna('time').values])
    
    solver_list.append(msolver)


print("solver created")

#loop over years

date_list = []
EOF_list = []
pseudo_pc_list=[]

num_analoga = 5

#loop over days of a year
for year in range(start_year,end_year+1):
    i=0
    
    #indexes to cut out current year out of norms
    start_index_cut = (year-start_year)*21
    end_index_cut = 21 + (year-start_year)*21
    
    #loop over targetdays
    for _,TD in ds_rea.sel(time=slice(str(year) + '-01-01', str(year) + '-12-31')).groupby("time"):
        #select solver
        my_solver = solver_list[i]
        
        N = 1
        var = 0
        #while variance ist <0.9 find variancefraction to determine num of eofs
        while var < .9:
            var = np.sum(my_solver.varianceFraction(neigs=N).data)
            N = N+1
        
        #eofs and pcs 
        eofs_slp, eofs_rhum, eofs_shum = my_solver.eofs(neofs=N)
        pcs = my_solver.pcs(npcs=N)
        
        SLP = TD.slp.values
        RHUM = TD.rhum.values
        SHUM = TD.shum.values
        
        #calculate pseudo-pcs and norm
        pseudo_pcs = my_solver.projectField([SLP, RHUM, SHUM],neofs=N)
    
        norm = np.sum(np.sqrt((pcs - pseudo_pcs)**2),axis=1)
        
        #pcs of first 10 days are below 21xN
        #fill values are added to the norm for correct dimensions
        if i < 10:
            fill_values = [999 for k in range(10-i)]
            norm = np.insert(norm, 0,fill_values)
                    
        #cut out current year
        norm[np.s_[start_index_cut:end_index_cut:]] = 999
        
        #find analog dates with argmin, set norm[index] to nan to find 2nd, 3rd,... minimum
        analog_dates = []
        for a in range(0,num_analoga):
            index=np.nanargmin(norm)
            analog_dates.append(get_Date_from_index(index, TD))
            norm[norm == norm[index]] = np.nan
        
        #save analog dates, eofs and pseudo-pcs
        date_list.append([_,analog_dates])
        EOF_list.append([_,eofs_slp,eofs_rhum, eofs_shum])
        pseudo_pc_list.append([_,pseudo_pcs])
        
        i+=1
        print(_)

        
pickle.dump(date_list, open("analog_dates_test.p", "wb" ))
pickle.dump(EOF_list, open("EOFS_test.p", "wb" ))
pickle.dump(pseudo_pc_list, open("pseudo_pcs_test.p", "wb" ))
#open with 
pickle_analog = pickle.load(open("analog_dates_test.p", "rb" ))
pickle_eof = pickle.load(open("EOFS_test.p", "rb" ))
pickle_pseudo_pc = pickle.load(open("pseudo_pcs_test.p", "rb" ))
      

#plot
#plt.contourf(eofs_slp[0,:,:])  
#plt.contourf(pickle_eof[0][1][0,:,:])