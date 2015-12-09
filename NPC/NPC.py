import numpy as np
import math
import re

# ~~~~~~~~~~~~~~~~~~~~~~~~~~Part 2~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_sentence(file,t):
	f=open(file,'r')
	x=[]
	y=[]
	n=0 #number of sentences
	xtemp=[]
	ytemp=[]
	if t=='in':
		lines=[line.strip() for line in f]
		for i in range(len(lines)):
			if len(lines[i])!=0:
				xtemp.append(lines[i])
			else:
				x.append(xtemp)
				# n+=1
				xtemp=[]
		return x
	else:
		lines=[line.split() for line in f]
		for i in range(len(lines)):
			if len(lines[i])!=0:
				xtemp.append(lines[i][0])
				ytemp.append(lines[i][1])
			else:
				x.append(xtemp)
				y.append(ytemp)
				# n+=1
				xtemp=[]
				ytemp=[]
		return x,y


def emission_para_est(xtrain1,ytrain1,xtest1):
	xtrain=[]
	ytrain=[]
	for i in range(len(xtrain1)):
		for j in range(len(xtrain1[i])):
			xtrain.append(xtrain1[i][j])
			ytrain.append(ytrain1[i][j])
	xtest=[]
	for i in range(len(xtest1)):
		for j in range(len(xtest1[i])):
			xtest.append(xtest1[i][j])
	ydistinct=[]
	ycount={}
	for i in ytrain:
		if i not in ydistinct:
			ydistinct.append(i)
			ycount[i]=1
		else: 
			ycount[i]+=1
	xtraindistinct=[]
	for i in xtrain:
		if i not in xtraindistinct:
			xtraindistinct.append(i)
	xtestdistinct=[]
	for i in xtest:
		if i not in xtestdistinct:
			xtestdistinct.append(i)
	xnewdistinct=[]
	for i in xtestdistinct:
		if i not in xtraindistinct:
			xnewdistinct.append(i)	
	xalldistinct=xtraindistinct+xnewdistinct
	
	# print len(ytrain),len(xtraindistinct),len(xnewdistinct),len(xtestdistinct),len(xalldistinct)
	e={}
	count={}
	for i in xalldistinct:
		e[i]={}
		count[i]={}
		for j in ydistinct:
			e[i][j]=0
			count[i][j]=ycount[j]
	for i in range(len(xtrain)):
		e[xtrain[i]][ytrain[i]]+=1
	for i in xtestdistinct:
		if i in xtraindistinct: 
			for j in ydistinct:
				count[i][j]+=1
		else:
			for j in ydistinct:
				count[i][j]+=1
				e[i][j]=1
	for i in xalldistinct:
		for j in ydistinct:
			e[i][j]=1.0*e[i][j]/count[i][j]
	return e,ydistinct,xalldistinct


def tagger(xtest,e,yall,xall,outputfile=''):
	if outputfile!='':
		fo=open(outputfile,'w+')

		y=[]
		for i in range(len(xtest)):
			y.append([])
			for j in xtest[i]:
				argmax=max(e[j], key=e[j].get)
				y[i].append(argmax)
				fo.write(j+' '+argmax+'\n')
			fo.write('\n')

		fo.close()
		return y
	else:
		y=[]
		for i in range(len(xtest)):
			y.append([])
			for j in xtest[i]:
				argmax=max(e[j], key=e[j].get)
				y[i].append(argmax)
		return y


def accuracy_for_test(ytag,ytest,xtest):
	correct=0
	total=0
	for i in range(len(ytest)):
		for j in range(len(ytest[i])):
			total+=1
			if ytag[i][j]==ytest[i][j]:
				correct+=1
			else:
				print xtest[i][j],ytest[i][j],ytag[i][j]
	accuracy=1.0*correct/total
	return accuracy


def accuracy(ytag,ytest):
	correct=0
	total=0
	for i in range(len(ytest)):
		for j in range(len(ytest[i])):
			total+=1
			if ytag[i][j]==ytest[i][j]:
				correct+=1
	accuracy=1.0*correct/total
	return accuracy


# ~~~~~~~~~~~~~~~~~~~~~~~~~~Part 3~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def transition_para_est(ytrain):
	ydistinct=[]
	for i in range(len(ytrain)):
		for j in ytrain[i]:
			if j not in ydistinct:
				ydistinct.append(j)
	t={}
	count={}
	row=ydistinct+['Start']
	column=ydistinct+['Stop']
	for i in row:
		t[i]={}
		count[i]=0
		for j in column:
			t[i][j]=0
	for i in range(len(ytrain)):
		for j in range(len(ytrain[i])+1):
			if j==0:
				t['Start'][ytrain[i][j]]+=1
				count['Start']+=1
			elif j==len(ytrain[i]):
				t[ytrain[i][j-1]]['Stop']+=1
				count[ytrain[i][j-1]]+=1
			else:
				t[ytrain[i][j-1]][ytrain[i][j]]+=1
				count[ytrain[i][j-1]]+=1
	for i in row:
		for j in column:
			t[i][j]=1.0*t[i][j]/count[i]	
	return t,ydistinct


