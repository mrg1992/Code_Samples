import csv
import copy
import numpy as np

class InputData:
    def __init__(self, routeFileName, shipmentFileName, routeVehicleFileName, cityDistrictFileName, vehicleFileName, ozelCustomerFileName):
        self.routeFileName = routeFileName
        self.shipmentFileName = shipmentFileName
        self.routeVehicleFileName = routeVehicleFileName
        self.cityDistrictFileName = cityDistrictFileName
        self.vehicleFileName = vehicleFileName
        self.ozelCustomerFileName = ozelCustomerFileName

    def _routeDict(self):
        routeDict = {}
        routes = []
        with open(self.routeFileName) as routeCSV:
            routeReader = csv.reader(routeCSV, delimiter=';')
            for row in routeReader:
                routes.append(row)
        for i in range(1, len(routes)):
            if routes[i][0] not in routeDict:
                routeDict[routes[i][0]] = [routes[i][1], routes[i][2], float(routes[i][3]), float(routes[i][4]), float(routes[i][5]), float(routes[i][6]), float(routes[i][7]), float(routes[i][8])]
        return routeDict
    
    def _vehicleDict(self):
        vehicleDict = {}
        vehicles = []
        with open(self.vehicleFileName) as vehicleCSV:
            vehicleReader = csv.reader(vehicleCSV, delimiter=';')
            for row in vehicleReader:
                vehicles.append(row)
        for i in range(1, len(vehicles)):
            vehicles[i][1] = vehicles[i][1].replace(',', '.')
            vehicles[i][2] = vehicles[i][2].replace(',', '.')
            vehicles[i][3] = vehicles[i][3].replace(',', '.')
            if vehicles[i][0] not in vehicleDict:
                vehicleDict[vehicles[i][0]] = [float(vehicles[i][1]), float(vehicles[i][2]), float(vehicles[i][3])]
                if 'TC' in vehicles[i][0]:
                    vehicleDict[vehicles[i][0]].append('TC')
                elif 'Amb' in vehicles[i][0]:
                    vehicleDict[vehicles[i][0]].append('AMBIENT')
        return vehicleDict
    
    def _routeVehicleDict(self):
        routeVehicleDict = {}
        routeVehicle = []
        with open(self.routeVehicleFileName) as routeVehicleCSV:
            routeVehicleReader = csv.reader(routeVehicleCSV, delimiter=';')
            for row in routeVehicleReader:
                routeVehicle.append(row)
        for i in range(1, len(routeVehicle)):
            if (routeVehicle[i][0], routeVehicle[0][1].upper()) not in routeVehicleDict:
                for j in range(1, len(routeVehicle[i])):
                    routeVehicleDict[(routeVehicle[i][0], routeVehicle[0][j].upper())] = int(routeVehicle[i][j])          
        return routeVehicleDict
    
    def _shipmentDict(self):
        shipmentDict = {}
        shipment = []
        with open(self.shipmentFileName) as shipmentCSV:
            shipmentReader = csv.reader(shipmentCSV, delimiter=';')
            for row in shipmentReader:
                shipment.append(row)
        for i in range(1, len(shipment)):
            
            shipment[i][11] = shipment[i][11].replace('.', '')
            
            shipment[i][10] = shipment[i][10].replace(',', '.')
            shipment[i][11] = shipment[i][11].replace(',', '.')
            if shipment[i][2] not in shipmentDict:
                if shipment[i][5] == 'GEBZE':
                    shipment[i][5] = 'KOCAELİ'
                shipmentDict[shipment[i][2]] = [shipment[i][0], shipment[i][1], shipment[i][3], shipment[i][4], shipment[i][5], shipment[i][6], shipment[i][7], [shipment[i][8]], [shipment[i][9]], float(shipment[i][10]), float(shipment[i][11]), shipment[i][12], shipment[i][13], shipment[i][14]]
            elif shipment[i][2] in shipmentDict:
                shipmentDict[shipment[i][2]][9] = shipmentDict[shipment[i][2]][9] + float(shipment[i][10])
                shipmentDict[shipment[i][2]][10] = shipmentDict[shipment[i][2]][10] + float(shipment[i][11])
                shipmentDict[shipment[i][2]][7].append(shipment[i][8])
                shipmentDict[shipment[i][2]][8].append(shipment[i][9])
        return shipmentDict
    
    def _cityDistrictDict(self):
        cityDistrictDict = {}
        cityDistricts = []
        with open(self.cityDistrictFileName) as cityDistrictCSV:
            cityDistrictReader = csv.reader(cityDistrictCSV, delimiter=';')
            for row in cityDistrictReader:
                cityDistricts.append(row)
        for i in range(1, len(cityDistricts)):
            cityDistricts[i][4] = cityDistricts[i][4].replace(',', '.')
            cityDistricts[i][5] = cityDistricts[i][5].replace(',', '.')
            if cityDistricts[i][1] not in cityDistrictDict:
                
                cityDistrictDict[cityDistricts[i][1]] = [int(cityDistricts[i][2]), int(cityDistricts[i][3]), float(cityDistricts[i][4]), float(cityDistricts[i][5]), cityDistricts[i][6], cityDistricts[i][7], int(cityDistricts[i][8]), int(cityDistricts[i][9]), int(cityDistricts[i][10])]
        return cityDistrictDict
    
    ###########################################################
    ###########################################################
    
    def _customerSet(self, shipmentDict):
        customerSet = []
        for key in shipmentDict:
            if shipmentDict[key][2] not in customerSet:
                customerSet.append(shipmentDict[key][2])
        return customerSet
    
    def _shipmentSet(self, shipmentDict):
        shipmentSet = []
        for key in shipmentDict:
            shipmentSet.append(key)
        return shipmentSet
    
    def _routeSet(self, routeDict):
        routeSet = []
        for key in routeDict:
            routeSet.append(key)
        return routeSet
    
    def _ozelShipmentSet(self, shipmentDict):
        ozelCustomerSet = []
        ozelShipmentSet = []
        with open(self.ozelCustomerFileName, encoding="ANSI") as ozelCSV:
            ozelReader = csv.reader(ozelCSV, delimiter=';')
            for row in ozelReader:
                if 'shipto' not in row[0]:
                    ozelCustomerSet.append(row[0])
        for shipmentNo in shipmentDict:
            if shipmentDict[shipmentNo][2] in ozelCustomerSet:
                ozelShipmentSet.append(shipmentNo)
        return ozelShipmentSet
    
    ##########################################################
    ##########################################################
    
    def _ozelShipmentSeparateDict(self, shipmentDict, ozelShipmentSet):
        ozelShipmentDict = {}
        newShipmentDict = copy.deepcopy(shipmentDict)
        for shipmentNo in shipmentDict:
            if shipmentNo in ozelShipmentSet:
                ozelShipmentDict[shipmentNo] = shipmentDict[shipmentNo]
                del(newShipmentDict[shipmentNo])
        return [ozelShipmentDict, newShipmentDict]
    
    def _routeCoverDict(self, shipmentDict, routeDict):
        routeCoverDict = {}
        for shipmentNo in shipmentDict:
            for routeID in routeDict:
                tempKey = (shipmentNo, routeID)
                if shipmentDict[shipmentNo][4] in routeDict[routeID][0]:
                    routeCoverDict[tempKey] = 1
                elif shipmentDict[shipmentNo][4] not in routeDict[routeID][0]:
                    routeCoverDict[tempKey] = 0
        return routeCoverDict
        
    def _vehicleCapacityDict(self, vehicleDict):
        vehicleCapacityDict = {}
        for key in vehicleDict:
            vehicleCapacityDict[(key, 'volume')] = vehicleDict[key][0]
            vehicleCapacityDict[(key, 'weight')] = vehicleDict[key][1]
        return vehicleCapacityDict
    
    def _shipmentSizeDict(self, shipmentDict):
        shipmentSizeDict = {}
        for key in shipmentDict:
            shipmentSizeDict[(key, 'volume')] = shipmentDict[key][9]
            shipmentSizeDict[(key, 'weight')] = shipmentDict[key][10]
        return shipmentSizeDict
    
    def _allowVehicleDict(self, shipmentDict, vehicleDict, cityDistrictDict):
        allowVehicleDict = {}
        for shipmentNo in shipmentDict:
            if shipmentDict[shipmentNo][6] == 'TC':
                flag = 0
            elif shipmentDict[shipmentNo][6] != 'TC':
                flag = 1
            tempKey = shipmentDict[shipmentNo][4]
            #print([tempKey, shipmentNo])
            #if tempKey not in cityDistrictDict:
            #    tempKey = (shipmentDict[shipmentNo][4], shipmentDict[shipmentNo][4])
            allowVehicleDict[(shipmentNo, 'KAMYONTC')] = cityDistrictDict[tempKey][6]
            allowVehicleDict[(shipmentNo, 'KAMYONAMB')] = flag * cityDistrictDict[tempKey][6]
            
            allowVehicleDict[(shipmentNo, 'TIRTC')] = cityDistrictDict[tempKey][7]
            allowVehicleDict[(shipmentNo, 'TIRAMB')] = flag * cityDistrictDict[tempKey][7]
            
            allowVehicleDict[(shipmentNo, 'KAMYONETTC')] = cityDistrictDict[tempKey][8]
            allowVehicleDict[(shipmentNo, 'KAMYONETAMB')] = flag * cityDistrictDict[tempKey][8]
        return allowVehicleDict
    
    def _partialCostDict(self, shipmentDict, cityDistrictDict):
        partialCostDict = {}
        for shipmentNo in shipmentDict:
            if shipmentDict[shipmentNo][6] == 'TC':
                isTC = 1
                isAmb = 0
            elif shipmentDict[shipmentNo][6] == 'AMBIENT':
                isTC = 0
                isAmb = 1
            partialCostDict[shipmentNo] = isAmb * cityDistrictDict[shipmentDict[shipmentNo][4]][2] + isTC * cityDistrictDict[shipmentDict[shipmentNo][4]][3]
        return partialCostDict
    
    def _shipmentCoverDict(self, shipmentDict, customerSet):
        shipmentCoverDict = {}
        for shipmentNo in shipmentDict:
            for customerNo in customerSet:
                tempKey = (shipmentNo, customerNo)
                if shipmentDict[shipmentNo][2] == customerNo:
                    shipmentCoverDict[tempKey] = 1
                else:
                    shipmentCoverDict[tempKey] = 0
        return shipmentCoverDict
    
    def _vehicleAdditionalCostDict(self, vehicleDict):
        vehicleAdditionalCostDict = {}
        for key in vehicleDict:
            vehicleAdditionalCostDict[key] = vehicleDict[key][2]
        return vehicleAdditionalCostDict
    
    def _checkOTdict(self, shipmentDict):
        checkOTdict = {}
        for shipmentNo in shipmentDict:
            if shipmentDict[shipmentNo][2] not in checkOTdict:
                if shipmentDict[shipmentNo][11] == 'OT':
                    checkOTdict[shipmentDict[shipmentNo][2]] = 1
                elif shipmentDict[shipmentNo][11] != 'OT':
                    checkOTdict[shipmentDict[shipmentNo][2]] = 0
        return checkOTdict
    
    def _leadTimeFTLdict(self, shipmentDict, cityDistrictDict):
        leadTimeFTLdict = {}
        for shipmentNo in shipmentDict:
            leadTimeFTLdict[shipmentNo] = cityDistrictDict[shipmentDict[shipmentNo][4]][0]
        return leadTimeFTLdict
    
    def _leadTimePartialDict(self, shipmentDict, cityDistrictDict):
        leadTimePartialDict = {}
        for shipmentNo in shipmentDict:
            leadTimePartialDict[shipmentNo] = cityDistrictDict[shipmentDict[shipmentNo][4]][1]
        return leadTimePartialDict
    
    def _timeIntervalDict(self, shipmentDict):
        timeIntervalDict = {}
        for key in shipmentDict:
            strDeliveryDate = shipmentDict[key][1]
            strOrderDate = shipmentDict[key][0]
            timeIntervalDict[key] = int(strDeliveryDate[0:2]) + 30 * int(strDeliveryDate[3:5]) + 365 * int(strDeliveryDate[6:10]) - (int(strOrderDate[0:2]) + 30 * int(strOrderDate[3:5]) + 365 * int(strOrderDate[6:10]))
        return timeIntervalDict
    
    def _routeVehicleCostDict(self, routeDict):
        routeVehicleCostDict = {}
        for key in routeDict:
            routeVehicleCostDict[(key, 'KAMYONAMB')] = routeDict[key][2]
            routeVehicleCostDict[(key, 'TIRAMB')] = routeDict[key][3]
            routeVehicleCostDict[(key, 'KAMYONETAMB')] = routeDict[key][4]
            routeVehicleCostDict[(key, 'KAMYONTC')] = routeDict[key][5]
            routeVehicleCostDict[(key, 'TIRTC')] = routeDict[key][6]
            routeVehicleCostDict[(key, 'KAMYONETTC')] = routeDict[key][7]
        return routeVehicleCostDict
              
    def _ozelRouteVehicleAssignDict(self, ozelShipmentDict, routeDict, routeCoverDict, routeVehicleDict, routeVehicleCostDict, allowVehicleDict, vehicleDict):
        ozelRouteVehicleAssignDict = {}
        ozelCustomerShipmentDict = {}
        ozelCustomerDetailDict = {}
        for shipmentNo in ozelShipmentDict:
            if ozelShipmentDict[shipmentNo][2] not in ozelCustomerShipmentDict:
               ozelCustomerShipmentDict[ozelShipmentDict[shipmentNo][2]] = [shipmentNo]
            else:
                ozelCustomerShipmentDict[ozelShipmentDict[shipmentNo][2]].append(shipmentNo)
        for customerID in ozelCustomerShipmentDict:
            totalCustomerWeight = 0
            isTC = 0
            tempShipments = []
            for shipmentNo in ozelCustomerShipmentDict[customerID]:
                totalCustomerWeight = totalCustomerWeight + ozelShipmentDict[shipmentNo][10]
                isTC = isTC + int(ozelShipmentDict[shipmentNo][6] == 'TC')
                tempShipments.append(shipmentNo)
            ozelCustomerDetailDict[customerID] = [tempShipments, totalCustomerWeight, int(isTC > 0)]
        #for customerID in ozelCustomerDetailDict:
        #    if ozelCustomerDetailDict[customerID][1] > vehicleDict['TIRTC']
        
        
        
        for customerID in ozelCustomerDetailDict:
            tempPossibleVehicleTypes = []
            if ozelCustomerDetailDict[customerID][2] == 1:
                for vehicleType in vehicleDict:
                    if 'TC' in vehicleType and vehicleDict[vehicleType][1] >= ozelCustomerDetailDict[customerID][1]:
                        tempPossibleVehicleTypes.append(vehicleType)       
            else:
                for vehicleType in vehicleDict:
                    if 'AMB' in vehicleType and vehicleDict[vehicleType][1] >= ozelCustomerDetailDict[customerID][1]:
                        tempPossibleVehicleTypes.append(vehicleType)
            ozelCustomerDetailDict[customerID].append(tempPossibleVehicleTypes)
        
        for customerID in ozelCustomerDetailDict:
            tempPossibleRouteVehicles = []
            for vehicleType in ozelCustomerDetailDict[customerID][3]:
                for routeID in routeDict:
                    if routeVehicleDict[(routeID, vehicleType)] * allowVehicleDict[(ozelCustomerDetailDict[customerID][0][0], vehicleType)] == 1:
                        tempPossibleRouteVehicles.append((routeID, vehicleType))
            costs = []
            for i in range(len(tempPossibleRouteVehicles)):
                costs.append(routeVehicleCostDict[tempPossibleRouteVehicles[i]])
            index = np.argmin(costs)
            tempRouteVehicle = tempPossibleRouteVehicles[index]            
            ozelCustomerDetailDict[customerID].append(tempRouteVehicle)
        for customerID in ozelCustomerDetailDict:
            for shipmentNo in ozelCustomerDetailDict[customerID][0]:
                ozelRouteVehicleAssignDict[shipmentNo] = [ozelCustomerDetailDict[customerID][4][0], ozelCustomerDetailDict[customerID][4][1]]
        return [ozelRouteVehicleAssignDict, ozelCustomerDetailDict]
                    
    def _routeDetailDict(self, routeDict):
        routeDetailDict = {}
        for routeID in routeDict:
            if 'STANBUL' in routeDict[routeID][0]:
                routeDetailDict[routeID] = 1
            else:
                routeDetailDict[routeID] = 0
        return routeDetailDict