# Naive Bayes Classifier with Laplacian Correction

This project provides a naive bayes classifier features:
 - Flexible Data Input
 - Laplacian Correction
 - Hashtable Counting
 - Gaussian Distribution Modeling for Continuous Values

## How to use it

### Install prerequisite
```
pip install -r requirements.txt
```

### Run classifier
You need python 2.7, and the classifier can be run as follows:
```
python bayes.py
```

Note: `data.csv` is used for training and `sample.csv` is used for prediction.

## About the features

### Flexible Data Input
The classifier accept any data in table form.

#### Working with Continous Values
By default data is used as nominal / discrete values. If continuous values are used, you must add the name of the column to the `isCont` list in the code under `config values`.

Given are two different data sets `data1.csv` and `data2.csv` for demonstration.

### Laplacian Correction
Laplacian Correction is used to avoid distortion caused by zero-occurences.

### Hashtable Counting
Efficient counting with three levels of hashtables, so that all counting can be done in a single data scan.

### Gaussian Distribution Modeling for Continuous Values
Continuous data are fitted into a Normal distribution. The PDF of resulting Normal distribution, will then be used instead of the conditional probability.