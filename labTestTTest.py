__author__ = 'ayanmukhopadhyay'

import numpy as np
import pandas as pd
import csv
from datetime import datetime
from sklearn.feature_extraction import DictVectorizer
import scipy.stats
from pandas import Series


'''
Method for one hot encoding a data frame
'''
def one_hot_dataframe(data, cols, replace=False):
    """ Takes a dataframe and a list of columns that need to be encoded.
        Returns a 3-tuple comprising the data, the vectorized data,
        and the fitted vectorizor."""
    vec = DictVectorizer(sparse=False)
    vecData = pd.DataFrame(vec.fit_transform(data[cols].T.to_dict().values()))
    vecData.columns = vec.get_feature_names()
    vecData.index = data.index
    if replace is True:
        data = data.drop(cols, axis=1)
        data = data.join(vecData)
    return (data, vecData, vec)
'''
Use this code only for the first time if the data has not been generated
Else just read the data and join it
'''


'''
df = pd.read_pickle("dataPickle")
for indexStay, rowStay in df.iterrows():
    print(type(rowStay.DISCHARGE_DATE))
    print(type(rowStay.RUID))
    print(rowStay.DISCHARGE_DATE)
    print(rowStay.RUID)
    break

columns = df.columns.values

adt = pd.read_csv("adt_Ahmet.csv",quoting=csv.QUOTE_NONE,encoding='cp1252')

#adt["DISCHARGE_DATE"] = pd.to_datetime(adt["DISCHARGE_DATE"],format="%Y-%m-%d")
for indexStay, rowStay in adt.iterrows():
    print(type(rowStay.DISCHARGE_DATE))
    print(type(rowStay.RUID))
    print(rowStay.DISCHARGE_DATE)
    print(rowStay.RUID)
    break
for counter in range(len(adt.index)):
   #adt.xs(counter,copy=False)["DISCHARGE_DATE"] = datetime.strptime(adt.xs(counter)["DISCHARGE_DATE"],'%Y-%m-%d')
    adt.ix[counter,"DISCHARGE_DATE"] = datetime.strptime(adt.ix[counter,"DISCHARGE_DATE"],'%Y-%m-%d')

for indexStay, rowStay in adt.iterrows():
    print(type(rowStay.DISCHARGE_DATE))
    print(type(rowStay.RUID))
    print(rowStay.DISCHARGE_DATE)
    print(rowStay.RUID)
    break
joinedData = pd.merge(df,adt,how='inner',on=['RUID','DISCHARGE_DATE'])
joinedData.to_pickle("joinedData")
'''
joinedData = pd.read_pickle("joinedData")
print(joinedData.head(10))
# print(columns)
#
# #iterate through the columns
# for counterCol in range(3,len(columns)):
#     columnData = df[columns[counterCol]]
#     print("a")


