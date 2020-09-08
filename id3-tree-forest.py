#Hrvoje Abramovic 0036506160
#Umjetna inteligencija lab 3
import math
import random
import sys


## Imena atributa, struktura podataka koje omogucu O(1) mapiranje ime -> indeks i indeks -> ime
featureIndexes = {} ## mapping featureName -> featureIndex in table -- filled in loadTrainData
possibleValues = [] ## all values that encountered in training for a certain feature -- filled in loadTrainData
header = [] ## header feature names

## Funkcija za brojanje razlicitih vrijednosti nekog atributa - vraca dictionary oblika {vrijednost : broj_pojavljivanja}
def countValuesOfFeature(dataMatrix, feature):
    
    valuesDict = {}
    featureId = featureIndexes[feature]
    
    for  line in dataMatrix:
        
        if line[featureId] not in valuesDict:
            valuesDict.update({line[featureId]:1})
        else:
            valuesDict.update( {line[featureId] : valuesDict[line[featureId]]+1} )
            
    return valuesDict

## Funkcija koja racuna entropiju zadnjeg stupca zadane matrice, vraca broj
def dataMatrixEntropy(dataMatrix):
    
    valuesDict = countValuesOfFeature(dataMatrix, header[-1])

    entropy = 0
    
    for num in valuesDict.values():
        entropy -= num/len(dataMatrix) * math.log((num/len(dataMatrix)),2)
    
    return entropy


## Funkcija koja za zadani put i ime datoteke vraca configuracijske parametre
def getConfiguration(confPath):
    
    with open(confPath, 'r', encoding = 'utf-8') as confFile:
        configuration = confFile.readlines()
    
    paramValues = ['test', 'ID3', -1, 1, 1, 1]
    paramNames = ['mode', 'model', 'max_depth', 'num_trees', 'feature_ratio', 'example_ratio']
    
    
    for line in configuration:
        (name, value) = line.strip().split('=')
        
        paramIndex = paramNames.index(name)
        paramValues[paramIndex] = value
    
    return paramValues


## Funckija za ucitavanje skupa podataka za treniranje
def loadTrainData(trainPath):
    
    with open(trainPath, 'r', encoding = 'utf-8') as trainFile:
        trainData = trainFile.readlines()
        
    index = 0
    
    for feature in trainData[0].strip().split(','):
        featureIndexes.update({feature:index})
        header.append(feature)
        possibleValues.append(set())
        index+=1
        
    trainMatrix = []
    
    for line in trainData[1:]:
        line = line.strip()
        values = line.split(',')
        for i in  range(len(values)):
            if values[i] not in possibleValues[i]:
                possibleValues[i].add(values[i])
                
        trainMatrix.append(values)
        
    return trainMatrix


## Funckija za ucitvanje podataka za testiranje
def loadTestData(testPath):
    
    with open(testPath, 'r', encoding = 'utf-8') as testFile:
        testData = testFile.readlines()
    
    testMatrix = []
    groundTruth = []
    
    for line in testData[1:]:
        values = line.strip().split(',')
        testMatrix.append(values)
        groundTruth.append(values[-1])
    
    return (testMatrix, groundTruth)


## Vraca tavlicu koju cine retci tablice table, kojoj je feature = value
def tableSelect(table, feature, value):
    
    featureIndex = featureIndexes[feature]
    
    newTable = []
    
    
    for line in table:
        if line[featureIndex] == value:
            newTable.append(line)
    
    
    return newTable
    
## Izracunava IG za zadanu matricu i atribut feature
def computeIG(dataMatrix, feature):
    
    IG = dataMatrixEntropy(dataMatrix)
    lenAll = len(dataMatrix)

    for value in possibleValues[featureIndexes[feature]]:
        
        tempTable = tableSelect(dataMatrix, feature, value)
        
        if len(tempTable) == 0:
            continue
        
        IG -= (len(tempTable)/lenAll)*dataMatrixEntropy(tempTable)
        
    
    
    return IG

