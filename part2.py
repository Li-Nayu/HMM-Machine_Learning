# -*- coding: utf-8 -*-
'''
Created on Mon Nov 23 2015

@author: Li Nayu
'''

from __future__ import division
from time import time 
import numpy as np


# import training data and learn
def readTrainingData():

	fp = open("c:/Users/Li Nayu/Desktop/Machine Learning/project/HMM-Machine_Learning/POS/train")

	xTrain = []
	yTrain = []
	y = []

	# to get distinct y=>yTrain, distinct x =>xTrain, and all the training data
	trainingData =[]
	line = fp.readline()
	while line:
		list = line.split(' ')
		for word in list:
			if word[-1] == '\n':
				trainingData.append(word[:-1])
				#print word
				if word[:-1] not in yTrain:
					yTrain.append(word[:-1])
				y.append(word[:-1])
			else:
				trainingData.append(word)
				if word  not in xTrain:
					xTrain.append(word)

		line = fp.readline()

	fp.close()

    # remove the null value
 	yList = []
 	for val in yTrain:
 		if val:
 			yList.append(val)
 	yTrain = yList

	return trainingData, xTrain, yTrain, y


# Estimate the emission parameters from the training set using MLE
def count():

	length = len(y)

	count_y = np.zeros(yLen)
	count_y_x = np.zeros((xLen,yLen))

	for i in range(yLen):
		yTemp = yTrain[i]
		for j in range(length):
			if y[j] == yTemp:
				count_y[i] += 1
	#print yTrain
	#print count_y

	for i in range(xLen):
		xTemp = xTrain[i]
		for j in range(yLen):
			yTemp = yTrain[j]
			for k in range(trainingDataLen):
				if trainingData[k] == xTemp:
					if trainingData[k + 1] == yTemp:
						count_y_x[i,j] += 1

	#print count_y_x

	return count_y, count_y_x


def MLEForOldWord():

	xNum = np.shape(count_y_x)[1]
	yNum = np.shape(count_y)[0]

	prob = np.zeros((yNum,xNum))
	for i in range(yNum):
		for j in range(xNum):
			prob[i,j] = count_y_x[i,j] / (count_y[i] + 1)
			#print count_y_x

	indexOld = np.argmax(prob,0)
	return indexOld


def MLEForNewWord():
	
	prob = []
	for k in range(yLen):
		prob.append((1 / (1 + count_y[k])))
	prob = np.mat(prob)
 	indexNew = np.argmax(prob)

 	return indexNew


def tagger():

	devin = open("c:/Users/Li Nayu/Desktop/Machine Learning/project/HMM-Machine_Learning/POS/dev.in")
	data =[]
	line = devin.readline()
	while line:
		list = line.split(' ')
		for word in list:
			if word[-1] == '\n':
				data.append(word[:-1])
		line = devin.readline()
	devin.close()
	#print data

	devout2 = []

	for i in range(len(data)):

		if data[i] in xTrain:
			for j in range(xLen):
				if data[i] == xTrain[j]: 
					devout2.append(data[i])
					devout2.append(yTrain[indexOld[j]])		
		elif data[i] == '':
			devout2.append('')
		else:
			devout2.append(data[i])
			devout2.append(yTrain[indexNew])

	return devout2


def accuracy():

	fp = open("c:/Users/Li Nayu/Desktop/Machine Learning/project/HMM-Machine_Learning/POS/dev.out")

	devout1 =[]
	line = fp.readline()
	while line:
		list = line.split(' ')
		for word in list:
			if word[-1] == '\n':
				devout1.append(word[:-1])
				#print word
			else:
				devout1.append(word)
		line = fp.readline()

	fp.close()

	right = 0
	error = 0
	for i in range(len(devout1)):
		if devout1[i] in yTrain:
			if devout1[i] == devout2[i]:
				right += 1
			else:
				error += 1
	print right,error

	accuracy = right / (right + error)

	return accuracy


if __name__ == "__main__":

	t = time() 

	trainingData, xTrain, yTrain, y = readTrainingData()
	trainingDataLen = len(trainingData) - 1
	yLen = len(yTrain)
	xLen = len(xTrain)

	count_y,count_y_x = count()
	count_y_x = np.mat(count_y_x).T

	indexOld = MLEForOldWord()
	indexNew = MLEForNewWord()
	devout2 = tagger()
	
	acc = accuracy()
	print acc

	print "total run time:"
	print time()-t