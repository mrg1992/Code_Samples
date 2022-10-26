from __future__ import division
import xlsxwriter
from InputData import InputData
import os
import pandas as pd
from OzelModel import OzelModel


dirPath = os.path.dirname(os.path.abspath(__file__))
outputPathExcel = dirPath + '\\SetsAndParamsExcel'
outputPathCSV = dirPath + '\\GAMS'
inputPath = dirPath + '\\RawData'
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

#[ozelRouteVehicleAssignDict, ozelCustomerDetailDict] = inputObject._ozelRouteVehicleAssignDict(ozelShipmentDict, routeDict, routeCoverDict, routeVehicleDict, routeVehicleCostDict, allowVehicleDict, vehicleDict)

###############################################################
#Sets:
customerSet = inputObject._customerSet(shipmentDict) #set of customers
shipmentSet = inputObject._shipmentSet(shipmentDict) #set of orders
vehicleTypeSet = ['KAMYONAMB', 'KAMYONETAMB', 'TIRAMB', 'KAMYONTC', 'KAMYONETTC', 'TIRTC'] # set of vehicle types
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

if not os.path.exists(outputPathExcel):
    os.makedirs(outputPathExcel)
    

#ozelShipmentSet:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'ozelShipmentSet.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
#worksheet.write(0, 0, 'ShipmentNo', cell_format)
for i in range(len(ozelShipmentSet)):
    worksheet.write(i, 0, ozelShipmentSet[i], cell_format)
workbook.close()

#ozelCustomerSet:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'ozelCustomerSet.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
#worksheet.write(0, 0, 'CustomerID', cell_format)
for i in range(len(ozelCustomerSet)):
    worksheet.write(i, 0, ozelCustomerSet[i], cell_format)
workbook.close()

#ozelCustomerShipmentBinaryDict:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'ozelCustomerShipmentBinaryDict.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
worksheet.write(0, 0, 'CustomerNo', cell_format)
x = []
y = []
for key in ozelCustomerShipmentBinaryDict:
    if key[0] not in x:
        x.append(key[0])
    if key[1] not in y:
        y.append(key[1])
for i in range(len(x)):
    worksheet.write(i + 1, 0, x[i], cell_format)
    for j in range(len(y)):
        worksheet.write(0, j + 1, y[j], cell_format)
        worksheet.write(i + 1, j + 1, ozelCustomerShipmentBinaryDict[(x[i], y[j])], cell_format)
workbook.close()


#ozelRouteCoverDict:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'ozelRouteCoverDict.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
worksheet.write(0, 0, 'ShipmentNo', cell_format)
x = []
y = []
for key in ozelRouteCoverDict:
    if key[0] not in x:
        x.append(key[0])
    if key[1] not in y:
        y.append(key[1])
for i in range(len(x)):
    worksheet.write(i + 1, 0, x[i], cell_format)
    for j in range(len(y)):
        worksheet.write(0, j + 1, y[j], cell_format)
        worksheet.write(i + 1, j + 1, ozelRouteCoverDict[(x[i], y[j])], cell_format)
workbook.close()

#ozelAllowVehicleDict:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'ozelAllowVehicleDict.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
worksheet.write(0, 0, 'ShipmentNo', cell_format)
x = []
y = []
for key in ozelAllowVehicleDict:
    if key[0] not in x:
        x.append(key[0])
    if key[1] not in y:
        y.append(key[1])
for i in range(len(x)):
    worksheet.write(i + 1, 0, x[i], cell_format)
    for j in range(len(y)):
        worksheet.write(0, j + 1, y[j], cell_format)
        worksheet.write(i + 1, j + 1, ozelAllowVehicleDict[(x[i], y[j])], cell_format)
workbook.close()

#ozelShipmentSizeDict:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'ozelShipmentSizeDict.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
worksheet.write(0, 0, 'ShipmentNo', cell_format)
x = []
y = []
for key in ozelShipmentSizeDict:
    if key[0] not in x:
        x.append(key[0])
    if key[1] not in y:
        y.append(key[1])