## Klasa node koja je cvor stabla
class node:
    
    def __init__(self, feature, mostCommon = None, depth = None):
        self.feature = feature
        self.subtrees = {}
        self.mostCommon  = mostCommon
        self.depth = depth
        
        
    def addChild(self, value, node):
        self.subtrees.update({value:node})
        return
    
    
## Klasa ID3 koja predstavlja jedno stablo
class ID3:
    
    def __init__(self, mode, maxDepth):
        
        self.mode = mode
        self.maxDepth = maxDepth
        self.tree = None
        
           
    ## rekurzivna funkcija koja gradi stablo   
    def id3(self, dataMatrix, notVisited,depth, parentMostCommon = None ):
        
        if not dataMatrix:
            return parentMostCommon
        
        goalFreq = countValuesOfFeature(dataMatrix, header[-1])
        
        mostCommon = None
        mostCommonNum = -1
        
        for value in goalFreq:
            if goalFreq[value] >= mostCommonNum:
                if mostCommon is not None and goalFreq[value] == mostCommonNum and value > mostCommon:
                    continue
                mostCommon = value
                mostCommonNum = goalFreq[value]
        
        #mostCommon = max(goalFreq, key = goalFreq.get)
        
        if not notVisited or goalFreq[mostCommon] == len(dataMatrix):
            return mostCommon
        
        if depth == self.maxDepth:
            return mostCommon
        
        
        maxIG = -1000
        selectedFeature = None
        
        for feature in notVisited:
            tempIG = computeIG(dataMatrix, feature)
            tempIG = round(tempIG, 7)
            if self.mode != "test":
                print("IG("+feature+") = "+str(tempIG), end = "  ")
            if maxIG <= tempIG:
                if selectedFeature is not None and maxIG == tempIG and feature > selectedFeature:
                    continue
                selectedFeature = feature
                maxIG = tempIG
        
        if self.mode != "test":
            print()
        newNode = node(selectedFeature, mostCommon, depth)
        newNotVisited = notVisited.copy()
        newNotVisited.remove(selectedFeature)
        
        for value in possibleValues[featureIndexes[selectedFeature]]:
            tempTable = tableSelect(dataMatrix, selectedFeature, value)
            #if len(tempTable) == 0:
            #    continue
            tempNode = self.id3(tempTable, newNotVisited, depth + 1, mostCommon)
            newNode.addChild(value, tempNode)
            
        return newNode
        
        
    ## funkcija za treniranje
    def fit(self, dataMatrix, features = "ALL"):
        notVisited = set()
        if features == "ALL":
            notVisited.update(header[:-1])
        else:
            notVisited.update(features)
        self.tree = self.id3(dataMatrix, notVisited, 0)
        return
        
    ## funckija za predikciju nad jednim primjerom
    def predictSingle(self, values):
        
        currentNode = self.tree
        
        while isinstance(currentNode, node):
            
            idNow = featureIndexes[currentNode.feature]
            
            if values[idNow] not in currentNode.subtrees:
                return currentNode.mostCommon
            
            currentNode = currentNode.subtrees[values[idNow]]
            
            
        return currentNode
        
        
        
    ## funkcija za predikciju nad skupom primjera
    def predict(self, dataMatrix):
        predictions = []
        for example in dataMatrix:
            predictions.append(self.predictSingle(example))
            
            
        return predictions
   

