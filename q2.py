import csv
import copy

# @todo remove
import pprint
pp = pprint.PrettyPrinter(indent=4)

className = '' # last column will alwasy be the target class
iMap      = {} # indexMap
data      = {} # @todo data might not be needed
counters  = {}
classCount = {}

def addCount(attr, label, cl):
    global counters

    if attr == "Name" or attr == "new":
        return

    if label not in counters[attr]:
        counters[attr][label] = 1
    else:
        counters[attr][label] += 1

    if attr == className:
        return

    if label not in classCount[attr]:
        classCount[attr][label] = {}

    if cl not in classCount[attr][label]:
        classCount[attr][label][cl] = 1
    else:
        classCount[attr][label][cl] += 1
        
# Read and prepare data
with open('data.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    firstRow = next(reader)
    className = firstRow[-1] # last column will alwasy be the target class
    
    i = 0
    for attr in firstRow:        
        iMap[i] = attr
        data[attr] = []
        counters[attr] = {}
        classCount[attr] = {}
        i += 1

    for row in reader:
        i = 0
        for elem in row:
            print(elem)
            data[iMap[i]].append(elem)
            addCount(iMap[i], elem, row[-1])
            i += 1

    # todo remove
    pp.pprint(counters)
    pp.pprint(classCount)
    
    
# Calculate Prior
# Use Hashtable to get O(1) access
priors = {}
total = float(len(counters[className]))

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
            cond[attr][cl] = classCount[attr][label][cl]/float(total)

pp.pprint(cond)