for i in range(len(x)):
    worksheet.write(i + 1, 0, x[i], cell_format)
    for j in range(len(y)):
        worksheet.write(0, j + 1, y[j], cell_format)
        worksheet.write(i + 1, j + 1, ozelShipmentSizeDict[(x[i], y[j])], cell_format)
workbook.close()

#vehicleIsTCdict:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'vehicleIsTCdict.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
#worksheet.write(0, 0, 'ShipmentNo', cell_format)
#worksheet.write(0, 1, 'PartialCost', cell_format)
j = 0
for key in vehicleIsTCdict:
    worksheet.write(j, 0, key, cell_format)
    worksheet.write(j, 1, vehicleIsTCdict[key], cell_format)
    j = j + 1
workbook.close()

#ozelIsTCdict:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'ozelIsTCdict.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
#worksheet.write(0, 0, 'ShipmentNo', cell_format)
#worksheet.write(0, 1, 'PartialCost', cell_format)
j = 0
for key in ozelIsTCdict:
    worksheet.write(j, 0, key, cell_format)
    worksheet.write(j, 1, ozelIsTCdict[key], cell_format)
    j = j + 1
workbook.close()



#customerSet:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'customerSet.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
#worksheet.write(0, 0, 'CustomerID', cell_format)
for i in range(len(customerSet)):
    worksheet.write(i, 0, customerSet[i], cell_format)
workbook.close()

#shipmentSet:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'shipmentSet.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
#worksheet.write(0, 0, 'ShipmentNo', cell_format)
for i in range(len(shipmentSet)):
    worksheet.write(i, 0, shipmentSet[i], cell_format)
workbook.close()

#vehicleTypeSet:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'vehicleTypeSet.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
#worksheet.write(0, 0, 'VehicleType', cell_format)
for i in range(len(vehicleTypeSet)):
    worksheet.write(i,0, vehicleTypeSet[i], cell_format)
workbook.close()

#routeSet:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'routeSet.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
#worksheet.write(0, 0, 'RouteID', cell_format)
for i in range(len(routeSet)):
    worksheet.write(i,0, routeSet[i], cell_format)
workbook.close()


#dimentionSet:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'dimensionSet.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
#worksheet.write(0, 0, 'Dimentions', cell_format)
for i in range(len(dimensionSet)):
    worksheet.write(i,0, dimensionSet[i], cell_format)
workbook.close()

##############################################################
    
#routeCoverDict:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'routeCoverDict.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
worksheet.write(0, 0, 'ShipmentNo', cell_format)
x = []
y = []
for key in routeCoverDict:
    if key[0] not in x:
        x.append(key[0])
    if key[1] not in y:
        y.append(key[1])
for i in range(len(x)):
    worksheet.write(i + 1, 0, x[i], cell_format)
    for j in range(len(y)):
        worksheet.write(0, j + 1, y[j], cell_format)
        worksheet.write(i + 1, j + 1, routeCoverDict[(x[i], y[j])], cell_format)
workbook.close()

#routeVehicleDict:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'routeVehicleDict.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
worksheet.write(0, 0, 'ShipmentNo', cell_format)
x = []
y = []
for key in routeVehicleDict:
    if key[0] not in x:
        x.append(key[0])
    if key[1] not in y:
        y.append(key[1])
for i in range(len(x)):
    worksheet.write(i + 1, 0, x[i], cell_format)
    for j in range(len(y)):
        worksheet.write(0, j + 1, y[j], cell_format)
        worksheet.write(i + 1, j + 1, routeVehicleDict[(x[i], y[j])], cell_format)
workbook.close()

#vehicleCapacityDict:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'vehicleCapacityDict.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
worksheet.write(0, 0, 'VehicleType', cell_format)
x = []
y = []
for key in vehicleCapacityDict:
    if key[0] not in x:
        x.append(key[0])
    if key[1] not in y:
        y.append(key[1])
