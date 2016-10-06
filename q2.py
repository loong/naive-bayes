import csv
import copy

# @todo remove
import pprint

className = 'region'

pp = pprint.PrettyPrinter(indent=4)

iMap = {} # indexMap
data = {}
counters = {}

def addCount(attr, val):
    global counters

    if attr not in counters[attr]:
        counters[attr][val] = 1
    else:
        counters[attr][val] += 1
        
# Read and prepare data
with open('data.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    firstRow = next(reader)
    
    i = 0
    for label in firstRow:
        iMap[i] = label
        data[label] = []
        counters[label] = {}
        i += 1

    print(data)
    print()

    for row in reader:
        i = 0
        for elem in row:
            data[iMap[i]].append(elem)
            addCount(iMap[i], elem)
            i += 1

    # todo remove
    pp.pprint(data)
    pp.pprint(counters)
    
# Calculate Prior
# Use Hashtable to get O(1) access

count = {}
total = 0.0
for elem in data[className]:
    total += 1
    if elem not in count:
        count[elem] = 1
    else:
        count[elem] += 1

for k in count.keys():
    count[k] = count[k]/total

print(count)

# Calculate conditional probabilities
for attr in iMap.values():
    
    # ignore
    if attr == "Name" or attr == className:
        continue
