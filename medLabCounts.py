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

medData = pd.read_csv("/Users/ayanmukhopadhyay/Documents/Vanderbilt/AdvancedStatisticalComputing/Project/Data/FONNESBECK_MED_20151202.csv",quoting=csv.QUOTE_NONE)
medDataNP = medData.values #would rather iterate over a numpy array


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
    numMedications=0
    try:
        admit = datetime.strptime(rowStay.Admission_date,'%m/%d/%Y')
        discharge = datetime.strptime(rowStay.DISCHARGE_DATE,'%m/%d/%Y')
    except TypeError:
        print("Error in row " + str(counterRow))
        continue
    for counter in range(counterStart,len(medDataNP)):
        if rowStay.RUID == medDataNP[counter][0]:
            foundPatient = True
            try:
                currDate = datetime.strptime(medDataNP[counter][1],'%m/%d/%y')
                #print(currDate)
            except ValueError:
                currDate = datetime.strptime(medDataNP[counter][1],'%m/%d/%Y')
                #print(currDate)
            except TypeError:
                continue

            if admit <= currDate  <= discharge:
                numMedications+=1

        elif foundPatient:
            counterEnd = counter
            hospStaysUpdated[counterRow] = [rowStay.RUID,admit,discharge,numMedications]
            break

        elif rowStay.RUID < medDataNP[counter][0]:
            break

    counterRow+=1

columnNames=['RUID','Admission_date','DISCHARGE_DATE','NUM_Medication']
df = pd.DataFrame(index=range(len(hospStaysUpdated)), columns=columnNames)
for counter in range(len(hospStaysUpdated)):
    df.iloc[counter] = hospStaysUpdated[counter]

#pickle the data frame
df.to_pickle("dataPickleMedCounts")




