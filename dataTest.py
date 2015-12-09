__author__ = 'ayanmukhopadhyay'

import pandas as pd
import csv
from datetime import datetime
import numpy as np
from itertools import chain
import sys
# bp = pd.read_csv("/Users/ayanmukhopadhyay/Documents/Vanderbilt/AdvancedStatisticalComputing/Project/Data/FONNESBECK_BP_20151202.csv",quoting=csv.QUOTE_NONE)
# print(bp.shape[0])


labData = pd.read_csv("/Users/ayanmukhopadhyay/Documents/Vanderbilt/AdvancedStatisticalComputing/Project/Data/FONNESBECK_LAB_20151202.csv",quoting=csv.QUOTE_NONE)
# labData.Lab_date = pd.to_datetime(labData.Lab_date)
# print(labData.head(10))
print(labData.columns.values)
labDataNP = labData.values
uniqueTests = pd.unique(labData.Lab_name.ravel())
uniqueTestsVal = uniqueTests
#print(len(uniqueTests))

testsDict = {}
for counter in range(len(uniqueTests)):
    testsDict.update({uniqueTests[counter]:counter})

patientData = pd.read_csv("/Users/ayanmukhopadhyay/Documents/Vanderbilt/AdvancedStatisticalComputing/Project/Data/FONNESBECK_ADT_20151202.csv",quoting=csv.QUOTE_NONE,encoding='cp1252')
print(patientData.columns.values)
#patientData['Admission_date'] = pd.to_datetime(patientData['Admission_date'])
#patientData['DISCHARGE_DATE'] = pd.to_datetime(patientData['DISCHARGE_DATE'])

#
# total = pd.merge(labData,patientData,how='inner',on='RUID')
#
# #print(total.head())
#
# #create lab reports based on per stay at the hospital
# npTotal = total.values #create numpy array. Iterating over rows would be faster

#get admission dates - each should be later a unique identifier (combined with patientID) for a row
admitDates = pd.unique(patientData.Admission_date.ravel())
#get list of rows where event = discharge. Each row corresponds to a stay
hospStays = patientData.loc[patientData.Event == "Discharge"]
hospStaysUpdated = np.zeros((len(hospStays.index)),dtype=object)
labsAll = []


lastID = 0
counterStart = 0
counterEnd = 0
#for each stay, get details about lab
counterRow = 0
for indexStay, rowStay in hospStays.iterrows():
    # if counterRow < 3410:
    #     counterRow+=1
    #     print(counterRow,rowStay.RUID)
    #     continue
    # print(counterRow,rowStay.RUID)
    if counterRow%100 == 0:
        print(counterRow)
    if counterRow > 0 and lastID != rowStay.RUID:
        counterStart = counterEnd
    lastID = rowStay.RUID
    #flag to see if we have found the id while iterating through the list
    foundPatient = False
    #convert to datetime once for each stay
    admit = datetime.strptime(rowStay.Admission_date,'%m/%d/%Y')
    discharge = datetime.strptime(rowStay.DISCHARGE_DATE,'%m/%d/%Y')
    # admit = rowStay.Admission_date
    # discharge = rowStay.DISCHARGE_DATE
    #print (admit)
    #print (discharge)
    #print (rowStay.RUID)
    labs = np.zeros(len(uniqueTests),dtype=object)
    labs[:] = -1
    #create a dataFrame for each stay. This is temporary. For each stay, let us have a data Frame that keeps each event
    #as a row and tests in columns. Then, we can find the mean and the median and discard the rest
    tempLabReportsPerStay = pd.DataFrame

    for counter in range(counterStart,len(labDataNP)):
        if rowStay.RUID == labDataNP[counter][0]:
            foundPatient = True
            try:
                currDate = datetime.strptime(labDataNP[counter][2],'%m/%d/%y')
            except ValueError:
                currDate = datetime.strptime(labDataNP[counter][2],'%m/%d/%Y')
            if admit <= currDate  <= discharge:
            #if admit <= labDataNP[counter][2] <= discharge:
                if labs[testsDict[labDataNP[counter][1]]] == -1: #if -1, nothing has been appended to this lab test for this stay
                    try:
                        #print(labDataNP[counter][3])
                        labs[testsDict[labDataNP[counter][1]]] = [float(labDataNP[counter][3])]
                    except ValueError:
                        labs[testsDict[labDataNP[counter][1]]] = [labDataNP[counter][3]]
                    except TypeError:
                        labs[testsDict[labDataNP[counter][1]]] = [labDataNP[counter][3]]


                else:#we already have at least 1 observation for this test. Append to this.
                    #print(labDataNP[counter][3])
                    try:
                        labs[testsDict[labDataNP[counter][1]]].append(float(labDataNP[counter][3]))
                    except ValueError:
                        labs[testsDict[labDataNP[counter][1]]].append(labDataNP[counter][3])
                    except TypeError:
                        labs[testsDict[labDataNP[counter][1]]].append(labDataNP[counter][3])

            # elif datetime.strptime(labDataNP[counter][2],'%m/%d/%y') > discharge:
            #     counterStart = counter
            #     labsAll.append(labs)
            #     break
        elif foundPatient:
            counterEnd = counter
            labsAll.append(labs)
            #for each lab type, find start observation, end observation and mean observation
            labDataSummary = [-1]*3
            for counterLabType in range(len(labs)):
                if labs[counterLabType]!=-1:
                    labStart = labs[counterLabType][0]
                    labEnd = labs[counterLabType][-1]
                    #if just one entry, that is the mean
                    if len(labs[counterLabType])==1:
                            labMean = labs[counterLabType][0]
                    else:#if more than one entry, check if all the values are floats: if yes, take mean, or take most freq value
                        #if (isinstance(labs[counterLabType][0],float)):
                        if all([isinstance(y,float) for y in labs[counterLabType]])==True:
                            #find the mean of floats
                            try:
                                labMean = sum(labs[counterLabType])/len(labs[counterLabType])
                            except TypeError:
                                #print(labs[counterLabType])
                                #print(counterLabType)
                                #print("Baal Chire Aati Badh")
                                sys.exit()

                        else:
                            #find the most commonly occurring value among strings
                            labMean = max(set(labs[counterLabType]),key=labs[counterLabType].count)
                    labDataSummary = [labStart,labEnd,labMean]
                #replace the lab observation by the 3 values we need
                labs[counterLabType] = labDataSummary
            temp = [[rowStay.RUID],[admit],[discharge]]
            temp.extend(labs)
            hospStaysUpdated[counterRow]= list(chain.from_iterable(temp))#flatten the list
            break

        elif rowStay.RUID < labDataNP[counter][0]:
            break

    counterRow+=1

#print("Generated Data")
npHospStays = np.array(hospStaysUpdated)
np.save('hospStaysLabs',npHospStays)








