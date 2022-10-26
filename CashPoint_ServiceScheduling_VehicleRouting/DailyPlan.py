from InputClass_5_split import InputClass
from SolutionClass_12_Final import SolutionClass
from SolutionClass_13_MP import SolutionClass2
import time
import os
import copy
import shelve
import csv
import sys
from dateutil import rrule
from datetime import datetime
import numpy as np



startDate = str(sys.argv[1])#'2019-09-23'
finishDate = str(sys.argv[2])#'2019-09-28'

dateObjectList = []
for dt in rrule.rrule(rrule.DAILY,
                      dtstart=datetime.strptime(startDate, '%Y-%m-%d'),
                      until=datetime.strptime(finishDate, '%Y-%m-%d')):
    dateObjectList.append(dt)
dateList = []
for dateObject in dateObjectList:
    dateList.append(dateObject.strftime('%Y-%m-%d'))


timeKeyList = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']
if len(sys.argv) >= 4:
    timeKeyList = []
    for timeKey in sys.argv[3:len(sys.argv)]:
        timeKeyList.append(str(timeKey))


dirPath = os.path.dirname(os.path.abspath(__file__))

superDistMatFileName = dirPath + '/InputData/DistanceMatrix' + '/superDistMat_dumb'
normalDistMatFileName =  dirPath + '/InputData/DistanceMatrix' + '/normalDistMat_dumb'

eMachineFileName = dirPath + '/InputData' + '/e-Machines.csv'
branchFileName = dirPath + '/InputData' + '/Branches.csv'
corporateFileName = dirPath + '/InputData' + '/CorporateCustomers.csv'
cmcFileName = dirPath + '/InputData' + '/CMC.csv'
vehiclesFileName = dirPath + '/InputData' + '/Vehicles.csv'
vehicleTypeFileName = dirPath + '/InputData' + '/VehicleTypes.csv'
orderFileName = dirPath + '/InputData' + '/Orders.csv'
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

dateRemoveList = []
for orderKey in orderDict:
    if orderKey[0] not in dateList:
        dateRemoveList.append(orderKey)
for orderKey in dateRemoveList:
    del(orderDict[orderKey])
    del(adhocDict[orderKey])
    orderDictKeysList.remove(orderKey)

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
cmcQueueCapacity = cmcDict[list(cmcDict.keys())[0]]['Simultanious_Loading_Capacity']
cmcQueueDuration = cmcDict[list(cmcDict.keys())[0]]['Simultanious_Loading_Duration_m']
cmcStartTime = 0.0
cmcStatusDict = {}
cmcStatusDictKeysList = []
for t in range(0, 36 * 3600, int(cmcQueueDuration * 60)):
    tempKey = (t, t + cmcQueueDuration * 60)
    cmcStatusDictKeysList.append(tempKey)
    cmcStatusDict[tempKey] = {}
    cmcStatusDict[tempKey]['Queue_Vehicles'] = []
cmcStatusDictGeneral = {}
for key in orderDict:
    cmcStatusDictGeneral[key] = cmcStatusDict

cmcStatusDictNight = {}
cmcStatusDictKeysListNight = []
for t in range(-6 * 3600, 12 * 3600, int(cmcQueueDuration * 60)):
    tempKey = (t, t + cmcQueueDuration * 60)
    cmcStatusDictKeysListNight.append(tempKey)
    cmcStatusDictNight[tempKey] = {}
    cmcStatusDictNight[tempKey]['Queue_Vehicles'] = []
cmcStatusDictGeneralNight = {}
for key in orderDict:
    cmcStatusDictGeneralNight[key] = cmcStatusDictNight

        

rows = []
with open('MasterPlan_VehicleCount.csv') as vcCSV:
    vcReader = csv.reader(vcCSV, delimiter = ';')
    next(vcReader, None)
    for row in vcReader:
        N_hd = int(row[0])
        N_sd = int(row[1])
        N_sn = int(row[2])

with shelve.open(superDistMatFileName, 'r') as superDistMatDict:
    with shelve.open(normalDistMatFileName, 'r') as normalDistMatDict:
        solutionObject = SolutionClass(eMachineDict, branchDict, corporateDict, cmcDict, generalDict, vehiclesDict, vehicleTypeDict, orderDict, adhocDict, serviceTypeDict, normalDistMatDict, superDistMatDict, timeKeyList)
        [N_hd, hardRouteDict, N_sd, locationKeysDict, vehicleKeysDict, softRouteDict, gDict] = solutionObject._integratedRouting(generalServicePointDict, cmcStatusDictGeneral, cmcStatusDictKeysList, N_sd, N_hd)
        N_hd_List = []
        for key in N_hd:
            N_hd_List.append(N_hd[key])
        N_hard_day_max= np.max(N_hd_List)
        solutionObject2 = SolutionClass2(eMachineDict, branchDict, corporateDict, cmcDict, generalDict, vehiclesDict, vehicleTypeDict, orderDict, adhocDict, serviceTypeDict, normalDistMatDict, superDistMatDict, timeKeyList, N_hard_day_max)
        [N_sn, locationKeysDictNight, vehicleKeysDictNight, softNightRouteDict] = solutionObject2._integratedRouting(generalServicePointDict, cmcStatusDictGeneralNight, cmcStatusDictKeysListNight, N_sn)
        solutionObject._dailyPlan2CSV(softRouteDict, hardRouteDict)
        solutionObject2._dailyPlan2CSV(softNightRouteDict, {})

        
        


totalRunTimeEnd = time.time()
print("\nRunTime (minutes):")
print((totalRunTimeEnd - totalRunTimeStart)/60)




