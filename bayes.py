""" Naive Bayes Classifier with Laplace Correction"""

import csv
import copy
import math
import pprint

import numpy

######################################################################
## Config constants
CONT_FIELDS = ["new"]           # mark continuous fields

TRAINING_FILE = "data.csv"  # input data
SAMPLE_FILE = "sample.csv"  # data to be classified

pretty = pprint.PrettyPrinter(indent=4)
######################################################################
## globals

className = ''  # last column will alwasy be the target class
counters = {}   # contains counting of attr labels as HT for O(1) access
classCount = {} # contains total counts of attr as HT for O(1) access
cont = {} 
contKeys = []

######################################################################
### Helpers

def normpdf(x, mean, sd):
    """ Normal probability density function taken from
        http://stackoverflow.com/questions/12412895/
    """
    
    var = float(sd)**2
    pi = 3.1415926
    denom = (2*pi*var)**.5
    num = math.exp(-(float(x)-float(mean))**2/(2*var))
    return num/denom


def getCond(attr, label, cl):
    """Gets, which handles the case if there is no data for a combination
    """
    if cl not in cond[attr][label]:
        return 0
    else:
        return cond[attr][label][cl]

# getCondLap similar to getCond, just using laplacian correction
def getCondLap(attr, label, cl):
    if cl not in condLap[attr][label]:
        numAttr = len(counters[className])
        totalNum = float(counters[className][cl])
                
        return 1 / (totalNum + numAttr)
    else:
        return condLap[attr][label][cl]

# addCount is used to count all the needed elements with the help of
# hash tables so we only need to iterate through the data once
def addCount(attr, val, cl):
    global counters

    if attr in CONT_FIELDS:
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
with open(TRAINING_FILE, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    firstRow = next(reader)
    className = firstRow[-1] # last column will alwasy be the target class

    iMap = {} # indexMap
    i = 0
    for attr in firstRow:        
        iMap[i] = attr

        if attr in CONT_FIELDS:
            cont[attr] = {}
        else:
            counters[attr] = {}
            classCount[attr] = {}
            
        i += 1

    # read in all data
    for row in reader:
        i = 0
        for elem in row:
            addCount(iMap[i], elem, row[-1])
            i += 1

    # calc mean and sd for continous attr
    for k in cont.keys():
        for cl in cont[k].keys():
            arr = numpy.array(cont[k][cl])
            
            cont[k][cl] = {}
            cont[k][cl]["mean"] = numpy.mean(arr, axis=0)
            cont[k][cl]["std"] = numpy.std(arr, axis=0)
    
    # pretty.pprint(counters)
    # pretty.pprint(classCount)

    if "new" in cont:
        print "----------------------------------------------------------------------"
        print "  Normal Distributions for discretization"
        print "----------------------------------------------------------------------"        
        pretty.pprint(cont["new"])

# sample
data = {}
contData = {}
with open(SAMPLE_FILE, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    firstRow = next(reader)
    
    iMap = {}
    i = 0
    for attr in firstRow:        
        iMap[i] = attr

        if attr in CONT_FIELDS:
            contData[attr] = []
        else:
            data[attr] = []
            
        i += 1

    for row in reader:
        i = 0
        for elem in row:
            attr = iMap[i]
            if attr in CONT_FIELDS:
                contData[attr].append(elem)
            else:
                data[attr].append(elem)
            i += 1

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
pretty.pprint(priors)

######################################################################
### Calculate conditional probabilities
cond = {}
condLap = {}

for attr in counters:
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
            condLap[attr][label][cl] = (totalClass + 1) / (totalNum + numAttr)

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
            

    for attr in cont:
        for i in range(len(contData[attr])):
            
            val = normpdf(contData[attr][i], cont[attr][cl]["mean"], cont[attr][cl]["std"])
            print "  P(", attr, "=", contData[attr][i], "|", cl, ") = ", val



######################################################################
### Process sample data

keys = data.keys()
numRows = len(data[keys[0]])

# loop through each row indivdually
for i in range(numRows):
    print
    print "----------------------------------------------------------------------"
    print "  Sample Row " + str(i)
    print "----------------------------------------------------------------------"

    rowProbs = []
    rowProbLaps = []
    mapBack = {}
    mapBackLaps = {}

    # get conditional probabilities for each attr to class (here
    # region) pair and then make the product
    for cl in counters[className].keys():
        rowProb = rowProbLap = 1
        
        for k in keys:
            val = data[k][i]

            # get conditional probability
            prop = getCond(k, val, cl)
            propLap = getCondLap(k, val, cl)

            #print "P( "+k+"='"+val+"' | "+className+"='"+cl+"' ) = \t" + str(prop)

            # make product
            rowProb *= prop
            rowProbLap *= propLap
            
        for k in contKeys:
            
            # get conditional probability
            val = contData[k][i]
            prop = normpdf(val, cont[k][cl]["mean"], cont[k][cl]["std"])
            
            #print "P( "+k+"="+val+" | "+className+"='"+cl+"' ) =   \t\t"+str(prop)

            # make product
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


    # do prediciton
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
