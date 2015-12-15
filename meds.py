__author__ = 'ayanmukhopadhyay'
import pandas as pd
import csv
from datetime import datetime
import numpy as np
import sys

patientData = pd.read_csv("/Users/ayanmukhopadhyay/Documents/Vanderbilt/AdvancedStatisticalComputing/Project/Data/FONNESBECK_ADT_20151202.csv",quoting=csv.QUOTE_NONE,encoding='cp1252')
print(patientData.columns.values)

#get list of rows where event = discharge. Each row corresponds to a stay
hospStays = patientData.loc[patientData.Event == "Discharge"]
#object to store rows that are created
hospStaysUpdated = np.zeros((len(hospStays.index)),dtype=object)

#read medicine data
medData = pd.read_csv("/Users/ayanmukhopadhyay/Documents/Vanderbilt/AdvancedStatisticalComputing/Project/Data/FONNESBECK_MED_20151202.csv",quoting=csv.QUOTE_NONE)
medDataNP = medData.values #would rather iterate over a numpy array

counterRow=0
counterStart=0
lastID = 0
for indexStay, rowStay in hospStays.iterrows():
    #print row counter
    if counterRow%100==0:
        print(counterRow)
    #check if the current patient has been found
    foundPatient=False
    if counterRow > 0 and lastID != rowStay.RUID:
        counterStart = counterEnd
    lastID = rowStay.RUID
    #create temporary variables for storing total doses of medicines and the number of different types of medicines
    numMedications=0
    tempMeds=[]
    try:
        #parse date
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
            #if the recorded incident was within the stay we are looking for
            if admit <= currDate  <= discharge:
                numMedications+=1
                tempMeds.append(medDataNP[counter][2])

        elif foundPatient:
            #update the details in the container for final results
            counterEnd = counter
            hospStaysUpdated[counterRow] = [rowStay.RUID,admit,discharge,numMedications,len(set(tempMeds))]
            break

        elif rowStay.RUID < medDataNP[counter][0]:
            break

    counterRow+=1

#pickle the final data
columnNames=['RUID','Admission_date','DISCHARGE_DATE','NUM_Medication','Unique_Medication']
df = pd.DataFrame(index=range(len(hospStaysUpdated)+3), columns=columnNames)
for counter in range(len(hospStaysUpdated)):
    df.iloc[counter] = hospStaysUpdated[counter]

#pickle the data frame
df.to_pickle("dataPickleMeds")









