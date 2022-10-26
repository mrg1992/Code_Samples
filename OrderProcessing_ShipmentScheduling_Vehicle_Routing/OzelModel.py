import csv
import copy
import numpy as np
from InputData import InputData


class OzelModel:
    def __init__(self, ozelShipmentDict, routeDict, routeCoverDict, routeVehicleDict, routeVehicleCostDict, allowVehicleDict, vehicleDict):
        self.ozelShipmentDict = ozelShipmentDict
        self.routeDict = routeDict
        self.routeCoverDict = routeCoverDict
        self.routeVehicleCostDict = routeVehicleCostDict
        self.allowVehicleDict = allowVehicleDict
        self.vehicleDict = vehicleDict
    
###############################

    def _ozelCustomerShipmentBinaryDict(self):
        ozelCustomerShipmentDict = {}
        ozelCustomerSet = []
        for shipmentNo in self.ozelShipmentDict:
            if self.ozelShipmentDict[shipmentNo][2] not in ozelCustomerShipmentDict:
                ozelCustomerSet.append(self.ozelShipmentDict[shipmentNo][2])
                ozelCustomerShipmentDict[self.ozelShipmentDict[shipmentNo][2]] = [shipmentNo]
            else:
                ozelCustomerShipmentDict[self.ozelShipmentDict[shipmentNo][2]].append(shipmentNo)
        ozelCustomerShipmentBinaryDict = {}
        for customerNo in ozelCustomerShipmentDict:
            for shipmentNo in self.ozelShipmentDict:
                if shipmentNo in ozelCustomerShipmentDict[customerNo]:
                    ozelCustomerShipmentBinaryDict[(customerNo, shipmentNo)] = 1
                else:
                    ozelCustomerShipmentBinaryDict[(customerNo, shipmentNo)] = 0
        return [ozelCustomerShipmentBinaryDict, ozelCustomerSet]
    
    def _isTCdict(self):
        isTCdict = {}
        for shipmentNo in self.ozelShipmentDict:
            if self.ozelShipmentDict[shipmentNo][6] == 'TC':
                isTCdict[shipmentNo] = 1
            else:
                isTCdict[shipmentNo] = 0
        return isTCdict
    
    def _vehicleIsTCdict(self):
        vehicleIsTCdict = {}
        for vehicleType in self.vehicleDict:
            if 'TC' in vehicleType:
                vehicleIsTCdict[vehicleType] = 1
            else:
                vehicleIsTCdict[vehicleType] = 0
        return vehicleIsTCdict