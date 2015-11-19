import numpy as np
from __future__ import division

def readTrainingData():

	fp = open("c:/Users/Li Nayu/Desktop/Machine Learning/project/NPC/train")

	x = []
	yTrain = []

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
			else:
				trainingData.append(word)
				if word  not in x:
					x.append(word)

		line = fp.readline()

	fp.close()

    #remove the null value
 	yList = []
 	for val in yTrain:
 		if val:
 			yList.append(val)

 	yTrain = yList

	return trainingData, x, yTrain


#(5 pts)Estimate the emission parameters from the training set using MLE
def count():

	trainingData, x, yTrain = readTrainingData()

	#dict_count_y = {}
	#dict_count_y_x = {}

	traingingDataLen = len(trainingData)
	yLen = len(yTrain)
	xLen = len(x)

	count_y = np.zeros(yLen)
	count_y_x = np.zeros((xLen,yLen))

	for i in range(yLen):
		for j in range(traingingDataLen):
			if trainingData[j] == yTrain[i]:
				count_y[i] += 1
	print yTrain
	print count_y

	for i in range(xLen):
		for j in range(yLen):
			for k in range(traingingDataLen - 1):
				if trainingData[k] == x[i]:
					if trainingData[k + 1] == yTrain[j]:
						count_y_x[i,j] += 1

	print count_y_x

	return count_y, count_y_x


#(10 pts)
def MLEForOldWord(count_y,count_y_x):

	xNum = np.shape(count_y_x)[1]
	yNum = np.shape(count_y)[0]

	for k in range(yNum):
		count_y[k] += 1
	prob = np.zeros((yNum,xNum))
	for i in range(yNum):
		for j in range(xNum):
			prob[i,j] = count_y_x[i,j] / count_y[i]
			#print count_y_x

	indexOld = np.argmax(prob,0)
	return indexOld


def tagger():

	trainingData, x, yTrain = readTrainingData()
	count_y, count_y_x = count()
	count_y_x = np.mat(count_y_x)
	count_y_x = count_y_x.T

	devin = open("c:/Users/Li Nayu/Desktop/Machine Learning/project/NPC/dev.in")
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

		if data[i] in x:
			for j in range(len(x)):
				if data[i] == x[j]: 
					indexOld = MLEForOldWord(count_y,count_y_x)
					devout2.append(data[i])
					devout2.append(yTrain[indexOld[j]])
		
		elif data[i] == '':
			devout2.append('')

		else:
			prob = []
			for k in range(len(yTrain)):
				prob.append((1 / (1 + count_y[k])))

			prob = np.mat(prob).T
 			indexNew = np.argmax(prob,0)
			devout2.append(data[i])
			devout2.append(yTrain[indexNew[0]])

	return devout2


def accuracy(devout2):

	trainingData, x, yTrain = readTrainingData()

	fp = open("c:/Users/Li Nayu/Desktop/Machine Learning/project/NPC/dev.out")

	devout =[]
	line = fp.readline()
	while line:
		list = line.split(' ')
		for word in list:
			if word[-1] == '\n':
				devout.append(word[:-1])
				#print word
			else:
				devout.append(word)
		line = fp.readline()

	fp.close()

	right = 0
	error = 0
	for i in range(len(devout)):
		if devout[i] in yTrain:
			if devout[i] == devout2[i]:
				right += 1
			else:
				error += 1

	#print right,err

	accuracy = right / (right + error)
	print accuracy
	return accuracy


devout2 = tagger()
print devout2
acc = accuracy(devout2)