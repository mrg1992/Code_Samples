import math
import numpy as np
import copy
import calendar
import csv


class SolutionClass2:
    def __init__(self, eMachineDict, branchDict, corporateDict, cmcDict, generalDict, vehiclesDict, vehicleTypeDict, ordersDict, adhocDict, serviceTypeDict, normalDistMatDict, superDistMatDict, timeKeyList, offsetN_sd = 21):
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
        self.logCounter = 0  
        self.offsetN_sd = offsetN_sd
        '''for loc in self.generalDict:
            if self.generalDict[loc]['Model'] == 'E-Machine':
                self.generalDict[loc]['Visit_Frequency_pw'] = 0
                for key in self.ordersDict:
                    if loc in self.ordersDict[key] or loc in self.adhocDict[key]:
                        self.generalDict[loc]['Visit_Frequency_pw'] = self.generalDict[loc]['Visit_Frequency_pw'] + 1#int(loc in self.ordersDict[key]) + int(loc in self.adhocDict[key])
            else:
                if self.generalDict[loc]['Model'] != 'CMC':
                    self.generalDict[loc]['Visit_Frequency_pw_fake'] = self.generalDict[loc]['Visit_Frequency_pw']
    '''
    
    def _secondsToClock(self, seconds):
        if seconds < 0:
            seconds = 24 * 3600 + seconds
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
    
    def _clockToSeconds(self, strTime, flag = 1):
        if flag == 0:
            if len(strTime) == 8:
                return int(strTime[0:2])*3600 + int(strTime[3:5])*60 + int(strTime[6:8])
            elif len(strTime) == 5:
                return int(strTime[0:2])*3600 + int(strTime[3:5])*60
        else:
            if len(strTime) == 8:
                sec = int(strTime[0:2])*3600 + int(strTime[3:5])*60 + int(strTime[6:8])
            elif len(strTime) == 5:
                sec = int(strTime[0:2])*3600 + int(strTime[3:5])*60
            if sec >= 12 * 3600:
                sec =  sec - 24*3600
            return sec
            
    
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
        with open('log_night.txt', 'a') as f:
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
            index = np.argmax(distList)
        return [locationList[index], 0.95*distList[index], distLabelList[index]]
    
    def _closestLocationDuration(self, originID, locationList, weekDay, tempTime, funcFlag = 0):
        distList = []
        distLabelList = []
        #with shelve.open(self.superDistMatFileName, 'r') as superDistMat:
        if funcFlag == 0:
            with open('log_night.txt', 'a') as f:
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
            return [locationList[index], 0.95*distList[index], distLabelList[index]]
        else:
            with open('log_night.txt', 'a') as f:
                print('#############################################\n#############################################\n', file=f)
                print('log counter: %d ;;; Length of LocationList: %d' %(self.logCounter, len(locationList)), file=f)
                locID = locationList[0]
                distKey = self.generalDict[originID]['Latitude'] + ',' + self.generalDict[originID]['Longitude'] + ';' + self.generalDict[locID]['Latitude'] + ',' + self.generalDict[locID]['Longitude']
                timeKey = self._fixDistMatTimeKeys(tempTime)
                print([-1, 1], file=f)
                temp = self.superDistMatDict[distKey][weekDay][timeKey]
            return [0.95*temp[0], temp[1]]
                
                
                
    
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
    
    def _assignLocations2vehicles(self, locationList, N, maxF):
        if len(locationList) > 0:
            print('####  Key Assignment  Start ####')
            tempLocationList = copy.deepcopy(locationList)
            vehicleKeysDict = {}
            locationKeysDict = {}
            #N = math.ceil(len(locationList)/maxKeyNumber)
            #maxF = 0
            cmcID = list(self.cmcDict.keys())[0]
            tempVehicleID = list(self.vehiclesDict.keys())[0]
            initialVehicleID = 1
            myVehiclesDict = {}
            myVehiclesDict[initialVehicleID] = self.vehiclesDict[tempVehicleID]
            for i in range(2, N + 1):
                myVehicleID = i
                #print([i, N, self.offsetN_sd, len(list(self.vehiclesDict.keys())), list(self.vehiclesDict.keys())])
                myVehiclesDict[myVehicleID] = self.vehiclesDict[list(self.vehiclesDict.keys())[i - 1 + self.offsetN_sd]]
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
    
    def _checkRouting(self, myVehiclesDict, vehicleKeysDict, locationKeysDict, cmcStatusDictInput, cmcStatusDictKeysList, partialOrderDictOriginal, partialOrderDictKeysListOriginal, partialAdhocDictOriginal, shift):
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
                            
                            tempTime = -3600 #self._clockToSeconds(myVehiclesDict[vID]['Start_Time'])
                            [cmcStatusDict[key], tempTime] = self._cmcStatusUpdate(cmcStatusDict[key], cmcStatusDictKeysList, tempTime, vID)
                            print('+#+#+#+#+#+#+#+')
                            print(tempTime/3600)
                            print('+#+#+#+#+#+#+#+')
                            arrival = tempTime - (myVehiclesDict[vID]['Time_at_CMC_bl_m']) * 60
                            vMaxTime = 9*3600  #arrival + 13 * 3600#24 * 3600 #self._clockToSeconds(myVehiclesDict[vID]['Max_Time'])
                
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
                            tempTime = 6 * 3600
                            arrival = tempTime - (myVehiclesDict[vID]['Time_at_CMC_bl_m']) * 60
                            vMaxTime = 10*3600#arrival + 13 * 3600#24 * 3600 #self._clockToSeconds(myVehiclesDict[vID]['Max_Time'])
                
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

                        if workingTime[vID] < 7*3600:
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
                            vMaxTime = 9*3600 #self._clockToSeconds(routeDict[key][vID][0][1]) + 13 *3600#24 * 3600#self._clockToSeconds(myVehiclesDict[vID]['Max_Time'])


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
            [successFlag, routeDict, locationKeysDict, vehicleKeysDict, cmcStatusDict] = self._checkRouting(myVehiclesDict, vehicleKeysDict, locationKeysDict, cmcStatusDict, cmcStatusDictKeysList, partialOrderDict, partialOrderDictKeysList, partialAdhocDict, shift)
            if successFlag == 1:
                return [N, locationKeysDict, vehicleKeysDict, routeDict, cmcStatusDict]
            else:
                N = N + 1
                              
    
                                
    
    def _integratedRouting(self, generalServicePointDict, cmcStatusDictGeneral_orig, cmcStatusDictKeysList, initial_N_sn = 4):
        cmcStatusDict = copy.deepcopy(cmcStatusDictGeneral_orig)
        [locList_SD, locList_SN, locList_HD] = [[], [], []]
        #[N_hd, hardRouteDict] = [{}, {}]
        for locID in generalServicePointDict:
            if generalServicePointDict[locID]['Model'] == 'E-Machine' and generalServicePointDict[locID]['Shift'] == 'Night':
                locList_SN.append(locID)
        
        [orderDict_SD, orderDict_SN, orderDict_HD] = [{}, {}, {}]
        for orderKey in self.ordersDict:
            for locID in self.ordersDict[orderKey]:
                if generalServicePointDict[locID]['Model'] == 'E-Machine' and generalServicePointDict[locID]['Shift'] == 'Night':
                    if orderKey not in orderDict_SN:
                        orderDict_SN[orderKey] = {}
                    orderDict_SN[orderKey][locID] = self.ordersDict[orderKey][locID]

        adhocDict_SN = {}
        for orderKey in self.adhocDict:
            if orderKey not in adhocDict_SN:
                adhocDict_SN[orderKey] = {}
            for locID in self.adhocDict[orderKey]:
                if generalServicePointDict[locID]['Model'] == 'E-Machine' and generalServicePointDict[locID]['Shift'] == 'Night':
                    adhocDict_SN[orderKey][locID] = self.adhocDict[orderKey][locID]
        
        [N_sn, locationKeysDict, vehicleKeysDict, softRouteDict, cmcStatusDict] = self._MP_ST(initial_N_sn, locList_SN, orderDict_SN, list(orderDict_SN.keys()), adhocDict_SN, cmcStatusDict, cmcStatusDictKeysList, 'Night')
            
        return [N_sn, locationKeysDict, vehicleKeysDict, softRouteDict]
        
        
            
    def _dailyPlan2CSV(self, softRouteDict, hardRouteDict, csvFileName = 'DailyPlan_Night.csv'):
        rows = [['Date', 'Shift', 'VehicleID', 'CurrentLocation', 'Arrival', 'Departure', 'ServiceType', 'ServiceDuration', 'DeliverySize', 'PickUpSize', 'DeliveryAmount', 'PickUpAmount', 'SizeCapacityUsage', 'AmountCapacityUsage', 'SizeCapacity', 'AmountCapacity', 'Kilometre', 'FuelCost', 'WorkingTime', 'WorkingTimeCost', 'OrderID', 'DistLabel']]
        for key in softRouteDict:
            for vid in softRouteDict[key]:
                for item in softRouteDict[key][vid]:
                    #print(vid - 1 + self.offsetN_sd)
                    if type(vid) == int:
                        temp = [key[0], key[1], list(self.vehiclesDict.keys())[vid - 1 + self.offsetN_sd]]
                    else:
                        temp = [key[0], key[1], vid]
                    for element in item:
                        temp.append(element)
                    rows.append(temp)
        '''
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
                    temp = [key[0], key[1], 'H-' + str(vid)]
                    for element in item:
                        temp.append(element)
                    rows.append(temp)
        '''
        with open(csvFileName, 'w', newline = '') as outputCSV:
            outputWriter = csv.writer(outputCSV, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            outputWriter.writerows(rows)


#########################################################################################
#########################################################################################
#########################################################################################
            
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
                            vMaxTime = 9*3600 #self._clockToSeconds(dayStartTime) + maxWorkingTime * 3600#24 * 3600 #self._clockToSeconds(myVehiclesDict[vID]['Max_Time'])
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

                        if workingTime[vID] <= 7*3600:
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
                            vMaxTime = 9 * 3600 #dayStartTime + maxWorkingTime *3600#24 * 3600#self._clockToSeconds(myVehiclesDict[vID]['Max_Time'])


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