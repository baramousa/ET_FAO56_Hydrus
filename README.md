# ET_FAO56_Hydrus
Python code for calculating Evapotranspiration ET according to FAO56 and separate it into Evaporation and Transpiration based on LAI (leaf area index), An output file is produced which is an input for Hydrus1-d model

The code read weather data from csv file similar to the one attached here. 
Names of the columns that need to be in the weather csv are :
- Date: in days
- TMAX,TMIN : max and min temperature in degrees
- RH I(%);RH II(%): max and min relative humidity
- WS(Km/hr): wind speed at 2m height
- SSH: sunshine hours per day
- RF(mm): daily precipitation in mm
- J: number of day in the year
##################################################################################################################################
##################################################################################################################################
In the python script following parameters need to be determined:
- path (string): the path to the project where the weather data are located
- file_name (string): name of the weather.csv data, for example "Weather_GKVK_2017_2018_ir" 
- The Crop coefficients depending on the growth stage (take from FAO56 tables): kcinit, kcbmid, kclate (doubles)
- starting and ending dates to be considered in hydrus model (or the period that will be printed in the output file):
  start_date(string) 
  end_date(string) 

- p_height(double): MAX PLANT HEIGHT in meters
- LAI(double): max LAI
- z(double): elevation above sea level
- lat(double):Latitude in radian
-gwth_period(list of integers): length of growth periods according to FAO, Linit,Ldev,Lmid,Llate growth periods tables pg 107, for example,  gwth_period=[20,35,40,30]
- t_sow(string): the time of seed sowing
