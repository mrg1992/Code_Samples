import networkx as nx
import random
import numpy as np
import math
import copy
import time
import os
import matplotlib.pyplot as plt
import xlsxwriter

dirPath = os.path.dirname(os.path.abspath(__file__))
outputFileName = dirPath + '\\Drone_Result.xlsx'

def calcChargingTime(x):
    tC = 60
    return tC * x / 100

def findFeasibleNodes(graph, droneDict, stationNodes, serviceNodeDict, practicalEdgeConsumptionDict, practicalServiceConsumptionDict, X):
    currentNode = droneDict['Current_Node']
    #currentNodeType = droneDict['current_Node_Type']
    unservicedNodes = droneDict['Unservised_Nodes']
    #capacity = droneDict['Capacity']
    battery = droneDict['Capacity'] * X / 100
    feasibleServiceNodes = []
    for node in unservicedNodes:
        pathToNode = nx.shortest_path(graph, currentNode, node)
        edgePathToNode = []
        for i in range(len(pathToNode) - 1):
            edgePathToNode.append((pathToNode[i], pathToNode[i + 1]))
        consumption = 0
        #print(pathToNode, currentNode, node)
        for edge in edgePathToNode:
            #print(edge)
            consumption = consumption + practicalEdgeConsumptionDict[edge] * graph[edge[0]][edge[1]]['cost']
        consumption = consumption + practicalServiceConsumptionDict[node] * serviceNodeDict[node]
        tempGoToRechargeConsumptionList = []
        for station in stationNodes:
            pathToStation = nx.shortest_path(graph, node, station)
            edgePathToStation = []
            for i in range(len(pathToStation) - 1):
                edgePathToStation.append((pathToStation[i], pathToStation[i + 1]))    
            tempConsumption = 0
            for edge in edgePathToStation:
                tempConsumption = tempConsumption + practicalEdgeConsumptionDict[edge] * graph[edge[0]][edge[1]]['cost']
            tempGoToRechargeConsumptionList.append(tempConsumption)
        consumption = consumption + min(tempGoToRechargeConsumptionList)
        if consumption < battery:
            feasibleServiceNodes.append(node)
    return feasibleServiceNodes     
            
def findY(graph, droneDict, stationNodes, serviceNodeDict, practicalEdgeConsumptionDict, practicalServiceConsumptionDict):
    currentNode = droneDict['Current_Node']
    unservicedNodes = droneDict['Unservised_Nodes']
    #battery = droneDict['Battery']
    yList = []
    yNodeList = []
    yGoToStationList = []
    for i in range(len(unservicedNodes)):
        node = unservicedNodes[i]
        pathToNode = nx.shortest_path(graph, currentNode, node)
        edgePathToNode = []
        for i in range(len(pathToNode) - 1):
            edgePathToNode.append((pathToNode[i], pathToNode[i + 1]))
        tempY = 0
        for edge in edgePathToNode:
            tempY = tempY + practicalEdgeConsumptionDict[edge] * graph[edge[0]][edge[1]]['cost']
        tempY = tempY + practicalServiceConsumptionDict[node] * serviceNodeDict[node]
        tempGoToRechargeConsumptionList = []
        for j in range(len(stationNodes)):
            station = stationNodes[j]
            pathToStation = nx.shortest_path(graph, node, station)
            edgePathToStation = []
            for i in range(len(pathToStation) - 1):
                edgePathToStation.append((pathToStation[i], pathToStation[i + 1]))
            temp = 0
            for edge in edgePathToStation:
                temp = temp + practicalEdgeConsumptionDict[edge] * graph[edge[0]][edge[1]]['cost']
            tempGoToRechargeConsumptionList.append(temp)
        tempIndex = np.argmin(tempGoToRechargeConsumptionList)
        tempY = tempY + tempGoToRechargeConsumptionList[tempIndex]
        tempGoToStation = stationNodes[tempIndex]
        yList.append(tempY)
        yNodeList.append(node)
        yGoToStationList.append(tempGoToStation)
    index = np.argmin(yList)
    return [yList[index], yNodeList[index], yGoToStationList[index]]

