# -*- coding: utf-8 -*-
'''
Created on Mon Nov 23 2015

@author: Li Nayu
'''

from __future__ import division
from time import time
import numpy as np

# Part3
def readTrainingData():

	fp = open("c:/Users/Li Nayu/Desktop/Machine Learning/project/HMM-Machine_Learning/NPC/train")

	xTrain = [] # for all of the x data without duplicates
	yTrain = [] # lerning the labels without duplicates

	y = [] # for all the label
	x = [] # for all the observation word sequences

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
				if word not in xTrain:
					xTrain.append(word)
				x.append(word)

		line = fp.readline()

	fp.close()

	return trainingData, xTrain, yTrain, x, y


def countEmissionParameter():

	countEmiss = np.zeros((yTrainLen,xTrainLen))

	for i in range(xTrainLen):
		xTemp = x[i]
		for j in range(yTrainLen):
			yTemp = yTrain[j]
			for k in range(trainingDataLen):
				if trainingData[k] == xTemp:
					if trainingData[k + 1] == yTemp:
						countEmiss[j,i] += 1
	#print countEmiss

	return countEmiss


def emissionParameter():

	ep = np.zeros((yTrainLen,xTrainLen))

	for i in range(yTrainLen):
		for j in range(xTrainLen):
			ep[i,j] = countEmiss[i,j] / (count_y[i] + 1)

	return ep


def countTransitionParameters():

	count_y = np.zeros(yTrainLen)
	countTrans = np.zeros((yTrainLen,yTrainLen))
	for i in range(yLen-1):
		for j in range(yTrainLen):
			if y[i] == yTrain[j]:
				count_y[j] += 1
				yTemp = y[i+1]
				for k in range(yTrainLen):
					if yTemp == yTrain[k]:
						countTrans[j,k] += 1

	# for the 1st start
	for m in range(yTrainLen):
		if yTrain[m] == '':
			count_y[m] += 1
			for n in range(yTrainLen):
				if y[0] == yTrain[n]:
					countTrans[m,n] += 1

	return countTrans, count_y


def transitionParameter():

	tp = np.zeros((yTrainLen,yTrainLen))
	for i in range(yTrainLen):
		for j in range(yTrainLen):
			tp[i,j] = countTrans[i,j] / count_y[i]
	#print tp

	return tp


def readTestData():

	fp = open("c:/Users/Li Nayu/Desktop/Machine Learning/project/HMM-Machine_Learning/NPC/dev.in")

	testData =[]
	line = fp.readline()
	while line:
		list = line.split(' ')
		for word in list:
			if word[-1] == '\n':
				testData.append(word[:-1])
				#print word				
		line = fp.readline()

	fp.close()

	return testData


def Viterbi():

	score = np.zeros((yTrainLen,xInLen))
	path = np.zeros((yTrainLen,xInLen))

	epNew = []

	# initialize
	for i in range(yTrainLen):
		epNew.append(1 / (count_y[i] + 1))
		if valIndex == i:			
			score[valIndex,-1] = 1
			#print valIndex
		else:
			score[i,-1] = 0

	for j in range(xInLen):
		for i in range(yTrainLen):

			if xIn[j] in xTrain:
				scoreTemp = []
				for m in range(xTrainLen):
					if xIn[j] == xTrain[m]:

						for n in range(yTrainLen):
							scoreTemp.append(score[n,j-1]*tp[n,i]*ep[i,m])
						score[i,j] = max(scoreTemp)
						path[i,j] = scoreTemp.index(max(scoreTemp))

			elif xIn[j] == '':
				for m in range(yTrainLen):
					if i == valIndex:
						score[valIndex,j] = 1
					else:
						score[i,j] = 0
				scoreTemp = []
				for n in range(yTrainLen):
					scoreTemp.append(score[n,j-1]*tp[n,valIndex])
				path[:,j] = scoreTemp.index(max(scoreTemp))

			else:
				scoreTemp = []
				for n in range(yTrainLen):
					scoreTemp.append(score[n,j-1]*tp[n,i]*epNew[i])
				score[i,j] = max(scoreTemp)
				path[i,j] = scoreTemp.index(max(scoreTemp))
	#print score

	return path,score


def tagger():

	yOut = np.zeros(xInLen, dtype = int)
	testDataIndex = xInLen - 1
	yOut[testDataIndex] = valIndex
	former = 0
	for i in range(testDataIndex):
		former = path[former,testDataIndex-i]
		yOut[testDataIndex-i-1] = former

	return yOut


def accuracy():

	fp = open("c:/Users/Li Nayu/Desktop/Machine Learning/project/HMM-Machine_Learning/NPC/dev.out")

	yIn = []

	line = fp.readline()
	while line:
		list = line.split(' ')
		for word in list:
			if word[-1] == '\n':
				yIn.append(word[:-1])
		line = fp.readline()

	fp.close()

	right = 0
	error = 0
	yInLen = len(yIn)
	for i in range(yInLen):
		j = yOut[i]
		if yIn[i] == yTrain[j]:
			right += 1
		else:
			error += 1
	print right,error

	accuracy = right / (right + error)

	return accuracy


if __name__ == '__main__':

	t = time() 
 
	trainingData, xTrain, yTrain, x, y = readTrainingData()
	trainingDataLen = len(trainingData) - 1
	yTrainLen = len(yTrain)
	xTrainLen = len(xTrain)
	xLen = len(x)
	yLen = len(y)

	for i in range(yTrainLen):
		if yTrain[i] == '':
			valIndex = i
			#print valIndex

	countEmiss = countEmissionParameter()
	countTrans, count_y = countTransitionParameters()
	ep = emissionParameter()
	tp = transitionParameter()

	xIn = readTestData()
	xInLen = len(xIn)

	path,score = Viterbi()
	yOut = tagger()
	acc = accuracy()
	print acc

	print "total run time:"
	print time()-t