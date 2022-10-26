from InputClass_5_split import InputClass
from SolutionClass_12_Final import SolutionClass
from SolutionClass_13_MP import SolutionClass2
import time
import os
import copy
import csv
import numpy as np
import sys
from dateutil import rrule
from datetime import datetime


startDate = str(sys.argv[1])
finishDate = str(sys.argv[2])

dateObjectList = []
for dt in rrule.rrule(rrule.DAILY,
                      dtstart=datetime.strptime(startDate, '%Y-%m-%d'),
                      until=datetime.strptime(finishDate, '%Y-%m-%d')):
    dateObjectList.append(dt)
dateList = []
for dateObject in dateObjectList:
    dateList.append(dateObject.strftime('%Y-%m-%d'))



dirPath = os.path.dirname(os.path.abspath(__file__))

superDistMatFileName = dirPath + '/InputData/DistanceMatrix' + '/superDistMat_dumb'
normalDistMatFileName =  dirPath + '/InputData/DistanceMatrix' + '/normalDistMat_dumb'

eMachineFileName = dirPath + '/InputData' + '/e-Machines.csv'
branchFileName = dirPath + '/InputData' + '/Branches.csv'
corporateFileName = dirPath + '/InputData' + '/CorporateCustomers.csv'
cmcFileName = dirPath + '/InputData' + '/CMC.csv'
vehiclesFileName = dirPath + '/InputData' + '/Vehicles.csv'
vehicleTypeFileName = dirPath + '/InputData' + '/VehicleTypes.csv'
orderFileName = dirPath + '/InputData' + '/Orders_Merged_Export.csv'
serviceFileName = dirPath + '/InputData' + '/ServiceType.csv'

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

vehiclesDict = inputObject._vehiclesDict()
vehicleTypeDict = inputObject._vehicleTypeDict()
serviceTypeDict = inputObject._serviceTypeDict()

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
#####################################################################
#####################################################################
#####################################################################

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

totalWorkingHourDict = {}
totalWorkingHourCostDict = {}
totalKmDict = {}
totalFuelCost = {}
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
                totalFuelCost[vid] = {}
            '''if date not in totalWorkingHourDict[vid]:
                totalWorkingHourDict[vid][date] = 0
                totalWorkingHourCostDict[vid][date] = 0
                totalKmDict[vid][date] = 0
                totalFuelCost[vid][date] = 0'''
            totalWorkingHourDict[vid][date] = workingTime
            totalWorkingHourCostDict[vid][date] = workingTimeCost
            totalKmDict[vid][date] = km
            totalFuelCost[vid][date] = fuelCost
        prevRow = copy.deepcopy(row)

##############################################
#######   Working Hour  #######
rows = [['Vehicle_ID']]
for dt in dateList:
    rows[0].append(dt)
for vid in totalWorkingHourDict:
    subRow = [vid]
    for date in totalWorkingHourDict[vid]:
        if date in dateList:
            subRow.append(totalWorkingHourDict[vid][date])
    rows.append(subRow)