columns = joinedData.columns.values
readmittedIn30 = joinedData.readmittedIn30.values
#print('sum = %d' % np.sum(readmittedIn30))
reAd30 = joinedData.loc[joinedData.readmittedIn30 == 1]
NotReAd30 = joinedData.loc[joinedData.readmittedIn30 == 0]
#print(len(reAd30.index))
#print(len(NotReAd30.index))
chosenlabs = []
chosenlabsCat = []
attemptedLabsCont = 0
attemptedLabsCat = 0
for counter in range(3,len(columns)):
    #print indices
    if counter%100==0:
        print(counter)
    #only look at the final values
    if 'End' in columns[counter]:
        stringVal = False
        invalidRe, invalidReNot = 0,0 #count if all values are -1, i.e. not available
        #if data wasnt found
        invalidIndicator = -1
        if joinedData[columns[counter]].dtype == np.float64 or joinedData[columns[counter]].dtype == np.int64:
            continue
        dfTempRe = reAd30[columns[counter]]
        dfTempReNot = NotReAd30[columns[counter]]
        #create containers for storing values for this column for read30 and noread30
        reVals = [0]*len(dfTempRe.index)
        notReVals = [0]*len(dfTempReNot.index)
        #go through the data and see if they are all strings or numbers
        dfTempNP = dfTempRe.values
        dfTempNotNP = dfTempReNot.values
        for counterObs in range(dfTempNP.shape[0]):
            #we still do not know if the entire column is string or floats. Check to decide the test
            try:
                testVal = float(dfTempNP[counterObs])
            except TypeError:
                stringVal=True
                testVal = str(dfTempNP[counterObs])
            except ValueError:
                stringVal=True
                testVal = str(dfTempNP[counterObs])
                #not all columns are numeric

            if testVal==invalidIndicator:
                invalidRe+=1
            else:
                reVals.append(testVal)
        #check the percentage of invalid data in the column
        percentInvalidRe = invalidRe/dfTempNP.shape[0] * 100

        for counterObs in range(dfTempNotNP.shape[0]):
            try:
                testVal = float(dfTempNotNP[counterObs])
            except TypeError:
                stringVal=True
                testVal = str(dfTempNotNP[counterObs])
            except ValueError:
                stringVal=True
                testVal = str(dfTempNotNP[counterObs])
                continue
                #not all columns are numeric
            if testVal==invalidIndicator:
                invalidReNot+=1
            else:
                notReVals.append(testVal)

        percentInvalidNotRe = invalidReNot/dfTempNotNP.shape[0] * 100

        #check if the column has enough data for both reAd30 and notReAd30
        if percentInvalidNotRe < 80 and percentInvalidRe < 80:
            if stringVal:
                #do chis square test
                attemptedLabsCat+=1
                # print("Implement chi square")
                #dfTemp, _, _ = one_hot_dataframe(Series.to_frame(dfTempRe), [columns[counter]], replace=True)
                dfTemp, _, _ = one_hot_dataframe(joinedData[['readmittedIn30',columns[counter]]], [columns[counter]], replace=True)
                #print(dfTemp.shape)
                chiSqInputRe = []
                chiSqInputReNot = []
                for counterCol in range(len(dfTemp.columns.values)):
                    if counterCol<2:
                        continue
                    categories = dfTemp.columns.values[counterCol]
                    chiSqInputRe.append(dfTemp[(dfTemp[categories]!=-1)&(dfTemp['readmittedIn30']==1)][categories].sum())
                    chiSqInputReNot.append(dfTemp[(dfTemp[categories]!=-1)&(dfTemp['readmittedIn30']==0)][categories].sum())
                # for counterCol in range(len(dfTemp.columns.values)):
                #     if counterCol<2:
                #         continue
                #     categories = dfTemp.columns.values[counterCol]
                #     chiSqInputReNot.append(dfTemp[(dfTemp[categories]!=-1)&(dfTemp['readmittedIn30']==0)][categories].sum())

                #perform chiSqaureTest
                obs = np.array([chiSqInputRe,chiSqInputReNot])
                chi2, p, dof, expected = scipy.stats.chi2_contingency(obs)
                print(p)
                if p<=0.05:
                    # print("Found Cov")
                    chosenlabsCat.append(columns[counter])


            else:
                #perform T Test
                attemptedLabsCont+=1
                #do t test
                tStat, pVal = scipy.stats.ttest_ind(reVals,notReVals)
                if pVal <= 0.05:
                    chosenlabs.append(columns[counter])
                    print(pVal)
                    print(columns[counter])

print(chosenlabs)
print(attemptedLabsCont)
print(attemptedLabsCat)
print(chosenlabsCat)
                

#sum(reVals)/len(reVals)


        # dfTemp, _, _ = one_hot_dataframe(dfTemp, [columns[counter]], replace=True)
        # reAd30 = joinedData.loc[joinedData.readmissionIn30 == 1]
        # NotReAd30 = joinedData.loc[joinedData.readmissionIn30 == 0]
        # ds1 = reAd30.columns[counter].values
        # ds2 = reAd30.columns[counter].values








