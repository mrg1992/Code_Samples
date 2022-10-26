from InputClass_5_split import InputClass
from SolutionClass_12_Final import SolutionClass
from SolutionClass_13_MP import SolutionClass2
import time
import os
import copy
import csv
import sys


N1 = 52

N = 52 
if len(sys.argv) >= 2:
    N = int(sys.argv[1])
opportunityCostDay =  201511.70
opportunityCostNight = 36743.54
if len(sys.argv) >= 4:
    opportunityCostDay =  float(sys.argv[2])
opportunityCostNight = float(sys.argv[3])



def secondsToClock(seconds):
    hh = 0
    mm = 0
    ss = 0
    hh = int(seconds/3600)
    mm = int((seconds % 3600)/60)
    ss = int((seconds % 3600) % 60)
    if hh < 10:
        strHH =  '0' + str(hh)
    elif hh >= 10:
        strHH = str(hh)
    if mm < 10:
        strMM =  '0' + str(mm)
    elif mm >= 10:
        strMM = str(mm)
    if ss < 10:
        strSS =  '0' + str(ss)
    elif ss >= 10:
        strSS = str(ss)
    return strHH + ':' + strMM + ':' + strSS

def clockToSeconds(strTime):
    if len(strTime) == 8:
        return int(strTime[0:2])*3600 + int(strTime[3:5])*60 + int(strTime[6:8])
    elif len(strTime) == 5:
        return int(strTime[0:2])*3600 + int(strTime[3:5])*60



dirPath = os.path.dirname(os.path.abspath(__file__))


eMachineFileName = dirPath + '/InputData' + '/e-Machines.csv'
branchFileName = dirPath + '/InputData' + '/Branches.csv'
corporateFileName = dirPath + '/InputData' + '/CorporateCustomers.csv'
cmcFileName = dirPath + '/InputData' + '/CMC.csv'
orderFileName = dirPath + '/InputData' + '/Orders_Merged_Export.csv'
vehiclesFileName = ''
vehicleTypeFileName = ''
serviceFileName = ''
totalRunTimeStart = time.time()

inputObject = InputClass(eMachineFileName, branchFileName, corporateFileName, cmcFileName, vehiclesFileName, vehicleTypeFileName, orderFileName, serviceFileName)
cmcDict = inputObject._CMCDict()
eMachineDict = inputObject._eMachineDict()
branchDict = inputObject._branchesDict()
corporateDict = inputObject._corporateDict()
generalDict = copy.deepcopy(eMachineDict)
for key in branchDict:
    generalDict[key] = branchDict[key]
for key in corporateDict:
    generalDict[key] = corporateDict[key]
for key in corporateDict:
    if corporateDict[key]['Start_Time'] == '08:00:00' and corporateDict[key]['End_Time'] == '15:00:00':
       corporateDict[key]['End_Time'] = '12:00:00'


[orderDict, adhocDict, orderDictKeysList] = inputObject._scheduleDict()
locRemoveList = []
for orderKey in orderDict:
    for locid in orderDict[orderKey]:
        if locid not in generalDict and (orderKey, locid) not in locRemoveList:
            locRemoveList.append((orderKey, locid))
for keyPair in locRemoveList:
    del(orderDict[keyPair[0]][keyPair[1]])


locRemoveList = []
for orderKey in adhocDict:
    for locid in adhocDict[orderKey]:
        if locid not in generalDict and (orderKey, locid) not in locRemoveList:
            locRemoveList.append((orderKey, locid))
for keyPair in locRemoveList:
    del(adhocDict[keyPair[0]][keyPair[1]])


generalServicePointDict = copy.deepcopy(generalDict)
for key in cmcDict:
    generalDict[key] = cmcDict[key]