for i in range(len(x)):
    worksheet.write(i + 1, 0, x[i], cell_format)
    for j in range(len(y)):
        worksheet.write(0, j + 1, y[j], cell_format)
        worksheet.write(i + 1, j + 1, vehicleCapacityDict[(x[i], y[j])], cell_format)
workbook.close()

#shipmentSizeDict:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'shipmentSizeDict.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
worksheet.write(0, 0, 'ShipmentNo', cell_format)
x = []
y = []
for key in shipmentSizeDict:
    if key[0] not in x:
        x.append(key[0])
    if key[1] not in y:
        y.append(key[1])
for i in range(len(x)):
    worksheet.write(i + 1, 0, x[i], cell_format)
    for j in range(len(y)):
        worksheet.write(0, j + 1, y[j], cell_format)
        worksheet.write(i + 1, j + 1, shipmentSizeDict[(x[i], y[j])], cell_format)
workbook.close()

#allowVehicleDict:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'allowVehicleDict.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
worksheet.write(0, 0, 'ShipmentNo', cell_format)
x = []
y = []
for key in allowVehicleDict:
    if key[0] not in x:
        x.append(key[0])
    if key[1] not in y:
        y.append(key[1])
for i in range(len(x)):
    worksheet.write(i + 1, 0, x[i], cell_format)
    for j in range(len(y)):
        worksheet.write(0, j + 1, y[j], cell_format)
        worksheet.write(i + 1, j + 1, allowVehicleDict[(x[i], y[j])], cell_format)
workbook.close()

#partialCostDict:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'partialCostDict.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
#worksheet.write(0, 0, 'ShipmentNo', cell_format)
#worksheet.write(0, 1, 'PartialCost', cell_format)
j = 0
for key in partialCostDict:
    worksheet.write(j, 0, key, cell_format)
    worksheet.write(j, 1, partialCostDict[key], cell_format)
    j = j + 1
workbook.close()

#shipmentCover:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'shipmentCover.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
worksheet.write(0, 0, 'ShipmentNo', cell_format)
x = []
y = []
for key in shipmentCover:
    if key[0] not in x:
        x.append(key[0])
    if key[1] not in y:
        y.append(key[1])
for i in range(len(x)):
    worksheet.write(i + 1, 0, x[i], cell_format)
    for j in range(len(y)):
        worksheet.write(0, j + 1, y[j], cell_format)
        worksheet.write(i + 1, j + 1, shipmentCover[(x[i], y[j])], cell_format)
workbook.close()

#vehicleAdditionalCost
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'vehicleAdditionalCost.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
#worksheet.write(0, 0, 'VehicleType', cell_format)
#worksheet.write(0, 1, 'AdditionalCost', cell_format)
j = 0
for key in vehicleAdditionalCost:
    worksheet.write(j, 0, key, cell_format)
    worksheet.write(j, 1, vehicleAdditionalCost[key], cell_format)
    j = j + 1
workbook.close()

#checkOTdict:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'checkOTdict.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
#worksheet.write(0, 0, 'CustomerID', cell_format)
#worksheet.write(0, 1, 'OT', cell_format)
j = 0
for key in checkOTdict:
    worksheet.write(j, 0, key, cell_format)
    worksheet.write(j, 1, checkOTdict[key], cell_format)
    j = j + 1
workbook.close()

#leadTimeFTLdict:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'leadTimeFTLdict.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
#worksheet.write(0, 0, 'ShipmentNo', cell_format)
#worksheet.write(0, 1, 'LeadTimeFTL', cell_format)
j = 0
for key in leadTimeFTLdict:
    worksheet.write(j, 0, key, cell_format)
    worksheet.write(j, 1, leadTimeFTLdict[key], cell_format)
    j = j + 1
workbook.close()

#leadTimePartialDict:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'leadTimePartialDict.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
#worksheet.write(0, 0, 'ShipmentNo', cell_format)
#worksheet.write(0, 1, 'LeadTimePartial', cell_format)
j = 0
for key in leadTimePartialDict:
    worksheet.write(j, 0, key, cell_format)
    worksheet.write(j, 1, leadTimePartialDict[key], cell_format)
    j = j + 1
