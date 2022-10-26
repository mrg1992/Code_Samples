import networkx as nx
from itertools import combinations
import random
import numpy as np
import math
import copy
import time
import xlsxwriter
import win32com.client as win32
import os
import matplotlib.pyplot as plt

dirPath = os.path.dirname(os.path.abspath(__file__))

totalRunTimeStart = time.time()
#####   Set the input values below:
###############################################
###############################################
[seedList, numOfNodesEdgesAgentsDict, blockPercentList] = [list(range(1, 101)), {100: {300: [3, 6, 9]}, 200: {600: [4, 8, 12]}, 300: {900: [5, 10, 15]}, 400: {1200: [6, 12, 18]}, 500: {1500: [7, 14, 21]}}, [10, 20, 30, 40]]
###############################################
###############################################


def findStop(graph,source, destination, agentsDict, blockedEdges):
    tempStopDetail = {}
    timesOfFirstStop = []
    for i in agentsDict:
        tempStopDetail[i] = [[], 0, 0, [], 0]
        #[0.edgesBeforeBlock, 1.ifArrived, 2.ifBlocked, 3.blockedEdge, timeBeforeStop]
        for edge in agentsDict[i][1]:
            if edge in blockedEdges:
                tempStopDetail[i][2] = 1
                tempStopDetail[i][3] = edge
                break
            else:
                tempStopDetail[i][0].append(edge)
                tempStopDetail[i][4] = tempStopDetail[i][4] + graph[edge[0]][edge[1]]['cost']
                if destination in edge:
                    tempStopDetail[i][1] = 1
                    break
    for i in agentsDict:
        timesOfFirstStop.append(tempStopDetail[i][4])
    return [np.min(timesOfFirstStop), tempStopDetail]



outputFileName = dirPath + '\\ResultOutptRandomGraph.xlsx'
workbook = xlsxwriter.Workbook(outputFileName)
worksheet = workbook.add_worksheet('Sheet1')

merge_format = workbook.add_format({
    'align': 'center',
    'valign': 'vcenter'})
worksheet.merge_range('F1:G1', 'Offline', merge_format)
worksheet.merge_range('H1:I1', 'Online', merge_format)
cell_format = workbook.add_format({'bold': False, 'align': 'center', 'valign': 'vcenter', 'font_color': 'black'})
worksheet.write('J1', 'Online/Offline', cell_format)
worksheet.write(1, 0, 'Seed', cell_format)
worksheet.write(1, 1, 'NoN', cell_format)
worksheet.write(1, 2, 'NoE', cell_format)
worksheet.write(1, 3, 'PoB', cell_format)
worksheet.write(1, 4, 'NoA', cell_format)
worksheet.write(1, 5, 'Runtime(ms)', cell_format)
worksheet.write(1, 6, 'Time of Arrival', cell_format)
worksheet.write(1, 7, 'Runtime(ms)', cell_format)
worksheet.write(1, 8, 'Time of Arrival', cell_format)
worksheet.write(1, 9, 'Time of Arrival Ratio', cell_format)
lineCounter = 2

ratioDict = {}

