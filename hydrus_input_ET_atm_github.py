# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 12:01:28 2021
A script that read weather data that include date, max and min temp, 
max and min relative humidity, wind speed in km/hr, rainfall(include irrigation!!) in mm ,and J, plant height in cm,
kcb coeff see FAO56 page 135 and 136. Then calculate ETR and separate to Ep and Tp. 
a csv input file which include the atmospheric data for hydrus is then produced

Notes:
**due to lack of continuous observation of either LAI or crop heights during the seasons (few*kcmax) of kcmax 
had to be ignored so ke is always assumed to equal kcmax-kcb
** to be improved is kcmax between sowing and t_init, this code assume all period pre t_init to equal kinit
 
* info needed are :
    -p_height, LAI ,gwth_period(adapted to actual sowing and harvesting dates),kcinit,kcbmid,kclate as well as 
    the name of input weather data and start and end dates of the season
@author: Albara
"""



import os
import pandas as pd
import numpy as np
import datetime
import math
#########################################################################################
######################################################################################
##################################### INPUT ##################################################
#######################################################################################
#####################################################################################

#path to the folder where the weather data are located
path="C:\\Projects\\FOR2432\\A_WP3_model\\DATA_preperation_boundary_observed\\"
os.chdir(path)
#name of the weather data csv file
file_name="Weather_GKVK_2017_2018_ir" # data 2017-2021

#Crop coefficients depending on the growth stage (take from FAO56 tables)
kcinit=0.15
kcbmid=1.15
kclate=0.25
# starting and ending dates to be considered in hydrus model (or the period that will be printed in the output file)
start_date = "2018-06-15"#se3 long ir
end_date = "2018-12-15"#se3 long ir

#MAX PLANT HEIGHT in meters
p_height=2.25
# max LAI
LAI=2.75
#elevation above sea level
z=934 
##Latitude in radian R reads angles in radian by default
lat=13.0875*3.14/180

#Linit,Ldev,Lmid,Llate growth periods tables pg 107 FAO56
gwth_period=[20,35,40,30]#se5/maize 
#the time of seed sowing, accoring to the growth periods other crop dates are calculated
t_sow='07.08.2018'
t_sow = datetime.datetime.strptime(t_sow, '%d.%m.%Y')#se5 IR
###################################################################################
###################################################################################

t_init = t_sow + datetime.timedelta(days=gwth_period[0])
t_dev = t_init + datetime.timedelta(days=gwth_period[1])
t_mid = t_dev + datetime.timedelta(days=gwth_period[2])
t_late = t_mid + datetime.timedelta(days=gwth_period[3])


#name of the output csv for hydrus
file_out=file_name[18:22]+"_atmo.csv"
#read input csv in pandas dataframe
data= pd.read_csv(file_name+".csv",decimal=".", sep=";")

data['Date'] =pd.to_datetime(data['Date'], format='%d.%m.%y')


data['amp']=(data['TMAX']-data['TMIN'])/2
data['avg']=(data['TMAX']+data['TMIN'])/2

TMEAN=(data['TMAX']+data['TMIN'])/2
TMAX=data['TMAX']#name of the column with max temp
#converting tmax to kelvin
TMAXK=TMAX+273.16
#converting tmin to kelvin
TMIN=data['TMIN'] #name of the column with min temp
TMINK=TMIN+273.16

Pr=101.3*(((293-0.0065*z)/293)**5.26)
psych=0.665/1000*Pr
esTMAX=0.6108*np.exp(17.27*TMAX/(TMAX+237.3))
esTMIN=0.6108*np.exp(17.27*TMIN/(TMIN+237.3))
es=(esTMAX+esTMIN)/2
delta=4098*es/(TMEAN+237.3)**2
RHMAX=data['RH I(%)'] #name of column with max relative humidity
RHMIN=data['RH II(%)'] #name of column with min relative humidity
ea=(esTMIN*RHMAX/100+esTMAX*RHMIN/100)/2

J=data['J']
dr=1+0.033*np.cos(2*3.14*J/365)
sde=0.409*np.sin((2*3.14*J/365-1.39))

ws=np.arccos((-np.tan(lat))*np.tan(sde))

Ra=24*60/np.pi*0.082*dr*(ws*np.sin(lat)*np.sin(sde)+np.cos(lat)*np.cos(sde)*np.sin(ws))
N=24/np.pi*ws
n=data['SSH']# name of column with sunshine hours
Rs=(0.25+0.5*n/N)*Ra#here we have it measured convert by multiplying by 0.0864
Rso=(0.75+2*z/100000)*Ra
Rnl=4.903*10**-9*(TMAXK**4+TMINK**4)/2*(0.34-0.14*np.sqrt(ea))*(1.35*Rs/Rso-0.35)
Rns=0.77*Rs
Rn=Rns-Rnl
u2=data['WS(Km/hr)']*1000/60/60# col with wind speed in km/hr
Etr=(0.408*delta*Rn+psych*(900)/(TMEAN+273)*u2*(es-ea))/(delta+psych*(1+0.34*u2))

#Modification Kcb based on local weather conditons
#here only kcbmid should be adjusted according to max plant heigh
u2_avg=data[(data.Date>t_dev)&(data.Date<=t_mid)]['WS(Km/hr)'].mean()*1000/60/60
RHMIN_avg=data[(data.Date>t_dev)&(data.Date<=t_mid)]['RH II(%)'].mean()
#modification of kcbfull according to weather an max plant height
kcbfull=kcbmid+(0.04*(u2_avg-2)-0.004*(RHMIN_avg-45))*(p_height/3)**0.3
#modification of kcb mid according to LAI

kcbmid=kcinit+(kcbfull-kcinit)*(1-math.exp(-0.7*LAI))

u2_init=data[(data.Date>t_sow)&(data.Date<=t_init)]['WS(Km/hr)'].mean()*1000/60/60
u2_dev=data[(data.Date>t_init)&(data.Date<=t_dev)]['WS(Km/hr)'].mean()*1000/60/60
u2_mid=data[(data.Date>t_dev)&(data.Date<=t_mid)]['WS(Km/hr)'].mean()*1000/60/60
u2_late=data[(data.Date>t_mid)&(data.Date<=t_late)]['WS(Km/hr)'].mean()*1000/60/60

RHMIN_init=data[(data.Date>t_sow)&(data.Date<=t_init)]['RH II(%)'].mean()
RHMIN_dev=data[(data.Date>t_init)&(data.Date<=t_dev)]['RH II(%)'].mean()
RHMIN_mid=data[(data.Date>t_dev)&(data.Date<=t_mid)]['RH II(%)'].mean()
RHMIN_late=data[(data.Date>t_mid)&(data.Date<=t_late)]['RH II(%)'].mean()

kcbmax1=[]
kcbmax2=[]

##adjust kcb according to humiditz hieight and so
#data.loc[data['Date'] <= t_init, ['kcb']]=kcinit
#data.loc[data['Date'] <= t_init, ['kcbmax1']]=1.2+(0.04*(u2_init-2)-0.004*(RHMIN_init-45))*(0.15*p_height/3)**0.3
#data.loc[data['Date'] <= t_init, ['kcbmax2']]=data.loc[:, 'kcb'] +0.05

##calculate kcmax1 and 2 according to time and growing stage
for i in range(len(data)):
#for i in range(240,280):
    if data.Date[i]<=t_init:
        data.loc[i, 'kcb']=kcinit
        kcbmax1.append(1.2+(0.04*(u2_init-2)-0.004*(RHMIN_init-45))*(0.15*p_height/3)**0.3)

        kcbmax2.append(data.loc[i, 'kcb']+0.05)
    elif (data.Date[i]>t_init) & (data.Date[i]<t_dev):
        delta=data.Date[i]-t_init
        data.loc[i, 'kcb']=kcinit+(kcbmid-kcinit)*(delta.days)/gwth_period[1]
        kcbmax1.append(1.2+(0.04*(u2_init-2)-0.004*(RHMIN_init-45))*(0.5*p_height/3)**0.3)

        kcbmax2.append(data.loc[i, 'kcb']+0.05)
        
    elif (data.Date[i]>=t_dev) & (data.Date[i]<t_mid):
        data.loc[i, 'kcb']=kcbmid
        kcbmax1.append(1.2+(0.04*(u2_init-2)-0.004*(RHMIN_init-45))*(p_height/3)**0.3)

        kcbmax2.append(data.loc[i, 'kcb']+0.05)
    elif (data.Date[i]>=t_mid) & (data.Date[i]<t_late):
        delta=data.Date[i]-t_mid
        data.loc[i, 'kcb']=kcbmid-(kcbmid-kclate)*(delta.days)/gwth_period[3]
        kcbmax1.append(1.2+(0.04*(u2_init-2)-0.004*(RHMIN_init-45))*(p_height/3)**0.3)

        kcbmax2.append(data.loc[i, 'kcb']+0.05)
    else:
        data.loc[i, 'kcb']=kcinit
        kcbmax1.append(1.2)
        kcbmax2.append(data.loc[i, 'kcb']+0.05)
        
kcb=data['kcb']
data['kcbmax1']=kcbmax1
data['kcbmax2']=kcbmax2
kcmax=data[['kcbmax1','kcbmax2']].max(axis=1)
#fc=((adjkcb-0.15)/(kcmax-0.15))**(1+0.5*p_height)#fraction of soil coverd by plant
#few=1-fc #fraction of soil exposed for evaporation depending on type of irrigation may change, check FAO56
data['ke']=kcmax-kcb
#data['ke2']=few*kcmax
#ke=data[['ke1','ke2']].min(axis=1)
ke=data['ke']
data['Ep']=Etr*ke
data['Tp']=Etr*kcb
data['ETR']=Etr

# filter out the data to the desired modeling period

after_start_date = data["Date"] >= start_date
before_end_date = data["Date"] <= end_date
between_two_dates = after_start_date & before_end_date
data_f = data.loc[between_two_dates]
#preparing the atmo.csv for hydrus
tAtm=list(range(1,len(data_f)+1))
Prec=data_f['RF(mm)']/10 #remember to add irrigation
rSoil=data_f['Ep']/10
rRoot=data_f['Tp']/10
hCritA=np.full((len(data_f), ), 15000)
rB=np.full((len(data_f), ), 0)
hB=np.full((len(data_f), ), 0)
ht=np.full((len(data_f), ), 0)
tTop=data_f['avg']
tBot=np.full((len(data_f), ), 0)
Ampl=data_f['amp']
RootDepth=np.full((len(data_f), ), 0)
results=pd.DataFrame({'tAtm':tAtm,'Prec':Prec,'rSoil':rSoil,'rRoot':rRoot,'hCritA':hCritA,'rB':rB,'hB':hB,'ht':ht,'tTop':tTop,'tBot':tBot,'Ampl':Ampl,'RootDepth':RootDepth,'date':data_f.Date})
#results=results.reset_index(drop=True)
results.index = np.arange(1, len(results) + 1)
results.to_csv(file_out,decimal=',',sep=';')
#data_f.to_csv('tst.csv',decimal=',',sep=';')