workbook.close()

#timeIntervalDict:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'timeIntervalDict.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
#worksheet.write(0, 0, 'ShipmentNo', cell_format)
#worksheet.write(0, 1, 'TimeInterval', cell_format)
j = 0
for key in timeIntervalDict:
    worksheet.write(j, 0, key, cell_format)
    worksheet.write(j, 1, timeIntervalDict[key], cell_format)
    j = j + 1
workbook.close()

#routeVehicleCostDict:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'routeVehicleCostDict.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
worksheet.write(0, 0, 'RouteID', cell_format)
x = []
y = []
for key in routeVehicleCostDict:
    if key[0] not in x:
        x.append(key[0])
    if key[1] not in y:
        y.append(key[1])
for i in range(len(x)):
    worksheet.write(i + 1, 0, x[i], cell_format)
    for j in range(len(y)):
        worksheet.write(0, j + 1, y[j], cell_format)
        worksheet.write(i + 1, j + 1, routeVehicleCostDict[(x[i], y[j])], cell_format)
workbook.close()

#routeDetailDict:
workbook = xlsxwriter.Workbook(outputPathExcel + '\\' + 'routeDetailDict.xlsx')
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
#worksheet.write(0, 0, 'RouteID', cell_format)
#worksheet.write(0, 1, 'RouteDetail', cell_format)
j = 0
for key in routeDetailDict:
    worksheet.write(j, 0, key, cell_format)
    worksheet.write(j, 1, routeDetailDict[key], cell_format)
    j = j + 1

workbook.close()

###############################################################################################
###############################################################################################
###############################################################################################

if not os.path.exists(outputPathCSV):
    os.makedirs(outputPathCSV)


#ozelShipmentSet:
df = pd.read_excel(outputPathExcel + '\\' + 'ozelShipmentSet.xlsx')
df.to_csv(outputPathCSV + '\\' + 'ozelShipmentSet.csv', index = False)

#ozelCustomerSet:
df = pd.read_excel(outputPathExcel + '\\' + 'ozelCustomerSet.xlsx')
df.to_csv(outputPathCSV + '\\' + 'ozelCustomerSet.csv', index = False)

#ozelCustomerShipmentBinaryDict:
df = pd.read_excel(outputPathExcel + '\\' + 'ozelCustomerShipmentBinaryDict.xlsx')
df.to_csv(outputPathCSV + '\\' + 'ozelCustomerShipmentBinaryDict.csv', index = False)

#ozelRouteCoverDict:
df = pd.read_excel(outputPathExcel + '\\' + 'ozelRouteCoverDict.xlsx')
df.to_csv(outputPathCSV + '\\' + 'ozelRouteCoverDict.csv', index = False)

#ozelAllowVehicleDict:
df = pd.read_excel(outputPathExcel + '\\' + 'ozelAllowVehicleDict.xlsx')
df.to_csv(outputPathCSV + '\\' + 'ozelAllowVehicleDict.csv', index = False)

#ozelShipmentSizeDict:
df = pd.read_excel(outputPathExcel + '\\' + 'ozelShipmentSizeDict.xlsx')
df.to_csv(outputPathCSV + '\\' + 'ozelShipmentSizeDict.csv', index = False)

#vehicleIsTCdict:
df = pd.read_excel(outputPathExcel + '\\' + 'vehicleIsTCdict.xlsx')
df.to_csv(outputPathCSV + '\\' + 'vehicleIsTCdict.csv', index = False)

#ozelIsTCdict:
df = pd.read_excel(outputPathExcel + '\\' + 'ozelIsTCdict.xlsx')
df.to_csv(outputPathCSV + '\\' + 'ozelIsTCdict.csv', index = False)





#customerSet:
df = pd.read_excel(outputPathExcel + '\\' + 'customerSet.xlsx')
df.to_csv(outputPathCSV + '\\' + 'customerSet.csv', index = False)