## klasa za Random forest
class RF:
    def __init__(self, mode, maxDepth, numTrees, featureRatio, exampleRatio):
        self.mode = mode
        self.maxDepth = maxDepth
        self.numTrees = numTrees
        self.featureRatio = featureRatio
        self.exampleRatio = exampleRatio
        self.ID3s = []
        
    ## Funkcija za treniranje
    def fit(self, dataMatrix):
        numFeatures = round(self.featureRatio * (len(header)-1))
        numExamples = round(self.exampleRatio * len(dataMatrix))
        
        for i in range(self.numTrees):
            featureSubset = random.sample(header[:-1], numFeatures)
            exampleSubset = random.sample(range(len(dataMatrix)), numExamples)
            
            for feature in featureSubset:
                print(feature, end = ' ')
            print()
            
            for example in exampleSubset:
                print(example, end = ' ')
            print()
            
            tempDataMatrix = [dataMatrix[e] for e in exampleSubset]
            
            
            tempTree = ID3(self.mode, self.maxDepth)
            tempTree.fit(tempDataMatrix, featureSubset)
            
            self.ID3s.append(tempTree)
            
        return
    
    ## Funkcija za predikciju
    def predict(self, dataMatrix):
        predictions = []
        for example in dataMatrix:
            prediction = {}
            for tree in self.ID3s:
                tempPred = tree.predictSingle(example)
                if tempPred not in prediction:
                    prediction.update({tempPred : 1})
                else:
                    prediction.update({tempPred :  prediction[tempPred]+1})
                    
            mostCommonNum = -1
            mostCommonPred = None
            
            for pred in prediction:
                if prediction[pred] >= mostCommonNum:
                    if mostCommonPred is not None and prediction[pred] == mostCommonNum and pred > mostCommonPred:
                        continue
                    mostCommonPred = pred
                    mostCommonNum =  prediction[pred]
                    
            predictions.append(mostCommonPred)
            
        return predictions

## Funkcija koja za zadane liste predictions i ground Truth ispisuje matricu zabune
def printConfusion(predictions, groundTruth):
    
    values = set()
    
    for i in range(len(predictions)):
        values.add(predictions[i])
        values.add(groundTruth[i])
    
    
    
    values = list(values)
    #values = possibleValues[-1].copy()
    #values = list(possibleValues[-1])
    values.sort()
    indexMapping = {}
    
    
    for i in range(len(values)):
        indexMapping.update({values[i]:i})
    
    
    confusionMatrix = [[0 for i in range(len(values))] for j in range(len(values))]

        
    for i in range(len(predictions)):
        row = indexMapping[groundTruth[i]]
        col = indexMapping[predictions[i]]
        confusionMatrix[row][col]+=1
        
    
    for line in confusionMatrix:
        for i in line:
            print(i, end = ' ')
            
        print()
    
    return

## Funkcija koja za zadan pocetni cvor ispisuje stablo po razinama
def printTree(rootNode):
    
    bfs = [rootNode]
    print('0:'+rootNode.feature, end = '')
    while bfs:
        currentNode = bfs.pop(0)
        if currentNode.depth != 0:
            print(', '+str(currentNode.depth)+':'+currentNode.feature, end = '')
        for sub in currentNode.subtrees.values():
            if isinstance(sub, node):
                bfs.append(sub)
                     
    print()
    return  

## Funkcija koja ispisuje listu        
def printPredictions(predictions):
    for prediction in predictions:
        print(prediction, end = ' ')
    print()        
    return

## Funkcija koja ispisuje tocnost algoritma na temelju predictions i groundTruth
def getAccuracy(predictions, groundTruth):
    correct = 0
    for (pred, truth) in zip(predictions, groundTruth):
        if pred == truth:
            correct+=1
    return correct/len(groundTruth)

## Glavna funckija
def main():
    parameters = sys.argv
    
    trainPath = parameters[1]
    testPath = parameters[2]
    confPath = parameters[3]
    
    (mode, model, maxDepth, numTrees, featureRatio, exampleRatio) = getConfiguration(confPath)
    maxDepth = int(maxDepth)
    numTrees = int(numTrees)
    featureRatio = float(featureRatio)
    exampleRatio = float(exampleRatio)
    trainData = loadTrainData(trainPath)
    (testData, groundTruth) = loadTestData(testPath)
    
    ## MATRICA ZABUNE I UPLOADATI RJ
    #print(header)
    #print(model + "!")    
    if model == 'ID3':
        myModel = ID3(mode, maxDepth)
        myModel.fit(trainData)
        predictions = myModel.predict(testData)
        printTree(myModel.tree)
        printPredictions(predictions)
        print(getAccuracy(predictions, groundTruth))
        printConfusion(predictions, groundTruth)
    else:
        myModel = RF(mode, maxDepth, numTrees, featureRatio, exampleRatio)
        myModel.fit(trainData)
        predictions = myModel.predict(testData)
        printPredictions(predictions)
        print(getAccuracy(predictions, groundTruth))
        printConfusion(predictions, groundTruth)

    return

main()