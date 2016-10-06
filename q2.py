import csv
import copy

# @todo remove
import pprint
pp = pprint.PrettyPrinter(indent=4)

className = '' # last column will alwasy be the target class
iMap      = {} # indexMap
data      = {} # @todo data might not be needed
counters  = {}

def addCount(attr, val, cl):
    global counters

    if val not in counters[attr]:
        counters[attr][val] = 1
    else:
        counters[attr][val] += 1

    if cl not in counters[attr+className]:
        counters[attr+className][cl] = 1
    else:
        counters[attr+className][cl] += 1
        
# Read and prepare data
with open('data.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    firstRow = next(reader)
    className = firstRow[-1] # last column will alwasy be the target class
    
    i = 0
    for label in firstRow:
        iMap[i] = label
        data[label] = []
        counters[label] = {}
        counters[label+className] = {}
        i += 1

    print(data)
    print()

    for row in reader:
        i = 0
        for elem in row:
            print(elem)
            data[iMap[i]].append(elem)
            addCount(iMap[i], elem, row[-1])
            i += 1

    # todo remove
    pp.pprint(data)
    pp.pprint(counters)
    
# Calculate Prior
# Use Hashtable to get O(1) access
priors = {}
total = float(len(counters[className]))

for k in counters[className].keys():
    priors[k] = counters[className][k]/total

print("Priors:")
print(priors)

# Calculate conditional probabilities
# for cl in counters[className].keys(): # cl = class
  #  if cl == "Name" or cl == className or cl == "new":
        

        