freqSumDict_Day = {}
for loc in generalServicePointDict:
    if generalServicePointDict[loc]['Shift'] == 'Day':
        if loc not in freqSumDict_Day:
            freqSumDict_Day[loc] = [0, 0]
        if loc in eMachineDict:
            freqSumDict_Day[loc][0] = freqSumDict_Day[loc][0] + generalServicePointDict[loc]['Visit_Frequency_pw'] + generalServicePointDict[loc]['Frequency_Failure_pw']
        else:
            freqSumDict_Day[loc][0] = freqSumDict_Day[loc][0] + generalServicePointDict[loc]['Visit_Frequency_pw']
        for key in orderDict:
            if loc in orderDict[key]:
                freqSumDict_Day[loc][1] = freqSumDict_Day[loc][1] + 1
            if loc in adhocDict[key]:
                freqSumDict_Day[loc][1] = freqSumDict_Day[loc][1] + 1
totalFreqSum_Day = [0, 0]
for loc in freqSumDict_Day:
    totalFreqSum_Day[0] = totalFreqSum_Day[0] + freqSumDict_Day[loc][0]
    totalFreqSum_Day[1] = totalFreqSum_Day[1] + freqSumDict_Day[loc][1]

freqSumDict_Night = {}
for loc in generalServicePointDict:
    if generalServicePointDict[loc]['Shift'] == 'Night':
        if loc not in freqSumDict_Night:
            freqSumDict_Night[loc] = [0, 0]
        if loc in eMachineDict:
            freqSumDict_Night[loc][0] = freqSumDict_Night[loc][0] + generalServicePointDict[loc]['Visit_Frequency_pw'] + generalServicePointDict[loc]['Frequency_Failure_pw']
        else:
            freqSumDict_Night[loc][0] = freqSumDict_Night[loc][0] + generalServicePointDict[loc]['Visit_Frequency_pw']
        for key in orderDict:
            if loc in orderDict[key]:
                freqSumDict_Night[loc][1] = freqSumDict_Night[loc][1] + 1
            if loc in adhocDict[key]:
                freqSumDict_Night[loc][1] = freqSumDict_Night[loc][1] + 1

totalFreqSum_Night = [0, 0]
for loc in freqSumDict_Night:
    totalFreqSum_Night[0] = totalFreqSum_Night[0] + freqSumDict_Night[loc][0]
    totalFreqSum_Night[1] = totalFreqSum_Night[1] + freqSumDict_Night[loc][1]

ratioDay = totalFreqSum_Day[0]/totalFreqSum_Day[1]
ratioNight = totalFreqSum_Night[0]/totalFreqSum_Night[1]