def findClosestNode(graph, currentNode, listOfDestinations):
    tempDists = []
    for i in range(len(listOfDestinations)):
        tempDists.append(nx.shortest_path_length(graph, currentNode, listOfDestinations[i]))
    index = np.argmin(tempDists)
    return listOfDestinations[index]


totalRunTimeStart = time.time()

random.seed(1)

capacity = 720
X = 80
LC = 0.002 * capacity
UC = 0.008 * capacity
LT = 5
UT = 60



myFakeGraph = nx.generators.lattice.grid_2d_graph(10, 12)
fakeEdges = list(myFakeGraph.edges())
allNodes = list(myFakeGraph.nodes())

myGraph = nx.DiGraph()
myGraph.add_nodes_from(allNodes)
for edge in fakeEdges:
    myGraph.add_edge(edge[0], edge[1], cost = random.uniform(LT,UT))
    myGraph.add_edge(edge[1], edge[0], cost = random.uniform(LT,UT))

allEdges = list(myGraph.edges())

flag1 = 1
while flag1:
    flag1 = 0
    stationNodes = random.sample(allNodes, 10)
    for node1 in stationNodes:
        for node2 in list(set(stationNodes)-set([node1])):
            if (node1, node2) in allEdges:
                flag1 = 1
serviceNodes = list(set(allNodes) - set(stationNodes))
serviceNodeDict = {}

startingNode = random.choice(stationNodes)
edgeConsumptionRateDict = {}
practicalEdgeConsumptionDict = {}
serviceConsumptionRateDict = {}
practicalServiceConsumptionDict = {}


for edge in allEdges:
    edgeConsumptionRateDict[edge] = random.uniform(LC,UC)
    practicalEdgeConsumptionDict[edge] = UC
for node in serviceNodes:
    serviceNodeDict[node] = random.uniform(5,60)
    serviceConsumptionRateDict[node] = random.uniform(LC,UC)
    practicalServiceConsumptionDict[node] = UC