with open('WorkingHour_Day.csv', 'w', newline = '') as outputCSV:
    outputWriter = csv.writer(outputCSV, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
    outputWriter.writerows(rows)
#############################################
#######   Working Hour Cost  #######
rows = [['Vehicle_ID']]
for dt in dateList:
    rows[0].append(dt)
for vid in totalWorkingHourCostDict:
    subRow = [vid]
    for date in totalWorkingHourCostDict[vid]:
        if date in dateList:
            subRow.append(totalWorkingHourCostDict[vid][date])
    rows.append(subRow)

with open('WorkingHourCost_Day.csv', 'w', newline = '') as outputCSV:
    outputWriter = csv.writer(outputCSV, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
    outputWriter.writerows(rows)
#############################################
#######   Total Km  #######
rows = [['Vehicle_ID']]
for dt in dateList:
    rows[0].append(dt)
for vid in totalKmDict:
    subRow = [vid]
    for date in totalKmDict[vid]:
        if date in dateList:
            subRow.append(totalKmDict[vid][date])
    rows.append(subRow)

with open('Km_Day.csv', 'w', newline = '') as outputCSV:
    outputWriter = csv.writer(outputCSV, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
    outputWriter.writerows(rows)
#############################################
#######   Total Km  #######
rows = [['Vehicle_ID']]
for dt in dateList:
    rows[0].append(dt)
for vid in totalFuelCost:
    subRow = [vid]
    for date in totalFuelCost[vid]:
        if date in dateList:
            subRow.append(totalFuelCost[vid][date])
    rows.append(subRow)

with open('FuelCost_Day.csv', 'w', newline = '') as outputCSV:
    outputWriter = csv.writer(outputCSV, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
    outputWriter.writerows(rows)
    
#############################################################################################################################
#############################################################################################################################
#############################################################################################################################
#############################################################################################################################

totalWorkingHourDict = {}
totalWorkingHourCostDict = {}
totalKmDict = {}
totalFuelCost = {}
with open('DailyPlan_Night.csv') as dpdCSV:
    dpdReader = csv.reader(dpdCSV, delimiter = ';')
    row_count = sum(1 for row1 in dpdReader) - 1
    
with open('DailyPlan_Night.csv') as dpdCSV:
    dpdReader = csv.reader(dpdCSV, delimiter = ';')
    #row_count = sum(1 for row1 in dpdReader) - 1
    next(dpdReader, None)
    prevRow = []
    counter = 0
    for row in dpdReader:
        counter = counter + 1
        if counter == 1 or counter == row_count:
            prevRow = copy.deepcopy(row)
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
                totalFuelCost[vid] = {}
            '''if date not in totalWorkingHourDict[vid]:
                totalWorkingHourDict[vid][date] = 0
                totalWorkingHourCostDict[vid][date] = 0
                totalKmDict[vid][date] = 0
                totalFuelCost[vid][date] = 0'''
            totalWorkingHourDict[vid][date] = workingTime
            totalWorkingHourCostDict[vid][date] = workingTimeCost
            totalKmDict[vid][date] = km
            totalFuelCost[vid][date] = fuelCost
        prevRow = copy.deepcopy(row)

##############################################
#######   Working Hour  #######
rows = [['Vehicle_ID']]
for dt in dateList:
    rows[0].append(dt)
for vid in totalWorkingHourDict:
    subRow = [vid]
    for date in totalWorkingHourDict[vid]:
        if date in dateList:
            subRow.append(totalWorkingHourDict[vid][date])
    rows.append(subRow)

with open('WorkingHour_Night.csv', 'w', newline = '') as outputCSV:
    outputWriter = csv.writer(outputCSV, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
    outputWriter.writerows(rows)
#############################################
#######   Working Hour Cost  #######
rows = [['Vehicle_ID']]
for dt in dateList:
    rows[0].append(dt)
for vid in totalWorkingHourCostDict:
    subRow = [vid]
    for date in totalWorkingHourCostDict[vid]:
        if date in dateList:
            subRow.append(totalWorkingHourCostDict[vid][date])
    rows.append(subRow)

with open('WorkingHourCost_Night.csv', 'w', newline = '') as outputCSV:
    outputWriter = csv.writer(outputCSV, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
    outputWriter.writerows(rows)
#############################################
#######   Total Km  #######
rows = [['Vehicle_ID']]
for dt in dateList:
    rows[0].append(dt)
for vid in totalKmDict:
    subRow = [vid]
    for date in totalKmDict[vid]:
        if date in dateList:
            subRow.append(totalKmDict[vid][date])
    rows.append(subRow)

with open('Km_Night.csv', 'w', newline = '') as outputCSV:
    outputWriter = csv.writer(outputCSV, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
    outputWriter.writerows(rows)
#############################################
#######   Total Km  #######
rows = [['Vehicle_ID']]
for dt in dateList:
    rows[0].append(dt)
for vid in totalFuelCost:
    subRow = [vid]
    for date in totalFuelCost[vid]:
        if date in dateList:
            subRow.append(totalFuelCost[vid][date])
    rows.append(subRow)

with open('FuelCost_Night.csv', 'w', newline = '') as outputCSV:
    outputWriter = csv.writer(outputCSV, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
    outputWriter.writerows(rows)

            
            