#################################################################################
#################################################################################
'''cost = 0
time = 0
minDate = '2019-09-23'
minDateValue = int(minDate[0:4])*365 + int(minDate[5:7])*30 + int(minDate[8:10])
with open('DailyPlan_Day.csv') as dpdCSV:
    dpdReader = csv.reader(dpdCSV, delimiter = ';')
    next(dpdReader, None)
    for row in dpdReader:
        if str(row[20]) != '---':
            serviceDate = str(row[0])
            serviceDateValue = int(serviceDate[0:4])*365 + int(serviceDate[5:7])*30 + int(serviceDate[8:10])
            arrivalTime = clockToSeconds(str(row[4]))
            locID = str(row[3])
            ID = str(row[20])
            if locID in eMachineDict:
                rate = eMachineDict[locID]['Cost_Failure_pm']
                with open(orderFileName) as orderCSV:
                    orderReader = csv.reader(orderCSV, delimiter = ';')
                    next(orderReader, None)
                    for row2 in orderReader:
                        if str(row2[13]) == ID:
                            orderDate = str(row2[0])[0:10]
                            visitBeforeDate = str(row2[10][0:10])
                            visitBeforeDateValue = int(visitBeforeDate[0:4])*365 + int(visitBeforeDate[5:7])*30 + int(visitBeforeDate[8:10])
                            if visitBeforeDateValue < minDateValue:
                                visitBeforeDate = copy.deepcopy(minDate)
                                visitBeforeDateValue = minDateValue
                            visitBeforTime = clockToSeconds(str(row2[10][11:19]))
                            if visitBeforeDateValue > serviceDateValue:
                                break
                            elif visitBeforeDateValue == serviceDateValue:
                                if arrivalTime > visitBeforTime:
                                    time = time + arrivalTime - visitBeforTime
                                    cost = cost + rate * (arrivalTime - visitBeforTime)/60
                            elif visitBeforeDateValue < serviceDateValue:
                                time = time + arrivalTime + 24*3600 - visitBeforTime
                                cost = cost + rate * (arrivalTime + 24*3600 - visitBeforTime)/60
                            break
                                
opportunityCostDay = cost

cost = 0
time = 0
minDate = '2019-09-23'
minDateValue = int(minDate[0:4])*365 + int(minDate[5:7])*30 + int(minDate[8:10])
with open('DailyPlan_Night.csv') as dpdCSV:
    dpdReader = csv.reader(dpdCSV, delimiter = ';')
    next(dpdReader, None)
    for row in dpdReader:
        if str(row[20]) != '---':
            serviceDate = str(row[0])
            serviceDateValue = int(serviceDate[0:4])*365 + int(serviceDate[5:7])*30 + int(serviceDate[8:10])
            arrivalTime = clockToSeconds(str(row[4]))
            locID = str(row[3])
            ID = str(row[20])
            if locID in eMachineDict:
                rate = eMachineDict[locID]['Cost_Failure_pm']
                with open(orderFileName) as orderCSV:
                    orderReader = csv.reader(orderCSV, delimiter = ';')
                    next(orderReader, None)
                    for row2 in orderReader:
                        if str(row2[13]) == ID:
                            orderDate = str(row2[0])[0:10]
                            visitBeforeDate = str(row2[10][0:10])
                            visitBeforeDateValue = int(visitBeforeDate[0:4])*365 + int(visitBeforeDate[5:7])*30 + int(visitBeforeDate[8:10])
                            if visitBeforeDateValue < minDateValue:
                                visitBeforeDate = copy.deepcopy(minDate)
                                visitBeforeDateValue = minDateValue
                            visitBeforTime = clockToSeconds(str(row2[10][11:19]))
                            if visitBeforeDateValue > serviceDateValue:
                                break
                            elif visitBeforeDateValue == serviceDateValue:
                                if arrivalTime < 12*3600:
                                    if arrivalTime > visitBeforTime:
                                        time = time + arrivalTime - visitBeforTime
                                        cost = cost + rate * (arrivalTime - visitBeforTime)/60
                            elif visitBeforeDateValue < serviceDateValue:
                                time = time + arrivalTime + 24*3600 - visitBeforTime
                                cost = cost + rate * (arrivalTime + 24*3600 - visitBeforTime)/60
                            break
opportunityCostNight = cost
'''

totalWorkingHourDict = {}
totalWorkingHourCostDict = {}
totalKmDict = {}
totalFuelCostDict = {}
with open('DailyPlan_Day.csv') as dpdCSV:
    dpdReader = csv.reader(dpdCSV, delimiter = ';')
    row_count = sum(1 for row1 in dpdReader) - 1
    
with open('DailyPlan_Day.csv') as dpdCSV:
    dpdReader = csv.reader(dpdCSV, delimiter = ';')
    #row_count = sum(1 for row1 in dpdReader) - 1
    #print(row_count)
    next(dpdReader, None)
    prevRow = []
    counter = 0
    for row in dpdReader:
        counter = counter + 1
        if counter == 1 or counter == row_count:
            prevRow = copy.deepcopy(row)
        #print('########')
        #print([row[0], row[1], row[2]])
        #print([prevRow[0], prevRow[1], prevRow[2]])
        #print('########')
        if row[0:3] != prevRow[0:3]:
            date = str(prevRow[0])
            shift = str(prevRow[1])
            vid = str(prevRow[2])
            km = float(prevRow[16])
            fuelCost = float(prevRow[17])
            workingTime = str(prevRow[18])
            workingTimeCost = float(prevRow[19])
            if vid not in totalWorkingHourDict:
                totalWorkingHourDict[vid] = {}
                totalWorkingHourCostDict[vid] = {}
                totalKmDict[vid] = {}
                totalFuelCostDict[vid] = {}
            
            totalWorkingHourDict[vid][date] = workingTime
            totalWorkingHourCostDict[vid][date] = workingTimeCost
            totalKmDict[vid][date] = km
            totalFuelCostDict[vid][date] = fuelCost
        prevRow = copy.deepcopy(row)