for numOfNodes in numOfNodesEdgesAgentsDict:
    ratioDict[numOfNodes] = {}
    for numOfEdges in numOfNodesEdgesAgentsDict[numOfNodes]:
        for numOfAgents in numOfNodesEdgesAgentsDict[numOfNodes][numOfEdges]:
            ratioDict[numOfNodes][numOfAgents] = {}
            for blockPercent in blockPercentList:
                ratioDict[numOfNodes][numOfAgents][blockPercent] = []
                for seed in seedList:
                    random.seed(seed)
                    location = {}
                    for i in range(1, numOfNodes + 1):
                        location[i] = [random.randrange(1,101), random.randrange(1,101)]
                        
                    myGraph = nx.Graph()

                    for i in range(1, numOfNodes + 1):
                        myGraph.add_node(i)

                    edgeCombinations = list(combinations(list(myGraph.nodes()),2))
                    allEdges = random.sample(edgeCombinations, numOfEdges)
                    
                    blockedEdges = random.sample(allEdges, math.floor(blockPercent * numOfEdges / 100))
                    fakeBlockededges = copy.deepcopy(blockedEdges)
                    for bEdge in fakeBlockededges:
                        blockedEdges.append((bEdge[1], bEdge[0]))

                    for edge in allEdges:
                        myGraph.add_edge(edge[0], edge[1], cost = math.sqrt((location[edge[0]][0] - location[edge[1]][0])**2 + (location[edge[0]][1] - location[edge[1]][1])**2))

                    offlineGraph = copy.deepcopy(myGraph)
                    offStart = time.time()
                    for edge in blockedEdges:
                        if edge in offlineGraph.edges():
                            offlineGraph.remove_edge(*(edge))
                    while 1:
                        [sourceNode, destinationNode] = random.sample(range(1, numOfNodes + 1), 2)
                        if nx.has_path(offlineGraph, sourceNode, destinationNode):
                            break
                    #offStart = time.time()
                    offlineTime = nx.shortest_path_length(offlineGraph, sourceNode, destinationNode, 'cost')   
                    offEnd = time.time()
                    offlineRunTime = offEnd - offStart

                    myTempGraph = copy.deepcopy(myGraph)

                    onlineStart = time.time()
                    agents = {}
                    for i in range(1, numOfAgents + 1):
                        tempEdgesInPath = []
                        agents[i] = [nx.shortest_path(myTempGraph, sourceNode, destinationNode, 'cost')]
                        for j in range(1, len(agents[i][0])):
                            tempEdgesInPath.append((agents[i][0][j - 1], agents[i][0][j]))
                        agents[i].append(tempEdgesInPath)
                        for edge in tempEdgesInPath:
                            myTempGraph[edge[0]][edge[1]]['cost'] = myTempGraph[edge[0]][edge[1]]['cost'] * 2

                    for edge in list(myTempGraph.edges()):
                        myTempGraph[edge[0]][edge[1]]['cost'] = myGraph[edge[0]][edge[1]]['cost']


                    flag = 1
                    arrivedAgent = -1
                    timeOfArrival = -1000
                    updatedAgents = copy.deepcopy(agents)
                    while flag:
                        [timeOfFirstStop, tempStopDict] = findStop(myTempGraph, sourceNode, destinationNode, updatedAgents, blockedEdges)
                        #[0.edgesBeforeBlock, 1.ifArrived, 2.ifBlocked, 3.blockedEdge, 4.timeBeforeStop]
                        #print('#############')
                        #print(tempStopDict)
                        #print('#############')
    
                        listToRemove = []
                        incompletePathDict = {}
                        complementaryPathDict = {}
                        updatedPathDict = {}
                        for i in tempStopDict:
                            incompletePathDict[i] = [sourceNode]
                            complementaryPathDict = {}
                            if tempStopDict[i][4] == timeOfFirstStop:
                                listToRemove.append(tempStopDict[i][3])
                                if tempStopDict[i][1] == 1:
                                    flag = 0
                                    arrivedAgent = i
                                    timeOfArrival = timeOfFirstStop
                                    arrivalPath = tempStopDict[i][0]
                                    break
                        if flag == 0:
                            break
    
                        for edge in listToRemove:
                            if edge in myTempGraph.edges():
                                myTempGraph.remove_edge(edge[0], edge[1])
        
                        for i in tempStopDict:
        
                            if tempStopDict[i][3] != []:
                                
                                if tempStopDict[i][4] == timeOfFirstStop:
                                    if tempStopDict[i][0] == []:
                                        if nx.has_path(myTempGraph, sourceNode, destinationNode):
                                            updatedPathDict[i] = nx.shortest_path(myTempGraph, sourceNode, destinationNode, 'cost')
                                    else:
                                        for edge in tempStopDict[i][0]:
                                            incompletePathDict[i].append(edge[1])
                                        if nx.has_path(myTempGraph, sourceNode, destinationNode):
                                            complementaryPathDict[i] = nx.shortest_path(myTempGraph, incompletePathDict[i][len(incompletePathDict[i]) - 1], destinationNode, 'cost')
                                            updatedPathDict[i] = incompletePathDict[i]
                                            for j in range(1, len(complementaryPathDict[i])):
                                                updatedPathDict[i].append(complementaryPathDict[i][j])
                                        else:
                                            del(updatedAgents[i])
                                else:
                                    timeTrack = 0
                                    for j in range(len(tempStopDict[i][0])):
                                        timeTrack = timeTrack + myTempGraph[tempStopDict[i][0][j][0]][tempStopDict[i][0][j][1]]['cost']
                                        incompletePathDict[i].append(tempStopDict[i][0][j][1])
                
                                        if timeTrack > timeOfFirstStop:
                                            if nx.has_path(myTempGraph, sourceNode, destinationNode):
                                                #print('#######')
                                                #print(tempStopDict[i][0][j])
                                                #print('#######')
                                                complementaryPathDict[i] =  nx.shortest_path(myTempGraph, tempStopDict[i][0][j][1], destinationNode, 'cost')
                                                updatedPathDict[i] = incompletePathDict[i]
                                                for k in range(1, len(complementaryPathDict[i])):
                                                    updatedPathDict[i].append(complementaryPathDict[i][k])
                                            else:
                                                del(updatedAgents[i])
                                    
                            
                        for i in updatedPathDict:
                            pathNodes = updatedPathDict[i]
                            pathEdges = []
                            for j in range(1, len(pathNodes)):
                                pathEdges.append((pathNodes[j - 1], pathNodes[j]))
                            updatedAgents[i] = [pathNodes, pathEdges]

                    onlineEnd = time.time()
                    onlineRunTime = onlineEnd - onlineStart
                    ratioDict[numOfNodes][numOfAgents][blockPercent].append(timeOfArrival/offlineTime)
                    #print(arrivedAgent)
                    #print([seed, numOfNodes, numOfEdges, blockPercent, timeOfArrival, offlineTime, timeOfArrival/offlineTime])
                    #print(arrivalPath)
                    worksheet.write(lineCounter, 0, seed, cell_format)
                    worksheet.write(lineCounter, 1, numOfNodes, cell_format)
                    worksheet.write(lineCounter, 2, numOfEdges, cell_format)
                    worksheet.write(lineCounter, 3, blockPercent, cell_format)
                    worksheet.write(lineCounter, 4, numOfAgents, cell_format)
                    worksheet.write(lineCounter, 5, format(offlineRunTime * 1000, '.3f'), cell_format)
                    worksheet.write(lineCounter, 6, format(offlineTime, '.3f'), cell_format)
                    worksheet.write(lineCounter, 7, format(onlineRunTime * 1000, '.3f'), cell_format)
                    worksheet.write(lineCounter, 8, format(timeOfArrival, '.3f'), cell_format)
                    worksheet.write(lineCounter, 9, format(timeOfArrival/offlineTime, '.3f'), cell_format)
                    lineCounter = lineCounter + 1
                
