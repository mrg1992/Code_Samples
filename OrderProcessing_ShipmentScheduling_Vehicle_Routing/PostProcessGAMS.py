import csv
from InputData import InputData
from SolutionToExcel_Sorted import SolutionToExcel
from OzelModel import OzelModel
import os


dirPath = os.path.dirname(os.path.abspath(__file__))
finalOutputPath = dirPath + '\\SolutionPostProcessed'
inputPath = dirPath + '\\RawData'
solutionFileNameOzel = dirPath + '\\GAMS\\' + 'solutionOzel.csv'
solutionFileNameFTL = dirPath + '\\GAMS\\' + 'solutionFTL.csv'
solutionFileNamePartial = dirPath + '\\GAMS\\' + 'solutionPartial.csv'
routeFileName = inputPath + '\\' + 'rota_bilgileri.csv'
orderFileName = inputPath + '\\' + 'siparisler.csv'
routeVehicleFileName = inputPath + '\\' + 'rota_arac_uygunlugu.csv'
cityDistrictFileName = inputPath + '\\' + 'il_ilce_bilgileri.csv'
vehicleFileName = inputPath + '\\' + 'arac_kapasite.csv'
ozelCustomerFileName = inputPath + '\\' + 'ozel_shipto.csv'

inputObject = InputData(routeFileName, orderFileName, routeVehicleFileName, cityDistrictFileName, vehicleFileName, ozelCustomerFileName)

###############################################################
#Basic Structures
routeDict = inputObject._routeDict()
cityDistrictDict = inputObject._cityDistrictDict()
shipmentDict = inputObject._shipmentDict()
vehicleDict = inputObject._vehicleDict()
###############################################################


###############################################################
#Initial Ozel
ozelShipmentSet = inputObject._ozelShipmentSet(shipmentDict)
routeCoverDict = inputObject._routeCoverDict(shipmentDict, routeDict)
routeVehicleDict = inputObject._routeVehicleDict()
allowVehicleDict = inputObject._allowVehicleDict(shipmentDict, vehicleDict, cityDistrictDict)
routeVehicleCostDict = inputObject._routeVehicleCostDict(routeDict)
[ozelShipmentDict, shipmentDict] = inputObject._ozelShipmentSeparateDict(shipmentDict, ozelShipmentSet)

ozelObject = OzelModel(ozelShipmentDict, routeDict, routeCoverDict, routeVehicleDict, routeVehicleCostDict, allowVehicleDict, vehicleDict)

[ozelCustomerShipmentBinaryDict, ozelCustomerSet] = ozelObject._ozelCustomerShipmentBinaryDict()
ozelIsTCdict = ozelObject._isTCdict()
ozelShipmentSizeDict = inputObject._shipmentSizeDict(ozelShipmentDict)
ozelRouteCoverDict = inputObject._routeCoverDict(ozelShipmentDict, routeDict)
ozelAllowVehicleDict = inputObject._allowVehicleDict(ozelShipmentDict, vehicleDict, cityDistrictDict)

vehicleIsTCdict = ozelObject._vehicleIsTCdict()

###############################################################
#Sets:
customerSet = inputObject._customerSet(shipmentDict) #set of customers
shipmentSet = inputObject._shipmentSet(shipmentDict) #set of orders
vehicleTypeSet = ['KAMYONTC', 'KAMYONAMB', 'KAMYONETTC', 'KAMYONETAMB', 'TIRTC', 'TIRAMB'] # set of vehicle types
routeSet = inputObject._routeSet(routeDict) #set of routes
#ozelShipmentSet = inputObject._ozelShipmentSet(shipmentDict) #set of of ozelship
dimensionSet = ['volume', 'weight']
##############################################################


##############################################################
#Parameters:
routeCoverDict = inputObject._routeCoverDict(shipmentDict, routeDict) #if route r can cover order i
routeVehicleDict = inputObject._routeVehicleDict()                     # if vehicle type k can be used in road r 
vehicleCapacityDict = inputObject._vehicleCapacityDict(vehicleDict)    #capacity of each vehicle
shipmentSizeDict = inputObject._shipmentSizeDict(shipmentDict)              #shipment number
allowVehicleDict = inputObject._allowVehicleDict(shipmentDict, vehicleDict, cityDistrictDict) #if vehicle type k is allowed to be used in order i
partialCostDict = inputObject._partialCostDict(shipmentDict, cityDistrictDict)   #unit partial cost
shipmentCover = inputObject._shipmentCoverDict(shipmentDict, customerSet)  #if order i belongs to customer j 
vehicleAdditionalCost = inputObject._vehicleAdditionalCostDict(vehicleDict) #additional cost
checkOTdict = inputObject._checkOTdict(shipmentDict)             #if the cusomer is OT
leadTimeFTLdict = inputObject._leadTimeFTLdict(shipmentDict, cityDistrictDict) #leadtime of ftl
leadTimePartialDict = inputObject._leadTimePartialDict(shipmentDict, cityDistrictDict) #leadtime of partial
timeIntervalDict = inputObject._timeIntervalDict(shipmentDict)   #time (delivery-creating date+1)
routeVehicleCostDict = inputObject._routeVehicleCostDict(routeDict)  # cost pf vehicle type k in route r
routeDetailDict = inputObject._routeDetailDict(routeDict)
#####################################################################

    
keysOzel = []
with open(solutionFileNameOzel) as ozelCSV:
    ozelReader = csv.reader(ozelCSV, delimiter = ',')
    for row in ozelReader:
        keysOzel.append((row[0], row[1], row[2]))


keysFTL = []
with open(solutionFileNameFTL) as ftlCSV:
    ftlReader = csv.reader(ftlCSV, delimiter=',')
    for row in ftlReader:
        keysFTL.append((row[0], row[1], row[2]))

keysPartial = []
with open(solutionFileNamePartial) as partialCSV:
    partialReader = csv.reader(partialCSV, delimiter=',')
    for row in partialReader:
        keysPartial.append(row[0])



if not os.path.exists(finalOutputPath):
    os.makedirs(finalOutputPath)
solutionObject = SolutionToExcel(ozelShipmentDict, shipmentDict, keysOzel, keysFTL, keysPartial, routeDict, routeVehicleCostDict, partialCostDict, vehicleCapacityDict, vehicleAdditionalCost)
solutionObject._exportXLSX(finalOutputPath + '\\' + 'Raporlar.xlsx')

