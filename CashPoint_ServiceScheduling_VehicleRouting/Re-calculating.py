from InputClass_5_split import InputClass
from SolutionClass_12_Final import SolutionClass
from SolutionClass_13_MP import SolutionClass2
import time
import os
import copy
import shelve
import csv
from dateutil import rrule
from datetime import datetime
import numpy as np
import sys


shift = 'Day'
vehicleID = 'Vehicle22' 
dayStartTime = '09:30:00'
startLocationID = 'S1C1359'
startLocationArrival = '13:37:41'
startKm = 98.08
startUnitCapacity = 11.5
startMoneyCapacity = 182145560.0
startDistLabel = '268211604'
hadLunchFlag = 1


shift = str(sys.argv[1])
vehicleID = str(sys.argv[2]) 
dayStartTime = str(sys.argv[3])
startLocationID = str(sys.argv[4])
startLocationArrival = str(sys.argv[5])
startKm = float(sys.argv[6])
startUnitCapacity = float(sys.argv[7])
startMoneyCapacity = float(sys.argv[8])
startDistLabel = str(sys.argv[9])
hadLunchFlag = int(sys.argv[10])




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
reOptimizeFileName = dirPath + '/InputData' + '/re-optimizing_InputTemplate.csv'

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
generalServicePointDict = copy.deepcopy(generalDict)
for key in cmcDict:
    generalDict[key] = cmcDict[key]
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

        
timeKeyList = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']


with open('MasterPlan_VehicleCount.csv') as vcCSV:
    vcReader = csv.reader(vcCSV, delimiter = ';')
    next(vcReader, None)
    for row in vcReader:
        N_hd = int(row[0])
        N_sd = int(row[1])
        N_sn = int(row[2])
rows = []
reOptDict = {}
initialReturnFlag = 0
with open(reOptimizeFileName) as optCSV:
    optReader = csv.reader(optCSV, delimiter = ';')
    next(optReader, None)
    for row in optReader:
        if str(row[2]) != 'Done':
            date = str(row[0])
            locID = str(row[1])
            locationType = generalDict[locID]['Type']
            status = str(row[2])
            if status == 'Remaining':
                planned = 1
            else:
                planned = 0
            serviceType = str(row[3])
            visitBefore = str(row[4])
            priority = int(row[5])
            deliverySize = float(row[6])
            pickUpSize = float(row[7])
            deliveryAmount = float(row[8])
            pickUpAmount = float(row[9])
            orderID = str(row[10])
            if status == 'Add' and 'Replenish' in serviceType:
                initialReturnFlag = 1
            key = (date, shift)
            
            if key not in reOptDict:
                reOptDict[key] = {}
                reOptDict[key][locID] = [[locationType, planned, priority, serviceType, deliverySize, pickUpSize, deliveryAmount, pickUpAmount, orderID, visitBefore]]
                # [0.locationType, 1.planned, 2.priority, 3.serviceType, 4.deliverySize, 5.pickUpSize, 6.deliveryAmount, 7.pickUpAmount, 8.orderID, 9.visitBefore]
            else:
                if locID not in reOptDict[key]:
                    reOptDict[key][locID] = [[locationType, planned, priority, serviceType, deliverySize, pickUpSize, deliveryAmount, pickUpAmount, orderID, visitBefore]]
                else:
                    reOptDict[key][locID].append([locationType, planned, priority, serviceType, deliverySize, pickUpSize, deliveryAmount, pickUpAmount, orderID, visitBefore])
        
    

partialAdhocDictOriginal = {}
partialAdhocDictOriginal[(date, shift)] = {}
partialOrderDictOriginal = reOptDict


with shelve.open(superDistMatFileName, 'r') as superDistMatDict:
    with shelve.open(normalDistMatFileName, 'r') as normalDistMatDict:
        if shift == 'Day':
            solutionObject = SolutionClass(eMachineDict, branchDict, corporateDict, cmcDict, generalDict, vehiclesDict, vehicleTypeDict, orderDict, adhocDict, serviceTypeDict, normalDistMatDict, superDistMatDict, timeKeyList)
            [routeDict, missing] = solutionObject._reOptimize(vehicleID, dayStartTime, startLocationID, startLocationArrival, startKm, startUnitCapacity, startMoneyCapacity, startDistLabel, initialReturnFlag, hadLunchFlag, cmcStatusDictGeneral, cmcStatusDictKeysList, partialOrderDictOriginal, partialAdhocDictOriginal, date, shift)
            solutionObject._dailyPlan2CSV(routeDict, {}, 'ReOptimized_DailyPlan_Day.csv')
        else:
            solutionObject2 = SolutionClass2(eMachineDict, branchDict, corporateDict, cmcDict, generalDict, vehiclesDict, vehicleTypeDict, orderDict, adhocDict, serviceTypeDict, normalDistMatDict, superDistMatDict, timeKeyList)
            [routeDict, missing] = solutionObject2._reOptimize(vehicleID, dayStartTime, startLocationID, startLocationArrival, startKm, startUnitCapacity, startMoneyCapacity, startDistLabel, initialReturnFlag, hadLunchFlag, cmcStatusDictGeneralNight, cmcStatusDictKeysListNight, partialOrderDictOriginal, partialAdhocDictOriginal, date, shift)
            solutionObject2._dailyPlan2CSV(routeDict, {}, 'ReOptimized_DailyPlan_Night.csv')
        #solutionObject2 = SolutionClass2(eMachineDict, branchDict, corporateDict, cmcDict, generalDict, vehiclesDict, vehicleTypeDict, orderDict, adhocDict, serviceTypeDict, normalDistMatDict, superDistMatDict, timeKeyList)
        #[N_sn, locationKeysDictNight, vehicleKeysDictNight, softNightRouteDict] = solutionObject2._integratedRouting(generalServicePointDict, cmcStatusDictGeneralNight, cmcStatusDictKeysListNight, N_sn)
        #solutionObject._dailyPlan2CSV(softRouteDict, {}, 'ReOptimized_DailyPlan_Day.csv')
        #solutionObject2._dailyPlan2CSV(softNightRouteDict, {}, 'ReOptimized_DailyPlan_Night.csv')

        
        


totalRunTimeEnd = time.time()
print("\nRunTime (minutes):")
print((totalRunTimeEnd - totalRunTimeStart)/60)