workbook.close()

excel = win32.gencache.EnsureDispatch('Excel.Application')
wb = excel.Workbooks.Open(outputFileName)
ws = wb.Worksheets('Sheet1')
ws.Columns.AutoFit()     
wb.Save()
excel.Application.Quit()     

fig_index = 0
markerList = ['ro-', 'bx-', 'g^-']
markerIndex = 0
for numOfNodes in ratioDict:
    for key in numOfNodesEdgesAgentsDict[numOfNodes]:
        numOfEdges = key
    yMaxDict = {}
    yAvgDict = {}
    for numOfAgents in ratioDict[numOfNodes]:
        x = []
        yMaxDict[numOfAgents] = []
        yAvgDict[numOfAgents] = []
        for blockPercent in ratioDict[numOfNodes][numOfAgents]:
            x.append(blockPercent)
            yMaxDict[numOfAgents].append(np.max(ratioDict[numOfNodes][numOfAgents][blockPercent]))
            yAvgDict[numOfAgents].append(np.mean(ratioDict[numOfNodes][numOfAgents][blockPercent]))
    fig_index = fig_index + 1
    plt.figure(fig_index)
    markerIndex = 0
    for  numOfAgents in ratioDict[numOfNodes]:
        myLabel = 'NoA: ' + str(numOfAgents)
        marker =  markerList[(markerIndex % 3)]
        markerIndex = markerIndex + 1
        plt.plot(x, yMaxDict[numOfAgents], marker, label = myLabel)
        plt.xlabel('Percentage of Blockages (%)')
        plt.ylabel('Maximum competitive ratio')
        title = str(numOfNodes) + ' Nodes,  ' + str(numOfEdges) + ' Edges'
        plt.title(title)
        plt.legend(loc = 'upper left')
    plt.show()    
    fig_index = fig_index + 1
    plt.figure(fig_index)
    markerIndex = 0
    for  numOfAgents in ratioDict[numOfNodes]:
        myLabel = 'NoA: ' + str(numOfAgents)
        marker =  markerList[(markerIndex % 3)]
        markerIndex = markerIndex + 1
        plt.plot(x, yAvgDict[numOfAgents], marker, label = myLabel)
        plt.xlabel('Percentage of Blockages (%)')
        plt.ylabel('Average competitive ratio')
        title = str(numOfNodes) + ' Nodes, ' + str(numOfEdges) + ' Edges'
        plt.title(title)
        plt.legend(loc = 'upper left')
    plt.show()
    
totalRunTimeFinish = time.time()

totalRunTime = totalRunTimeFinish - totalRunTimeStart

print("Total RunTime: ")
print(totalRunTime)    
    
    
        



