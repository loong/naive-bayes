######################################################################
### @author Long Hoang <long@mindworker.de>
###
### itsc: lhoang
### stuid: 20149163
###
### Reachable via email Whatsapp +852 53292129

import csv
import copy
import math
import numpy

import pprint
pp = pprint.PrettyPrinter(indent=4)

######################################################################
## configs values
isCont = ["new"]           # mark continuous fields

trainingFile = "data2.csv"  # input data
sampleFile = "sample2.csv"  # data to be classified

######################################################################
## globals

className  = '' # last column will alwasy be the target class
counters   = {} # contains counting of attr labels as HT for O(1) access
classCount = {} # contains total counts of attr as HT for O(1) access
cont       = {} 
contKeys   = []
######################################################################
### Helpers

# Normpdf taken from http://stackoverflow.com/questions/12412895/calculate-probability-in-normal-distribution-given-mean-std-in-python
def normpdf(x, mean, sd):
    var = float(sd)**2
    pi = 3.1415926
    denom = (2*pi*var)**.5
    num = math.exp(-(float(x)-float(mean))**2/(2*var))
    return num/denom

def getCond(attr, label, cl):
    if cl not in cond[attr][label]:
        return 0
    else:
        return cond[attr][label][cl]

def getCondLap(attr, label, cl):
    if cl not in condLap[attr][label]:
        numAttr = len(counters[className])
        totalNum = float(counters[className][cl])
                
        return 1 / (totalNum + numAttr)
    else:
        return condLap[attr][label][cl]

def addCount(attr, val, cl):
    global counters

    if attr in isCont:
        if cl not in cont[attr]:
            cont[attr][cl] = []

        cont[attr][cl].append(float(val))
        return
        

    if val not in counters[attr]:
        counters[attr][val] = 1
    else:
        counters[attr][val] += 1

    if attr == className:
        return

    if val not in classCount[attr]:
        classCount[attr][val] = {}

    if cl not in classCount[attr][val]:
        classCount[attr][val][cl] = 1
    else:
        classCount[attr][val][cl] += 1
        
######################################################################
### Read and prepare data

# training
with open(trainingFile, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    firstRow = next(reader)
    className = firstRow[-1] # last column will alwasy be the target class

    iMap = {} # indexMap
    i = 0
    for attr in firstRow:        
        iMap[i] = attr

        if attr in isCont:
            cont[attr] = {}
        else:
            counters[attr] = {}
            classCount[attr] = {}
            
        i += 1

    for row in reader:
        i = 0
        for elem in row:
            addCount(iMap[i], elem, row[-1])
            i += 1

    # calc mean and sd
    for k in cont.keys():
        for cl in cont[k].keys():
            arr = numpy.array(cont[k][cl])
            
            cont[k][cl] = {}
            cont[k][cl]["mean"] = numpy.mean(arr, axis=0)
            cont[k][cl]["std"] = numpy.std(arr, axis=0)
    
    # pp.pprint(counters)
    # pp.pprint(classCount)

    if "new" in cont:
        print "----------------------------------------------------------------------"
        print "  Normal Distributions for discretization"
        print "----------------------------------------------------------------------"        
        pp.pprint(cont["new"])

# sample
data = {}
contData = {}
with open(sampleFile, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    firstRow = next(reader)
    
    iMap = {}
    i = 0
    for attr in firstRow:        
        iMap[i] = attr

        if attr in isCont:
            contData[attr] = []
        else:
            data[attr] = []
            
        i += 1

    for row in reader:
        i = 0
        for elem in row:
            attr = iMap[i]
            if attr in isCont:
                contData[attr].append(elem)
            else:
                data[attr].append(elem)
            i += 1

    # pp.pprint(data)

    contKeys = contData.keys()
    
######################################################################
### Calculate Prior
###
### Use Hashtable to get O(1) access
priors = {}
total = 0.0

for k in counters[className].keys():
    total += counters[className][k]
    
for k in counters[className].keys():
    priors[k] = counters[className][k]/total
    
print "----------------------------------------------------------------------"
print "  Priors"
print "----------------------------------------------------------------------"
pp.pprint(priors)

######################################################################
### Calculate conditional probabilities
cond = {}
condLap = {}

for attr in counters.keys():
    if attr == "Name" or attr == className or attr == "new":
        continue

    cond[attr] = {}
    condLap[attr] = {}
    
    for label in counters[attr]:
        cond[attr][label] = {}
        condLap[attr][label] = {}
        
        for cl in classCount[attr][label].keys():
            numAttr = len(counters[className])
            totalClass = classCount[attr][label][cl]
            totalNum = float(counters[className][cl])
            cond[attr][label][cl] = totalClass / totalNum
            condLap[attr][label][cl] = (totalClass + 1 ) / (totalNum + numAttr)

print "----------------------------------------------------------------------"
print "  Conditional Probabilities"
print "----------------------------------------------------------------------"

for cl in counters[className].keys():
    print "Class ", cl

    for attr in classCount.keys():
        for label in classCount[attr]:
            val = getCond(attr, label, cl)
            print "  P(", attr, "=", label, "|", cl, ") = ", val

    for attr in cont:
        for i in range(len(contData[attr])):

            val = normpdf(contData[attr][i], cont[attr][cl]["mean"], cont[attr][cl]["std"])
            print "  P(", attr, "=", contData[attr][i], "|", cl, ") = ", val
        
        
print "----------------------------------------------------------------------"
print "  Conditional Probabilities with Laplace according to lecture notes"
print "----------------------------------------------------------------------"

for cl in counters[className].keys():
    print "Class ", cl

    for attr in classCount.keys():
        for label in classCount[attr]:
            val = getCondLap(attr, label, cl)
            print "  P(", attr, "=", label, "|", cl, ") = ", val

    
keys = data.keys()
numRows = len(data[keys[0]])


for i in range(numRows):
    print
    print "----------------------------------------------------------------------"
    print "  Sample Row " + str(i)
    print "----------------------------------------------------------------------"

    rowProbs = []
    rowProbLaps = []
    mapBack = {}
    mapBackLaps = {}
    
    for cl in counters[className].keys():
        rowProb = rowProbLap = 1
        
        for k in keys:
            val = data[k][i]

            prop = getCond(k, val, cl)
            propLap = getCondLap(k, val, cl)

            #print "P( "+k+"='"+val+"' | "+className+"='"+cl+"' ) = \t" + str(prop)
            rowProb *= prop
            rowProbLap *= propLap
            
        for k in contKeys:
            val = contData[k][i]
            prop = normpdf(val, cont[k][cl]["mean"], cont[k][cl]["std"])
            
            #print "P( "+k+"="+val+" | "+className+"='"+cl+"' ) =   \t\t"+str(prop)
            rowProb *= prop
            rowProbLap *= prop

        p = rowProb*priors[cl]
        pLap = rowProbLap*priors[cl]
        rowProbs.append(p)
        rowProbLaps.append(pLap)

        mapBack[p] = cl
        mapBackLaps[pLap] = cl

        print "P( sample |", cl, ") =", rowProb
        print "P( sample |", cl, ") =", rowProbLap, "# with laplace"

    m = max(rowProbs)
    print
    print "No correction:"
    print "--------------"
    print "max of", rowProbs, "=>", m
    print "Prediction =>", mapBack[m]

    m = max(rowProbLaps)
    print
    print "With correction:"
    print "----------------"
    print "max of", rowProbLaps, "=>", m
    print "Prediction =>", mapBackLaps[m]