droneDict = {}
droneDict['Time'] = [[0.0, 0.0]]
droneDict['Capacity'] = capacity
droneDict['Battery'] = 0
droneDict['Current_Node'] = startingNode
droneDict['Current_Node_Type'] = 0
#droneDict['Feasible_Nodes'] = []
droneDict['Serviced_Nodes'] = []
droneDict['Unservised_Nodes'] = list(serviceNodeDict.keys())
#droneDict['Discovered_Edges'] = []
droneDict['General_Path'] = [[startingNode, 'charge', []]]
#droneDict['Battery_History'] = [0]


        
timeTrack = 0
flag = 1
while flag:
    feasibleNodes = findFeasibleNodes(myGraph, droneDict, stationNodes, serviceNodeDict, practicalEdgeConsumptionDict, practicalServiceConsumptionDict, X)
    if len(feasibleNodes) > 0:
        percentToCharge = X - (droneDict['Battery'] / droneDict['Capacity']) * 100
        chargingTime = calcChargingTime(percentToCharge)
        droneDict['Time'][len(droneDict['Time']) - 1][1] = droneDict['Time'][len(droneDict['Time']) - 1][1] + chargingTime
        timeTrack = timeTrack + chargingTime
        droneDict['Battery'] = droneDict['Capacity'] * X / 100
        #droneDict['Battery_History'].append()
        nextStop = findClosestNode(myGraph, droneDict['Current_Node'], feasibleNodes)
        pathToNode = nx.shortest_path(myGraph, droneDict['Current_Node'], nextStop)
        edgePathToNode = []
        for i in range(len(pathToNode) - 1):
            edgePathToNode.append((pathToNode[i], pathToNode[i + 1]))
        consumption = 0
        for edge in edgePathToNode:
            consumption = consumption + edgeConsumptionRateDict[edge] * myGraph[edge[0]][edge[1]]['cost']
            practicalEdgeConsumptionDict[edge] = edgeConsumptionRateDict[edge]
            timeTrack = timeTrack + myGraph[edge[0]][edge[1]]['cost']
            droneDict['Time'].append([timeTrack, timeTrack])
            droneDict['General_Path'].append([edge[1], 'pass'])
        droneDict['General_Path'][len(droneDict['General_Path']) - 1][1] = 'service'    
        timeTrack = timeTrack + serviceNodeDict[droneDict['General_Path'][len(droneDict['General_Path']) - 1][0]]
        droneDict['Time'][len(droneDict['Time']) - 1][1] = droneDict['Time'][len(droneDict['Time']) - 1][1] + serviceNodeDict[droneDict['General_Path'][len(droneDict['General_Path']) - 1][0]]
        consumption = consumption + serviceConsumptionRateDict[node] * serviceNodeDict[node]
        practicalServiceConsumptionDict[node] = serviceConsumptionRateDict[node]
        droneDict['Current_Node'] = nextStop
        droneDict['Battery'] = droneDict['Battery'] - consumption
        droneDict['Current_Node_Type'] = 1
        droneDict['Serviced_Nodes'].append(nextStop)
        droneDict['Unservised_Nodes'].remove(nextStop)
    else:
        [Y, nextStop, nextStation] = findY(myGraph, droneDict, stationNodes, serviceNodeDict, practicalEdgeConsumptionDict, practicalServiceConsumptionDict)
        percentToCharge = Y - droneDict['Battery'] / droneDict['Capacity'] * 100
        chargingTime = calcChargingTime(percentToCharge)
        droneDict['Time'][len(droneDict['Time']) - 1][1] = droneDict['Time'][len(droneDict['Time']) - 1][1] + chargingTime
        timeTrack = timeTrack + chargingTime
        droneDict['Battery'] = droneDict['Capacity'] * Y / 100
        pathToNode = nx.shortest_path(myGraph, droneDict['Current_Node'], nextStop)
        edgePathToNode = []
        for i in range(len(pathToNode) - 1):
            edgePathToNode.append((pathToNode[i], pathToNode[i + 1]))
        consumption = 0
        for edge in edgePathToNode:
            consumption = consumption + edgeConsumptionRateDict[edge] * myGraph[edge[0]][edge[1]]['cost']
            practicalEdgeConsumptionDict[edge] = edgeConsumptionRateDict[edge]
            timeTrack = timeTrack + myGraph[edge[0]][edge[1]]['cost']
            droneDict['Time'].append([timeTrack, timeTrack])
            droneDict['General_Path'].append([edge[1], 'pass'])
        droneDict['General_Path'][len(droneDict['General_Path']) - 1][1] = 'service'            
        timeTrack = timeTrack + serviceNodeDict[droneDict['General_Path'][len(droneDict['General_Path']) - 1][0]]
        droneDict['Time'][len(droneDict['Time']) - 1][1] = droneDict['Time'][len(droneDict['Time']) - 1][1] + serviceNodeDict[droneDict['General_Path'][len(droneDict['General_Path']) - 1][0]]
        consumption = consumption + serviceConsumptionRateDict[node] * serviceNodeDict[node]
        practicalServiceConsumptionDict[node] = serviceConsumptionRateDict[node]
        droneDict['Current_Node'] = nextStop
        #droneDict['Battery'] = droneDict['Battery'] - consumption
        droneDict['Current_Node_Type'] = 1
        droneDict['Serviced_Nodes'].append(nextStop)
        droneDict['Unservised_Nodes'].remove(nextStop)
        nextStop = nextStation
        pathToStation = nx.shortest_path(myGraph, droneDict['Current_Node'], nextStop)
        edgePathToStation = []
        for i in range(len(pathToStation) - 1):
            edgePathToStation.append((pathToStation[i], pathToStation[i + 1]))
        for edge in edgePathToStation:
            consumption = consumption + edgeConsumptionRateDict[edge] * myGraph[edge[0]][edge[1]]['cost']
            practicalEdgeConsumptionDict[edge] = edgeConsumptionRateDict[edge]
            timeTrack = timeTrack + myGraph[edge[0]][edge[1]]['cost']
            droneDict['Time'].append([timeTrack, timeTrack])
            droneDict['General_Path'].append([edge[1], 'pass'])
        droneDict['General_Path'][len(droneDict['General_Path']) - 1][1] = 'charge'
        droneDict['Current_Node'] = nextStop
        droneDict['Battery'] = droneDict['Battery'] - consumption
        droneDict['Current_Node_Type'] = 0
    
    if droneDict['Current_Node_Type'] == 1:
        while 1:
            feasibleNodes = findFeasibleNodes(myGraph, droneDict, stationNodes, serviceNodeDict, practicalEdgeConsumptionDict, practicalServiceConsumptionDict, droneDict['Battery']/droneDict['Capacity']*100)
            if len(feasibleNodes) > 0:
                nextStop = findClosestNode(myGraph, droneDict['Current_Node'], feasibleNodes)
                pathToNode = nx.shortest_path(myGraph, droneDict['Current_Node'], nextStop)
                edgePathToNode = []
                for i in range(len(pathToNode) - 1):
                    edgePathToNode.append((pathToNode[i], pathToNode[i + 1]))        
                consumption = 0
                for edge in edgePathToNode:
                    consumption = consumption + edgeConsumptionRateDict[edge] * myGraph[edge[0]][edge[1]]['cost']
                    practicalEdgeConsumptionDict[edge] = edgeConsumptionRateDict[edge]
                    timeTrack = timeTrack + myGraph[edge[0]][edge[1]]['cost']
                    droneDict['Time'].append([timeTrack, timeTrack])
                    droneDict['General_Path'].append([edge[1], 'pass'])
                droneDict['General_Path'][len(droneDict['General_Path']) - 1][1] = 'service'            
                timeTrack = timeTrack + serviceNodeDict[droneDict['General_Path'][len(droneDict['General_Path']) - 1][0]]
                droneDict['Time'][len(droneDict['Time']) - 1][1] = droneDict['Time'][len(droneDict['Time']) - 1][1] + serviceNodeDict[droneDict['General_Path'][len(droneDict['General_Path']) - 1][0]]
                consumption = consumption + serviceConsumptionRateDict[node] * serviceNodeDict[node]
                practicalServiceConsumptionDict[node] = serviceConsumptionRateDict[node]
                droneDict['Current_Node'] = nextStop
                droneDict['Battery'] = droneDict['Battery'] - consumption
                droneDict['Current_Node_Type'] = 1
                droneDict['Serviced_Nodes'].append(nextStop)
                droneDict['Unservised_Nodes'].remove(nextStop)
            else:
                consumption = 0
                nextStop = findClosestNode(myGraph, droneDict['Current_Node'], stationNodes)
                pathToStation = nx.shortest_path(myGraph, droneDict['Current_Node'], nextStop)
                edgePathToStation = []
                for i in range(len(pathToStation) - 1):
                    edgePathToStation.append((pathToStation[i], pathToStation[i + 1]))
                for edge in edgePathToStation:
                    consumption = consumption + edgeConsumptionRateDict[edge] * myGraph[edge[0]][edge[1]]['cost']
                    practicalEdgeConsumptionDict[edge] = edgeConsumptionRateDict[edge]
                    timeTrack = timeTrack + myGraph[edge[0]][edge[1]]['cost']
                    droneDict['Time'].append([timeTrack, timeTrack])
                    droneDict['General_Path'].append([edge[1], 'pass'])
                droneDict['General_Path'][len(droneDict['General_Path']) - 1][1] = 'charge'
                droneDict['Current_Node'] = nextStop
                droneDict['Battery'] = droneDict['Battery'] - consumption
                droneDict['Current_Node_Type'] = 0
                break
    if len(droneDict['Unservised_Nodes']) == 0:
        flag = 0
        
totalRunTimeFinish = time.time()        
totalRunTime = totalRunTimeFinish - totalRunTimeStart


workbook = xlsxwriter.Workbook(outputFileName)
worksheet = workbook.add_worksheet('Sheet1')
cell_format = workbook.add_format({'bold': True, 'align': 'center', 'font_color': 'black'})
worksheet.write(0,0, 'NodeID', cell_format)
worksheet.write(0,1, 'Action', cell_format)
worksheet.write(0,2, 'Arrival', cell_format)
worksheet.write(0,3, 'Departure', cell_format)
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'font_color': 'black'})
for i in range(len(droneDict['General_Path'])):
    worksheet.write(i + 1,0, str(droneDict['General_Path'][i][0]), cell_format)
    worksheet.write(i + 1,1, droneDict['General_Path'][i][1], cell_format)
    worksheet.write(i + 1,2, droneDict['Time'][i][0], cell_format)
    worksheet.write(i + 1,3, droneDict['Time'][i][1], cell_format)
workbook.close()

print('############################')
print('Run Time (seconds):')
print(totalRunTime)
