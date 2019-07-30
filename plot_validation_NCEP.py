# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 12:05:11 2019

"""
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import time
import numpy as np
import pickle
from itertools import chain 

####Plotting routine for analog days with their respective target day 

#choose variable
var_list = ["RR","Tx","Tn","SPEI"]
var = var_list[1]
ds_sparta = xr.open_mfdataset('./' + str(var) + '/*.nc', decode_cf=True)

filename = 'analog_dates_test.p'
analoga = pickle.load(open(filename, "rb" ))

filename = 'corr_'+var+'_1979-01-01_test.p'
corr = pickle.load(open(filename, "rb" ))
print()

filename = 'rmse_'+var+'_1979-01-01_test.p'
rmse = pickle.load(open(filename, "rb" ))


#search for specific day to show: 17:18 --> 1979-01-18
date_string_an = []
for TD, AN in analoga[17:18]:
    date_string_td = str(TD)
    for i in AN:
        date_string_an.append(str(i))

#find td and analog days in spartacus
day_td = ds_sparta.sel(time=slice(date_string_td, date_string_td))
day_1 = ds_sparta.sel(time=slice(date_string_an[0], date_string_an[0]))
day_2 = ds_sparta.sel(time=slice(date_string_an[1], date_string_an[1]))
day_3 = ds_sparta.sel(time=slice(date_string_an[2], date_string_an[2]))
day_4 = ds_sparta.sel(time=slice(date_string_an[3], date_string_an[3]))
day_5 = ds_sparta.sel(time=slice(date_string_an[4], date_string_an[4]))

#find maximum and minimum value for scaling purposes
max_list = []
min_list = []
max_list.append(np.nanmax(day_td[var].values))
min_list.append(np.nanmin(day_td[var].values))

for m in range(5):
    name_day = 'day_'+str(m+1)
    max_list.append(np.nanmax(globals()[name_day][var].values))
    min_list.append(np.nanmin(globals()[name_day][var].values))

max_all = np.nanmax(max_list)
min_all = np.nanmin(min_list)

#plot td with their analog days
fig, axes = plt.subplots(3,2, figsize=(25,18))
levels = np.arange(min_all,max_all,0.5)
xr.plot.plot(day_td[var], ax = axes[0,0], levels = levels, cmap = 'bwr')
axes[0,0].set_title('Target Day: '+date_string_td)
xr.plot.plot(day_1[var], ax = axes[0,1], levels = levels, cmap = 'bwr')
axes[0,1].set_title('1. Analogon: '+date_string_an[0])
xr.plot.plot(day_2[var], ax = axes[1,0], levels = levels, cmap = 'bwr')
axes[1,0].set_title('2. Analogon: '+date_string_an[1])
xr.plot.plot(day_3[var], ax = axes[1,1], levels = levels, cmap = 'bwr')
axes[1,1].set_title('3. Analogon: '+date_string_an[2])
xr.plot.plot(day_4[var], ax = axes[2,0], levels = levels, cmap = 'bwr')
axes[2,0].set_title('4. Analogon: '+date_string_an[3])
xr.plot.plot(day_5[var], ax = axes[2,1], levels = levels, cmap = 'bwr')
axes[2,1].set_title('5. Analogon: '+date_string_an[4])
fig.colorbar()
plt.show()
    

#plot difference between td and analog 
#diff = day_1[var][0,:,:] - day_2[var][0,:,:]
#    
#xr.plot.plot(diff)



####Plotting routine for correlation coefficient and rmse
#plot for 1 year
start_day = '1979-01-01'
end_day = '1979-12-31'

td_ind = []
for TD, AD in analoga:
    #print(TD)
    td_ind.append(TD)

#find index of start and end day in data
start_day_occurences = np.where(td_ind == np.datetime64(start_day))
start_day_idx = int(start_day_occurences[0])

end_day_occurences = np.where(td_ind == np.datetime64(end_day))
end_day_idx = int(end_day_occurences[0])

days = td_ind[start_day_idx:end_day_idx+1]

#to handle the data easier, save the analog corrcoef and rmse in matrix
num_analoga = 5
co = np.zeros((len(days), num_analoga), dtype='float')
rm = np.zeros((len(days), num_analoga), dtype='float')
for i, coef in enumerate(corr[start_day_idx:end_day_idx+1]):
    for j in range(5):
        co[i,j] = coef[j]
for k, r in enumerate(rmse[start_day_idx:end_day_idx+1]):
    for l in range(5):
        rm[k,l] = r[l]
        
ana_corr_1 = co[:,0]
ana_corr_2 = co[:,1]
ana_corr_3 = co[:,2]
ana_corr_4 = co[:,3]
ana_corr_5 = co[:,4]

ana_rmse_1 = rm[:,0]
ana_rmse_2 = rm[:,1]
ana_rmse_3 = rm[:,2]
ana_rmse_4 = rm[:,3]
ana_rmse_5 = rm[:,4]

list_ana_corr = [ana_corr_1,ana_corr_2,ana_corr_3,ana_corr_4,ana_corr_5]
list_ana_rmse = [ana_rmse_1,ana_rmse_2,ana_rmse_3,ana_rmse_4,ana_rmse_5]

#plot
fig,(ax1,ax2) = plt.subplots(2,1, figsize=(15,10))
for i in range(5):
    ax1.plot(days, list_ana_corr[i], label='analogon_'+str(i+1))
    ax2.plot(days, list_ana_rmse[i], label='analogon_'+str(i+1))

ax1.legend(loc = 1)
ax2.legend(loc = 3)
months = mdates.MonthLocator()  # every month
months_fmt = mdates.DateFormatter('%Y-%m')
ax1.xaxis.set_major_locator(months)
ax1.xaxis.set_major_formatter(months_fmt)
ax2.xaxis.set_major_locator(months)
ax2.xaxis.set_major_formatter(months_fmt)
plt.show()

#show median of corr and rmse for each analogon
for i,corr in enumerate(list_ana_corr):
    print('corr for analogon_' + str(i+1) + ': ', np.nanmedian(corr))
for i,rmse in enumerate(list_ana_rmse):
    print('rmse for analogon_' + str(i+1) + ': ', np.nanmedian(rmse))