import csv
import copy
import math
import numpy

def normpdf(x, mean, sd):
    var = float(sd)**2
    pi = 3.1415926
    denom = (2*pi*var)**.5
    num = math.exp(-(float(x)-float(mean))**2/(2*var))
    return num/denom

# @todo remove
import pprint
pp = pprint.PrettyPrinter(indent=4)

isCont = ["new"]
trainingFile = "data2.csv"
sampleFile = "sample2.csv"

className  = '' # last column will alwasy be the target class
counters   = {}
classCount = {}
cont       = {}

def addCount(attr, val, cl):
    global counters

    if attr in isCont:
        if cl not in cont[attr]:
            cont[attr][cl] = []
        else:
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
        
# Read and prepare data
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
                
    # todo remove
    pp.pprint(counters)
    pp.pprint(classCount)
    print("Continous")
    pp.pprint(cont)
    
    
# Calculate Prior
# Use Hashtable to get O(1) access
priors = {}
total = 0.0

for k in counters[className].keys():
    total += counters[className][k]
    
for k in counters[className].keys():
    priors[k] = counters[className][k]/total

print("Priors:")
print(priors)

# Calculate conditional probabilities
cond = {}

for attr in counters.keys():
    if attr == "Name" or attr == className or attr == "new":
        continue

    cond[attr] = {}
    
    for label in counters[attr]:
        total = counters[attr][label]

        for cl in classCount[attr][label].keys():
            print label + " " + cl + " " + str(classCount[attr][label][cl]),
            print " " + str(total)

            cond[attr][cl] = classCount[attr][label][cl]/float(total)

pp.pprint(cond)

# load sampe data
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

    # todo remove
    pp.pprint(data)
    
keys = data.keys()
contKeys = contData.keys()
numRows = len(data[keys[0]])

for i in range(numRows):
    print "----------------------------------------------------------------------"
    print "Sample Row " + str(i)
    print "----------------------------------------------------------------------"
    for cl in counters[className].keys():
        for k in keys:
            val = data[k][i]
            prop = cond[k][cl]

            print "P( "+k+"='"+val+"' | "+className+"='"+cl+"' ) = \t"+str(prop)

        for k in contKeys:
            val = contData[k][i]
            prop = normpdf(contData[k][i], cont[k][cl]["mean"], cont[k][cl]["std"])
            
            print "P( "+k+"="+val+" | "+className+"='"+cl+"' ) =   \t\t"+str(prop)
    
