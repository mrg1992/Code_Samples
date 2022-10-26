import xlsxwriter
import win32com.client as win32
import copy
import numpy as np

class SolutionToExcel:
    def __init__(self, ozelShipmentDict, shipmentDict, keysOzel, keysFTL, keysPartial, routeDict, routeVehicleCostDict, partialCostDict, vehicleCapacityDict, vehicleAdditionalCost):
        self.ozelShipmentDict = ozelShipmentDict
        self.shipmentDict = shipmentDict
        #self.ozelRouteVehicleAssignDict = ozelRouteVehicleAssignDict
        #self.ozelCustomerDetailDict = ozelCustomerDetailDict
        self.keysOzel = keysOzel
        self.keysFTL = keysFTL
        self.keysPartial = keysPartial
        self.routeDict = routeDict
        self.routeVehicleCostDict = routeVehicleCostDict
        self.partialCostDict = partialCostDict
        self.vehicleCapacityDict = vehicleCapacityDict
        self.vehicleAdditionalCost = vehicleAdditionalCost
                
    def _exportXLSX(self, outputFileName):
        summaryDict = {}
        ozelRowVectorDict = {}
        FTLRowVectorDict = {}
        generalFTLRowVectorList = []
        partialRowVectorDict = {}
        
        vehicleTypeList = ['KAMYONAMB',	'TIRAMB',	'KAMYONETAMB',	'KAMYONTC',	'TIRTC',	'KAMYONETTC']
        vehicleFullness = {}
        workbook = xlsxwriter.Workbook(outputFileName)
        worksheet = workbook.add_worksheet('t1-Raporu')
        cell_format = workbook.add_format({'bold': True, 'align': 'center', 'font_color': 'black'})
        worksheet.write(8,0, 'Özel Shipto Detay', cell_format)
        worksheet.write(9,0, 'Araç No', cell_format)
        worksheet.write(9,1, 'Araç Tipi', cell_format)
        worksheet.write(9,2, 'Teslimat No', cell_format)
        worksheet.write(9,3, 'Müşteri', cell_format)
        worksheet.write(9,4, 'Ship-to Party', cell_format)
        worksheet.write(9,5, 'Rota ID', cell_format)
        worksheet.write(9,6, 'İl', cell_format)
        worksheet.write(9,7, 'İlçe', cell_format)
        worksheet.write(9,8, 'Palet Sayısı', cell_format)
        worksheet.write(9,9, 'Ağırlık', cell_format)
        worksheet.write(9,10, 'Rota', cell_format)
        worksheet.write(9,11, 'TC/AMB', cell_format)
        
        totalCostFTL = 0
        totalCostPartial = 0
        totalDeliveryFTL = 0
        totalDeliveryPartial = 0
        totalWeightFTL = 0
        totalWeightPartial = 0
        totalPalletFTL = 0
        totalPalletPartial = 0
        weightCapacity = 0
        tempVehicleNo = 0
        ozelCounter = 0
        #totalCounter = 0
        cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
        
        '''
        for customerID in self.ozelCustomerDetailDict:
            tempVehicleNo = tempVehicleNo + 1
            tempCustomerName = self.ozelshipmentDict[self.ozelCustomerDetailDict[customerID][0][0]][3]
            tempCustomerNo = customerID
            tempRouteID = self.ozelCustomerDetailDict[customerID][4][0]
            tempVehicleType = self.ozelCustomerDetailDict[customerID][4][1]
            tempCity = self.ozelshipmentDict[self.ozelCustomerDetailDict[customerID][0][0]][4]
            tempDistrict = self.ozelshipmentDict[self.ozelCustomerDetailDict[customerID][0][0]][5]
            tempRouteName = self.routeDict[tempRouteID][0]
            for ozelShipmentNo in self.ozelCustomerDetailDict[customerID][0]:
                k = k + 1
                tempPallet = self.ozelshipmentDict[ozelShipmentNo][9]
                tempWeight = self.ozelshipmentDict[ozelShipmentNo][10]
                tempTC_AMB = self.ozelshipmentDict[ozelShipmentNo][6]
                ozelRowVector = [tempVehicleNo, tempVehicleType, ozelShipmentNo, tempCustomerName, tempCustomerNo, tempRouteID, tempCity, tempDistrict, tempPallet, tempWeight, tempRouteName, tempTC_AMB]
                for i in range(len(ozelRowVector)):
                    worksheet.write(9 + k, i, ozelRowVector[i], cell_format)
                ozelVehicleCount = copy.deepcopy(tempVehicleNo)'''
        
        k = 0
        ozelVehicleCount = 0
        #ozelExtendedDict = {}
        routeVehicle = {}
        ozelCustomerDict = {}
        for key in self.keysOzel:
            tempShipmentNo = key[0]
            tempCustomerNo = self.ozelShipmentDict[tempShipmentNo][2] 
            tempRouteID = key[1]
            tempVehicleType = key[2]
            if (tempRouteID, tempVehicleType) not in routeVehicle:
                #tempVehicleNo = tempVehicleNo + 1
                routeVehicle[(tempRouteID, tempVehicleType)] = [tempShipmentNo]
                if tempCustomerNo not in ozelCustomerDict:
                    ozelCustomerDict[tempCustomerNo] = [(tempRouteID, tempVehicleType)]
                else:
                    ozelCustomerDict[tempCustomerNo].append((tempRouteID, tempVehicleType))
            else:
                routeVehicle[(tempRouteID, tempVehicleType)].append(tempShipmentNo)        
        for customerNo in ozelCustomerDict:
            for key in ozelCustomerDict[customerNo]:
                tempVehicleNo = tempVehicleNo + 1
                ozelRowVectorDict[tempVehicleNo] = {}
                tempRouteID = key[0]
                tempVehicleType = key[1]
                for tempShipmentNo in routeVehicle[(tempRouteID, tempVehicleType)]:
                    #k = k + 1
                    tempCustomerName = self.ozelShipmentDict[tempShipmentNo][3]
                    tempCity = self.ozelShipmentDict[tempShipmentNo][4]
                    tempDistrict = self.ozelShipmentDict[tempShipmentNo][5]
                    tempRouteName = self.routeDict[tempRouteID][0]
                    tempPallet = self.ozelShipmentDict[tempShipmentNo][9]
                    tempWeight = self.ozelShipmentDict[tempShipmentNo][10]
                    tempTC_AMB = self.ozelShipmentDict[tempShipmentNo][6]
                    ozelRowVector = [tempVehicleNo, tempVehicleType, tempShipmentNo, tempCustomerName, customerNo, tempRouteID, tempCity, tempDistrict, tempPallet, tempWeight, tempRouteName, tempTC_AMB]
                    if customerNo not in ozelRowVectorDict[tempVehicleNo]:
                        ozelRowVectorDict[tempVehicleNo][customerNo] = [ozelRowVector]
                    else:
                        ozelRowVectorDict[tempVehicleNo][customerNo].append(ozelRowVector)
                    #for i in range(len(ozelRowVector)):
                        #worksheet.write(9 + k, i, ozelRowVector[i], cell_format)
                ozelVehicleCount = copy.deepcopy(tempVehicleNo)
        
        for vNo in np.sort(list(ozelRowVectorDict.keys())):
            for cID in np.sort(list(ozelRowVectorDict[vNo].keys())):
                for rowVector in ozelRowVectorDict[vNo][cID]:
                    k = k + 1
                    for i in range(len(rowVector)):
                        worksheet.write(9 + k, i, rowVector[i], cell_format)
    
        baseline = 9 + k + 2
        cell_format = workbook.add_format({'bold': True, 'align': 'center', 'font_color': 'black', 'bg_color': 'yellow'})
        worksheet.write(baseline, 0, 'FTL Rota Detayı', cell_format)
        worksheet.write(baseline + 1,0, 'Araç No', cell_format)
        worksheet.write(baseline + 1,1, 'Araç Tipi', cell_format)
        worksheet.write(baseline + 1,2, 'Teslimat No', cell_format)
        worksheet.write(baseline + 1,3, 'Müşteri', cell_format)
        worksheet.write(baseline + 1,4, 'Ship-to Party', cell_format)
        worksheet.write(baseline + 1,5, 'Rota ID', cell_format)
        worksheet.write(baseline + 1,6, 'İl', cell_format)
        worksheet.write(baseline + 1,7, 'İlçe', cell_format)
        worksheet.write(baseline + 1,8, 'Palet Sayısı', cell_format)
        worksheet.write(baseline + 1,9, 'Ağırlık', cell_format)
        worksheet.write(baseline + 1,10, 'Rota', cell_format)
        worksheet.write(baseline + 1,11, 'TC/AMB', cell_format)
        worksheet.write(baseline + 1,12, 'DO-OT', cell_format)
        worksheet.write(baseline + 1,13, 'Parsiyel Maliyet', cell_format)
        
        cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
        counterShipmentFTL = 0
        counterVehicleFTL = 0
        routeVehicle = {}
        for key in self.keysFTL:
            if (key[1], key[2]) not in routeVehicle:
                routeVehicle[(key[1], key[2])] = [key[0]]
            elif (key[1], key[2]) in routeVehicle:
                routeVehicle[(key[1], key[2])].append(key[0])
        tempVehicleNo = ozelVehicleCount
        for key in routeVehicle:
            tempVehicleNo = tempVehicleNo + 1
            FTLRowVectorDict[tempVehicleNo] = {}
            tempVehicleType = key[1]
            tempRouteID = key[0]
            for shipmentNo in routeVehicle[key]:
                #counterShipmentFTL = counterShipmentFTL + 1
                tempCustomerName = self.shipmentDict[shipmentNo][3]
                tempCustomerNo = self.shipmentDict[shipmentNo][2]
                tempCity = self.shipmentDict[shipmentNo][4]
                tempDistrict = self.shipmentDict[shipmentNo][5]
                tempPallet = self.shipmentDict[shipmentNo][9]
                totalPalletFTL = totalPalletFTL + tempPallet
                tempWeight = self.shipmentDict[shipmentNo][10]
                totalWeightFTL = totalWeightFTL + tempWeight
                tempRouteName = self.routeDict[tempRouteID][0]
                tempTC_AMB = self.shipmentDict[shipmentNo][6]
                tempDO_OT = self.shipmentDict[shipmentNo][11]
                tempPartialCost = tempWeight * self.partialCostDict[shipmentNo]
                FTLRowVector = [tempVehicleNo, tempVehicleType, shipmentNo, tempCustomerName, tempCustomerNo, tempRouteID, tempCity, tempDistrict, tempPallet, tempWeight, tempRouteName, tempTC_AMB, tempDO_OT, tempPartialCost]
                if tempCustomerNo not in FTLRowVectorDict[tempVehicleNo]:
                    FTLRowVectorDict[tempVehicleNo][tempCustomerNo] = [FTLRowVector]
                else:
                    FTLRowVectorDict[tempVehicleNo][tempCustomerNo].append(FTLRowVector)
                if tempCustomerNo not in summaryDict:
                    summaryDict[tempCustomerNo] = [[shipmentNo, 'FTL', tempVehicleNo, tempRouteID]]
                elif tempCustomerNo in summaryDict:
                    summaryDict[tempCustomerNo].append([shipmentNo, 'FTL', tempVehicleNo, tempRouteID])
                #for i in range(len(FTLRowVector)):
                #    worksheet.write(baseline + counterShipmentFTL + 1, i, FTLRowVector[i], cell_format)
        for vNo in np.sort(list(FTLRowVectorDict.keys())):
            for cID in np.sort(list(FTLRowVectorDict[vNo].keys())):
                for rowVector in FTLRowVectorDict[vNo][cID]:
                    counterShipmentFTL = counterShipmentFTL + 1
                    for i in range(len(rowVector)):
                        worksheet.write(baseline + counterShipmentFTL + 1, i, rowVector[i], cell_format)
        
        cell_format = workbook.add_format({'bold': True, 'align': 'center', 'font_color': 'black', 'bg_color': 'blue'})
        worksheet.write(baseline, 15, 'FTL Rota Genel', cell_format)
        worksheet.write(baseline + 1, 15, 'ID', cell_format)
        worksheet.write(baseline + 1, 16, 'Rota ID', cell_format)
        worksheet.write(baseline + 1, 17, 'Rota', cell_format)
        worksheet.write(baseline + 1, 18, 'Araç Tipi', cell_format)
        worksheet.write(baseline + 1, 19, 'FTL Maliyet', cell_format)
        worksheet.write(baseline + 1, 20, 'Parsiyel Maliyet', cell_format)
        worksheet.write(baseline + 1, 21, 'Toplam Palet', cell_format)
        worksheet.write(baseline + 1, 22, 'Toplam Ağırlık', cell_format)
        worksheet.write(baseline + 1, 23, 'Doluluk Oranı (%)', cell_format)
        
        vehicleNo = ozelVehicleCount
        vehicleLineCounter = 0
        for key in routeVehicle:
            routeVehiclePallet = 0
            routeVehicleWeight = 0
            routeVehicleFTLCost = 0
            routeVehiclePartialCost = 0
            palletCapacity = self.vehicleCapacityDict[(key[1], 'volume')]
            weightCapacity = self.vehicleCapacityDict[(key[1], 'weight')]
            vehicleNo = vehicleNo + 1
            vehicleLineCounter = vehicleLineCounter + 1
            routeID = key[0]
            routeName = self.routeDict[routeID][0]
            customerCount = 0
            tempCustomerList = []
            for shipmentNo in routeVehicle[key]:
                if self.shipmentDict[shipmentNo][2] not in tempCustomerList:
                    customerCount = customerCount + 1
                    tempCustomerList.append(self.shipmentDict[shipmentNo][2])
                routeVehiclePallet = routeVehiclePallet + self.shipmentDict[shipmentNo][9]
                routeVehicleWeight = routeVehicleWeight + self.shipmentDict[shipmentNo][10]
                routeVehiclePartialCost = routeVehiclePartialCost + self.partialCostDict[shipmentNo] * self.shipmentDict[shipmentNo][10]
                #totalCostPartial = totalCostPartial + routeVehiclePartialCost
            if customerCount > 2:
                routeVehicleFTLCost = self.routeVehicleCostDict[key] + (customerCount - 2) * self.vehicleAdditionalCost[key[1]]
            elif customerCount <= 2:
                routeVehicleFTLCost = self.routeVehicleCostDict[key]
            totalCostFTL = totalCostFTL + routeVehicleFTLCost
            fullnessPercent = (routeVehiclePallet/palletCapacity) * 100
            generalFTLRowVector = [vehicleNo, routeID, routeName, key[1], routeVehicleFTLCost, routeVehiclePartialCost, routeVehiclePallet, routeVehicleWeight, fullnessPercent]            
            generalFTLRowVectorList.append(generalFTLRowVector)
            if key[1] not in vehicleFullness:
                vehicleFullness[key[1]] = [fullnessPercent]
            elif key[1] in vehicleFullness:
                vehicleFullness[key[1]].append(fullnessPercent)
                
            cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
            for i in range(len(generalFTLRowVector)):
                worksheet.write(baseline + vehicleLineCounter + 1, i + 15, generalFTLRowVector[i], cell_format)
            
                
        cell_format = workbook.add_format({'bold': True, 'align': 'center', 'font_color': 'black', 'bg_color': 'lime'})
        worksheet.write(baseline, 25, 'Parsiyel Genel', cell_format)
        worksheet.write(baseline + 1, 25, 'Teslimat No', cell_format)
        worksheet.write(baseline + 1, 26, 'Müşteri', cell_format)
        worksheet.write(baseline + 1, 27, 'Ship-to Party', cell_format)
        worksheet.write(baseline + 1, 28, 'İl', cell_format)
        worksheet.write(baseline + 1, 29, 'İlçe', cell_format)
        worksheet.write(baseline + 1, 30, 'Maliyet', cell_format)
        worksheet.write(baseline + 1, 31, 'TC/AMB', cell_format)
        worksheet.write(baseline + 1, 32, 'Palet Sayısı', cell_format)
        worksheet.write(baseline + 1, 33, 'Ağırlık', cell_format)
        worksheet.write(baseline + 1, 34, 'DO-OT', cell_format)
        worksheet.write(baseline + 1, 35, 'Çıkış Günü', cell_format)
        
        k = 0
        for shipmentNo in self.keysPartial:
            #k = k + 1
            tempCustomerName = self.shipmentDict[shipmentNo][3]
            tempCustomerNo = self.shipmentDict[shipmentNo][2]
            tempCity = self.shipmentDict[shipmentNo][4]
            tempDistrict = self.shipmentDict[shipmentNo][5]
            tempPallet = self.shipmentDict[shipmentNo][9]
            totalPalletPartial = totalPalletPartial + tempPallet
            tempWeight = self.shipmentDict[shipmentNo][10]
            totalWeightPartial = totalWeightPartial + tempWeight
            tempPartialCost = self.partialCostDict[shipmentNo] * tempWeight
            totalCostPartial = totalCostPartial + tempPartialCost
            tempTC_AMB = self.shipmentDict[shipmentNo][6]
            tempDO_OT = self.shipmentDict[shipmentNo][11]
            partialRowVector = [shipmentNo, tempCustomerName, tempCustomerNo, tempCity, tempDistrict, tempPartialCost, tempTC_AMB, tempPallet, tempWeight, tempDO_OT]
            if tempCustomerNo not in partialRowVectorDict:
                partialRowVectorDict[tempCustomerNo] = [partialRowVector]
            else:
                partialRowVectorDict[tempCustomerNo].append(partialRowVector)
            if tempCustomerNo not in summaryDict:
                summaryDict[tempCustomerNo] = [[shipmentNo, 'Parsiyel', '-', '-']]
            elif tempCustomerNo in summaryDict:
                summaryDict[tempCustomerNo].append([shipmentNo, 'Parsiyel', '-', '-'])
            
            cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
            #for i in range(len(partialRowVector)):
                #worksheet.write(baseline + k + 1, 25 + i, partialRowVector[i], cell_format)
        
        for cID in np.sort(list(partialRowVectorDict.keys())):
            for rowVector in partialRowVectorDict[cID]:
                k = k + 1
                for i in range(len(rowVector)):
                    worksheet.write(baseline + k + 1, 25 + i, rowVector[i], cell_format)
        
        
        cell_format = workbook.add_format({'bold': True, 'align': 'center', 'font_color': 'black'})
        worksheet.write(0, 0, 'Toplam Çıkış Maliyetleri', cell_format)
        worksheet.write(1, 0, 'FTL', cell_format)
        worksheet.write(1, 1, 'Parsiyel', cell_format)
        worksheet.write(1, 2, 'Toplam', cell_format)
        
        worksheet.write(0, 4, 'Toplam Palet', cell_format)
        worksheet.write(1, 4, 'FTL', cell_format)
        worksheet.write(1, 5, 'Parsiyel', cell_format)
        worksheet.write(1, 6, 'Toplam', cell_format)
        
        worksheet.write(4, 0, 'Toplam Teslimat Çıkış Adetleri', cell_format)
        worksheet.write(5, 0, 'FTL', cell_format)
        worksheet.write(5, 1, 'Parsiyel', cell_format)
        worksheet.write(5, 2, 'Toplam', cell_format)
        
        worksheet.write(4, 4, 'Toplam Ağırlık', cell_format)
        worksheet.write(5, 4, 'FTL', cell_format)
        worksheet.write(5, 5, 'Parsiyel', cell_format)
        worksheet.write(5, 6, 'Toplam', cell_format)
        
        
        cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
        worksheet.write(2, 0, format(totalCostFTL/1000, '.3f'), cell_format)
        worksheet.write(2, 1, format(totalCostPartial/1000, '.3f'), cell_format)
        worksheet.write(2, 2, format((totalCostFTL + totalCostPartial)/1000, '.3f'), cell_format)
        
        worksheet.write(2, 4, totalPalletFTL, cell_format)
        worksheet.write(2, 5, totalPalletPartial, cell_format)
        worksheet.write(2, 6, totalPalletFTL + totalPalletPartial, cell_format)
        
        worksheet.write(6, 0, len(self.keysFTL), cell_format)
        worksheet.write(6, 1, len(self.keysPartial), cell_format)
        worksheet.write(6, 2, len(self.keysFTL) + len(self.keysPartial), cell_format)
        
        worksheet.write(6, 4, format(totalWeightFTL/1000, '.3f'), cell_format)
        worksheet.write(6, 5, format(totalWeightPartial/1000, '.3f'), cell_format)
        worksheet.write(6, 6, format((totalWeightFTL + totalWeightPartial)/1000, '.3f'), cell_format)
        
        cell_format = workbook.add_format({'bold': True, 'align': 'center', 'font_color': 'black'})
        worksheet.write(0, 8, 'Doluluk Oranları', cell_format)
        worksheet.write(1, 8, 'KAMYONAMB', cell_format)
        worksheet.write(1, 9, 'TIRAMB', cell_format)
        worksheet.write(1, 10, 'KAMYONETAMB', cell_format)
        worksheet.write(1, 11, 'KAMYONTC', cell_format)
        worksheet.write(1, 12, 'TIRTC', cell_format)
        worksheet.write(1, 13, 'KAMYONETTC', cell_format)
        
        for vehicleType in vehicleTypeList:
            if vehicleType not in vehicleFullness:
                vehicleFullness[vehicleType] = 0
        cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
        worksheet.write(2, 8, format(np.mean(vehicleFullness['KAMYONAMB']), '.3f') + ' %', cell_format)
        worksheet.write(2, 9, format(np.mean(vehicleFullness['TIRAMB']), '.3f') + ' %', cell_format)
        worksheet.write(2, 10, format(np.mean(vehicleFullness['KAMYONETAMB']), '.3f') + ' %', cell_format)
        worksheet.write(2, 11, format(np.mean(vehicleFullness['KAMYONTC']), '.3f') + ' %', cell_format)
        worksheet.write(2, 12, format(np.mean(vehicleFullness['TIRTC']), '.3f') + ' %', cell_format)
        worksheet.write(2, 13, format(np.mean(vehicleFullness['KAMYONETTC']), '.3f') + ' %', cell_format)
        
        worksheet2 = workbook.add_worksheet('Dağıtılmış Ship-to\'lar')
        cell_format = workbook.add_format({'bold': True, 'align': 'center', 'font_color': 'black'})
        worksheet2.write(0,0, 'Shipto-ID', cell_format)
        worksheet2.write(0,1, 'Teslimat No', cell_format)
        worksheet2.write(0,2, 'Teslimat Modu (Ftl/Parsiyel)', cell_format)
        worksheet2.write(0,3, 'Araç ID', cell_format)
        worksheet2.write(0,4, 'Rota ID', cell_format)
        
        cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
        rowIndex = 0
        for customerID in summaryDict:
            for i in range(len(summaryDict[customerID])):
                rowIndex = rowIndex + 1
                worksheet2.write(rowIndex,0, customerID, cell_format)
                worksheet2.write(rowIndex,1, summaryDict[customerID][i][0], cell_format)
                worksheet2.write(rowIndex,2, summaryDict[customerID][i][1], cell_format)
                worksheet2.write(rowIndex,3, summaryDict[customerID][i][2], cell_format)
                worksheet2.write(rowIndex,4, summaryDict[customerID][i][3], cell_format)
                
        
        workbook.close()
        
        
        excel = win32.gencache.EnsureDispatch('Excel.Application')
        wb = excel.Workbooks.Open(outputFileName)
        ws1 = wb.Worksheets('t1-Raporu')
        ws2 = wb.Worksheets('Dağıtılmış Ship-to\'lar')
        ws1.Columns.AutoFit()
        ws1.Cells(baseline + 1, 15 + 1).Interior.ColorIndex = 8
        for i in range(9):
            ws1.Cells(baseline + 2, 15 + 1 + i).Interior.ColorIndex = 8
        ws2.Columns.AutoFit()
        wb.Save()
        excel.Application.Quit()