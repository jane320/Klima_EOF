# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 10:50:32 2019

@author: nikta
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import pickle
import time
import datetime

#Zeitserie des Korrelationskoeffizienten für spezifisches Jahr und mehreren Analog-Tagen

#Wähle zu validierende Variable aus
var_list = ["RR","Tx","Tn","SPEI"]
var = var_list[1]

#Öffne den Datensatz der analogen Tage
filename = 'analog_dates_test.p'
analoga = pickle.load(open(filename, "rb" ))
#Öffne den Spartacus Datensatz
ds_sparta = xr.open_mfdataset('./' + str(var) + '/*.nc', decode_cf=True)

#Wähle den Validierungszeitraum aus
start_day = '1979-01-01'
end_day = '1979-12-31'

#Finde den Index wo der Validierungszeitraum beginnt und endet
td = []
for TD, AD in analoga:
    print(TD)
    td.append(TD)

start_day_occurences = np.where(td == np.datetime64(start_day))
start_day_idx = int(start_day_occurences[0])

end_day_occurences = np.where(td == np.datetime64(end_day))
end_day_idx = int(end_day_occurences[0])

#Variablen für den Korrelationskoeffizienten und RMSE
name1 = 'ana_corr_'+var+'_'+start_day+'_test' 
name2 = 'corr_'+var+'_'+start_day+'_test'
name3 = 'rmse_'+var+'_'+start_day+'_test'
globals()[name1] = []
globals()[name2] = []
globals()[name3] = []

t_start = time.time()

#num_analoga = 5

#corrcoef im Validierungszeitraum berechnen und speichern
#Schleife über alle TD und alle Analoga i in AD (hier 5 pro TD)
for TD, AD in analoga[start_day_idx:end_day_idx+1]:
    correlation = []
    rmse = []
    for i in AD:       
        date_string_1 = str(TD) #Target Day
        date_string_2 = str(i) #Analog Day
        
        #Finde TD und analogen Tag im Spartacus Datensatz
        day_1 = ds_sparta.sel(time=slice(date_string_1, date_string_1))
        day_2 = ds_sparta.sel(time=slice(date_string_2, date_string_2))
    
        x = day_1[var].values
        y = day_2[var].values        
        x=x.reshape((1,183690))[0]
        y=y.reshape((1,183690))[0]        
        x = x[~np.isnan(x)]
        y = y[~np.isnan(y)]
        
        #Berechne den Korrelationskoeffizienten
        cor=np.corrcoef(x,y)
        print(cor[0,1])
        correlation.append(cor[0,1])  
        
        #RMSE
        r = np.sqrt(( ( y - x )**2 ).mean())
        rmse.append(r)
    
    globals()[name1].append([TD, correlation])
    globals()[name2].append(correlation)
    globals()[name3].append(rmse)
    print(TD)
    
t_end_tmp = time.time()
print(str(datetime.timedelta(seconds=t_end_tmp - t_start)), '\n')
#Dauer 2:28:20.125097
#Dauer 1:30:---
    
#Ergebnis speichern
pickle.dump(globals()[name1], open('ana_corr_'+var+'_'+start_day+'_test.p', "wb" ))
pickle.dump(globals()[name2], open('corr_'+var+'_'+start_day+'_test.p', "wb" ))
pickle.dump(globals()[name3], open('rmse_'+var+'_'+start_day+'_test.p', "wb" ))