def viterbi(trainfile,testfile,outputfile):
	xtrain2,ytrain2=get_sentence(trainfile,'train')
	xtest2=get_sentence(testfile,'in')
	e,ydistinctold,xalldistinct=emission_para_est(xtrain2,ytrain2,xtest2)
	t,ydistinct=transition_para_est(ytrain2)

	fo=open(outputfile,'w+')

	yset=[]

	for i in range(len(xtest2)):
		n=len(xtest2[i])
		r={}
		y={}
		for j in range(n+2):
			r[j]={}
			if j!=0 and j!=n+1:
				for k in ydistinct:
					r[j][k]=-10000
		for j in range(n):
			y[j]={}
			for k in ydistinct:
				y[j][k]=''
		
		r[0]['Start']=1
		r[n+1]['Stop']=-10000

		#==============Take log to deal with underflow problem==============================
		nega=-100
		for k in ydistinct:
			tran=t['Start'][k]
			emis=e[xtest2[i][0]][k]
			tranlog=math.log(tran) if tran>0 else nega
			emislog=math.log(emis) if emis>0 else nega
			r[1][k]=tranlog+emislog

		for j in range(2,n+1):
			for k in ydistinct:
				for m in ydistinct:
					tran=t[m][k]
					emis=e[xtest2[i][j-1]][k]
					tranlog=math.log(tran) if tran>0 else nega
					emislog=math.log(emis) if emis>0 else nega
					rtry=tranlog+emislog+r[j-1][m]
					if r[j][k]<rtry:
						r[j][k]=rtry
						y[j-2][k]=m
		
		for k in ydistinct:
			tran=t[k]['Stop']
			tranlog=math.log(tran) if tran>0 else nega
			rtry=tranlog+r[n][k]
			if r[n+1]['Stop']<rtry:
				r[n+1]['Stop']=rtry
				y[n-1]['Stop']=k

		#==========Do not consider underflow problem======================================
		# for k in ydistinct:
		# 	r[1][k]=t['Start'][k]*e[xtest2[i][0]][k]

		# for j in range(2,n+1):
		# 	for k in ydistinct:
		# 		for m in ydistinct:
		# 			rtry=r[j-1][m]*t[m][k]*e[xtest2[i][j-1]][k]
		# 			if r[j][k]<rtry:
		# 				r[j][k]=rtry
		# 				y[j-2][k]=m
		# 		# print r[j][k],y[j-2][k]
		
		# for k in ydistinct:
		# 	rtry=r[n][k]*t[k]['Stop']
		# 	if r[n+1]['Stop']<rtry:
		# 		r[n+1]['Stop']=rtry
		# 		y[n-1]['Stop']=k
		# # print y
		# # print r

		ybest=[]
		ybest.append(y[n-1]['Stop'])
		for j in range(n-2,-1,-1):
			ybefore=ybest[len(ybest)-1]
			# print ybefore
			ybest.append(y[j][ybefore])
		ybestreverse=[]
		for j in range(len(ybest)-1,-1,-1):
			ybestreverse.append(ybest[j])
		yset.append(ybestreverse)
		for j in range(n):
			fo.write(xtest2[i][j]+' '+ybestreverse[j]+'\n')
		fo.write('\n')
	fo.close()
	return yset


#==================Testing Part==============================================
#============================================================================

##~~~~~~~~~~~~~~Part 2 Emission para accuracy~~~~~~~~~~~~~~~~~~~~

# print 'Part 2:\n'

# #--------NPC---------------------

# xtrainN,ytrainN=get_sentence('train','train')
# xtestN=get_sentence('dev.in','in')
# xtest1N,ytestN=get_sentence('dev.out','out')

# eN,yN,xN=emission_para_est(xtrainN,ytrainN,xtestN)

# ytagN=tagger(xtestN,eN,yN,xN,'dev.p2.out')
# # print ytag

# accuracyN=accuracy(ytagN,ytestN)
# print 'The accuracy score for NPC is:'
# print accuracyN


##~~~~~~~~~~~~~~Part 3 Transition para & Viterbi Accuracy~~~~~~~~~~~~~~

# print '\nPart 3:\n'

# #--------NPC Viterbi Accuracy---------------------

# ysetN3=viterbi('train','dev.in','dev.p3.out')
# # print yset

# xtestN3,ytestN3=get_sentence('dev.out','out')
# accuracyN3=accuracy(ysetN3,ytestN3)
# print 'The accuracy score for NPC is:'
# print accuracyN3



