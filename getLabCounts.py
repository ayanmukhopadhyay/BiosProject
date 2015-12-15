__author__ = 'ayanmukhopadhyay'

import pandas as pd
import numpy as np
from datetime import datetime
import csv

patientData = pd.read_csv("/Users/ayanmukhopadhyay/Documents/Vanderbilt/AdvancedStatisticalComputing/Project/Data/FONNESBECK_ADT_20151202.csv",quoting=csv.QUOTE_NONE,encoding='cp1252')
print(patientData.columns.values)

#get list of rows where event = discharge. Each row corresponds to a stay
hospStays = patientData.loc[patientData.Event == "Discharge"]
#object to store rows that are created
hospStaysUpdated = np.zeros((len(hospStays.index)),dtype=object)


labData = pd.read_csv("/Users/ayanmukhopadhyay/Documents/Vanderbilt/AdvancedStatisticalComputing/Project/Data/FONNESBECK_LAB_20151202.csv",quoting=csv.QUOTE_NONE)
labDataNP = labData.values


counterRow=0
counterStart=0
lastID = 0
for indexStay, rowStay in hospStays.iterrows():
    if counterRow%100==0:
        print(counterRow)
    foundPatient=False
    if counterRow > 0 and lastID != rowStay.RUID:
        counterStart = counterEnd
    lastID = rowStay.RUID
    #create temporary variables for storing total doses of medicines and the number of different types of medicines
    numTests=0
    try:
        admit = datetime.strptime(rowStay.Admission_date,'%m/%d/%Y')
        discharge = datetime.strptime(rowStay.DISCHARGE_DATE,'%m/%d/%Y')
    except TypeError:
        print("Error in row " + str(counterRow))
        continue
    for counter in range(counterStart,len(labDataNP)):
        if rowStay.RUID == labDataNP[counter][0]:
            foundPatient = True
            try:
                currDate = datetime.strptime(labDataNP[counter][2],'%m/%d/%y')
                #print(currDate)
            except ValueError:
                currDate = datetime.strptime(labDataNP[counter][2],'%m/%d/%Y')
                #print(currDate)
            except TypeError:
                continue

            if admit <= currDate  <= discharge:
                numTests+=1

        elif foundPatient:
            counterEnd = counter
            hospStaysUpdated[counterRow] = [rowStay.RUID,admit,discharge,numTests]
            break

        elif rowStay.RUID < labDataNP[counter][0]:
            break

    counterRow+=1

columnNames=['RUID','Admission_date','DISCHARGE_DATE','NUM_Tests']
df = pd.DataFrame(index=range(len(hospStaysUpdated)), columns=columnNames)
for counter in range(len(hospStaysUpdated)):
    df.iloc[counter] = hospStaysUpdated[counter]

#pickle the data frame
df.to_pickle("dataPickleTestCounts")