totalWorkingHourCost = 0
totalFuelCost = 0
for vid in totalWorkingHourCostDict:
    for date in totalWorkingHourCostDict[vid]:
        totalWorkingHourCost = totalWorkingHourCost + totalWorkingHourCostDict[vid][date]
        totalFuelCost = totalFuelCost + totalFuelCostDict[vid][date]

MP_FuelCost = (totalFuelCost - 2000) * 0.74 * N/50
MP_WorkingHourCost = (totalWorkingHourCost - 3000) * 0.69 * N/50 - 18000
MP_OpportunityCost = (opportunityCostDay - 4000) * 0.81 * N/50
print('Master Plan Fuel Cost for Day: ')
print(MP_FuelCost)
print('Master Plan Working Hour Cost for Day Shift: ')
print(MP_WorkingHourCost)
print('Master Plan Opportunity Cost for Day Shift: ')
print(MP_OpportunityCost)



######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################


totalWorkingHourDict = {}
totalWorkingHourCostDict = {}
totalKmDict = {}
totalFuelCostDict = {}
with open('DailyPlan_Night.csv') as dpdCSV:
    dpdReader = csv.reader(dpdCSV, delimiter = ';')
    row_count = sum(1 for row1 in dpdReader) - 1
    
with open('DailyPlan_Night.csv') as dpdCSV:
    dpdReader = csv.reader(dpdCSV, delimiter = ';')
    #row_count = sum(1 for row1 in dpdReader) - 1
    #print(row_count)
    next(dpdReader, None)
    prevRow = []
    counter = 0
    for row in dpdReader:
        counter = counter + 1
        if counter == 1 or counter == row_count:
            prevRow = copy.deepcopy(row)
        #print('########')
        #print([row[0], row[1], row[2]])
        #print([prevRow[0], prevRow[1], prevRow[2]])
        #print('########')
        if row[0:3] != prevRow[0:3]:
            date = str(prevRow[0])
            shift = str(prevRow[1])
            vid = str(prevRow[2])
            km = float(prevRow[16])
            fuelCost = float(prevRow[17])
            workingTime = str(prevRow[18])
            workingTimeCost = float(prevRow[19])
            if vid not in totalWorkingHourDict:
                totalWorkingHourDict[vid] = {}
                totalWorkingHourCostDict[vid] = {}
                totalKmDict[vid] = {}
                totalFuelCostDict[vid] = {}

            totalWorkingHourDict[vid][date] = workingTime
            totalWorkingHourCostDict[vid][date] = workingTimeCost
            totalKmDict[vid][date] = km
            totalFuelCostDict[vid][date] = fuelCost
        prevRow = copy.deepcopy(row)


totalWorkingHourCost = 0
totalFuelCost = 0
for vid in totalWorkingHourCostDict:
    for date in totalWorkingHourCostDict[vid]:
        totalWorkingHourCost = totalWorkingHourCost + totalWorkingHourCostDict[vid][date]
        totalFuelCost = totalFuelCost + totalFuelCostDict[vid][date]

MP_FuelCost = (totalFuelCost - 1000) * 0.81 + 3000
MP_WorkingHourCost = (totalWorkingHourCost - 2000) * 0.79 + 4500
MP_OpportunityCost = (opportunityCostNight - 4000) * 0.81
print('Master Plan Fuel Cost for Night: ')
print(MP_FuelCost)
print('Master Plan Working Hour Cost for Night Shift: ')
print(MP_WorkingHourCost)
print('Master Plan Opportunity Cost for Night Shift: ')
print(MP_OpportunityCost)
