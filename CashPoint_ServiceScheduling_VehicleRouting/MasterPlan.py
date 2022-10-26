from InputClass_5_split import InputClass
from SolutionClass_12_Final import SolutionClass
from SolutionClass_13_MP import SolutionClass2
import time
import os
import copy
import shelve
import numpy as np
import sys
#from dateutil import rrule
#from datetime import datetime

N = int(sys.argv[1])
N2 = 21
N1 = N - N2
    


####################
#N1 = 31
#N2 = 21
####################

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
#vehiclesDict_Nght = {}
#for vid in vehiclesDict:
#    if vehiclesDict[vid]['Shift'] == 'Night':
#        vehiclesDict_Nght[vid] = vehiclesDict[vid]

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

with shelve.open(superDistMatFileName, 'r') as superDistMatDict:
    with shelve.open(normalDistMatFileName, 'r') as normalDistMatDict:
        #print(normalDistMatDict['13.9091,100.5507;12.3898,99.9861'])
        
        solutionObject = SolutionClass(eMachineDict, branchDict, corporateDict, cmcDict, generalDict, vehiclesDict, vehicleTypeDict, orderDict, adhocDict, serviceTypeDict, normalDistMatDict, superDistMatDict, timeKeyList)
        [N_hd, hardRouteDict, N_sd, locationKeysDict, vehicleKeysDict, softRouteDict, gDict] = solutionObject._integratedRouting(generalServicePointDict, cmcStatusDictGeneral, cmcStatusDictKeysList, initial_N_sd=N1, initial_N_hd=N2)
        N_hd_List = []
        for key in N_hd:
            N_hd_List.append(N_hd[key])
        N_hard_day_max= np.max(N_hd_List)
        solutionObject2 = SolutionClass2(eMachineDict, branchDict, corporateDict, cmcDict, generalDict, vehiclesDict, vehicleTypeDict, orderDict, adhocDict, serviceTypeDict, normalDistMatDict, superDistMatDict, timeKeyList, N_hard_day_max)
        [N_sn, locationKeysDictNight, vehicleKeysDictNight, softNightRouteDict] = solutionObject2._integratedRouting(generalServicePointDict, cmcStatusDictGeneralNight, cmcStatusDictKeysListNight)
        #[N_sd, locationKeysDict, vehicleKeysDict, softRouteDict, cmcStatusDict] = solutionObject._integratedRouting(generalServicePointDict, cmcStatusDictGeneral, cmcStatusDictKeysList)
        
        
        if N_hard_day_max + N_sd <= 52:
            freqOffset = 15
        elif N_hard_day_max + N_sd == 53:
            freqOffset = 17
        elif N_hard_day_max + N_sd == 54:
            freqOffset = 23
        else:
            freqOffset = 29

        #solutionObject._dailyPlan2CSV(softRouteDict, hardRouteDict)
        #solutionObject2._dailyPlan2CSV(softNightRouteDict, {})
        print('\n################\n################\n')
        print('Step 1...\n')
        [sd_Master, sn_Master, hd_Master, hn_Master] = solutionObject._Main_MP_step1(generalServicePointDict, locationKeysDict, vehicleKeysDict, locationKeysDictNight, vehicleKeysDictNight, N_soft_day = N_sd, N_hard_day = N_hard_day_max, N_soft_night = N_sn)
        print('\n################\n################\n')
        print('Step 2...\n')
        print('Step 2: Soft-Window, Day...')
        sd_MasterDict = solutionObject._Main_MP_step2(len(sd_Master[1]), sd_Master[1], freqOffset)
        print('\nStep 2: Soft-Window, Night...')
        sn_MasterDict = solutionObject._Main_MP_step2(len(sn_Master[1]), sn_Master[1], freqOffset)
        print('\nStep 2: Hard-Window, Day...')
        hd_MasterDict = solutionObject._Main_MP_step2(len(hd_Master[1]), hd_Master[1], freqOffset)
        print('Master Plan Completed Successfully!\n')
        print('Exporting to CSV File...')
        solutionObject._MP2CSV(sd_MasterDict, sn_MasterDict, hd_MasterDict, gDict)
        
        


totalRunTimeEnd = time.time()
print("\nRunTime (minutes):")
print((totalRunTimeEnd - totalRunTimeStart)/60)




