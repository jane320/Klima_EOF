# Klima_EOF
Klima Übung

# Anomalies
The file anomalies_NCEP.py calculates the anomalies for each day of the NCEP dataset and saves them.
Change path and use the test files which are in the repository for sea level pressure, relative humidity and specific humidity. You will also need utils.py for calculating the anomalies.

# EOFs
For EOFs use analog_method_NCEP.py
The program calculates mutivariate EOFs as well as the analogous dates for each date of the dataset. Furthermore it does 5 analogues for each day of the predifined time series. 

# Validation 
For validation, the Spartacus Dataset is used. corr_coef_NCEP.py determines the correlation coefficient and RMSE for one specific year of the dataset and the wanted variable. The program plot_validation_NCEP.py creates several plots for the previously saved files regarding correlation coefficient and RMSE.

You can find some more precise description of the programs as well as the validation of the year 1979 in Projektarbeit_Klimamodellierung.pdf. 

