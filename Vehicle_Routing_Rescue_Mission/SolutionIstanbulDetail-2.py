import networkx as nx
import random
import numpy as np
import math
import copy
import time
import os
import matplotlib.pyplot as plt
import xlrd

dirPath = os.path.dirname(os.path.abspath(__file__))
inputName = dirPath + '\\349_nodes.xlsx'

totalRunTimeStart = time.time()

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


workBook = xlrd.open_workbook(inputName)
sheet = workBook.sheet_by_index(0)
numOfRows = sheet.nrows

myGraph = nx.Graph()
for i in range(1, numOfRows):
    myGraph.add_node(i)
numOfNodes = numOfRows - 1
print('Number of Nodes:')
print(numOfNodes)
allEdges = []
for i in range(1, numOfRows):
    for j in range(i, numOfRows):
        if sheet.cell_value(i, j) < 100000:
            myGraph.add_edge(i,j, cost = sheet.cell_value(i, j))
            allEdges.append((i,j))
numOfEdges = len(allEdges)
print('Number of Edges:')
print(numOfEdges)

ratioDict = {}

numOfAgents = 10
#tst = 0
for blockPercent in [10, 20, 30, 40]:
    ratioDict[blockPercent] = []
    for seed in range(1, 101):
        random.seed(seed)
        blockedEdges = random.sample(allEdges, math.floor(blockPercent * numOfEdges / 100))
        fakeBlockededges = copy.deepcopy(blockedEdges)
        for bEdge in fakeBlockededges:
            blockedEdges.append((bEdge[1], bEdge[0]))

        offlineGraph = copy.deepcopy(myGraph)
        offStart = time.time()
        for edge in blockedEdges:
            if edge in offlineGraph.edges():
                offlineGraph.remove_edge(*(edge))
        while 1:
            [sourceNode, destinationNode] = random.sample(range(1, numOfNodes + 1), 2)
            if nx.has_path(offlineGraph, sourceNode, destinationNode):
                #print('yes')
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
        ratioDict[blockPercent].append(timeOfArrival/offlineTime)
        #tst = tst + 1
        #print(tst)

x = []
yMax = []
yAvg = []
for blockPercent in ratioDict:
    x.append(blockPercent)
    yMax.append(np.max(ratioDict[blockPercent]))
    yAvg.append(np.mean(ratioDict[blockPercent]))
plt.figure(1)
plt.plot(x, yMax, 'rx-', label = 'Max')
plt.plot(x, yAvg, 'bo-', label = 'Avg')
plt.xlabel('Percentage of blockages (%)')
plt.ylabel('Competitive ratio')
myTitle = 'Istanbul detailed network - ' + str(numOfAgents) + ' first-responder teams'
plt.title(myTitle)
plt.legend(loc = 'upper left')
plt.show()
    


totalRunTimeFinish = time.time()

totalRunTime = totalRunTimeFinish - totalRunTimeStart

print("Total RunTime: ")
print(totalRunTime)    