#shipmentSet:
df = pd.read_excel(outputPathExcel + '\\' + 'shipmentSet.xlsx')
df.to_csv(outputPathCSV + '\\' + 'shipmentSet.csv', index = False)

#vehicleTypeSet:
df = pd.read_excel(outputPathExcel + '\\' + 'vehicleTypeSet.xlsx')
df.to_csv(outputPathCSV + '\\' + 'vehicleTypeSet.csv', index = False)

#routeSet:
df = pd.read_excel(outputPathExcel + '\\' + 'routeSet.xlsx')
df.to_csv(outputPathCSV + '\\' + 'routeSet.csv', index = False)

#dimensionSet:
df = pd.read_excel(outputPathExcel + '\\' + 'dimensionSet.xlsx')
df.to_csv(outputPathCSV + '\\' + 'dimensionSet.csv', index = False)

######################################################################

#routeCoverDict:
df = pd.read_excel(outputPathExcel + '\\' + 'routeCoverDict.xlsx')
df.to_csv(outputPathCSV + '\\' + 'routeCoverDict.csv', index = False)

#routeVehicleDict:
df = pd.read_excel(outputPathExcel + '\\' + 'routeVehicleDict.xlsx')
df.to_csv(outputPathCSV + '\\' + 'routeVehicleDict.csv', index = False)

#vehicleCapacityDict:
df = pd.read_excel(outputPathExcel + '\\' + 'vehicleCapacityDict.xlsx')
df.to_csv(outputPathCSV + '\\' + 'vehicleCapacityDict.csv', index = False)

#shipmentSizeDict:
df = pd.read_excel(outputPathExcel + '\\' + 'shipmentSizeDict.xlsx')
df.to_csv(outputPathCSV + '\\' + 'shipmentSizeDict.csv', index = False)

#allowVehicleDict:
df = pd.read_excel(outputPathExcel + '\\' + 'allowVehicleDict.xlsx')
df.to_csv(outputPathCSV + '\\' + 'allowVehicleDict.csv', index = False)

#partialCostDict
df = pd.read_excel(outputPathExcel + '\\' + 'partialCostDict.xlsx')
df.to_csv(outputPathCSV + '\\' + 'partialCostDict.csv', index = False)

#shipmentCover
df = pd.read_excel(outputPathExcel + '\\' + 'shipmentCover.xlsx')
df.to_csv(outputPathCSV + '\\' + 'shipmentCover.csv', index = False)

#vehicleAdditionalCost:
df = pd.read_excel(outputPathExcel + '\\' + 'vehicleAdditionalCost.xlsx')
df.to_csv(outputPathCSV + '\\' + 'vehicleAdditionalCost.csv', index = False)

#checkOTdict:
df = pd.read_excel(outputPathExcel + '\\' + 'checkOTdict.xlsx')
df.to_csv(outputPathCSV + '\\' + 'checkOTdict.csv', index = False)

#leadTimeFTLdict:
df = pd.read_excel(outputPathExcel + '\\' + 'leadTimeFTLdict.xlsx')
df.to_csv(outputPathCSV + '\\' + 'leadTimeFTLdict.csv', index = False)

#leadTimePartialDict:
df = pd.read_excel(outputPathExcel + '\\' + 'leadTimePartialDict.xlsx')
df.to_csv(outputPathCSV + '\\' + 'leadTimePartialDict.csv', index = False)

#timeIntervalDict:
df = pd.read_excel(outputPathExcel + '\\' + 'timeIntervalDict.xlsx')
df.to_csv(outputPathCSV + '\\' + 'timeIntervalDict.csv', index = False)

#routeVehicleCostDict:
df = pd.read_excel(outputPathExcel + '\\' + 'routeVehicleCostDict.xlsx')
df.to_csv(outputPathCSV + '\\' + 'routeVehicleCostDict.csv', index = False)

#routeDetailDict:
df = pd.read_excel(outputPathExcel + '\\' + 'routeDetailDict.xlsx')
df.to_csv(outputPathCSV + '\\' + 'routeDetailDict.csv', index = False)



