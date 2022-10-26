import csv
import numpy as np


class InputClass:
    def __init__(self, eMachineFileName, branchFileName, corporateFileName, cmcFileName, vehiclesFileName, vehicleTypeFileName, orderFileName, serviceFileName):
        self.eMachineFileName = eMachineFileName
        self.branchFileName = branchFileName
        self.corporateFileName = corporateFileName
        self.cmcFileName = cmcFileName
        self.vehiclesFileName = vehiclesFileName
        self.vehicleTypeFileName = vehicleTypeFileName
        self.orderFileName = orderFileName
        self.serviceFileName = serviceFileName
    
    def _decimalCut(self, strNum, N = 4):
        newStrNum = ''
        afterDecimal = 0
        decimalFlag = 0
        for char in strNum:
            if char == '.':
                decimalFlag = 1
                newStrNum = newStrNum + char
            if decimalFlag == 0:
                newStrNum = newStrNum + char
            elif decimalFlag == 1 and char != '.':
                afterDecimal = afterDecimal + 1
                if afterDecimal < N + 1:
                    newStrNum = newStrNum + char
                elif afterDecimal > N:
                    break
        return newStrNum
                            
    def secondsToClock(self, seconds):
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
    
    
    def _eMachineDict(self):
        eMachineDict = {}
        with open(self.eMachineFileName) as eMachineCSV:
            eMachineReader = csv.reader(eMachineCSV, delimiter = ';')
            next(eMachineReader, None)
            for row in eMachineReader:
                #print(row)
                eMachineID = str(row[1])
                eMachineDict[eMachineID] = {}
                eMachineDict[eMachineID]['Type'] = str(row[0])  #'E-Machine'#str(row[3])
                eMachineDict[eMachineID]['Brand'] = str(row[2])
                eMachineDict[eMachineID]['Model'] = 'E-Machine'
                eMachineDict[eMachineID]['CMC_ID'] = str(row[4])
                eMachineDict[eMachineID]['Latitude'] = self._decimalCut(str(row[5]))
                eMachineDict[eMachineID]['Longitude'] = self._decimalCut(str(row[6]))
                eMachineDict[eMachineID]['Shift'] = str(row[7])
                eMachineDict[eMachineID]['Start_Time'] = str(row[8])
                eMachineDict[eMachineID]['End_Time'] = str(row[9])
                eMachineDict[eMachineID]['Visit_Frequency_pw'] = int(row[10])
                eMachineDict[eMachineID]['Weekly_Visitability'] = [int(row[11]), int(row[12]), int(row[13]), int(row[14]), int(row[15]), int(row[16]), int(row[17])]
                eMachineDict[eMachineID]['Cost_Failure_pm'] = float(row[18])
                eMachineDict[eMachineID]['Frequency_Failure_pw'] = float(row[19])
                eMachineDict[eMachineID]['Hard_Window'] = int(row[20])
        return eMachineDict
    
    def _branchesDict(self):
        branchDict = {}
        with open(self.branchFileName) as branchCSV:
            branchReader = csv.reader(branchCSV, delimiter = ';')
            next(branchReader, None)
            for row in branchReader:
                branchID = str(row[0])
                branchDict[branchID] = {}
                #branchDict[branchID]['Branch_Name'] = str(row[1])
                branchDict[branchID]['Model'] = 'Branch'
                branchDict[branchID]['Type'] = str(row[2]) #'Branch'
                branchDict[branchID]['CMC_ID'] = str(row[3])
                branchDict[branchID]['Latitude'] = self._decimalCut(str(row[4]))
                branchDict[branchID]['Longitude'] = self._decimalCut(str(row[5]))
                branchDict[branchID]['Shift'] = str(row[6])
                branchDict[branchID]['Start_Time'] = str(row[7])
                branchDict[branchID]['End_Time'] = str(row[8])
                branchDict[branchID]['Visit_Frequency_pw'] = int(row[9])
                branchDict[branchID]['Weekly_Visitability'] = [int(row[10]), int(row[11]), int(row[12]), int(row[13]), int(row[14]), int(row[15]), int(row[16])]
                branchDict[branchID]['Cost_NotVisiting'] = float(row[17])
                branchDict[branchID]['Hard_Window'] = int(row[18])
        return branchDict
    
    def _corporateDict(self):
        corporateDict = {}
        with open(self.corporateFileName) as corporateCSV:
            corporateReader = csv.reader(corporateCSV, delimiter = ';')
            next(corporateReader, None)
            for row in corporateReader:
                clientID = str(row[0])
                corporateDict[clientID] = {}
                #corporateDict[clientID]['Client_Name'] = str(row[1])
                corporateDict[clientID]['Type'] = str(row[2])
                corporateDict[clientID]['Model'] = 'Corporate Customer'
                corporateDict[clientID]['CMC_ID'] = str(row[3])
                corporateDict[clientID]['Shift'] = str(row[4])
                corporateDict[clientID]['Latitude'] = self._decimalCut(str(row[5]))
                corporateDict[clientID]['Longitude'] = self._decimalCut(str(row[6]))
                corporateDict[clientID]['Start_Time'] = str(row[7])
                corporateDict[clientID]['End_Time'] = str(row[8])
                corporateDict[clientID]['Visit_Frequency_pw'] = int(row[9])
                corporateDict[clientID]['Weekly_Visitability'] = [int(row[10]), int(row[11]), int(row[12]), int(row[13]), int(row[14]), int(row[15]), int(row[16])]
                corporateDict[clientID]['Hard_Window'] = int(row[17])
        return corporateDict
    
    def _CMCDict(self):
        CMCDict = {}
        with open(self.cmcFileName) as cmcCSV:
            cmcReader = csv.reader(cmcCSV, delimiter = ';')
            next(cmcReader, None)
            for row in cmcReader:
                cmcID = str(row[0])
                CMCDict[cmcID] = {}
                CMCDict[cmcID]['CMC_Name'] = str(row[1])
                CMCDict[cmcID]['Type'] = 'CMC'
                CMCDict[cmcID]['Model'] = 'CMC'
                CMCDict[cmcID]['Latitude'] = self._decimalCut(str(row[2]))
                CMCDict[cmcID]['Longitude'] = self._decimalCut(str(row[3]))
                CMCDict[cmcID]['Simultanious_Loading_Capacity'] = int(row[4])
                CMCDict[cmcID]['Simultanious_Loading_Duration_m'] = float(row[5])
        return CMCDict
    
    def _vehiclesDict(self):
        vehicleDict = {}
        with open(self.vehiclesFileName) as vehiclesCSV:
            vehiclesReader = csv.reader(vehiclesCSV, delimiter = ';')
            next(vehiclesReader, None)
            for row in vehiclesReader:
                vehicleID = str(row[0])
                vehicleDict[vehicleID] = {}
                vehicleDict[vehicleID]['Vehicle_Type_ID'] = str(row[1])
                vehicleDict[vehicleID]['Location_Type'] = str(row[2])
                vehicleDict[vehicleID]['CMC_ID'] = str(row[3])
                #vehicleDict[vehicleID]['Shift'] = str(row[4])
                vehicleDict[vehicleID]['Start_Time'] = str(row[4])
                vehicleDict[vehicleID]['End_Time'] = str(row[5])
                vehicleDict[vehicleID]['Max_Time'] = str(row[6])
                vehicleDict[vehicleID]['Rest_Time_m'] = float(row[7])
                vehicleDict[vehicleID]['Max_Allowed_Keys'] = int(row[8])
                vehicleDict[vehicleID]['Total_Rent'] = float(row[9])
                vehicleDict[vehicleID]['Cost_Fuel_pkm'] = float(row[10])
                vehicleDict[vehicleID]['Cost_RunningTime'] = float(row[11])
                vehicleDict[vehicleID]['Cost_Overtime_WD_ph'] = float(row[12])
                vehicleDict[vehicleID]['Cost_Overtime_WE_ph'] = float(row[13])
                vehicleDict[vehicleID]['Time_at_CMC_bl_m'] = float(row[14])
                vehicleDict[vehicleID]['Time_at_CMC_aa_m'] = float(row[15])
        return vehicleDict
    
    def _vehicleTypeDict(self):
        vehicleTypeDict = {}
        with open(self.vehicleTypeFileName) as vehicleTypeCSV:
            vehicleTypeReader = csv.reader(vehicleTypeCSV, delimiter = ';')
            next(vehicleTypeReader, None)
            for row in vehicleTypeReader:
                vehicleTypeID = str(row[0])
                vehicleTypeDict[vehicleTypeID] = {}
                vehicleTypeDict[vehicleTypeID]['Type_Name'] = str(row[1])
                vehicleTypeDict[vehicleTypeID]['Capacity_unit'] = float(row[2])
                vehicleTypeDict[vehicleTypeID]['Insurance_Limit'] = float(row[3])
        return vehicleTypeDict
    
    def _serviceTypeDict(self):
        serviceTypeDict = {}
        with open(self.serviceFileName) as serviceTypeCSV:
            serviceTypeReader = csv.reader(serviceTypeCSV, delimiter = ';')
            next(serviceTypeReader, None)
            for row in serviceTypeReader:
                locType = str(row[0])
                serviceType = str(row[1])
                shift = str(row[2])
                serviceTypeDict[(locType, serviceType, shift)] = float(row[3])
        return serviceTypeDict
    
    
    def _scheduleDict(self):
        scheduleDict = {}
        orderKeysList = []
        adhocDict = {}
        #weekDayList = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        with open(self.orderFileName) as scheduleCSV:
            scheduleReader = csv.reader(scheduleCSV, delimiter = ';')
            next(scheduleReader, None)
            for row in scheduleReader:
                #uniqueRows
                if int(row[5]) == 1:
                    #if int(row[12]) == 0: 
                    orderDate = str(row[0])[0:10]
                    orderShift = str(row[11])
                    #orderWeekDay = weekDayList[calendar.weekday(int(orderDate[0:4]), int(orderDate[5:7]), int(orderDate[8:10]))]
                    orderKey1 = (orderDate, orderShift)
                    if orderKey1 not in scheduleDict:
                        adhocDict[orderKey1] = {}
                        orderKeysList.append(orderKey1)
                        scheduleDict[orderKey1] = {}
                        orderLocationID = str(row[3])                                
                        scheduleDict[orderKey1][orderLocationID] = [[]]
                        #[0: LocationType, 1:ServiceType, 2:Planned, 3:DeliverySize, 4:PickUpSize, 5:DeliveryAmount, 6:PickUpAmount, 7:VisitBeforeDate, 8:VisitBeforeTime]
                        scheduleDict[orderKey1][orderLocationID][0].append(str(row[2]))
                        scheduleDict[orderKey1][orderLocationID][0].append(str(row[4]))
                        scheduleDict[orderKey1][orderLocationID][0].append(int(row[5]))
                        scheduleDict[orderKey1][orderLocationID][0].append(float(row[6]))
                        scheduleDict[orderKey1][orderLocationID][0].append(float(row[7]))
                        scheduleDict[orderKey1][orderLocationID][0].append(float(row[8]))
                        scheduleDict[orderKey1][orderLocationID][0].append(float(row[9]))
                        scheduleDict[orderKey1][orderLocationID][0].append(str(row[10])[0:10])
                        scheduleDict[orderKey1][orderLocationID][0].append(str(row[10])[11:19])
                        scheduleDict[orderKey1][orderLocationID][0].append(int(row[12]))
                        scheduleDict[orderKey1][orderLocationID][0].append(str(row[13]))
                        scheduleDict[orderKey1][orderLocationID][0].append(str(row[1])[11:19])
                    else:
                        orderLocationID = str(row[3])
                        if orderLocationID not in scheduleDict[orderKey1]:
                            scheduleDict[orderKey1][orderLocationID] = [[]]
                            #[0: LocationType, 1:ServiceType, 2:Planned, 3:DeliverySize, 4:PickUpSize, 5:DeliveryAmount, 6:PickUpAmount, 7:VisitBeforeDate, 8:VisitBeforeTime]
                            scheduleDict[orderKey1][orderLocationID][0].append(str(row[2]))
                            scheduleDict[orderKey1][orderLocationID][0].append(str(row[4]))
                            scheduleDict[orderKey1][orderLocationID][0].append(int(row[5]))
                            scheduleDict[orderKey1][orderLocationID][0].append(float(row[6]))
                            scheduleDict[orderKey1][orderLocationID][0].append(float(row[7]))
                            scheduleDict[orderKey1][orderLocationID][0].append(float(row[8]))
                            scheduleDict[orderKey1][orderLocationID][0].append(float(row[9]))
                            scheduleDict[orderKey1][orderLocationID][0].append(str(row[10])[0:10])
                            scheduleDict[orderKey1][orderLocationID][0].append(str(row[10])[11:19])
                            scheduleDict[orderKey1][orderLocationID][0].append(int(row[12]))
                            scheduleDict[orderKey1][orderLocationID][0].append(str(row[13]))
                            scheduleDict[orderKey1][orderLocationID][0].append(str(row[1])[11:19])
                        else:
                            tempList = [str(row[2]), str(row[4]), int(row[5]), float(row[6]), float(row[7]), float(row[8]), float(row[9]), str(row[10])[0:10], str(row[10])[11:19], int(row[12]), str(row[13]), str(row[1])[11:19]]
                            scheduleDict[orderKey1][orderLocationID].append(tempList)
                else:
                    #if int(row[12]) == 0: 
                    orderDate = str(row[0])[0:10]
                    orderShift = str(row[11])
                    #orderWeekDay = weekDayList[calendar.weekday(int(orderDate[0:4]), int(orderDate[5:7]), int(orderDate[8:10]))]
                    orderKey1 = (orderDate, orderShift)
                    if orderKey1 not in adhocDict:
                        #orderKeysList.append(orderKey1)
                        orderLocationID = str(row[3])                                
                        adhocDict[orderKey1][orderLocationID] = [[]]
                        #[0: LocationType, 1:ServiceType, 2:Planned, 3:DeliverySize, 4:PickUpSize, 5:DeliveryAmount, 6:PickUpAmount, 7:VisitBeforeDate, 8:VisitBeforeTime]
                        adhocDict[orderKey1][orderLocationID][0].append(str(row[2]))
                        adhocDict[orderKey1][orderLocationID][0].append(str(row[4]))
                        adhocDict[orderKey1][orderLocationID][0].append(int(row[5]))
                        adhocDict[orderKey1][orderLocationID][0].append(float(row[6]))
                        adhocDict[orderKey1][orderLocationID][0].append(float(row[7]))
                        adhocDict[orderKey1][orderLocationID][0].append(float(row[8]))
                        adhocDict[orderKey1][orderLocationID][0].append(float(row[9]))
                        adhocDict[orderKey1][orderLocationID][0].append(str(row[10])[0:10])
                        adhocDict[orderKey1][orderLocationID][0].append(str(row[10])[11:19])
                        adhocDict[orderKey1][orderLocationID][0].append(int(row[12]))
                        adhocDict[orderKey1][orderLocationID][0].append(str(row[13]))
                        adhocDict[orderKey1][orderLocationID][0].append(str(row[1])[11:19])
                    else:
                        orderLocationID = str(row[3])
                        if orderLocationID not in adhocDict[orderKey1]:
                            adhocDict[orderKey1][orderLocationID] = [[]]
                            #[0: LocationType, 1:ServiceType, 2:Planned, 3:DeliverySize, 4:PickUpSize, 5:DeliveryAmount, 6:PickUpAmount, 7:VisitBeforeDate, 8:VisitBeforeTime]
                            adhocDict[orderKey1][orderLocationID][0].append(str(row[2]))
                            adhocDict[orderKey1][orderLocationID][0].append(str(row[4]))
                            adhocDict[orderKey1][orderLocationID][0].append(int(row[5]))
                            adhocDict[orderKey1][orderLocationID][0].append(float(row[6]))
                            adhocDict[orderKey1][orderLocationID][0].append(float(row[7]))
                            adhocDict[orderKey1][orderLocationID][0].append(float(row[8]))
                            adhocDict[orderKey1][orderLocationID][0].append(float(row[9]))
                            adhocDict[orderKey1][orderLocationID][0].append(str(row[10])[0:10])
                            adhocDict[orderKey1][orderLocationID][0].append(str(row[10])[11:19])
                            adhocDict[orderKey1][orderLocationID][0].append(int(row[12]))
                            adhocDict[orderKey1][orderLocationID][0].append(str(row[13]))
                            adhocDict[orderKey1][orderLocationID][0].append(str(row[1])[11:19])
                        else:
                            tempList = [str(row[2]), str(row[4]), int(row[5]), float(row[6]), float(row[7]), float(row[8]), float(row[9]), str(row[10])[0:10], str(row[10])[11:19], int(row[12]), str(row[13]), str(row[1])[11:19]]
                            adhocDict[orderKey1][orderLocationID].append(tempList)
                    
        return [scheduleDict, adhocDict, orderKeysList]

            
            

