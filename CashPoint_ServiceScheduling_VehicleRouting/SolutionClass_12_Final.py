import math
import numpy as np
import copy
import calendar
import csv
from datetime import datetime, timedelta


class SolutionClass:
    def __init__(self, eMachineDict, branchDict, corporateDict, cmcDict, generalDict, vehiclesDict, vehicleTypeDict, ordersDict, adhocDict, serviceTypeDict, normalDistMatDict, superDistMatDict, timeKeyList):
        self.eMachineDict = eMachineDict
        self.branchDict = branchDict
        self.corporateDict = corporateDict
        self.cmcDict = cmcDict
        self.generalDict = generalDict
        self.vehiclesDict = vehiclesDict
        self.vehicleTypeDict = vehicleTypeDict
        self.ordersDict = ordersDict
        self.serviceTypeDict = serviceTypeDict
        self.normalDistMatDict = normalDistMatDict
        self.superDistMatDict = superDistMatDict
        self.timeKeyList = timeKeyList
        self.adhocDict = adhocDict
        self.offsetN_sd = 0
        #self.vehiclesDict_Night = {}
        self.logCounter = 0
        #for vid in self.vehiclesDict:
        #    if self.vehiclesDict[vid]['Shift'] == 'Night':
        #        self.vehiclesDict_Night[vid] = self.vehiclesDict
        
        '''for loc in self.generalDict:
            if self.generalDict[loc]['Model'] == 'E-Machine':
                self.generalDict[loc]['Visit_Frequency_pw_fake'] = 0
                for key in self.ordersDict:
                    if loc in self.ordersDict[key] or loc in self.adhocDict[key]:
                        self.generalDict[loc]['Visit_Frequency_pw_fake'] = self.generalDict[loc]['Visit_Frequency_pw_fake'] + 1#int(loc in self.ordersDict[key]) + int(loc in self.adhocDict[key])
            else:
                if self.generalDict[loc]['Model'] != 'CMC':
                    self.generalDict[loc]['Visit_Frequency_pw_fake'] = self.generalDict[loc]['Visit_Frequency_pw']
        '''
        #for key in self.ordersDict:
        #    for locid in self.ordersDict[key]:
        #        for item in self.ordersDict[key][locid]:
        #            if item[2] == 0:
        #                self.generalDict[locid]['Start_Time'] = item[11]
    
    
    def _secondsToClock(self, seconds):
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
    
    def _clockToSeconds(self, strTime):
        if len(strTime) == 8:
            return int(strTime[0:2])*3600 + int(strTime[3:5])*60 + int(strTime[6:8])
        elif len(strTime) == 5:
            return int(strTime[0:2])*3600 + int(strTime[3:5])*60
    
    def _dateToWeekDay(self, strDate):
        weekDayList = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return weekDayList[calendar.weekday(int(strDate[0:4]), int(strDate[5:7]), int(strDate[8:10]))]
    
    def _furthestLocationDirect(self, originID, locationList):
        distList = []
        #with shelve.open(self.normalDistMatFileName, 'r') as normalDistMat:
        for i in range(len(locationList)):
            locID = locationList[i]
            distKey = self.generalDict[originID]['Latitude'] + ',' + self.generalDict[originID]['Longitude'] + ';' + self.generalDict[locID]['Latitude'] + ',' + self.generalDict[locID]['Longitude']
            #print([originID, locID, distKey])
            distList.append(self.normalDistMatDict[distKey]['Direct_Distance_m'])
        index = np.argmax(distList)
        return [locationList[index], distList[index]]
            
    def _closestLocationDirect(self, originID, locationList, funcFlag = 0):
        distList = []
        if funcFlag == 0:
            for i in range(len(locationList)):
                locID = locationList[i]
                distKey = self.generalDict[originID]['Latitude'] + ',' + self.generalDict[originID]['Longitude'] + ';' + self.generalDict[locID]['Latitude'] + ',' + self.generalDict[locID]['Longitude']
                distList.append(self.normalDistMatDict[distKey]['Direct_Distance_m'])
            index = np.argmin(distList)
            return [locationList[index], distList[index]]
        else:
            locID = locationList[0]
            distKey = self.generalDict[originID]['Latitude'] + ',' + self.generalDict[originID]['Longitude'] + ';' + self.generalDict[locID]['Latitude'] + ',' + self.generalDict[locID]['Longitude']
            return self.normalDistMatDict[distKey]['Distance_m']
    def _furthestLocationDuration(self, originID, locationList, weekDay, tempTime):
        self.logCounter = self.logCounter + 1
        with open('log_day.txt', 'a') as f:
            print('#############################################\n#############################################\n', file=f)
            print('log counter: %d ;;; Length of LocationList: %d' %(self.logCounter, len(locationList)), file=f)
            distList = []
            distLabelList = []
            for i in range(len(locationList)):
                locID = locationList[i]
                distKey = self.generalDict[originID]['Latitude'] + ',' + self.generalDict[originID]['Longitude'] + ';' + self.generalDict[locID]['Latitude'] + ',' + self.generalDict[locID]['Longitude']
                timeKey = self._fixDistMatTimeKeys(tempTime)
                print([-1,i+1], file= f)
                temp = self.superDistMatDict[distKey][weekDay][timeKey]
                distList.append(temp[0])
                distLabelList.append(temp[1])
            print('#############################################\n#############################################\n', file=f)
            index = np.argmax(distList)
        return [locationList[index], 0.95 * distList[index], distLabelList[index]]
    
    def _closestLocationDuration(self, originID, locationList, weekDay, tempTime, funcFlag = 0):
        self.logCounter = self.logCounter + 1
        distList = []
        distLabelList = []
        #with shelve.open(self.superDistMatFileName, 'r') as superDistMat:
        if funcFlag == 0:
            with open('log_day.txt', 'a') as f:
                print('#############################################\n#############################################\n', file=f)
                print('log counter: %d ;;; Length of LocationList: %d' %(self.logCounter, len(locationList)), file=f)
                for i in range(len(locationList)):
                    locID = locationList[i]
                    distKey = self.generalDict[originID]['Latitude'] + ',' + self.generalDict[originID]['Longitude'] + ';' + self.generalDict[locID]['Latitude'] + ',' + self.generalDict[locID]['Longitude']
                    timeKey = self._fixDistMatTimeKeys(tempTime)
                    print([-1, i + 1], file=f)
                    temp = self.superDistMatDict[distKey][weekDay][timeKey]
                    distList.append(temp[0])
                    distLabelList.append(temp[1])
                index = np.argmin(distList)
            return [locationList[index], 0.95 * distList[index], distLabelList[index]]
        else:
            with open('log_day.txt', 'a') as f:
                print('#############################################\n#############################################\n', file=f)
                print('log counter: %d ;;; Length of LocationList: %d' %(self.logCounter, len(locationList)), file=f)
                locID = locationList[0]
                distKey = self.generalDict[originID]['Latitude'] + ',' + self.generalDict[originID]['Longitude'] + ';' + self.generalDict[locID]['Latitude'] + ',' + self.generalDict[locID]['Longitude']
                timeKey = self._fixDistMatTimeKeys(tempTime)
                print([-1,  1], file=f)
                temp = self.superDistMatDict[distKey][weekDay][timeKey]
            return [0.95 * temp[0], temp[1]]
                
                
    
    def _fixDistMatTimeKeys(self, currentTime):
        timeKeyList = self.timeKeyList #list(superDistMatDict[list(superDistMatDict.keys())[0]]['Monday'].keys())
        beforeList = []
        afterList = []
        beforeDifferenceList = []
        afterDifferenceList = []
        unsortedTimeKeyList = []
        sortedTimeKeyList = []
        for j in range(len(timeKeyList)):
            timeKey = timeKeyList[j]
            unsortedTimeKeyList.append(self._clockToSeconds(timeKey))
            if self._clockToSeconds(timeKey) < currentTime:
                beforeList.append(timeKey)
                beforeDifferenceList.append(currentTime - self._clockToSeconds(timeKey))
        indexList = np.argsort(unsortedTimeKeyList)
        for i in range(len(indexList)):
            sortedTimeKeyList.append(timeKeyList[indexList[i]])
        
        for timeKey in timeKeyList:
            if self._clockToSeconds(timeKey) > currentTime:
                afterList.append(timeKey)
                afterDifferenceList.append(self._clockToSeconds(timeKey) - currentTime)
    
        index1 = np.argmin(beforeDifferenceList)
        downLimit = beforeList[index1]
        if len(afterDifferenceList) > 0:
            index2 = np.argmin(afterDifferenceList)
            upLimit = afterList[index2]
            if currentTime >= (self._clockToSeconds(upLimit) + self._clockToSeconds(downLimit))/2:
                return upLimit
            else:
                return downLimit
        else:
            upLimit = sortedTimeKeyList[0]
            if currentTime >= (self._clockToSeconds(upLimit) + 24*3600 + self._clockToSeconds(downLimit))/2:
                return upLimit
            else:
                return downLimit
    
    def _assignLocations2vehicles(self, locationList, N, maxF, funcFlagg = 0):
        if len(locationList) > 0:
            print('####  Key Assignment  Start ####')
            tempLocationList = copy.deepcopy(locationList)
            vehicleKeysDict = {}
            locationKeysDict = {}
            #N = math.ceil(len(locationList)/maxKeyNumber)
            #maxF = 0
            cmcID = list(self.cmcDict.keys())[0]
            tempVehicleID = list(self.vehiclesDict.keys())[self.offsetN_sd]
            initialVehicleID = 1
            myVehiclesDict = {}
            myVehiclesDict[initialVehicleID] = self.vehiclesDict[tempVehicleID]
            for i in range(2, N + 1):
                myVehicleID = i
                myVehiclesDict[myVehicleID] = self.vehiclesDict[list(self.vehiclesDict.keys())[i - 1 + int(funcFlagg == 1) * self.offsetN_sd]]
            #for locID in locationList:
            #    maxF = maxF + self.generalDict[locID]['Visit_Frequency_pw']
            #maxF = math.ceil(maxF/N)
            flag1 = 1
            while flag1:
                for vID in myVehiclesDict:
                    print(vID)
                    f = 0
                    vehicleKeysDict[vID] = []
                    currentLocation = self._furthestLocationDirect(cmcID, tempLocationList)[0]
                    f = f + self.generalDict[currentLocation]['Visit_Frequency_pw']
                    vehicleKeysDict[vID].append(currentLocation)
                    locationKeysDict[currentLocation] = vID
                    tempLocationList.remove(currentLocation)
                    if len(tempLocationList) == 0:
                        flag1 = 0
                    while len(tempLocationList) > 0:
                        currentLocation = self._closestLocationDirect(currentLocation, tempLocationList)[0]
                        f = f + self.generalDict[currentLocation]['Visit_Frequency_pw']
                        vehicleKeysDict[vID].append(currentLocation)
                        locationKeysDict[currentLocation] = vID
                        tempLocationList.remove(currentLocation)
                        if len(tempLocationList) == 0:
                            flag1 = 0
                            break
                        if len(vehicleKeysDict[vID]) >= (math.ceil(len(locationList)/N) + 3) or f >= maxF + 3:
                            break
                    if flag1 == 0:
                        break
            print('&&&&&&&&  Key Assignment Done! &&&&&&&&')
            return [myVehiclesDict, vehicleKeysDict, locationKeysDict]
        else:
            return [[], [], []]
    def _cmcStatusUpdate(self, cmcStatusDict, cmcStatusDictKeysList, timeSeconds, vehicleID):
        cmcStatusDictTemp = copy.deepcopy(cmcStatusDict)
        flag = 1
        while flag:
            for key in cmcStatusDictKeysList:
                #print([key, timeSeconds])
                if key[0] <= timeSeconds < key[1]:
                    if len(cmcStatusDictTemp[key]['Queue_Vehicles']) < self.cmcDict[list(self.cmcDict.keys())[0]]['Simultanious_Loading_Capacity']:
                        cmcStatusDictTemp[key]['Queue_Vehicles'].append(vehicleID)
                        vehicleNextRouteStartTime = key[1]
                        flag = 0
                        break
                    else:
                        timeSeconds = timeSeconds + self.cmcDict[list(self.cmcDict.keys())[0]]['Simultanious_Loading_Duration_m'] * 60
        return [cmcStatusDictTemp, vehicleNextRouteStartTime]
    
    def _checkRoutingFlagUpdate(self, weekDay, t, currentLocation, currentMoneyCapacity, currentUnitCapacity, vMaxTime):
        cmcID = list(self.cmcDict.keys())[0]
        [deltaT, distLabel] = self._closestLocationDuration(currentLocation, [cmcID], weekDay, t, funcFlag = 1)
        tempFlag1 = 1
        tempRouteFlag = 1
        if t + deltaT > vMaxTime:
            tempFlag1 = 0
            return [tempFlag1, tempRouteFlag, deltaT]
        else:
            if currentMoneyCapacity < 0 or currentUnitCapacity < 0:
                tempRouteFlag = 0
                return [tempFlag1, tempRouteFlag, deltaT]
            else:
                return [tempFlag1, tempRouteFlag, deltaT]
    
    def _checkRouting(self, myVehiclesDict, vehicleKeysDict, locationKeysDict, cmcStatusDictInput, cmcStatusDictKeysList, partialOrderDictOriginal, partialOrderDictKeysListOriginal, partialAdhocDictOriginal, shift, maxWorkingTime = 13):
        print('@@@@@@ Check Routing... @@@@@@@')
        partialOrderDict = copy.deepcopy(partialOrderDictOriginal)
        partialAdhocDict = copy.deepcopy(partialAdhocDictOriginal)
        routeDict = {}
        tempVehicleKeysDict = {}
        for key in vehicleKeysDict:
            if len(vehicleKeysDict[key]) > 0:
                tempVehicleKeysDict[key] = vehicleKeysDict[key]
        cmcStatusDict = {}
        
        tempKeysList = []
        tempSortList = []
        for j in range(len(partialOrderDictKeysListOriginal)):
            key = partialOrderDictKeysListOriginal[j]
            date = key[0]
            tempSortList.append(int(date[0:4])*365 + int(date[5:7])*30 + int(date[8:10]))
        index_list = np.argsort(tempSortList)
        for index in index_list:
            tempKeysList.append(partialOrderDictKeysListOriginal[index])
        
        partialOrderDictKeysList = copy.deepcopy(tempKeysList)
        for j in range(len(partialOrderDictKeysList)):
            kmDict = {}
            fakeKmDict = {}
            workingTime = {}
            fakeWorkingTime = {}
            key = partialOrderDictKeysList[j]
            #print(key)
            date = key[0]
            #print([date, date[0], date[1]])
            weekDay = self._dateToWeekDay(date)
            cmcStatusDict[key] = copy.deepcopy(cmcStatusDictInput[key])
            routeDict[key] = {}
            lunchDict = {}
            routeNo = -1
            #routeDict[key][routeNo + 1] = {}
            for ii in range(1, len(myVehiclesDict) + 1):
                routeDict[key][ii] = []
            flag1 = 1
            while flag1:
                routeNo = routeNo + 1
                
                print('RouteNo:')
                print(routeNo)
                if routeNo == 0:
                    completeOrderList = {}
                    completeAdhocList = {}
                    nextRouteInfo = {}
                    vehicleDoneFlag = {}
                    for vID in range(1, len(tempVehicleKeysDict) + 1):
                        print([key, routeNo, vID])
                        vehicleDoneFlag[vID] = 0
                        nextRouteInfo[vID] = []
                        lunchDict[vID] = [0]
                        routeFinishFlag = 1
                        completeOrderList[vID] = []
                        completeAdhocList[vID] = []
                        for loc in partialOrderDict[key]:
                            if loc in tempVehicleKeysDict[vID]:
                                completeOrderList[vID].append(loc)
                        for loc in partialAdhocDict[key]:
                            if loc in tempVehicleKeysDict[vID]:
                                completeAdhocList[vID].append([loc, len(partialAdhocDict[key][loc])])
                        if len(completeOrderList[vID]) > 0:
                            activeOrderList = []
                            queueOrderList = []
                            startTimeList = []
                            
                            for i in range(len(completeOrderList[vID])):
                                locID = completeOrderList[vID][i]
                                startTimeList.append(self._clockToSeconds(self.generalDict[locID]['Start_Time']))
                            #print(completeOrderList[vID])
                            startTime = np.min(startTimeList)
                            for i in range(len(completeOrderList[vID])):
                                if startTime == startTimeList[i]:
                                    activeOrderList.append(completeOrderList[vID][i])
                                else:
                                    queueOrderList.append(completeOrderList[vID][i])
                            
                            tempTime = 10 * 3600 - 10 #self._clockToSeconds(myVehiclesDict[vID]['Start_Time'])
                            [cmcStatusDict[key], tempTime] = self._cmcStatusUpdate(cmcStatusDict[key], cmcStatusDictKeysList, tempTime, vID)
                            print('+#+#+#+#+#+#+#+')
                            print(tempTime/3600)
                            print('+#+#+#+#+#+#+#+')
                            arrival = tempTime - (myVehiclesDict[vID]['Time_at_CMC_bl_m']) * 60
                            vMaxTime = arrival + maxWorkingTime * 3600#24 * 3600 #self._clockToSeconds(myVehiclesDict[vID]['Max_Time'])
                
                            departure = tempTime
                            
                            lunchDict[vID].append(tempTime)
                            currentLocation = list(self.cmcDict.keys())[0]#myVehiclesDict[vID]['CMC_ID']
                            currentServiceType = '---'
                            currentServiceDuration = '---'
                            currentUnitCapacity = self.vehicleTypeDict[myVehiclesDict[vID]['Vehicle_Type_ID']]['Capacity_unit']
                            currentMoneyCapacity = self.vehicleTypeDict[myVehiclesDict[vID]['Vehicle_Type_ID']]['Insurance_Limit']
                            #currentKM = 0
                            workingTime[vID] = departure - arrival
                            if j != 5:
                                workingTimeCost = ((workingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(workingTime[vID] <= 8 * 3600) +  int(workingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((workingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WD_ph'])
                            else:
                                workingTimeCost = ((workingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(workingTime[vID] <= 8 * 3600) +  int(workingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((workingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WE_ph'])
                            kmDict[vID] =  0
                            kmFuelCost = kmDict[vID] * myVehiclesDict[vID]['Cost_Fuel_pkm']
                            orderID = '---'
                            currentDeliverySize = '---'
                            currentPickUpSize = '---'##############################
                            currentDeliveryAmount = '---'
                            currentPickUpAmount = '---'
                            currentSizeCapacityUsage = '---'
                            currentAmountCapacityUsage = '---'
                            distLabel = '---'
                            routeDict[key][vID] = [[currentLocation, self._secondsToClock(arrival), self._secondsToClock(departure), currentServiceType, currentServiceDuration, currentDeliverySize, currentPickUpSize, currentDeliveryAmount, currentPickUpAmount, currentSizeCapacityUsage, currentAmountCapacityUsage, currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, orderID, distLabel]]
                            ###############################################
                            tempRemoveList = []
                            adhocRemoveList = []
                            for kk in range(len(completeAdhocList[vID])):
                                [loc, adhocCount] = completeAdhocList[vID][kk]
                                for adhoc in partialAdhocDict[key][loc]:
                                    if self._clockToSeconds(adhoc[11]) < departure:
                                        if loc not in partialOrderDict[key]:
                                            partialOrderDict[key][loc] = [adhoc]
                                        else:
                                            partialOrderDict[key][loc].append(adhoc)
                                        
                                        if loc not in completeOrderList[vID]:
                                            completeOrderList[vID].append(loc)
                                            queueOrderList.append(loc)
                                        else:
                                            if loc not in activeOrderList:
                                                if loc not in queueOrderList:
                                                    queueOrderList.append(loc)
                                        completeAdhocList[vID][kk][1] = completeAdhocList[vID][kk][1] - 1
                                        adhocRemoveList.append((loc, adhoc))
                                        if completeAdhocList[vID][kk][1] == 0:
                                            tempRemoveList.append(completeAdhocList[vID][kk])
                                            
                            for [loc, adhoc] in adhocRemoveList:
                                partialAdhocDict[key][loc].remove(adhoc)
                            for item in tempRemoveList:
                                completeAdhocList[vID].remove(item)

                            if len(queueOrderList) > 0:
                                tempQueueOrderList = []
                                for i in range(len(queueOrderList)):
                                    qLocID = queueOrderList[i]
                                    if tempTime >= self._clockToSeconds(self.generalDict[qLocID]['Start_Time']):
                                        activeOrderList.append(qLocID)
                                    else:
                                        tempQueueOrderList.append(qLocID)
                                queueOrderList = copy.deepcopy(tempQueueOrderList)                            
                            
                                
                                
                            
                            ###############################################
                            [nextLocation, deltaT, distLabel] = self._furthestLocationDuration(currentLocation, activeOrderList, weekDay, tempTime)
                            fakeTempTime = tempTime + deltaT
                            fakeKmDict[vID] = kmDict[vID] + self._closestLocationDirect(currentLocation, [nextLocation], funcFlag=1)/1000
                            arrival = fakeTempTime
                            fakeCurrentLocation = nextLocation
                            currentOrder = copy.deepcopy(partialOrderDict[key][fakeCurrentLocation])
                            currentLocationType = self.generalDict[fakeCurrentLocation]['Type']
                            fakeFakeTempTime = fakeTempTime
                            fakeServiceTimeList = []
                            for jj in range(len(currentOrder)):
                                order = currentOrder[jj]
                                orderID = order[10]
                                currentServiceType = order[1]
                                currentDeliverySize = order[3]
                                currentPickUpSize = order[4]
                                currentDeliveryAmount = order[5]
                                currentPickUpAmount = order[6]
                                fakeServiceTimeList.append(self.serviceTypeDict[(currentLocationType, currentServiceType, shift)])
                                currentServiceDuration = np.max(self.serviceTypeDict[(currentLocationType, currentServiceType, shift)])
                                currentSizeCapacityUsage = np.max([currentDeliverySize, currentPickUpSize])
                                currentAmountCapacityUsage = np.max([currentDeliveryAmount, currentPickUpAmount])
                                currentUnitCapacity = currentUnitCapacity - currentSizeCapacityUsage
                                currentMoneyCapacity = currentMoneyCapacity - currentAmountCapacityUsage
                                fakeTempTime = fakeFakeTempTime + currentServiceDuration
                                fakeWorkingTime[vID] = fakeTempTime - self._clockToSeconds(routeDict[key][vID][0][1])
                                if j != 5:
                                    workingTimeCost = ((fakeWorkingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WD_ph'])
                                else:
                                    workingTimeCost = ((fakeWorkingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WE_ph'])
                                #print(self._checkRoutingFlagUpdate(weekDay, fakeTempTime, fakeCurrentLocation, currentMoneyCapacity, currentUnitCapacity, vMaxTime))
                                [flag1, routeFinishFlag, cmcDeltaT] = self._checkRoutingFlagUpdate(weekDay, fakeTempTime, fakeCurrentLocation, currentMoneyCapacity, currentUnitCapacity, vMaxTime)
                                #print([flag1, routeFinishFlag])
                                if flag1 == 0:
                                    return [0, [], [], []]
                                else:
                                    if routeFinishFlag == 0:
                                        break
                                    else:
                                        currentLocation = fakeCurrentLocation
                                        tempTime = fakeTempTime
                                        kmDict[vID] = fakeKmDict[vID]
                                        kmFuelCost = kmDict[vID] * myVehiclesDict[vID]['Cost_Fuel_pkm']
                                        workingTime[vID] = fakeWorkingTime[vID]
                                        partialOrderDict[key][currentLocation].remove(order)
                                        if jj == len(currentOrder) - 1:
                                            completeOrderList[vID].remove(currentLocation)
                                            activeOrderList.remove(currentLocation)
                                        #print([currentLocation, len(completeOrderList[vID]), len(activeOrderList), len(queueOrderList)])
                                        #print(queueOrderList)
                                        routeDict[key][vID].append([currentLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), currentServiceType, self._secondsToClock(currentServiceDuration), currentDeliverySize, currentPickUpSize, currentDeliveryAmount, currentPickUpAmount, currentSizeCapacityUsage, currentAmountCapacityUsage, currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, orderID, distLabel])
                            
                            
                            if tempTime > 12 * 3600 and lunchDict[vID][0] < 1 and routeFinishFlag == 1 and key[1] == 'Day':
                                lunchDict[vID][0] = lunchDict[vID][0] + 1
                                if lunchDict[vID][0] == 1:
                                    arrival = tempTime
                                    tempTime = tempTime + myVehiclesDict[vID]['Rest_Time_m'] * 60
                                    workingTime[vID] = tempTime - self._clockToSeconds(routeDict[key][vID][0][1])
                                    if j != 5:
                                        workingTimeCost = ((fakeWorkingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WD_ph'])
                                    else:
                                        workingTimeCost = ((fakeWorkingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WE_ph'])
                                    routeDict[key][vID].append([currentLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), 'Rest', self._secondsToClock(myVehiclesDict[vID]['Rest_Time_m'] * 60), '---', '---', '---', '---', '---', '---', currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, '---', '---'])
                                    
                            
                            while routeFinishFlag == 1 and len(completeOrderList[vID]) > 0:
                                if len(queueOrderList) > 0:
                                    tempQueueOrderList = []
                                    for i in range(len(queueOrderList)):
                                        qLocID = queueOrderList[i]
                                        if tempTime >= self._clockToSeconds(self.generalDict[qLocID]['Start_Time']):
                                            activeOrderList.append(qLocID)
                                        else:
                                            tempQueueOrderList.append(qLocID)
                                    queueOrderList = copy.deepcopy(tempQueueOrderList)
                                if len(activeOrderList) > 0:
                                    [nextLocation, deltaT, distLabel] = self._closestLocationDuration(currentLocation, activeOrderList, weekDay, tempTime) 
                                    fakeTempTime = tempTime + deltaT
                                    fakeKmDict[vID] = kmDict[vID] + self._closestLocationDirect(currentLocation, [nextLocation], funcFlag=1)/1000
                                    arrival = fakeTempTime
                                    fakeCurrentLocation = nextLocation
                                    currentOrder = copy.deepcopy(partialOrderDict[key][fakeCurrentLocation])
                                    currentLocationType = self.generalDict[fakeCurrentLocation]['Type']
                                    fakeFakeTempTime = fakeTempTime
                                    fakeServiceTimeList = []
                                    for jj in range(len(currentOrder)):
                                        order = currentOrder[jj]
                                        orderID = order[10]
                                        currentServiceType = order[1]
                                        currentDeliverySize = order[3]
                                        currentPickUpSize = order[4]
                                        currentDeliveryAmount = order[5]
                                        currentPickUpAmount = order[6]
                                        fakeServiceTimeList.append(self.serviceTypeDict[(currentLocationType, currentServiceType, shift)])
                                        currentServiceDuration = np.max(fakeServiceTimeList)
                                        currentSizeCapacityUsage = np.max([currentDeliverySize, currentPickUpSize])
                                        currentAmountCapacityUsage = np.max([currentDeliveryAmount, currentPickUpAmount])
                                        currentUnitCapacity = currentUnitCapacity - currentSizeCapacityUsage#np.max([currentDeliverySize - currentPickUpSize])
                                        currentMoneyCapacity = currentMoneyCapacity - np.max([currentDeliveryAmount, currentPickUpAmount])
                                        fakeTempTime = fakeFakeTempTime + currentServiceDuration
                                        fakeWorkingTime[vID] = fakeTempTime - self._clockToSeconds(routeDict[key][vID][0][1])
                                        if j != 5:
                                            workingTimeCost = ((fakeWorkingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WD_ph'])
                                        else:
                                            workingTimeCost = ((fakeWorkingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WE_ph'])
                                        [flag1, routeFinishFlag, cmcDeltaT] = self._checkRoutingFlagUpdate(weekDay, fakeTempTime, fakeCurrentLocation, currentMoneyCapacity, currentUnitCapacity, vMaxTime)        
                                        #print([flag1, routeFinishFlag])
                                        if flag1 == 0:
                                            #print(routeDict[key][vID][routeNo])
                                            return [0, [], [], [], []]
                                        else:
                                            if routeFinishFlag == 0:
                                                break
                                            else:
                                                currentLocation = fakeCurrentLocation
                                                tempTime = fakeTempTime
                                                kmDict[vID] = fakeKmDict[vID]
                                                kmFuelCost = kmDict[vID] * myVehiclesDict[vID]['Cost_Fuel_pkm']
                                                workingTime[vID] = fakeWorkingTime[vID]
                                                partialOrderDict[key][currentLocation].remove(order)
                                                if jj == len(currentOrder) - 1:
                                                    completeOrderList[vID].remove(currentLocation)
                                                    activeOrderList.remove(currentLocation)
                                                #print([currentLocation, len(completeOrderList[vID]), len(activeOrderList), len(queueOrderList)])
                                                #print(queueOrderList)
                                                routeDict[key][vID].append([currentLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), currentServiceType, self._secondsToClock(currentServiceDuration), currentDeliverySize, currentPickUpSize, currentDeliveryAmount, currentPickUpAmount, currentSizeCapacityUsage, currentAmountCapacityUsage, currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, orderID, distLabel])
                                    
                                    if tempTime > 12 * 3600 and lunchDict[vID][0] < 1:
                                        lunchDict[vID][0] = lunchDict[vID][0] + 1
                                        if lunchDict[vID][0] == 1:
                                            arrival = tempTime
                                            tempTime = tempTime + myVehiclesDict[vID]['Rest_Time_m'] * 60
                                            workingTime[vID] = tempTime - self._clockToSeconds(routeDict[key][vID][0][1])
                                            if j != 5:
                                                workingTimeCost = ((fakeWorkingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WD_ph'])
                                            else:
                                                workingTimeCost = ((fakeWorkingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WE_ph'])
                                            routeDict[key][vID].append([currentLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), 'Rest', self._secondsToClock(myVehiclesDict[vID]['Rest_Time_m'] * 60), '---', '---', '---', '---', '---', '---', currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, '---', '---'])
                                    
                                else:
                                    if len(queueOrderList) > 0:
                                        startTimeList = []
                                        for k in range(len(queueOrderList)):
                                            qLocID = queueOrderList[k]
                                            startTimeList.append(self._clockToSeconds(self.generalDict[qLocID]['Start_Time']))
                                        startTime = np.min(startTimeList)
                                        tempTime = startTime
                                        tempQueueOrderList = []
                                        for k in range(len(queueOrderList)):
                                            if startTimeList[k] == startTime:
                                                activeOrderList.append(queueOrderList[k])
                                            else:
                                                tempQueueOrderList.append(queueOrderList[k])
                                        queueOrderList = copy.deepcopy(tempQueueOrderList)
                            
                            
                            nextLocation = list(self.cmcDict.keys())[0]#myVehiclesDict[vID]['CMC_ID']
                            [deltaT, distLabel] = self._closestLocationDuration(currentLocation, [nextLocation], weekDay, tempTime, funcFlag=1)
                            arrival = tempTime + deltaT
                            tempTime = tempTime + deltaT
                            kmDict[vID] = kmDict[vID] + self._closestLocationDirect(currentLocation, [nextLocation], funcFlag=1)/1000
                            kmFuelCost = kmDict[vID] * myVehiclesDict[vID]['Cost_Fuel_pkm']
                            workingTime[vID] = tempTime - self._clockToSeconds(routeDict[key][vID][0][1])
                            if j != 5:
                                workingTimeCost = ((workingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(workingTime[vID] <= 8 * 3600) +  int(workingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((workingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WD_ph'])
                            else:
                                workingTimeCost = ((workingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(workingTime[vID] <= 8 * 3600) +  int(workingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((workingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WE_ph'])   
                            #routeDict[key][routeNo][vID].append([nextLocation, tempTime, currentUnitCapacity, currentMoneyCapacity])
                            if routeFinishFlag == 0 and len(completeOrderList[vID]) > 0:
                                tempTime = tempTime + self.serviceTypeDict[('CMC', 'Reload Box', shift)]    
                                currentUnitCapacity = self.vehicleTypeDict[myVehiclesDict[vID]['Vehicle_Type_ID']]['Capacity_unit']
                                currentMoneyCapacity = self.vehicleTypeDict[myVehiclesDict[vID]['Vehicle_Type_ID']]['Insurance_Limit']
                                currentServiceType = 'Reload Box'
                                currentLocationType = 'CMC'
                                currentServiceDuration = self.serviceTypeDict[('CMC', currentServiceType, shift)]
                                routeDict[key][vID].append([nextLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), currentServiceType, self._secondsToClock(currentServiceDuration), '---', '---', '---', '---', '---', '---', currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, '---', distLabel])
                                nextRouteInfo[vID] = [completeOrderList[vID], tempTime]
                                
                            
                            elif len(completeOrderList[vID]) == 0:
                                tempTime = tempTime + 3600
                                currentUnitCapacity = self.vehicleTypeDict[myVehiclesDict[vID]['Vehicle_Type_ID']]['Capacity_unit']
                                currentMoneyCapacity = self.vehicleTypeDict[myVehiclesDict[vID]['Vehicle_Type_ID']]['Insurance_Limit']
                                currentServiceType = 'Stand By'
                                currentServiceDuration = self.serviceTypeDict[('CMC', 'Reload Box', shift)]
                                routeDict[key][vID].append([nextLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), currentServiceType, self._secondsToClock(3600), '---', '---', '---', '---', '---', '---', currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, '---', distLabel])
                                nextRouteInfo[vID] = [completeOrderList[vID], tempTime]
                        else:
                            
####^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                            tempTime = 15 * 3600
                            arrival = tempTime - (myVehiclesDict[vID]['Time_at_CMC_bl_m']) * 60
                            vMaxTime = arrival + maxWorkingTime * 3600#24 * 3600 #self._clockToSeconds(myVehiclesDict[vID]['Max_Time'])
                
                            departure = tempTime
                            
                            lunchDict[vID].append(tempTime)
                            currentLocation = list(self.cmcDict.keys())[0]#myVehiclesDict[vID]['CMC_ID']
                            currentServiceType = '---'
                            currentServiceDuration = '---'
                            currentUnitCapacity = self.vehicleTypeDict[myVehiclesDict[vID]['Vehicle_Type_ID']]['Capacity_unit']
                            currentMoneyCapacity = self.vehicleTypeDict[myVehiclesDict[vID]['Vehicle_Type_ID']]['Insurance_Limit']
                            #currentKM = 0
                            workingTime[vID] = departure - arrival
                            if j != 5:
                                workingTimeCost = ((workingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(workingTime[vID] <= 8 * 3600) +  int(workingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((workingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WD_ph'])
                            else:
                                workingTimeCost = ((workingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(workingTime[vID] <= 8 * 3600) +  int(workingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((workingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WE_ph'])
                            kmDict[vID] =  0
                            kmFuelCost = kmDict[vID] * myVehiclesDict[vID]['Cost_Fuel_pkm']
                            orderID = '---'
                            currentDeliverySize = '---'
                            currentPickUpSize = '---'##############################
                            currentDeliveryAmount = '---'
                            currentPickUpAmount = '---'
                            currentSizeCapacityUsage = '---'
                            currentAmountCapacityUsage = '---'
                            distLabel = '---'
                            routeDict[key][vID] = [[currentLocation, self._secondsToClock(arrival), self._secondsToClock(departure), currentServiceType, currentServiceDuration, currentDeliverySize, currentPickUpSize, currentDeliveryAmount, currentPickUpAmount, currentSizeCapacityUsage, currentAmountCapacityUsage, currentUnitCapacity, currentUnitCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, orderID, distLabel]]
                            nextRouteInfo[vID] = [completeOrderList[vID], departure]
####^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^                            

                    cmcArrivalTimeList = []
                    nextRouteInfoKeysList = list(nextRouteInfo.keys())
                    for k in range(len(nextRouteInfoKeysList)):
                        v_id = nextRouteInfoKeysList[k]
                        #print(nextRouteInfo[v_id])
                        cmcArrivalTimeList.append(nextRouteInfo[v_id][1])
                    indices = np.argsort(cmcArrivalTimeList)
                    for index in indices:
                        v_id = nextRouteInfoKeysList[index]
                        if len(nextRouteInfo[v_id][0]) > 0:
                            [cmcStatusDict[key], nextRouteInfo[v_id][1]] = self._cmcStatusUpdate(cmcStatusDict[key], cmcStatusDictKeysList, nextRouteInfo[v_id][1], v_id)
                            
                        
                else: #routeNo > 0
                    print('\n\n\n\n\-----------------n\n\n\n=============\n\n\n\n------------\n\n\nVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYYYYYYYYYYYY\n')
                    fakeSum = 0
                    for v_id in vehicleDoneFlag:
                        fakeSum = fakeSum + vehicleDoneFlag[v_id]
                    if fakeSum == len(vehicleDoneFlag):
                        break
                     
                    for vID in range(1, len(tempVehicleKeysDict) + 1):
                        print([key, routeNo, vID])
                        completeOrderList[vID] = nextRouteInfo[vID][0]
                        tempTime = nextRouteInfo[vID][1]

                        if workingTime[vID] <= 9*3600:
#################################################################################################################

                            tempRemoveList = []
                            adhocRemoveList = []
                            for kk in range(len(completeAdhocList[vID])):
                                [loc, adhocCount] = completeAdhocList[vID][kk]
                                for adhoc in partialAdhocDict[key][loc]:
                                    if self._clockToSeconds(adhoc[11]) < tempTime:
                                        if loc not in partialOrderDict[key]:
                                            partialOrderDict[key][loc] = [adhoc]
                                        else:
                                            partialOrderDict[key][loc].append(adhoc)
                                        
                                        if loc not in completeOrderList[vID]:
                                            completeOrderList[vID].append(loc)
                                        completeAdhocList[vID][kk][1] = completeAdhocList[vID][kk][1] - 1
                                        adhocRemoveList.append((loc, adhoc))
                                        if completeAdhocList[vID][kk][1] == 0:
                                            tempRemoveList.append(completeAdhocList[vID][kk])
                                            
                            for [loc, adhoc] in adhocRemoveList:
                                partialAdhocDict[key][loc].remove(adhoc)
                            for item in tempRemoveList:
                                completeAdhocList[vID].remove(item)
############################################################################################################                        



                        
                        if len(completeOrderList[vID]) > 0:
                            print('yes')
                            print(len(nextRouteInfo[vID][0]))
                            #nextRouteInfo[vID] = []
                            routeFinishFlag = 1
                            ######completeOrderList[vID] = nextRouteInfo[vID][0]
                            activeOrderList = []
                            queueOrderList = []
                            ######tempTime = nextRouteInfo[vID][1]
                            vMaxTime = self._clockToSeconds(routeDict[key][vID][0][1]) + maxWorkingTime *3600#24 * 3600#self._clockToSeconds(myVehiclesDict[vID]['Max_Time'])


                            for i in range(len(completeOrderList[vID])):
                                locID = completeOrderList[vID][i]
                                if tempTime >= self._clockToSeconds(self.generalDict[locID]['Start_Time']):
                                    activeOrderList.append(locID)
                                else:
                                    queueOrderList.append(locID)
                            currentLocation = list(self.cmcDict.keys())[0]#myVehiclesDict[vID]['CMC_ID']
                            currentUnitCapacity = self.vehicleTypeDict[myVehiclesDict[vID]['Vehicle_Type_ID']]['Capacity_unit']
                            currentMoneyCapacity = self.vehicleTypeDict[myVehiclesDict[vID]['Vehicle_Type_ID']]['Insurance_Limit']
                            #currentKM = 0
                            #routeDict[key][routeNo][vID] = [[currentLocation, tempTime, currentUnitCapacity, currentMoneyCapacity]]
                            [nextLocation, deltaT, distLabel] = self._furthestLocationDuration(currentLocation, activeOrderList, weekDay, tempTime)
                            fakeTempTime = tempTime + deltaT
                            fakeKmDict[vID] = kmDict[vID] + self._closestLocationDirect(currentLocation, [nextLocation], funcFlag=1)/1000
                            arrival = fakeTempTime
                            fakeCurrentLocation = nextLocation
                            currentOrder = copy.deepcopy(partialOrderDict[key][fakeCurrentLocation])
                            currentLocationType = self.generalDict[fakeCurrentLocation]['Type']
                            fakeFakeTempTime = fakeTempTime
                            fakeServiceTimeList = []
                            for jj in range(len(currentOrder)):
                                order = currentOrder[jj]
                                orderID = order[10]
                                currentServiceType = order[1]
                                currentDeliverySize = order[3]
                                currentPickUpSize = order[4]
                                currentDeliveryAmount = order[5]
                                currentPickUpAmount = order[6]
                                fakeServiceTimeList.append(self.serviceTypeDict[(currentLocationType, currentServiceType, shift)])
                                currentServiceDuration = np.max(fakeServiceTimeList)
                                currentSizeCapacityUsage = np.max([currentDeliverySize, currentPickUpSize])
                                currentAmountCapacityUsage = np.max([currentDeliveryAmount, currentPickUpAmount])
                                currentUnitCapacity = currentUnitCapacity - currentSizeCapacityUsage#np.max([currentDeliverySize, currentPickUpSize])
                                currentMoneyCapacity = currentMoneyCapacity - np.max([currentDeliveryAmount, currentPickUpAmount])
                                fakeTempTime = fakeFakeTempTime + currentServiceDuration
                                fakeWorkingTime[vID] = fakeTempTime - self._clockToSeconds(routeDict[key][vID][0][1])
                                if j != 5:
                                    workingTimeCost = ((fakeWorkingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WD_ph'])
                                else:
                                    workingTimeCost = ((fakeWorkingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WE_ph'])
                                [flag1, routeFinishFlag, cmcDeltaT] = self._checkRoutingFlagUpdate(weekDay, fakeTempTime, fakeCurrentLocation, currentMoneyCapacity, currentUnitCapacity, vMaxTime)
                                print([flag1, routeFinishFlag])
                                if flag1 == 0:
                                    #print(routeDict[key][vID][routeNo])
                                    return [0, [], [], [], []]
                                else:
                                    if routeFinishFlag == 0:
                                        break
                                    else:
                                        currentLocation = fakeCurrentLocation
                                        tempTime = fakeTempTime
                                        kmDict[vID] = fakeKmDict[vID]
                                        kmFuelCost = kmDict[vID] * myVehiclesDict[vID]['Cost_Fuel_pkm']
                                        workingTime[vID] = fakeWorkingTime[vID]
                                        partialOrderDict[key][fakeCurrentLocation].remove(order)
                                        if jj == len(currentOrder) - 1:
                                            completeOrderList[vID].remove(currentLocation)
                                            activeOrderList.remove(currentLocation)
                                        routeDict[key][vID].append([currentLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), currentServiceType, self._secondsToClock(currentServiceDuration), currentDeliverySize, currentPickUpSize, currentDeliveryAmount, currentPickUpAmount, currentSizeCapacityUsage, currentAmountCapacityUsage, currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, orderID, distLabel])
                            #if flag1 == 0:
                            #    break
                            if tempTime > 12 * 3600 and lunchDict[vID][0] < 1 and routeFinishFlag == 1:
                                lunchDict[vID][0] = lunchDict[vID][0] + 1
                                if lunchDict[vID][0] == 1:
                                    arrival = tempTime
                                    tempTime = tempTime + myVehiclesDict[vID]['Rest_Time_m'] * 60
                                    workingTime[vID] = tempTime - self._clockToSeconds(routeDict[key][vID][0][1])
                                    if j != 5:
                                        workingTimeCost = ((fakeWorkingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WD_ph'])
                                    else:
                                        workingTimeCost = ((fakeWorkingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WE_ph'])
                                    routeDict[key][vID].append([currentLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), 'Rest', self._secondsToClock(myVehiclesDict[vID]['Rest_Time_m'] * 60), '---', '---', '---', '---', '---', '---', currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, '---', '---'])
                                    
                            
                            while routeFinishFlag == 1 and len(completeOrderList[vID]) > 0:
                                if len(queueOrderList) > 0:
                                    tempQueueOrderList = []
                                    for i in range(len(queueOrderList)):
                                        qLocID = queueOrderList[i]
                                        if tempTime >= self._clockToSeconds(self.generalDict[qLocID]['Start_Time']):
                                            activeOrderList.append(qLocID)
                                        else:
                                            tempQueueOrderList.append(qLocID)
                                    queueOrderList = copy.deepcopy(tempQueueOrderList)
                                if len(activeOrderList) > 0:
                                    [nextLocation, deltaT, distLabel] = self._closestLocationDuration(currentLocation, activeOrderList, weekDay, tempTime) 
                                    fakeTempTime = tempTime + deltaT
                                    fakeKmDict[vID] = kmDict[vID] + self._closestLocationDirect(currentLocation, [nextLocation], funcFlag=1)/1000
                                    arrival = fakeTempTime
                                    fakeCurrentLocation = nextLocation
                                    currentOrder = copy.deepcopy(partialOrderDict[key][fakeCurrentLocation])
                                    currentLocationType = self.generalDict[fakeCurrentLocation]['Type']
                                    fakeFakeTempTime = fakeTempTime
                                    fakeServiceTimeList = []
                                    for jj in range(len(currentOrder)):
                                        order = currentOrder[jj]
                                        orderID = order[10]
                                        currentServiceType = order[1]
                                        currentDeliverySize = order[3]
                                        currentPickUpSize = order[4]
                                        currentDeliveryAmount = order[5]
                                        currentPickUpAmount = order[6]
                                        fakeServiceTimeList.append(self.serviceTypeDict[(currentLocationType, currentServiceType, shift)])
                                        currentServiceDuration = np.max(fakeServiceTimeList)
                                        currentSizeCapacityUsage = np.max([currentDeliverySize, currentPickUpSize])
                                        currentAmountCapacityUsage = np.max([currentDeliveryAmount, currentPickUpAmount])
                                        currentUnitCapacity = currentUnitCapacity - currentSizeCapacityUsage#np.max([currentDeliverySize - currentPickUpSize])
                                        currentMoneyCapacity = currentMoneyCapacity - np.max([currentDeliveryAmount, currentPickUpAmount])
                                        fakeTempTime = fakeFakeTempTime + currentServiceDuration
                                        fakeWorkingTime[vID] = fakeTempTime - self._clockToSeconds(routeDict[key][vID][0][1])
                                        if j != 5:
                                            workingTimeCost = ((fakeWorkingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WD_ph'])
                                        else:
                                            workingTimeCost = ((fakeWorkingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WE_ph'])
                                        [flag1, routeFinishFlag, cmcDeltaT] = self._checkRoutingFlagUpdate(weekDay, fakeTempTime, fakeCurrentLocation, currentMoneyCapacity, currentUnitCapacity, vMaxTime)        
                                        print([flag1, routeFinishFlag])
                                        if flag1 == 0:
                                            #print(routeDict[key][vID])
                                            return [0, [], [], [], []]
                                        else:
                                            if routeFinishFlag == 0:
                                                break
                                            else:
                                                currentLocation = fakeCurrentLocation
                                                tempTime = fakeTempTime
                                                kmDict[vID] = fakeKmDict[vID]
                                                kmFuelCost = kmDict[vID] * myVehiclesDict[vID]['Cost_Fuel_pkm']
                                                workingTime[vID] = fakeWorkingTime[vID]
                                                partialOrderDict[key][currentLocation].remove(order)
                                                if jj == len(currentOrder) - 1:
                                                    completeOrderList[vID].remove(currentLocation)
                                                    activeOrderList.remove(currentLocation)
                                                routeDict[key][vID].append([currentLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), currentServiceType, self._secondsToClock(currentServiceDuration), currentDeliverySize, currentPickUpSize, currentDeliveryAmount, currentPickUpAmount, currentSizeCapacityUsage, currentAmountCapacityUsage, currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, orderID, distLabel])
                                    #if flag1 == 0:
                                    #    return [0, [], []]
                                    if tempTime > 12 * 3600 and lunchDict[vID][0] < 1:
                                        lunchDict[vID][0] = lunchDict[vID][0] + 1
                                        if lunchDict[vID][0] == 1:
                                            arrival = tempTime
                                            tempTime = tempTime + myVehiclesDict[vID]['Rest_Time_m'] * 60
                                            workingTime[vID] = tempTime - self._clockToSeconds(routeDict[key][vID][0][1])
                                            if j != 5:
                                                workingTimeCost = ((fakeWorkingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WD_ph'])
                                            else:
                                                workingTimeCost = ((fakeWorkingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WE_ph'])
                                            routeDict[key][vID].append([currentLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), 'Rest', self._secondsToClock(myVehiclesDict[vID]['Rest_Time_m'] * 60), '---', '---', '---', '---', '---', '---', currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, '---', '---'])
                                    
                                else:
                                    if len(queueOrderList) > 0:
                                        startTimeList = []
                                        for k in range(len(queueOrderList)):
                                            qLocID = queueOrderList[k]
                                            startTimeList.append(self._clockToSeconds(self.generalDict[qLocID]['Start_Time']))
                                        startTime = np.min(startTimeList)
                                        tempTime = startTime
                                        tempQueueOrderList = []
                                        for k in range(len(queueOrderList)):
                                            if startTimeList[k] == startTime:
                                                activeOrderList.append(queueOrderList[k])
                                            else:
                                                tempQueueOrderList.append(queueOrderList[k])
                                        queueOrderList = copy.deepcopy(tempQueueOrderList)
                            
                            #if flag1 == 0:
                            #    return [0, [], []]
                            nextLocation = list(self.cmcDict.keys())[0]#myVehiclesDict[vID]['CMC_ID']
                            [deltaT, distLabel] = self._closestLocationDuration(currentLocation, [nextLocation], weekDay, tempTime, funcFlag=1)
                            arrival = tempTime + deltaT
                            tempTime = tempTime + deltaT
                            kmDict[vID] = kmDict[vID] + self._closestLocationDirect(currentLocation, [nextLocation], funcFlag=1)/1000
                            kmFuelCost = kmDict[vID] * myVehiclesDict[vID]['Cost_Fuel_pkm']
                            workingTime[vID] = tempTime - self._clockToSeconds(routeDict[key][vID][0][1])
                            if j != 5:
                                workingTimeCost = ((workingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(workingTime[vID] <= 8 * 3600) +  int(workingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((workingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WD_ph'])
                            else:
                                workingTimeCost = ((workingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(workingTime[vID] <= 8 * 3600) +  int(workingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((workingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WE_ph'])   
                            #routeDict[key][routeNo][vID].append([nextLocation, tempTime, currentUnitCapacity, currentMoneyCapacity])
                            if routeFinishFlag == 0 and len(completeOrderList[vID]) > 0:
                                tempTime = tempTime + self.serviceTypeDict[('CMC', 'Reload Box', shift)]    
                                currentUnitCapacity = self.vehicleTypeDict[myVehiclesDict[vID]['Vehicle_Type_ID']]['Capacity_unit']
                                currentMoneyCapacity = self.vehicleTypeDict[myVehiclesDict[vID]['Vehicle_Type_ID']]['Insurance_Limit']
                                currentServiceType = 'Reload Box'
                                currentServiceDuration = self.serviceTypeDict[('CMC', currentServiceType, shift)]
                                routeDict[key][vID].append([nextLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), currentServiceType, self._secondsToClock(currentServiceDuration), '---', '---', '---', '---', '---', '---', currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, '---', distLabel])
                                nextRouteInfo[vID] = [completeOrderList[vID], tempTime]
                            elif len(completeOrderList[vID]) == 0:
                                tempTime = tempTime + 3600
                                currentUnitCapacity = self.vehicleTypeDict[myVehiclesDict[vID]['Vehicle_Type_ID']]['Capacity_unit']
                                currentMoneyCapacity = self.vehicleTypeDict[myVehiclesDict[vID]['Vehicle_Type_ID']]['Insurance_Limit']
                                currentServiceType = 'Stand By'
                                currentServiceDuration = self.serviceTypeDict[('CMC', 'Reload Box', shift)]
                                routeDict[key][vID].append([nextLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), currentServiceType, self._secondsToClock(3600), '---', '---', '---', '---', '---', '---', currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, '---', distLabel])
                                nextRouteInfo[vID] = [completeOrderList[vID], tempTime]
                            
                        else:
                            vehicleDoneFlag[vID] = 1
                    cmcArrivalTimeList = []
                    nextRouteInfoKeysList = list(nextRouteInfo.keys())
                    for k in range(len(nextRouteInfoKeysList)):
                        v_id = nextRouteInfoKeysList[k]
                        cmcArrivalTimeList.append(nextRouteInfo[v_id][1])
                    indices = np.argsort(cmcArrivalTimeList)
                    for index in indices:
                        v_id = nextRouteInfoKeysList[index]
                        if len(nextRouteInfo[v_id][0]) > 0:
                            [cmcStatusDict[key], nextRouteInfo[v_id][1]] = self._cmcStatusUpdate(cmcStatusDict[key], cmcStatusDictKeysList, nextRouteInfo[v_id][1], v_id)
        
            if j < len(partialOrderDictKeysList) - 1:
                nextKey = partialOrderDictKeysList[j + 1]
                for vid in completeAdhocList:
                    for (loc, adhocCount) in completeAdhocList[vid]:
                        for adhoc in partialAdhocDict[key][loc]:
                            if loc not in partialOrderDict[nextKey]:
                                partialOrderDict[nextKey][loc] = [adhoc]
                            else:
                                partialOrderDict[nextKey][loc].append(adhoc)
            
        return [1, routeDict, locationKeysDict, vehicleKeysDict, cmcStatusDict]
                            
                            
    def _MP_ST(self, initial_N, locationList, partialOrderDict, partialOrderDictKeysList, partialAdhocDict, cmcStatusDictOriginal, cmcStatusDictKeysList, shift):
        N = initial_N
        while 1:
            print(N)
            maxF = 0
            for locID in locationList:
                maxF = maxF + self.generalDict[locID]['Visit_Frequency_pw']
            maxF = maxF/N    
            cmcStatusDict = copy.deepcopy(cmcStatusDictOriginal)
            [myVehiclesDict, vehicleKeysDict, locationKeysDict] = self._assignLocations2vehicles(locationList, N, maxF)
            [successFlag, routeDict, locationKeysDict1, vehicleKeysDict1, cmcStatusDict1] = self._checkRouting(myVehiclesDict, vehicleKeysDict, locationKeysDict, cmcStatusDict, cmcStatusDictKeysList, partialOrderDict, partialOrderDictKeysList, partialAdhocDict, shift, maxWorkingTime=14)
            if successFlag == 1:
                ################################################################################
                timeViolatingVehicleList = []
                workingTimeDict = {}
                for key in routeDict:
                    for vid in routeDict[key]:
                        if vid not in workingTimeDict:
                            workingTimeDict[vid] = []
                        workingTimeDict[vid].append(self._clockToSeconds(routeDict[key][vid][len(routeDict[key][vid]) - 1][15]))
                        if self._clockToSeconds(routeDict[key][vid][len(routeDict[key][vid]) - 1][15]) >= 12*3600:
                            if vid not in timeViolatingVehicleList:
                                timeViolatingVehicleList.append(vid)
                if len(timeViolatingVehicleList) > 0:
                    averageList = []
                    for jj in range(len(list(workingTimeDict.keys()))):
                        vid = list(workingTimeDict.keys())[jj]
                        averageList.append(np.mean(workingTimeDict[vid]))
                    indexList = np.argsort(averageList)
                    sortedVehicles = []
                    for index in indexList:
                        sortedVehicles.append(list(workingTimeDict.keys())[index])
                    
                    tempMaxViloation = []
                    for jj in range(len(timeViolatingVehicleList)):
                        vid = timeViolatingVehicleList[jj]
                        tempMaxViloation.append(np.max(workingTimeDict[vid]))
                    sortedViolatedVehicles = []
                    indexList = np.argsort(tempMaxViloation)
                    for index in indexList:
                        sortedViolatedVehicles.append(timeViolatingVehicleList[index])
                    
                    while len(sortedViolatedVehicles) > 0:
                        violatedVehicleLocationList = copy.deepcopy(vehicleKeysDict[sortedViolatedVehicles[len(sortedViolatedVehicles) - 1]])
                        smallVehicleLocationList = copy.deepcopy(vehicleKeysDict[sortedVehicles[0]])
                        tempDistList = []
                        for jj in range(len(smallVehicleLocationList)):
                            loc = smallVehicleLocationList[jj]                           
                            #print(loc)
                            tempDistList.append(self._closestLocationDirect(loc, [list(self.cmcDict.keys())[0]], funcFlag = 1))
                        index = np.argmin(tempDistList)
                        smallReference = smallVehicleLocationList[index]
                        tempDistList = []
                        for jj in range(len(violatedVehicleLocationList)):
                            loc = violatedVehicleLocationList[jj]
                            tempDistList.append(self._closestLocationDirect(loc, [smallReference], funcFlag=1))
                        index = np.argmin(tempDistList)
                        bigReference = violatedVehicleLocationList[index]
                        print('Big Reference')
                        print(bigReference)
                        print(violatedVehicleLocationList)
                        smallVehicleLocationList.append(bigReference)
                        violatedVehicleLocationList.remove(bigReference)
                        for i in range(4):
                            #while()
                            bigReference = self._closestLocationDirect(bigReference, violatedVehicleLocationList)[0]
                            print('New Big Reference:')
                            print(bigReference)
                            smallVehicleLocationList.append(bigReference)
                            violatedVehicleLocationList.remove(bigReference)
                        vehicleKeysDict[sortedViolatedVehicles[len(sortedViolatedVehicles) - 1]] = copy.deepcopy(violatedVehicleLocationList)
                        vehicleKeysDict[sortedVehicles[0]] = copy.deepcopy(smallVehicleLocationList)
                        del(sortedViolatedVehicles[len(sortedViolatedVehicles) - 1])
                        del(sortedVehicles[0])
                    [successFlag, routeDict, locationKeysDict1, vehicleKeysDict1, cmcStatusDict] = self._checkRouting(myVehiclesDict, vehicleKeysDict, locationKeysDict, cmcStatusDict, cmcStatusDictKeysList, partialOrderDict, partialOrderDictKeysList, partialAdhocDict, shift)
                        
                    if successFlag == 1:    
                        return [N, locationKeysDict, vehicleKeysDict, routeDict, cmcStatusDict]
                    else:
                        N = N + 1
                else:
                    return [N, locationKeysDict, vehicleKeysDict, routeDict, cmcStatusDict]
            else:
                N = N + 1
                              
    
    def _assignLocationsHT(self, N, cmcStatusDictInput, cmcStatusDictKeysList, partialOrderDictOriginal, partialOrderDictKeysList, gDictOriginal):
        with open("output.txt", "a") as f:
            beginFlag = 1
            while 1:
                if beginFlag == 1:
                    kmDict = {}
                    fakeKmDict = {}
                    workingTime = {}
                    gDict = copy.deepcopy(gDictOriginal)
                    locCounter = 0
                    beginFlag = 0
                    cmcStatusDict = copy.deepcopy(cmcStatusDictInput)
                    tempVehicleID = list(self.vehiclesDict.keys())[0]
                    initialVehicleID = 1
                    myVehiclesDict = {}
                    
                    myVehiclesDict[initialVehicleID] = self.vehiclesDict[tempVehicleID]
                    routeDict = {}
                    routeDict[initialVehicleID] = []
                    lunchDict = {}
                    lunchDict[initialVehicleID] = 0
                    
                    
                    for i in range(2, N + 1):
                        myVehicleID = i
                        myVehiclesDict[myVehicleID] = self.vehiclesDict[list(self.vehiclesDict.keys())[0]]
                        lunchDict[myVehicleID] = 0
                    
                    orderKey = partialOrderDictKeysList[0]
                    date = orderKey[0]
                    weekDay = self._dateToWeekDay(date)
                    shift = orderKey[1]
                    
                    
                    partialOrderDict = copy.deepcopy(partialOrderDictOriginal)
                    #lateCount = 0
                    #rmvList = []
                    #for locid in partialOrderDict[orderKey]:
                    #    if self._clockToSeconds(self.generalDict[locid]['Start_Time']) >= 17.45*3600:
                    #        rmvList.append(locid)
                    #for locid in rmvList:
                    #    del(partialOrderDict[orderKey][locid])
                    
                            
                            #lateCount = lateCount + 1
                    #earlyRatio = 1 - lateCount/len(partialOrderDict[orderKey])
                    #earlyThreshold = int(earlyRatio * N)
                    #print('EarlyThreshold, LateCount, earlyRatio:')
                    #print([earlyThreshold, lateCount, earlyRatio])
                        
                    
                    N1 = N - 8
                    
                    
                    routeDict = {}
                    for vID in range(1, N + 1):
                        if vID <= N1:
                            arrival = 7 * 3600#self._clockToSeconds(myVehiclesDict[vID]['Start_Time']) - 3600*2
                        else:
                            arrival = 11*3600
                        [cmcStatusDict, startTime] = self._cmcStatusUpdate(cmcStatusDict, cmcStatusDictKeysList, arrival, vID)
                        arrival = startTime - (myVehiclesDict[vID]['Time_at_CMC_bl_m']) * 60 
                        currentLocation = list(self.cmcDict.keys())[0]
                        tempTime = startTime
                        currentServiceType = '---'
                        currentServiceDuration = '---'
                        currentUnitCapacity = self.vehicleTypeDict[myVehiclesDict[vID]['Vehicle_Type_ID']]['Capacity_unit']
                        currentMoneyCapacity = self.vehicleTypeDict[myVehiclesDict[vID]['Vehicle_Type_ID']]['Insurance_Limit']
                        [currentDeliverySize, currentPickUpSize, currentDeliveryAmount, currentPickUpAmount, currentSizeCapacityUsage, currentAmountCapacityUsage] = ['---', '---', '---', '---', '---', '---']
                        kmDict[vID] = 0
                        kmFuelCost = 0
                        workingTime[vID] = tempTime - arrival
                        if weekDay != 'Saturday':
                            workingTimeCost = ((workingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(workingTime[vID] <= 8 * 3600) +  int(workingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((workingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WD_ph'])
                        else:
                            workingTimeCost = ((workingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(workingTime[vID] <= 8 * 3600) +  int(workingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((workingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WE_ph'])
                        orderID = '---'
                        distLabel = '---'
                        routeDict[vID] = [[currentLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), currentServiceType, currentServiceDuration, currentDeliverySize, currentPickUpSize, currentDeliveryAmount, currentPickUpAmount, currentSizeCapacityUsage, currentAmountCapacityUsage, currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, orderID, distLabel]]
                        #[currentLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), currentServiceType, currentServiceDuration, currentDeliverySize, currentPickUpSize, currentDeliveryAmount, currentPickUpAmount, currentSizeCapacityUsage, currentAmountCapacityUsage, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, '---', '---']
                    startEmergencyInterval = (8 * 3600, 8 * 3600 + 3600*2)
                    emergencyInterval = copy.deepcopy(startEmergencyInterval)
                
                print('##### Number of Vehicles #####', file=f)
                print(N, file=f)
                print('&&&&& Emergency Interval #####', file=f)
                print(emergencyInterval, file=f)
                listEmergency = []
                for locID in partialOrderDict[orderKey]:
                    timeWindowMidPoint = (np.max([self._clockToSeconds(gDict[locID]['Start_Time']), emergencyInterval[0]]) + self._clockToSeconds(gDict[locID]['End_Time'])) / 2
                    if emergencyInterval[0] == 12 * 3600 or emergencyInterval[0] == 18 * 3600:
                        if emergencyInterval[0] < timeWindowMidPoint < emergencyInterval[1]:
                            listEmergency.append(locID)
                    else:
                        if emergencyInterval[0] <= timeWindowMidPoint <= emergencyInterval[1]:
                            listEmergency.append(locID)
                altInterval = (emergencyInterval[0], emergencyInterval[0] + 3600 * 12)
                listAlternative = []
                for locID in partialOrderDict[orderKey]:
                    timeWindowMidPoint = (np.max([self._clockToSeconds(gDict[locID]['Start_Time']), emergencyInterval[0]]) + self._clockToSeconds(gDict[locID]['End_Time'])) / 2
                    if altInterval[0] <= timeWindowMidPoint <= altInterval[1] and (self._clockToSeconds(gDict[locID]['Start_Time']) <= emergencyInterval[0]) and (self._clockToSeconds(gDict[locID]['End_Time']) >= emergencyInterval[1]):
                        listAlternative.append(locID)
                
                listAvailable = []
                for locID in listAlternative:
                    if (locID not in listEmergency):
                        listAvailable.append(locID)
                print('!@#$%^&*&^%$#@!@#$%^&*&^%$#@! Length of listEmergency and listAvailabe !@#$%^&*&^%$#@!@#$%^&*&^%$#@!', file=f)
                print([len(listEmergency), len(listAvailable), len(listAlternative)], file=f)
                emptyFlag = 0
                    
                activeVehicleList = list(range(1, N + 1))
                activeVehicleRemoveList = []
                
                
                while emptyFlag == 0:
                    print('\nentered next location\n', file=f)
                    cmcUpdateList = []
                    print('N and lenght of activeVehicleList:', file=f)
                    print([N, len(activeVehicleList)], file=f)
                    for vID in activeVehicleList:
                        currentLocation = routeDict[vID][len(routeDict[vID]) - 1][0]
                        #print(routeDict[vID][len(routeDict[vID]) - 1][2])
                        currentTime = self._clockToSeconds(routeDict[vID][len(routeDict[vID]) - 1][2])
                        currentUnitCapacity = routeDict[vID][len(routeDict[vID]) - 1][11]
                        currentMoneyCapacity = routeDict[vID][len(routeDict[vID]) - 1][12]
                        print([vID, currentLocation, len(listEmergency), len(listAvailable), currentTime, emergencyInterval[1], currentUnitCapacity, currentMoneyCapacity], file=f)
                        if len(listEmergency) > 0:
                            if currentLocation != list(self.cmcDict.keys())[0]:
                                [nextLocation, deltaT, distLabel] = self._closestLocationDuration(currentLocation, listEmergency, weekDay, currentTime) 
                            else:
                                #print('wow')
                                [nextLocation, deltaT, distLabel] = self._furthestLocationDuration(currentLocation, listEmergency, weekDay, currentTime)
                                #print(deltaT)
                        elif len(listAvailable) > 0:
                            if currentLocation != list(self.cmcDict.keys())[0]:
                                [nextLocation, deltaT, distLabel] = self._closestLocationDuration(currentLocation, listAvailable, weekDay, currentTime)
                            else:
                                #print('wow')
                                [nextLocation, deltaT, distLabel] = self._furthestLocationDuration(currentLocation, listAvailable, weekDay, currentTime)
                                #print(deltaT)
                        else:
                            emergencyInterval = (emergencyInterval[0] + 3600*2, emergencyInterval[1] + 3600*2)
                            emptyFlag = 1
                            break
                            #######################################
                        arrival = np.max([currentTime + deltaT, self._clockToSeconds(gDict[nextLocation]['Start_Time'])])
                        fakeKmDict[vID] = kmDict[vID] + self._closestLocationDirect(currentLocation, [nextLocation], funcFlag=1)/1000
                        nextLocationType = gDict[nextLocation]['Type']
                        fakeUnitCapacity = currentUnitCapacity
                        fakeMoneyCapacity = currentMoneyCapacity
                        fakeTime = arrival
                        #fakeServiceTimeList = []
                        ####################################################################################
                        ####################################################################################
                        #for order in partialOrderDict[orderKey][nextLocation]:
                        order = partialOrderDict[orderKey][nextLocation][0]
                        orderID = order[10]
                        deliverySize = order[3]
                        deliveryAmount = order[5]
                        pickUpSize = order[4]
                        pickUpAmount = order[6]
                        nextSizeCapacityUsage = np.max([deliverySize, pickUpSize])
                        nextAmountCapacityUsage = np.max([deliveryAmount, pickUpAmount])
                        #print([fakeUnitCapacity, order], file = f)
                        fakeUnitCapacity = fakeUnitCapacity - np.max([deliverySize, pickUpSize])
                        fakeMoneyCapacity = fakeMoneyCapacity - np.max([deliveryAmount, pickUpAmount])
                        nextServiceType = order[1]
                        #fakeServiceTimeList.append(self.serviceTypeDict[(nextLocationType, nextServiceType, shift)])
                        nextServiceTime = self.serviceTypeDict[(nextLocationType, nextServiceType, shift)] #np.max(fakeServiceTimeList)
                        fakeTime = fakeTime + nextServiceTime
                            
                        if fakeTime > emergencyInterval[1] or fakeTime - self._clockToSeconds(routeDict[vID][0][1]) > 11*3600:
                            activeVehicleRemoveList.append(vID)
                            print('## Violated Emergency InterVal ##', file = f)
                            print([vID, nextLocation, len(listEmergency), len(listAvailable), fakeTime, emergencyInterval[1], fakeUnitCapacity, fakeMoneyCapacity], file=f)
                        
                        else:
                            if fakeUnitCapacity < 0 or fakeMoneyCapacity < 0:
                                print('## Violated Capacity ##', file = f)
                                print([vID, nextLocation, len(listEmergency), len(listAvailable), fakeTime, emergencyInterval[1], fakeUnitCapacity, fakeMoneyCapacity, deliverySize, deliveryAmount, pickUpSize, pickUpAmount], file=f)
                                nextLocation = list(self.cmcDict.keys())[0]
                                [deltaT, distLabel] = self._closestLocationDuration(currentLocation, [list(self.cmcDict.keys())[0]], weekDay, currentTime, funcFlag = 1)
                                arrival = currentTime + deltaT
                                kmDict[vID] = kmDict[vID] + self._closestLocationDirect(currentLocation, [list(self.cmcDict.keys())[0]], funcFlag = 1)/1000
                                cmcUpdateList.append([arrival, vID, distLabel, 'Reload Money', self.serviceTypeDict[('CMC', 'Reload Money', 'Day')], kmDict[vID], kmDict[vID]*myVehiclesDict[vID]['Cost_Fuel_pkm']])
                                activeVehicleRemoveList.append(vID)
                            else:
                                print('## Confirmed ##', file = f)
                                workingTime[vID] = fakeTime - self._clockToSeconds(routeDict[vID][0][1])
                                if weekDay != 'Saturday':
                                    workingTimeCost = ((workingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(workingTime[vID] <= 8 * 3600) +  int(workingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((workingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WD_ph'])
                                else:
                                    workingTimeCost = ((workingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(workingTime[vID] <= 8 * 3600) +  int(workingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((workingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WE_ph'])
                                kmDict[vID] = fakeKmDict[vID]
                                kmFuelCost = kmDict[vID] * myVehiclesDict[vID]['Cost_Fuel_pkm']
                                tempTime = fakeTime
                                currentUnitCapacity = fakeUnitCapacity
                                currentMoneyCapacity = fakeMoneyCapacity
                                routeDict[vID].append([nextLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), nextServiceType, nextServiceTime, deliverySize, pickUpSize, deliveryAmount, pickUpAmount, nextSizeCapacityUsage, nextAmountCapacityUsage, currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, orderID, distLabel])
                                del(partialOrderDict[orderKey][nextLocation][0])
                                if len(partialOrderDict[orderKey][nextLocation]) == 0:
                                    if nextLocation in listEmergency:
                                        listEmergency.remove(nextLocation)
                                    if nextLocation in listAvailable:
                                        listAvailable.remove(nextLocation)
                                    del(partialOrderDict[orderKey][nextLocation])
                                print([vID, nextLocation, len(listEmergency), len(listAvailable), fakeTime, emergencyInterval[1], fakeUnitCapacity, fakeMoneyCapacity, len(partialOrderDict[orderKey])], file=f)
                                if gDict[nextLocation]['Hard_Window'] == 1:
                                    gDict[nextLocation]['Start_Time'] = self._secondsToClock(emergencyInterval[0])
                                    gDict[nextLocation]['End_Time'] = self._secondsToClock(emergencyInterval[1])

                                if vID <= N1:
                                    restCondition = (fakeTime > 12*3600)
                                else:
                                    restCondition = (fakeTime > 17*3600)
                                if restCondition:
                                    lunchDict[vID] = lunchDict[vID] + 1
                                if lunchDict[vID] == 1:
                                    workingTime[vID] = self._clockToSeconds(routeDict[vID][len(routeDict[vID]) - 1][2]) + myVehiclesDict[vID]['Rest_Time_m'] * 60 - self._clockToSeconds(routeDict[vID][0][1])
                                    if weekDay != 'Saturday':
                                        workingTimeCost = ((workingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(workingTime[vID] <= 8 * 3600) +  int(workingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((workingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WD_ph'])
                                    else:
                                        workingTimeCost = ((workingTime[vID]/3600) * myVehiclesDict[vID]['Cost_RunningTime']) * int(workingTime[vID] <= 8 * 3600) +  int(workingTime[vID] > 8 * 3600) * ((8 * myVehiclesDict[vID]['Cost_RunningTime']) + ((workingTime[vID]/3600) - 8) * myVehiclesDict[vID]['Cost_Overtime_WE_ph'])
                                    routeDict[vID].append([nextLocation, routeDict[vID][len(routeDict[vID]) - 1][2], self._secondsToClock(self._clockToSeconds(routeDict[vID][len(routeDict[vID]) - 1][2]) + myVehiclesDict[vID]['Rest_Time_m'] * 60), 'Rest', self._secondsToClock(myVehiclesDict[vID]['Rest_Time_m'] * 60), '---', '---', '---', '---', '---', '---', routeDict[vID][len(routeDict[vID]) - 1][11], routeDict[vID][len(routeDict[vID]) - 1][12], routeDict[vID][len(routeDict[vID]) - 1][13], routeDict[vID][len(routeDict[vID]) - 1][14], self._secondsToClock(workingTime[vID]), workingTimeCost, '---', '---'])
                                    print('\n^^^^^ Lunch Time ^^^^^\n', file = f)
                                locCounter = locCounter + 1
                                if locCounter == 309:
                                    print('vaaaveyyylaaa')
                                
                    if len(cmcUpdateList) > 0:
                        tempList = []
                        for i in range(len(cmcUpdateList)):
                            tempList.append(cmcUpdateList[i][0])
                        indexList = np.argsort(tempList)
                        for i in range(len(indexList)):
                            index = indexList[i]
                            [cmcStatusDict, nextStartTime] = self._cmcStatusUpdate(cmcStatusDict, cmcStatusDictKeysList, cmcUpdateList[index][0] + cmcUpdateList[index][4], cmcUpdateList[index][1])
                            workingTime[cmcUpdateList[index][1]] = nextStartTime - self._clockToSeconds(routeDict[cmcUpdateList[index][1]][0][1])
                            if weekDay != 'Saturday':
                                workingTimeCost = ((workingTime[cmcUpdateList[index][1]]/3600) * myVehiclesDict[cmcUpdateList[index][1]]['Cost_RunningTime']) * int(workingTime[cmcUpdateList[index][1]] <= 8 * 3600) +  int(workingTime[cmcUpdateList[index][1]] > 8 * 3600) * ((8 * myVehiclesDict[cmcUpdateList[index][1]]['Cost_RunningTime']) + ((workingTime[cmcUpdateList[index][1]]/3600) - 8) * myVehiclesDict[cmcUpdateList[index][1]]['Cost_Overtime_WD_ph'])
                            else:
                                workingTimeCost = ((workingTime[cmcUpdateList[index][1]]/3600) * myVehiclesDict[cmcUpdateList[index][1]]['Cost_RunningTime']) * int(workingTime[cmcUpdateList[index][1]] <= 8 * 3600) +  int(workingTime[cmcUpdateList[index][1]] > 8 * 3600) * ((8 * myVehiclesDict[cmcUpdateList[index][1]]['Cost_RunningTime']) + ((workingTime[cmcUpdateList[index][1]]/3600) - 8) * myVehiclesDict[cmcUpdateList[index][1]]['Cost_Overtime_WE_ph'])
                            routeDict[cmcUpdateList[index][1]].append([list(self.cmcDict.keys())[0], self._secondsToClock(cmcUpdateList[index][0]), self._secondsToClock(nextStartTime),  'Reload Money', cmcUpdateList[index][4], '---', '---', '---', '---', '---', '---',  routeDict[cmcUpdateList[index][1]][0][11], routeDict[cmcUpdateList[index][1]][0][12], cmcUpdateList[index][5], cmcUpdateList[index][6], self._secondsToClock(workingTime[cmcUpdateList[index][1]]), workingTimeCost, '---', distLabel])
                    for vid in activeVehicleRemoveList:
                        activeVehicleList.remove(vid)
                    activeVehicleRemoveList = []
                    if len(activeVehicleList) == 0:
                        if len(listEmergency) == 0:
                            emergencyInterval = (emergencyInterval[0] + 3600*2, emergencyInterval[1] + 3600*2)
                            break
                        else:
                            N = N + 1
                            beginFlag = 1
                            break
                         
                if emergencyInterval[1] > self._clockToSeconds(myVehiclesDict[1]['Max_Time']) + 3*3600:
                    N = N + 1
                    beginFlag = 1 
                    
                elif len(partialOrderDict[orderKey]) == 0:
                    for vvid in routeDict:
                        if len(routeDict[vvid]) > 0:
                            currentLocation = routeDict[vvid][len(routeDict[vvid]) - 1][0]
                            tt = self._clockToSeconds(routeDict[vvid][len(routeDict[vvid]) - 1][2])
                            [deltaT, distLabel] = self._closestLocationDuration(currentLocation, [list(self.cmcDict.keys())[0]], weekDay, tt, funcFlag = 1)
                            nextLocation = list(self.cmcDict.keys())[0]
                            arrival = tt + deltaT
                            workingTime[vvid] = arrival - self._clockToSeconds(routeDict[vvid][0][1])
                            if weekDay != 'Saturday':
                                workingTimeCost = ((workingTime[vvid]/3600) * myVehiclesDict[vvid]['Cost_RunningTime']) * int(workingTime[vvid] <= 8 * 3600) +  int(workingTime[vvid] > 8 * 3600) * ((8 * myVehiclesDict[vvid]['Cost_RunningTime']) + ((workingTime[vvid]/3600) - 8) * myVehiclesDict[vvid]['Cost_Overtime_WD_ph'])
                            else:
                                workingTimeCost = ((workingTime[vvid]/3600) * myVehiclesDict[vvid]['Cost_RunningTime']) * int(workingTime[vvid] <= 8 * 3600) +  int(workingTime[vvid] > 8 * 3600) * ((8 * myVehiclesDict[vvid]['Cost_RunningTime']) + ((workingTime[vvid]/3600) - 8) * myVehiclesDict[vvid]['Cost_Overtime_WE_ph'])
                            kmDict[vvid] = kmDict[vvid] + self._closestLocationDirect(currentLocation, [list(self.cmcDict.keys())[0]], funcFlag = 1)/1000
                            kmFuelCost = kmDict[vvid] * myVehiclesDict[vvid]['Cost_Fuel_pkm']
                            routeDict[vvid].append([nextLocation, self._secondsToClock(arrival), '---', '---', '---', '---', '---', '---', '---', '---', '---', '---', '---', kmDict[vvid], kmFuelCost, self._secondsToClock(workingTime[vvid]), workingTimeCost, '---', distLabel])
                            for iii in range(len(routeDict[vvid])):
                                item = routeDict[vvid][iii]
                                if type(item[4]) == float:
                                    routeDict[vvid][iii][4] = self._secondsToClock(routeDict[vvid][iii][4])
                            
                    return [N, cmcStatusDict, routeDict, gDict]    
    
    
    def _hardRouting(self, cmcStatusDictOriginal, cmcStatusDictKeysList, orderHardDict, initial_N_hd):
        hardResultDict = {}
        gDict = copy.deepcopy(self.generalDict)
        sortedOrderKeyList = []
        tempSortedOrderKeyList = []
        tempList = []
        
        for i in range(len(list(orderHardDict.keys()))):
            orderKey = list(orderHardDict.keys())[i]
            tempList.append(len(orderHardDict[orderKey]))
        indexList = np.argsort(tempList)
        for index in indexList:
            tempSortedOrderKeyList.append(list(orderHardDict.keys())[index])
        for i in range(len(tempSortedOrderKeyList) - 1, -1, -1):
            sortedOrderKeyList.append(tempSortedOrderKeyList[i])
        
        tempN_hd_List = [initial_N_hd]
        for orderKey in sortedOrderKeyList:
            cmcStatusDict = copy.deepcopy(cmcStatusDictOriginal[orderKey])
            print('\n$$$$$ Date: %s &&&&&\n' %(orderKey[0]))
            tempHardList = self._assignLocationsHT(np.max(tempN_hd_List), cmcStatusDict, cmcStatusDictKeysList, orderHardDict, [orderKey], gDict)
            tempN_hd_List.append(tempHardList[0])
            gDict = tempHardList[3]
            hardResultDict[orderKey] = tempHardList
        for key in hardResultDict:
            hardResultDict[key] = hardResultDict[key][0:3]
        return [hardResultDict, gDict]
                                
    
    def _integratedRouting(self, generalServicePointDict, cmcStatusDictGeneral_orig, cmcStatusDictKeysList, initial_N_sd = 31, initial_N_hd = 21):
        cmcStatusDict = copy.deepcopy(cmcStatusDictGeneral_orig)
        [locList_SD, locList_SN, locList_HD] = [[], [], []]
        [N_hd, hardRouteDict] = [{}, {}]
        for locID in generalServicePointDict:
            if generalServicePointDict[locID]['Model'] == 'E-Machine' and generalServicePointDict[locID]['Shift'] == 'Day':
                locList_SD.append(locID)
            elif generalServicePointDict[locID]['Model'] == 'E-Machine' and generalServicePointDict[locID]['Shift'] == 'Night':
                locList_SN.append(locID)
            elif generalServicePointDict[locID]['Model'] != 'E-Machine' and generalServicePointDict[locID]['Shift'] == 'Day':
                locList_HD.append(locID)
        
        [orderDict_SD, orderDict_SN, orderDict_HD] = [{}, {}, {}]
        for orderKey in self.ordersDict:
            for locID in self.ordersDict[orderKey]:
                if generalServicePointDict[locID]['Model'] == 'E-Machine' and generalServicePointDict[locID]['Shift'] == 'Day':
                    if orderKey not in orderDict_SD:
                        orderDict_SD[orderKey] = {}
                    orderDict_SD[orderKey][locID] = self.ordersDict[orderKey][locID]
                elif generalServicePointDict[locID]['Model'] == 'E-Machine' and generalServicePointDict[locID]['Shift'] == 'Night':
                    if orderKey not in orderDict_SN:
                        orderDict_SN[orderKey] = {}
                    orderDict_SN[orderKey][locID] = self.ordersDict[orderKey][locID]
                elif generalServicePointDict[locID]['Model'] != 'E-Machine' and generalServicePointDict[locID]['Shift'] == 'Day':
                    if orderKey not in orderDict_HD:
                        orderDict_HD[orderKey] = {}
                    orderDict_HD[orderKey][locID] = self.ordersDict[orderKey][locID]
        
        [adhocDict_SD, adhocDict_SN] = [{}, {}]
        for orderKey in self.adhocDict:
            for locID in self.adhocDict[orderKey]:
                if generalServicePointDict[locID]['Model'] == 'E-Machine' and generalServicePointDict[locID]['Shift'] == 'Day':
                    if orderKey not in adhocDict_SD:
                        adhocDict_SD[orderKey] = {}
                    adhocDict_SD[orderKey][locID] = self.adhocDict[orderKey][locID]
                elif generalServicePointDict[locID]['Model'] == 'E-Machine' and generalServicePointDict[locID]['Shift'] == 'Night':
                    if orderKey not in adhocDict_SN:
                        adhocDict_SN[orderKey] = {}
                    adhocDict_SN[orderKey][locID] = self.adhocDict[orderKey][locID]
                
        
        [hardResultDict, gDict] = self._hardRouting(cmcStatusDict, cmcStatusDictKeysList, orderDict_HD, initial_N_hd)
        for key in hardResultDict:
            [N_hd[key], cmcStatusDict[key], hardRouteDict[key]]  = copy.deepcopy(hardResultDict[key])
        
        tempN_hd = []
        for key in N_hd:
            tempN_hd.append(N_hd[key])
        self.offsetN_sd = np.max(tempN_hd)
        
        [N_sd, locationKeysDict, vehicleKeysDict, softRouteDict, cmcStatusDict] = self._MP_ST(initial_N_sd, locList_SD, orderDict_SD, list(orderDict_SD.keys()), adhocDict_SD, cmcStatusDict, cmcStatusDictKeysList, 'Day')
            
        return [N_hd, hardRouteDict, N_sd, locationKeysDict, vehicleKeysDict, softRouteDict, gDict]
        
        
    def _Main_MP_step1(self, generalServicePointDict, locationKeysDict, vehicleKeysDict, locationKeysDictNight, vehicleKeysDictNight, N_soft_day, N_hard_day, N_soft_night, N_hard_night = 1):
        [locList_SD, maxF_SD] = [[], 0]
        [locList_SN, maxF_SN] = [[], 0]
        [locList_HD, maxF_HD] = [[], 0]
        [locList_HN, maxF_HN] = [[], 0]
        for locID in generalServicePointDict:
            if generalServicePointDict[locID]['Model'] == 'E-Machine' and generalServicePointDict[locID]['Shift'] == 'Day':
                locList_SD.append(locID)
                maxF_SD = maxF_SD + self.generalDict[locID]['Visit_Frequency_pw']
            elif generalServicePointDict[locID]['Model'] == 'E-Machine' and generalServicePointDict[locID]['Shift'] == 'Night':
                locList_SN.append(locID)
                maxF_SN = maxF_SN + self.generalDict[locID]['Visit_Frequency_pw']
            elif generalServicePointDict[locID]['Model'] != 'E-Machine' and generalServicePointDict[locID]['Shift'] == 'Day':
                locList_HD.append(locID)
                maxF_HD = maxF_HD + self.generalDict[locID]['Visit_Frequency_pw']
            elif generalServicePointDict[locID]['Model'] != 'E-Machine' and generalServicePointDict[locID]['Shift'] == 'Night':
                locList_HN.append(locID)
                maxF_HN = maxF_HN + self.generalDict[locID]['Visit_Frequency_pw']
        print('Sum of frequencies:')
        print([maxF_SD, maxF_SN, maxF_HD, maxF_HN])
        #N_soft_night = int(np.ceil(N_soft_day * (maxF_SN/maxF_SD)))
        N_hard_night = int(np.ceil(N_hard_day * (maxF_HN/maxF_HD)))
        print('Number of vehicles:')
        print([N_soft_day, N_soft_night, N_hard_day, N_hard_night])
        maxF_SD = maxF_SD/N_soft_day
        maxF_SN = maxF_SN/N_soft_night
        maxF_HD = maxF_HD/N_hard_day
        if N_hard_night > 0:
            maxF_HN = maxF_HN/N_hard_night
        print('1. Soft-Window & Day...')
        [sd_VehiclesDict, sd_VehicleKeysDict, sd_LocationKeysDict] = [{}, copy.deepcopy(vehicleKeysDict), copy.deepcopy(locationKeysDict)]#self._assignLocations2vehicles(locList_SD, N_soft_day, maxF_SD)
        print('2. Soft-Window & Night...')
        [sn_VehiclesDict, sn_VehicleKeysDict, sn_LocationKeysDict] = [{}, copy.deepcopy(vehicleKeysDictNight), copy.deepcopy(locationKeysDictNight)]#self._assignLocations2vehicles(locList_SN, N_soft_night, maxF_SN)
        print('3. Hard-Window & Day...')
        [hd_VehiclesDict, hd_VehicleKeysDict, hd_LocationKeysDict] = self._assignLocations2vehicles(locList_HD, N_hard_day, maxF_HD, funcFlagg= 1)
        print('4. Hard-Window & Night...')
        [hn_VehiclesDict, hn_VehicleKeysDict, hn_LocationKeysDict] = self._assignLocations2vehicles(locList_HN, N_hard_night, maxF_HN)
        return [[sd_VehiclesDict, sd_VehicleKeysDict, sd_LocationKeysDict], 
                [sn_VehiclesDict, sn_VehicleKeysDict, sn_LocationKeysDict],
                [hd_VehiclesDict, hd_VehicleKeysDict, hd_LocationKeysDict],
                [hn_VehiclesDict, hn_VehicleKeysDict, hn_LocationKeysDict]]
        
        
    def _Main_MP_step2(self, N, vehicleKeysDict, frequencyOffset = 15, numOfDays = 6):
        #weekDayList = ['Monday', 'Thursday', 'Tuesday', 'Friday', 'Wednesday', 'Saturday']
        #weekDayList = ['Thursday', Friday, Saturday, Monday, Tuesday, Wednesday]
        masterDict = {}
        locDict = {}
        bDict = {}
        for vID in range(1, N + 1):
            switchDays = [vID % 6, vID % 6 + 1, vID % 6 + 2, vID % 6 + 3, vID % 6 + 4, vID % 6 + 5]
            for jj in range(len(switchDays)):
                if switchDays[jj] >= 6:
                    switchDays[jj] = switchDays[jj] % 6
            bDict[vID] = {}
            locDict[vID] = {}
            masterDict[vID] = {}
            maxF = 0
            for locID in vehicleKeysDict[vID]:
                sumVisitable = 0
                for j in range(numOfDays):
                    sumVisitable = sumVisitable + self.generalDict[locID]['Weekly_Visitability'][j]
                locDict[vID][locID] = [self.generalDict[locID]['Visit_Frequency_pw'], sumVisitable]
                maxF = maxF + self.generalDict[locID]['Visit_Frequency_pw']
            maxF = maxF/numOfDays
            for dayIndex in range(numOfDays):
                masterDict[vID][dayIndex] = []
                bDict[vID][dayIndex] = []
                for loc_id in locDict[vID]:
                    freq = locDict[vID][loc_id][0]
                    if freq > 0 and self.generalDict[loc_id]['Weekly_Visitability'][dayIndex] == 1:
                        bDict[vID][dayIndex].append(loc_id)
                if len(bDict[vID][dayIndex]) > 0:
                    removeList = []
                    for loc_id in bDict[vID][dayIndex]:
                        if locDict[vID][loc_id][0] == locDict[vID][loc_id][1]:
                            removeList.append(loc_id)
                            masterDict[vID][dayIndex].append(loc_id)
                            locDict[vID][loc_id][0] = locDict[vID][loc_id][0] - 1
                    for loc_id in removeList:
                        bDict[vID][dayIndex].remove(loc_id)
                            
            for dayIndex in switchDays:
                removeList = []
                for loc_id in bDict[vID][dayIndex]:
                    freq = locDict[vID][loc_id][0]
                    if freq <= 0:
                        removeList.append(loc_id)
                for loc_id in removeList:
                    bDict[vID][dayIndex].remove(loc_id)
                while (len(masterDict[vID][dayIndex]) <= maxF + frequencyOffset) and (len(bDict[vID][dayIndex]) > 0):
                    loc = bDict[vID][dayIndex][len(bDict[vID][dayIndex]) - 1]
                    masterDict[vID][dayIndex].append(loc)
                    bDict[vID][dayIndex].remove(loc)
                    locDict[vID][loc][0] = locDict[vID][loc][0] - 1
        return masterDict
                
                    
    def _MP2CSV(self, sd_MasterDict, sn_MasterDict, hd_MasterDict, gDict, outputFileName1 = 'MasterPlan_Day.csv', outputFileName2 = 'MasterPlan_Night.csv', outputFileName3 = 'MasterPlan_VehicleCount.csv'):
        rows = [['Location ID', 'Vehicle ID', 'Week Day Index', 'Visiting Hour']]
        N_sd = 0
        for vID in sd_MasterDict:
            N_sd = N_sd + 1
            for dayIndex in np.sort(list(sd_MasterDict[vID].keys())):
                for locID in sd_MasterDict[vID][dayIndex]:
                    rows.append([locID, list(self.vehiclesDict.keys())[vID - 1 + self.offsetN_sd], dayIndex, '---'])
        
        N_hd = 0
        for vID in hd_MasterDict:
            N_hd = N_hd + 1
            for dayIndex in np.sort(list(hd_MasterDict[vID].keys())):
                for locID in hd_MasterDict[vID][dayIndex]:
                    if self.generalDict[locID]['Hard_Window'] == 1:
                        rows.append([locID, list(self.vehiclesDict.keys())[vID - 1], dayIndex, [gDict[locID]['Start_Time'], gDict[locID]['End_Time']]])
                    else:
                        rows.append([locID, list(self.vehiclesDict.keys())[vID - 1], dayIndex, '---'])
        with open(outputFileName1, 'w', newline = '') as outputCSV:
            outputWriter = csv.writer(outputCSV, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            outputWriter.writerows(rows)
        
        rows = [['Location ID', 'Vehicle ID', 'Week Day Index', 'Visiting Hour']]
        N_sn = 0
        for vID in sn_MasterDict:
            N_sn = N_sn + 1
            for dayIndex in np.sort(list(sn_MasterDict[vID].keys())):
                for locID in sn_MasterDict[vID][dayIndex]:
                    rows.append([locID, list(self.vehiclesDict.keys())[vID - 1 + self.offsetN_sd], dayIndex, '---'])
        with open(outputFileName2, 'w', newline = '') as outputCSV:
            outputWriter = csv.writer(outputCSV, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            outputWriter.writerows(rows)
        
        rows = [['Hard Time Window', 'Soft Time Window - Day', 'Soft Time Window - Night']]
        rows.append([N_hd, N_sd, N_sn])
        with open(outputFileName3, 'w', newline = '') as outputCSV:
            outputWriter = csv.writer(outputCSV, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            outputWriter.writerows(rows)
        
    def _dailyPlan2CSV(self, softRouteDict, hardRouteDict, csvFileName = 'DailyPlan_Day.csv'):
        rows = [['Date', 'Shift', 'VehicleID', 'CurrentLocation', 'Arrival', 'Departure', 'ServiceType', 'ServiceDuration', 'DeliverySize', 'PickUpSize', 'DeliveryAmount', 'PickUpAmount', 'SizeCapacityUsage', 'AmountCapacityUsage', 'SizeCapacity', 'AmountCapacity', 'Kilometre', 'FuelCost', 'WorkingTime', 'WorkingTimeCost', 'OrderID', 'DistLabel']]
        for key in softRouteDict:
            for vid in softRouteDict[key]:
                for item in softRouteDict[key][vid]:
                    if type(vid) == int:
                        temp = [key[0], key[1], list(self.vehiclesDict.keys())[vid - 1 + self.offsetN_sd]]
                    else:
                        temp = [key[0], key[1], vid]
                    strDate = temp[0]
                    for jj in range(len(item)):
                        #print(jj, item[jj], item)
                        if (jj == 1 or jj == 2) and ('-' not in item[jj]):        
                            if self._clockToSeconds(item[jj]) >= 24*3600:
                                strModifiedTime = self._secondsToClock(self._clockToSeconds(item[jj]) - 24*3600)
                                date = datetime.strptime(strDate, "%Y-%m-%d")
                                modifiedDate = date + timedelta(days=1)
                                strModifiedDate = datetime.strftime(modifiedDate, "%Y-%m-%d")
                                
                            else:
                                strModifiedTime = item[jj]
                                strModifiedDate = strDate
                            item[jj] = strModifiedDate + ' ' + strModifiedTime
                        element = item[jj]
                        temp.append(element)
                    rows.append(temp)
        
        tempList = []
        for jj in range(len(list(hardRouteDict.keys()))):
            key = list(hardRouteDict.keys())[jj]
            date = key[0]
            tempList.append(int(date[9:11]))
        indexList = np.argsort(tempList)
        sortedKeys = []
        for index in indexList:
            sortedKeys.append(list(hardRouteDict.keys())[index])
        
        for key in sortedKeys:
            for vid in hardRouteDict[key]:
                for item in hardRouteDict[key][vid]:
                    temp = [key[0], key[1], list(self.vehiclesDict.keys())[vid - 1]]
                    strDate = temp[0]
                    for jj in range(len(item)):
                        #print(jj, item[jj], item)
                        if (jj == 1 or jj == 2) and ('-' not in item[jj]):        
                            if self._clockToSeconds(item[jj]) >= 24*3600:
                                strModifiedTime = self._secondsToClock(self._clockToSeconds(item[jj]) - 24*3600)
                                date = datetime.strptime(strDate, "%Y-%m-%d")
                                modifiedDate = date + timedelta(days=1)
                                strModifiedDate = datetime.strftime(modifiedDate, "%Y-%m-%d")
                                
                            else:
                                strModifiedTime = item[jj]
                                strModifiedDate = strDate
                            item[jj] = strModifiedDate + ' ' + strModifiedTime
                        element = item[jj]
                        temp.append(element)
                    rows.append(temp)
        
        with open(csvFileName, 'w', newline = '') as outputCSV:
            outputWriter = csv.writer(outputCSV, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            outputWriter.writerows(rows)

#############################################################################################################
#############################################################################################################
#############################################################################################################
    
    def _reOptimize(self, vehicleID, dayStartTime, startLocationID, startLocationArrival, startKm, startUnitCapacity, startMoneyCapacity, startDistLabel, initialReturnFlag, hadLunchFlag, cmcStatusDictInput, cmcStatusDictKeysList, partialOrderDictOriginal, partialAdhocDictOriginal, date, shift, maxWorkingTime = 13):
        print('@@@@@@ Re-Optimizing... @@@@@@@')
        partialOrderDict = copy.deepcopy(partialOrderDictOriginal)
        partialAdhocDict = copy.deepcopy(partialAdhocDictOriginal)
        routeDict = {}
        cmcStatusDict = {}

        partialOrderDictKeysList = [(date, shift)]
        for j in range(len(partialOrderDictKeysList)):
            kmDict = {}
            fakeKmDict = {}
            workingTime = {}
            fakeWorkingTime = {}
            key = partialOrderDictKeysList[j]
            #print(key)
            date = key[0]
            #print([date, date[0], date[1]])
            weekDay = self._dateToWeekDay(date)
            cmcStatusDict[key] = copy.deepcopy(cmcStatusDictInput[key])
            routeDict[key] = {}
            lunchDict = {}
            routeNo = -1
            #routeDict[key][routeNo + 1] = {}
            
            routeDict[key][vehicleID] = []
            missingOrderIDList = []
            flag1 = 1
            while flag1:
                routeNo = routeNo + 1
                
                print('RouteNo:')
                print(routeNo)
                if routeNo == 0:
                    completeOrderList = {}
                    completeAdhocList = {}
                    nextRouteInfo = {}
                    vehicleDoneFlag = {}
                    for vID in [vehicleID]:
                        print([key, routeNo, vID])
                        vehicleDoneFlag[vID] = 0
                        nextRouteInfo[vID] = []
                        if hadLunchFlag == 0:
                            lunchDict[vID] = [0]
                        else:
                            lunchDict[vID] = [2]
                        routeFinishFlag = 1
                        completeOrderList[vID] = []
                        completeAdhocList[vID] = []
                        for loc in partialOrderDict[key]:
                            completeOrderList[vID].append(loc)
                        for loc in partialAdhocDict[key]:
                            completeAdhocList[vID].append([loc, len(partialAdhocDict[key][loc])])
                        if len(completeOrderList[vID]) > 0:
                            activeOrderList = []
                            queueOrderList = []
                            startTimeList = []
                            
                            for i in range(len(completeOrderList[vID])):
                                locID = completeOrderList[vID][i]
                                startTimeList.append(self._clockToSeconds(self.generalDict[locID]['Start_Time']))
                            #print(completeOrderList[vID])
                            startTime = np.min(startTimeList)
                            for i in range(len(completeOrderList[vID])):
                                if startTime == startTimeList[i]:
                                    activeOrderList.append(completeOrderList[vID][i])
                                else:
                                    queueOrderList.append(completeOrderList[vID][i])
                            
                            routeDict[key][vID] = []
                            tempTime = self._clockToSeconds(startLocationArrival)#10 * 3600 - 10 #self._clockToSeconds(myVehiclesDict[vID]['Start_Time'])
                            distLabel = startDistLabel
                            workingTime[vID] = tempTime - self._clockToSeconds(dayStartTime)
                            if weekDay not in ['Saturday', 'Sunday']:
                                workingTimeCost = ((workingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(workingTime[vID] <= 8 * 3600) +  int(workingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((workingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WD_ph'])
                            else:
                                workingTimeCost = ((workingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(workingTime[vID] <= 8 * 3600) +  int(workingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((workingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WE_ph'])
                            kmDict[vID] =  startKm
                            kmFuelCost = kmDict[vID] * self.vehiclesDict[vID]['Cost_Fuel_pkm']
                            lunchDict[vID].append(tempTime)
                            #[cmcStatusDict[key], tempTime] = self._cmcStatusUpdate(cmcStatusDict[key], cmcStatusDictKeysList, tempTime, vID)
                            #print('+#+#+#+#+#+#+#+')
                            #print(tempTime/3600)
                            #print('+#+#+#+#+#+#+#+')
                            currentLocation = startLocationID
                            currentUnitCapacity = startUnitCapacity
                            currentMoneyCapacity = startMoneyCapacity
                            fakeTempTime = tempTime
                            fakeKmDict[vID] = kmDict[vID]
                            fakeCurrentLocation = currentLocation
                            arrival = tempTime# - (self.vehiclesDict[vID]['Time_at_CMC_bl_m']) * 60
                            vMaxTime = self._clockToSeconds(dayStartTime) + maxWorkingTime * 3600#24 * 3600 #self._clockToSeconds(myVehiclesDict[vID]['Max_Time'])
                            currentOrder = copy.deepcopy(partialOrderDict[key][fakeCurrentLocation])
                            currentLocationType = self.generalDict[fakeCurrentLocation]['Type']
                            fakeFakeTempTime = fakeTempTime
                            fakeServiceTimeList = []
                            for jj in range(len(currentOrder)):
                                order = currentOrder[jj]
                                orderID = order[8]
                                currentServiceType = order[3]
                                currentDeliverySize = order[4]
                                currentPickUpSize = order[5]
                                currentDeliveryAmount = order[6]
                                currentPickUpAmount = order[7]
                                fakeServiceTimeList.append(self.serviceTypeDict[(currentLocationType, currentServiceType, shift)])
                                currentServiceDuration = np.max(self.serviceTypeDict[(currentLocationType, currentServiceType, shift)])
                                currentSizeCapacityUsage = np.max([currentDeliverySize, currentPickUpSize])
                                currentAmountCapacityUsage = np.max([currentDeliveryAmount, currentPickUpAmount])
                                currentUnitCapacity = currentUnitCapacity - currentSizeCapacityUsage
                                currentMoneyCapacity = currentMoneyCapacity - currentAmountCapacityUsage
                                fakeTempTime = fakeFakeTempTime + currentServiceDuration
                                fakeWorkingTime[vID] = fakeTempTime - self._clockToSeconds(dayStartTime)
                                if weekDay not in ['Saturday', 'Sunday']:
                                    workingTimeCost = ((fakeWorkingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WD_ph'])
                                else:
                                    workingTimeCost = ((fakeWorkingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WE_ph'])
                                #print(self._checkRoutingFlagUpdate(weekDay, fakeTempTime, fakeCurrentLocation, currentMoneyCapacity, currentUnitCapacity, vMaxTime))
                                [flag1, routeFinishFlag, cmcDeltaT] = self._checkRoutingFlagUpdate(weekDay, fakeTempTime, fakeCurrentLocation, currentMoneyCapacity, currentUnitCapacity, vMaxTime)
                                #print([flag1, routeFinishFlag])
                                if flag1 == 0:
                                    for locidd in partialOrderDict[key]:
                                        for tempOrder in locidd:
                                            missingOrderIDList.append(tempOrder[8])
                                    completeOrderList[vID] = []
                                    routeFinishFlag = 0
                                    break
                                else:
                                    if routeFinishFlag == 0:
                                        break
                                    else:
                                        currentLocation = fakeCurrentLocation
                                        tempTime = fakeTempTime
                                        kmDict[vID] = fakeKmDict[vID]
                                        kmFuelCost = kmDict[vID] * self.vehiclesDict[vID]['Cost_Fuel_pkm']
                                        workingTime[vID] = fakeWorkingTime[vID]
                                        partialOrderDict[key][currentLocation].remove(order)
                                        if jj == len(currentOrder) - 1:
                                            completeOrderList[vID].remove(currentLocation)
                                            activeOrderList.remove(currentLocation)
                                        #print([currentLocation, len(completeOrderList[vID]), len(activeOrderList), len(queueOrderList)])
                                        #print(queueOrderList)
                                        routeDict[key][vID].append([currentLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), currentServiceType, self._secondsToClock(currentServiceDuration), currentDeliverySize, currentPickUpSize, currentDeliveryAmount, currentPickUpAmount, currentSizeCapacityUsage, currentAmountCapacityUsage, currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, orderID, distLabel])
                            
                            if tempTime > 12 * 3600 and lunchDict[vID][0] < 1 and routeFinishFlag == 1 and key[1] == 'Day':
                                lunchDict[vID][0] = lunchDict[vID][0] + 1
                                if lunchDict[vID][0] == 1:
                                    arrival = tempTime
                                    tempTime = tempTime + self.vehiclesDict[vID]['Rest_Time_m'] * 60
                                    workingTime[vID] = tempTime - self._clockToSeconds(routeDict[key][vID][0][1])
                                    if weekDay not in ['Saturday', 'Sunday']:
                                        workingTimeCost = ((fakeWorkingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WD_ph'])
                                    else:
                                        workingTimeCost = ((fakeWorkingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WE_ph'])
                                    routeDict[key][vID].append([currentLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), 'Rest', self._secondsToClock(self.vehiclesDict[vID]['Rest_Time_m'] * 60), '---', '---', '---', '---', '---', '---', currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, '---', '---'])
                                    
                            if initialReturnFlag == 1:
                                routeFinishFlag = 0
                                
                            while routeFinishFlag == 1 and len(completeOrderList[vID]) > 0:
                                if len(queueOrderList) > 0:
                                    tempQueueOrderList = []
                                    for i in range(len(queueOrderList)):
                                        qLocID = queueOrderList[i]
                                        if tempTime >= self._clockToSeconds(self.generalDict[qLocID]['Start_Time']):
                                            activeOrderList.append(qLocID)
                                        else:
                                            tempQueueOrderList.append(qLocID)
                                    queueOrderList = copy.deepcopy(tempQueueOrderList)
                                if len(activeOrderList) > 0:
                                    [nextLocation, deltaT, distLabel] = self._closestLocationDuration(currentLocation, activeOrderList, weekDay, tempTime) 
                                    fakeTempTime = tempTime + deltaT
                                    fakeKmDict[vID] = kmDict[vID] + self._closestLocationDirect(currentLocation, [nextLocation], funcFlag=1)/1000
                                    arrival = fakeTempTime
                                    fakeCurrentLocation = nextLocation
                                    currentOrder = copy.deepcopy(partialOrderDict[key][fakeCurrentLocation])
                                    currentLocationType = self.generalDict[fakeCurrentLocation]['Type']
                                    fakeFakeTempTime = fakeTempTime
                                    fakeServiceTimeList = []
                                    for jj in range(len(currentOrder)):
                                        order = currentOrder[jj]
                                        orderID = order[8]
                                        currentServiceType = order[3]
                                        currentDeliverySize = order[4]
                                        currentPickUpSize = order[5]
                                        currentDeliveryAmount = order[6]
                                        currentPickUpAmount = order[7]
                                        fakeServiceTimeList.append(self.serviceTypeDict[(currentLocationType, currentServiceType, shift)])
                                        currentServiceDuration = np.max(fakeServiceTimeList)
                                        currentSizeCapacityUsage = np.max([currentDeliverySize, currentPickUpSize])
                                        currentAmountCapacityUsage = np.max([currentDeliveryAmount, currentPickUpAmount])
                                        currentUnitCapacity = currentUnitCapacity - currentSizeCapacityUsage#np.max([currentDeliverySize - currentPickUpSize])
                                        currentMoneyCapacity = currentMoneyCapacity - np.max([currentDeliveryAmount, currentPickUpAmount])
                                        fakeTempTime = fakeFakeTempTime + currentServiceDuration
                                        fakeWorkingTime[vID] = fakeTempTime - self._clockToSeconds(dayStartTime)
                                        if weekDay not in ['Saturday', 'Sunday']:
                                            workingTimeCost = ((fakeWorkingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WD_ph'])
                                        else:
                                            workingTimeCost = ((fakeWorkingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WE_ph'])
                                        [flag1, routeFinishFlag, cmcDeltaT] = self._checkRoutingFlagUpdate(weekDay, fakeTempTime, fakeCurrentLocation, currentMoneyCapacity, currentUnitCapacity, vMaxTime)        
                                        #print([flag1, routeFinishFlag])
                                        if flag1 == 0:
                                            #print(routeDict[key][vID][routeNo])
                                            for locidd in partialOrderDict[key]:
                                                for tempOrder in locidd:
                                                    missingOrderIDList.append(tempOrder[8])
                                            completeOrderList[vID] = []
                                            routeFinishFlag = 0
                                            break
                                        else:
                                            if routeFinishFlag == 0:
                                                break
                                            else:
                                                currentLocation = fakeCurrentLocation
                                                tempTime = fakeTempTime
                                                kmDict[vID] = fakeKmDict[vID]
                                                kmFuelCost = kmDict[vID] * self.vehiclesDict[vID]['Cost_Fuel_pkm']
                                                workingTime[vID] = fakeWorkingTime[vID]
                                                partialOrderDict[key][currentLocation].remove(order)
                                                if jj == len(currentOrder) - 1:
                                                    completeOrderList[vID].remove(currentLocation)
                                                    activeOrderList.remove(currentLocation)
                                                #print([currentLocation, len(completeOrderList[vID]), len(activeOrderList), len(queueOrderList)])
                                                #print(queueOrderList)
                                                routeDict[key][vID].append([currentLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), currentServiceType, self._secondsToClock(currentServiceDuration), currentDeliverySize, currentPickUpSize, currentDeliveryAmount, currentPickUpAmount, currentSizeCapacityUsage, currentAmountCapacityUsage, currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, orderID, distLabel])
                                    
                                    if tempTime > 12 * 3600 and lunchDict[vID][0] < 1:
                                        lunchDict[vID][0] = lunchDict[vID][0] + 1
                                        if lunchDict[vID][0] == 1:
                                            arrival = tempTime
                                            tempTime = tempTime + self.vehiclesDict[vID]['Rest_Time_m'] * 60
                                            workingTime[vID] = tempTime - self._clockToSeconds(routeDict[key][vID][0][1])
                                            if weekDay not in ['Saturday', 'Sunday']:
                                                workingTimeCost = ((fakeWorkingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WD_ph'])
                                            else:
                                                workingTimeCost = ((fakeWorkingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WE_ph'])
                                            routeDict[key][vID].append([currentLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), 'Rest', self._secondsToClock(self.vehiclesDict[vID]['Rest_Time_m'] * 60), '---', '---', '---', '---', '---', '---', currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, '---', '---'])
                                    
                                else:
                                    if len(queueOrderList) > 0:
                                        startTimeList = []
                                        for k in range(len(queueOrderList)):
                                            qLocID = queueOrderList[k]
                                            startTimeList.append(self._clockToSeconds(self.generalDict[qLocID]['Start_Time']))
                                        startTime = np.min(startTimeList)
                                        tempTime = startTime
                                        tempQueueOrderList = []
                                        for k in range(len(queueOrderList)):
                                            if startTimeList[k] == startTime:
                                                activeOrderList.append(queueOrderList[k])
                                            else:
                                                tempQueueOrderList.append(queueOrderList[k])
                                        queueOrderList = copy.deepcopy(tempQueueOrderList)
                            
                            
                            nextLocation = list(self.cmcDict.keys())[0]#myVehiclesDict[vID]['CMC_ID']
                            [deltaT, distLabel] = self._closestLocationDuration(currentLocation, [nextLocation], weekDay, tempTime, funcFlag=1)
                            arrival = tempTime + deltaT
                            tempTime = tempTime + deltaT
                            kmDict[vID] = kmDict[vID] + self._closestLocationDirect(currentLocation, [nextLocation], funcFlag=1)/1000
                            kmFuelCost = kmDict[vID] * self.vehiclesDict[vID]['Cost_Fuel_pkm']
                            workingTime[vID] = tempTime - self._clockToSeconds(routeDict[key][vID][0][1])
                            if weekDay not in ['Saturday', 'Sunday']:
                                workingTimeCost = ((workingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(workingTime[vID] <= 8 * 3600) +  int(workingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((workingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WD_ph'])
                            else:
                                workingTimeCost = ((workingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(workingTime[vID] <= 8 * 3600) +  int(workingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((workingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WE_ph'])   
                            #routeDict[key][routeNo][vID].append([nextLocation, tempTime, currentUnitCapacity, currentMoneyCapacity])
                            if routeFinishFlag == 0 and len(completeOrderList[vID]) > 0:
                                tempTime = tempTime + self.serviceTypeDict[('CMC', 'Reload Box', shift)]    
                                currentUnitCapacity = self.vehicleTypeDict[self.vehiclesDict[vID]['Vehicle_Type_ID']]['Capacity_unit']
                                currentMoneyCapacity = self.vehicleTypeDict[self.vehiclesDict[vID]['Vehicle_Type_ID']]['Insurance_Limit']
                                currentServiceType = 'Reload Box'
                                currentLocationType = 'CMC'
                                currentServiceDuration = self.serviceTypeDict[('CMC', currentServiceType, shift)]
                                routeDict[key][vID].append([nextLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), currentServiceType, self._secondsToClock(currentServiceDuration), '---', '---', '---', '---', '---', '---', currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, '---', distLabel])
                                nextRouteInfo[vID] = [completeOrderList[vID], tempTime]
                                
                            
                            elif len(completeOrderList[vID]) == 0:
                                tempTime = tempTime + 3600
                                currentUnitCapacity = self.vehicleTypeDict[self.vehiclesDict[vID]['Vehicle_Type_ID']]['Capacity_unit']
                                currentMoneyCapacity = self.vehicleTypeDict[self.vehiclesDict[vID]['Vehicle_Type_ID']]['Insurance_Limit']
                                currentServiceType = 'Stand By'
                                currentServiceDuration = self.serviceTypeDict[('CMC', 'Reload Box', shift)]
                                routeDict[key][vID].append([nextLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), currentServiceType, self._secondsToClock(3600), '---', '---', '---', '---', '---', '---', currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, '---', distLabel])
                                nextRouteInfo[vID] = [completeOrderList[vID], tempTime]
                        ###else:
                        

                    cmcArrivalTimeList = []
                    nextRouteInfoKeysList = list(nextRouteInfo.keys())
                    for k in range(len(nextRouteInfoKeysList)):
                        v_id = nextRouteInfoKeysList[k]
                        #print(nextRouteInfo[v_id])
                        cmcArrivalTimeList.append(nextRouteInfo[v_id][1])
                    indices = np.argsort(cmcArrivalTimeList)
                    for index in indices:
                        v_id = nextRouteInfoKeysList[index]
                        if len(nextRouteInfo[v_id][0]) > 0:
                            [cmcStatusDict[key], nextRouteInfo[v_id][1]] = self._cmcStatusUpdate(cmcStatusDict[key], cmcStatusDictKeysList, nextRouteInfo[v_id][1], v_id)
                            
                        
                else: #routeNo > 0
                    print('\n\n\n\n\-----------------n\n\n\n=============\n\n\n\n------------\n\n\nVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYYYYYYYYYYYY\n')
                    fakeSum = 0
                    for v_id in vehicleDoneFlag:
                        fakeSum = fakeSum + vehicleDoneFlag[v_id]
                    if fakeSum == len(vehicleDoneFlag):
                        break
                     
                    for vID in [vehicleID]:
                        print([key, routeNo, vID])
                        completeOrderList[vID] = nextRouteInfo[vID][0]
                        tempTime = nextRouteInfo[vID][1]

                        if workingTime[vID] <= 9*3600:
#################################################################################################################

                            tempRemoveList = []
                            adhocRemoveList = []
                            for kk in range(len(completeAdhocList[vID])):
                                [loc, adhocCount] = completeAdhocList[vID][kk]
                                for adhoc in partialAdhocDict[key][loc]:
                                    if self._clockToSeconds(adhoc[11]) < tempTime:
                                        if loc not in partialOrderDict[key]:
                                            partialOrderDict[key][loc] = [adhoc]
                                        else:
                                            partialOrderDict[key][loc].append(adhoc)
                                        
                                        if loc not in completeOrderList[vID]:
                                            completeOrderList[vID].append(loc)
                                        completeAdhocList[vID][kk][1] = completeAdhocList[vID][kk][1] - 1
                                        adhocRemoveList.append((loc, adhoc))
                                        if completeAdhocList[vID][kk][1] == 0:
                                            tempRemoveList.append(completeAdhocList[vID][kk])
                                            
                            for [loc, adhoc] in adhocRemoveList:
                                partialAdhocDict[key][loc].remove(adhoc)
                            for item in tempRemoveList:
                                completeAdhocList[vID].remove(item)
############################################################################################################                        



                        
                        if len(completeOrderList[vID]) > 0:
                            print('yes')
                            print(len(nextRouteInfo[vID][0]))
                            #nextRouteInfo[vID] = []
                            routeFinishFlag = 1
                            ######completeOrderList[vID] = nextRouteInfo[vID][0]
                            activeOrderList = []
                            queueOrderList = []
                            ######tempTime = nextRouteInfo[vID][1]
                            vMaxTime = dayStartTime + maxWorkingTime *3600#24 * 3600#self._clockToSeconds(myVehiclesDict[vID]['Max_Time'])


                            for i in range(len(completeOrderList[vID])):
                                locID = completeOrderList[vID][i]
                                if tempTime >= self._clockToSeconds(self.generalDict[locID]['Start_Time']):
                                    activeOrderList.append(locID)
                                else:
                                    queueOrderList.append(locID)
                            currentLocation = list(self.cmcDict.keys())[0]#myVehiclesDict[vID]['CMC_ID']
                            currentUnitCapacity = self.vehicleTypeDict[self.vehiclesDict[vID]['Vehicle_Type_ID']]['Capacity_unit']
                            currentMoneyCapacity = self.vehicleTypeDict[self.vehiclesDict[vID]['Vehicle_Type_ID']]['Insurance_Limit']
                            #currentKM = 0
                            #routeDict[key][routeNo][vID] = [[currentLocation, tempTime, currentUnitCapacity, currentMoneyCapacity]]
                            [nextLocation, deltaT, distLabel] = self._furthestLocationDuration(currentLocation, activeOrderList, weekDay, tempTime)
                            fakeTempTime = tempTime + deltaT
                            fakeKmDict[vID] = kmDict[vID] + self._closestLocationDirect(currentLocation, [nextLocation], funcFlag=1)/1000
                            arrival = fakeTempTime
                            fakeCurrentLocation = nextLocation
                            currentOrder = copy.deepcopy(partialOrderDict[key][fakeCurrentLocation])
                            currentLocationType = self.generalDict[fakeCurrentLocation]['Type']
                            fakeFakeTempTime = fakeTempTime
                            fakeServiceTimeList = []
                            for jj in range(len(currentOrder)):
                                order = currentOrder[jj]
                                orderID = order[8]
                                currentServiceType = order[3]
                                currentDeliverySize = order[4]
                                currentPickUpSize = order[5]
                                currentDeliveryAmount = order[6]
                                currentPickUpAmount = order[7]
                                fakeServiceTimeList.append(self.serviceTypeDict[(currentLocationType, currentServiceType, shift)])
                                currentServiceDuration = np.max(fakeServiceTimeList)
                                currentSizeCapacityUsage = np.max([currentDeliverySize, currentPickUpSize])
                                currentAmountCapacityUsage = np.max([currentDeliveryAmount, currentPickUpAmount])
                                currentUnitCapacity = currentUnitCapacity - currentSizeCapacityUsage#np.max([currentDeliverySize, currentPickUpSize])
                                currentMoneyCapacity = currentMoneyCapacity - np.max([currentDeliveryAmount, currentPickUpAmount])
                                fakeTempTime = fakeFakeTempTime + currentServiceDuration
                                fakeWorkingTime[vID] = fakeTempTime - self._clockToSeconds(dayStartTime)
                                if weekDay not in ['Saturday' , 'Sunday']:
                                    workingTimeCost = ((fakeWorkingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WD_ph'])
                                else:
                                    workingTimeCost = ((fakeWorkingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WE_ph'])
                                [flag1, routeFinishFlag, cmcDeltaT] = self._checkRoutingFlagUpdate(weekDay, fakeTempTime, fakeCurrentLocation, currentMoneyCapacity, currentUnitCapacity, vMaxTime)
                                print([flag1, routeFinishFlag])
                                if flag1 == 0:
                                    #print(routeDict[key][vID][routeNo])
                                    for locidd in partialOrderDict[key]:
                                        for tempOrder in locidd:
                                            missingOrderIDList.append(tempOrder[8])
                                    completeOrderList[vID] = []
                                    routeFinishFlag = 0
                                    break
                                else:
                                    if routeFinishFlag == 0:
                                        break
                                    else:
                                        currentLocation = fakeCurrentLocation
                                        tempTime = fakeTempTime
                                        kmDict[vID] = fakeKmDict[vID]
                                        kmFuelCost = kmDict[vID] * self.vehiclesDict[vID]['Cost_Fuel_pkm']
                                        workingTime[vID] = fakeWorkingTime[vID]
                                        partialOrderDict[key][fakeCurrentLocation].remove(order)
                                        if jj == len(currentOrder) - 1:
                                            completeOrderList[vID].remove(currentLocation)
                                            activeOrderList.remove(currentLocation)
                                        routeDict[key][vID].append([currentLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), currentServiceType, self._secondsToClock(currentServiceDuration), currentDeliverySize, currentPickUpSize, currentDeliveryAmount, currentPickUpAmount, currentSizeCapacityUsage, currentAmountCapacityUsage, currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, orderID, distLabel])
                            #if flag1 == 0:
                            #    break
                            if tempTime > 12 * 3600 and lunchDict[vID][0] < 1 and routeFinishFlag == 1:
                                lunchDict[vID][0] = lunchDict[vID][0] + 1
                                if lunchDict[vID][0] == 1:
                                    arrival = tempTime
                                    tempTime = tempTime + self.vehiclesDict[vID]['Rest_Time_m'] * 60
                                    workingTime[vID] = tempTime - self._clockToSeconds(routeDict[key][vID][0][1])
                                    if weekDay not in ['Saturday', 'Sunday']:
                                        workingTimeCost = ((fakeWorkingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WD_ph'])
                                    else:
                                        workingTimeCost = ((fakeWorkingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WE_ph'])
                                    routeDict[key][vID].append([currentLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), 'Rest', self._secondsToClock(self.vehiclesDict[vID]['Rest_Time_m'] * 60), '---', '---', '---', '---', '---', '---', currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, '---', '---'])
                                    
                            
                            while routeFinishFlag == 1 and len(completeOrderList[vID]) > 0:
                                if len(queueOrderList) > 0:
                                    tempQueueOrderList = []
                                    for i in range(len(queueOrderList)):
                                        qLocID = queueOrderList[i]
                                        if tempTime >= self._clockToSeconds(self.generalDict[qLocID]['Start_Time']):
                                            activeOrderList.append(qLocID)
                                        else:
                                            tempQueueOrderList.append(qLocID)
                                    queueOrderList = copy.deepcopy(tempQueueOrderList)
                                if len(activeOrderList) > 0:
                                    [nextLocation, deltaT, distLabel] = self._closestLocationDuration(currentLocation, activeOrderList, weekDay, tempTime) 
                                    fakeTempTime = tempTime + deltaT
                                    fakeKmDict[vID] = kmDict[vID] + self._closestLocationDirect(currentLocation, [nextLocation], funcFlag=1)/1000
                                    arrival = fakeTempTime
                                    fakeCurrentLocation = nextLocation
                                    currentOrder = copy.deepcopy(partialOrderDict[key][fakeCurrentLocation])
                                    currentLocationType = self.generalDict[fakeCurrentLocation]['Type']
                                    fakeFakeTempTime = fakeTempTime
                                    fakeServiceTimeList = []
                                    for jj in range(len(currentOrder)):
                                        order = currentOrder[jj]
                                        orderID = order[8]
                                        currentServiceType = order[3]
                                        currentDeliverySize = order[4]
                                        currentPickUpSize = order[5]
                                        currentDeliveryAmount = order[6]
                                        currentPickUpAmount = order[7]
                                        fakeServiceTimeList.append(self.serviceTypeDict[(currentLocationType, currentServiceType, shift)])
                                        currentServiceDuration = np.max(fakeServiceTimeList)
                                        currentSizeCapacityUsage = np.max([currentDeliverySize, currentPickUpSize])
                                        currentAmountCapacityUsage = np.max([currentDeliveryAmount, currentPickUpAmount])
                                        currentUnitCapacity = currentUnitCapacity - currentSizeCapacityUsage#np.max([currentDeliverySize - currentPickUpSize])
                                        currentMoneyCapacity = currentMoneyCapacity - np.max([currentDeliveryAmount, currentPickUpAmount])
                                        fakeTempTime = fakeFakeTempTime + currentServiceDuration
                                        fakeWorkingTime[vID] = fakeTempTime - self._clockToSeconds(dayStartTime)
                                        if weekDay not in ['Saturday', 'Sunday']:
                                            workingTimeCost = ((fakeWorkingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WD_ph'])
                                        else:
                                            workingTimeCost = ((fakeWorkingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WE_ph'])
                                        [flag1, routeFinishFlag, cmcDeltaT] = self._checkRoutingFlagUpdate(weekDay, fakeTempTime, fakeCurrentLocation, currentMoneyCapacity, currentUnitCapacity, vMaxTime)        
                                        print([flag1, routeFinishFlag])
                                        if flag1 == 0:
                                            #print(routeDict[key][vID])
                                            for locidd in partialOrderDict[key]:
                                                for tempOrder in locidd:
                                                    missingOrderIDList.append(tempOrder[8])
                                            completeOrderList[vID] = []
                                            routeFinishFlag = 0
                                            break
                                        else:
                                            if routeFinishFlag == 0:
                                                break
                                            else:
                                                currentLocation = fakeCurrentLocation
                                                tempTime = fakeTempTime
                                                kmDict[vID] = fakeKmDict[vID]
                                                kmFuelCost = kmDict[vID] * self.vehiclesDict[vID]['Cost_Fuel_pkm']
                                                workingTime[vID] = fakeWorkingTime[vID]
                                                partialOrderDict[key][currentLocation].remove(order)
                                                if jj == len(currentOrder) - 1:
                                                    completeOrderList[vID].remove(currentLocation)
                                                    activeOrderList.remove(currentLocation)
                                                routeDict[key][vID].append([currentLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), currentServiceType, self._secondsToClock(currentServiceDuration), currentDeliverySize, currentPickUpSize, currentDeliveryAmount, currentPickUpAmount, currentSizeCapacityUsage, currentAmountCapacityUsage, currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, orderID, distLabel])
                                    #if flag1 == 0:
                                    #    return [0, [], []]
                                    if tempTime > 12 * 3600 and lunchDict[vID][0] < 1:
                                        lunchDict[vID][0] = lunchDict[vID][0] + 1
                                        if lunchDict[vID][0] == 1:
                                            arrival = tempTime
                                            tempTime = tempTime + self.vehiclesDict[vID]['Rest_Time_m'] * 60
                                            workingTime[vID] = tempTime - self._clockToSeconds(routeDict[key][vID][0][1])
                                            if weekDay not in ['Saturday', 'Sunday']:
                                                workingTimeCost = ((fakeWorkingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WD_ph'])
                                            else:
                                                workingTimeCost = ((fakeWorkingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(fakeWorkingTime[vID] <= 8 * 3600) +  int(fakeWorkingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((fakeWorkingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WE_ph'])
                                            routeDict[key][vID].append([currentLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), 'Rest', self._secondsToClock(self.vehiclesDict[vID]['Rest_Time_m'] * 60), '---', '---', '---', '---', '---', '---', currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, '---', '---'])
                                    
                                else:
                                    if len(queueOrderList) > 0:
                                        startTimeList = []
                                        for k in range(len(queueOrderList)):
                                            qLocID = queueOrderList[k]
                                            startTimeList.append(self._clockToSeconds(self.generalDict[qLocID]['Start_Time']))
                                        startTime = np.min(startTimeList)
                                        tempTime = startTime
                                        tempQueueOrderList = []
                                        for k in range(len(queueOrderList)):
                                            if startTimeList[k] == startTime:
                                                activeOrderList.append(queueOrderList[k])
                                            else:
                                                tempQueueOrderList.append(queueOrderList[k])
                                        queueOrderList = copy.deepcopy(tempQueueOrderList)
                            
                            #if flag1 == 0:
                            #    return [0, [], []]
                            nextLocation = list(self.cmcDict.keys())[0]
                            [deltaT, distLabel] = self._closestLocationDuration(currentLocation, [nextLocation], weekDay, tempTime, funcFlag=1)
                            arrival = tempTime + deltaT
                            tempTime = tempTime + deltaT
                            kmDict[vID] = kmDict[vID] + self._closestLocationDirect(currentLocation, [nextLocation], funcFlag=1)/1000
                            kmFuelCost = kmDict[vID] * self.vehiclesDict[vID]['Cost_Fuel_pkm']
                            workingTime[vID] = tempTime - self._clockToSeconds(routeDict[key][vID][0][1])
                            if weekDay not in ['Saturday', 'Sunday']:
                                workingTimeCost = ((workingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(workingTime[vID] <= 8 * 3600) +  int(workingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((workingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WD_ph'])
                            else:
                                workingTimeCost = ((workingTime[vID]/3600) * self.vehiclesDict[vID]['Cost_RunningTime']) * int(workingTime[vID] <= 8 * 3600) +  int(workingTime[vID] > 8 * 3600) * ((8 * self.vehiclesDict[vID]['Cost_RunningTime']) + ((workingTime[vID]/3600) - 8) * self.vehiclesDict[vID]['Cost_Overtime_WE_ph'])   
                            #routeDict[key][routeNo][vID].append([nextLocation, tempTime, currentUnitCapacity, currentMoneyCapacity])
                            if routeFinishFlag == 0 and len(completeOrderList[vID]) > 0:
                                tempTime = tempTime + self.serviceTypeDict[('CMC', 'Reload Box', shift)]    
                                currentUnitCapacity = self.vehicleTypeDict[self.vehiclesDict[vID]['Vehicle_Type_ID']]['Capacity_unit']
                                currentMoneyCapacity = self.vehicleTypeDict[self.vehiclesDict[vID]['Vehicle_Type_ID']]['Insurance_Limit']
                                currentServiceType = 'Reload Box'
                                currentServiceDuration = self.serviceTypeDict[('CMC', currentServiceType, shift)]
                                routeDict[key][vID].append([nextLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), currentServiceType, self._secondsToClock(currentServiceDuration), '---', '---', '---', '---', '---', '---', currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, '---', distLabel])
                                nextRouteInfo[vID] = [completeOrderList[vID], tempTime]
                            elif len(completeOrderList[vID]) == 0:
                                tempTime = tempTime + 3600
                                currentUnitCapacity = self.vehicleTypeDict[self.vehiclesDict[vID]['Vehicle_Type_ID']]['Capacity_unit']
                                currentMoneyCapacity = self.vehicleTypeDict[self.vehiclesDict[vID]['Vehicle_Type_ID']]['Insurance_Limit']
                                currentServiceType = 'Stand By'
                                currentServiceDuration = self.serviceTypeDict[('CMC', 'Reload Box', shift)]
                                routeDict[key][vID].append([nextLocation, self._secondsToClock(arrival), self._secondsToClock(tempTime), currentServiceType, self._secondsToClock(3600), '---', '---', '---', '---', '---', '---', currentUnitCapacity, currentMoneyCapacity, kmDict[vID], kmFuelCost, self._secondsToClock(workingTime[vID]), workingTimeCost, '---', distLabel])
                                nextRouteInfo[vID] = [completeOrderList[vID], tempTime]
                            
                        else:
                            vehicleDoneFlag[vID] = 1
                    cmcArrivalTimeList = []
                    nextRouteInfoKeysList = list(nextRouteInfo.keys())
                    for k in range(len(nextRouteInfoKeysList)):
                        v_id = nextRouteInfoKeysList[k]
                        cmcArrivalTimeList.append(nextRouteInfo[v_id][1])
                    indices = np.argsort(cmcArrivalTimeList)
                    for index in indices:
                        v_id = nextRouteInfoKeysList[index]
                        if len(nextRouteInfo[v_id][0]) > 0:
                            [cmcStatusDict[key], nextRouteInfo[v_id][1]] = self._cmcStatusUpdate(cmcStatusDict[key], cmcStatusDictKeysList, nextRouteInfo[v_id][1], v_id)
        
            
        return [routeDict, missingOrderIDList]
        
    