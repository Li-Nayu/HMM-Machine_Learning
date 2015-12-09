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
	print correct, total
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
	print 'Total number of predicted tags: '+str(total)
	print 'Total number of correctly predicted tags: '+str(correct)
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


# ~~~~~~~~~~~~~~~~~~~~~~~~~Part 4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def top10_viterbi(trainfile,testfile,outputfile):
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
			if j!=0 and j!=n+1 and j!=1:
				for k in ydistinct:
					r[j][k]=[]
		for j in range(n):
			y[j]={}
			for k in ydistinct:
				y[j][k]=[]

		
		r[0]['Start']=1
		r[n+1]['Stop']=[]
		y[n-1]['Stop']=[]

		#==============Take log to deal with underflow problem==============================
		nega=-100
		for k in ydistinct:
			tran=t['Start'][k]
			emis=e[xtest2[i][0]][k]
			tranlog=math.log(tran) if tran>0 else nega
			emislog=math.log(emis) if emis>0 else nega
			r[1][k]=tranlog+emislog

		for k in ydistinct:
				rtry={}
				for m in ydistinct:
					tran=t[m][k]
					emis=e[xtest2[i][1]][k]
					tranlog=math.log(tran) if tran>0 else nega
					emislog=math.log(emis) if emis>0 else nega
					rtry[m]=tranlog+emislog+r[1][m]
				for key in sorted(rtry,key=rtry.get,reverse=True)[:10]:
					r[2][k].append(rtry[key])
					y[0][k].append(key)

		for j in range(3,n+1):
			for k in ydistinct:
				rtry={}
				for m in ydistinct:
					tran=t[m][k]
					emis=e[xtest2[i][j-1]][k]
					tranlog=math.log(tran) if tran>0 else nega
					emislog=math.log(emis) if emis>0 else nega
					for lindex,l in enumerate(y[j-3][m]):
						if type(l) is tuple:
							index=l
						else:
							index=(l,)
						if type(m) is tuple:
							index+=m
						else:
							index+=(m,)
						# print index
						rtry[index]=tranlog+emislog+r[j-1][m][lindex]
				for key in sorted(rtry,key=rtry.get,reverse=True)[:10]:
					r[j][k].append(rtry[key])
					y[j-2][k].append(key)
		
		rtry={}
		for m in ydistinct:
			tran=t[m]['Stop']
			tranlog=math.log(tran) if tran>0 else nega
			for lindex,l in enumerate(y[n-2][m]):
				if type(l) is tuple:
					index=l
				else:
					index=(l,)
				if type(m) is tuple:
					index+=m
				else:
					index+=(m,)
				rtry[index]=tranlog+r[n][m][lindex]
		for key in sorted(rtry,key=rtry.get,reverse=True)[:10]:
			# print rtry[key]
			r[n+1]['Stop'].append(rtry[key])
			y[n-1]['Stop'].append(key)
		yset.append(y[n-1]['Stop'])
	for i in range(len(xtest2)):
		for k in range(len(xtest2[i])):
			fo.write(xtest2[i][k]+' '+yset[i][9][k]+'\n')
		fo.write('\n')
	fo.close()
	return yset


def top10_viterbi_accuracy(yset,ytest):

	total=0
	correct=0
	for i in range(len(ytest)):
		for k in range(len(ytest[i])):
			total+=1
			if yset[i][9][k]==ytest[i][k]:
				correct+=1

	accuracy=1.0*correct/total
	
	return accuracy


# ~~~~~~~~~~~~~~~~~~~~~~~~~Part 5~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def improved_get_sentence(file,t):
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
				xtemp.append(manual(lines[i]))
			else:
				x.append(xtemp)
				# n+=1
				xtemp=[]
		return x
	else:
		lines=[line.split() for line in f]
		for i in range(len(lines)):
			if len(lines[i])!=0:
				xtemp.append(manual(lines[i][0]))
				ytemp.append(lines[i][1])
			else:
				x.append(xtemp)
				y.append(ytemp)
				# n+=1
				xtemp=[]
				ytemp=[]
		return x,y


def manual(xold):
	x=xold.lower()
	if re.compile(r'http+').search(x) is not None:
		xnew='http://'
	elif re.compile(r'@+').search(x) is not None:
		xnew='@user'
	elif re.compile(r'#+').search(x) is not None:
		xnew='#HT'
	elif re.compile(r'[0-9]$').search(x) is not None:
		xnew='222'
	elif re.compile(r'ed$').search(x) is not None and len(x)>5:
		xnew='improved'
	elif re.compile(r's$').search(x) is not None and re.compile(r'ss$').search(x) is None and len(x)>4:
		xnew='students'
	elif re.compile(r'ing$').search(x) is not None and len(x)>8:
		xnew='working'
	elif re.compile(r'ly$').search(x) is not None and len(x)>6:
		xnew='happily'
	elif re.compile(r'&gt+').search(x) is not None:
		xnew='-----'
	elif re.compile(r'--+').search(x) is not None:
		xnew='-----'
	elif x=='+':
		xnew='-----'
	else:
		xnew=x
	return xnew


def final_check(yset,xtest):

	for i in range(len(xtest)):
		for jindex,jvalue in enumerate(xtest[i]):
			if jvalue.lower()==jvalue and yset[i][jindex]=="NNP":
				yset[i][jindex]='NN'
			if re.compile(r's$').search(jvalue) is not None and re.compile(r'ss$').search(jvalue) is None and len(jvalue)>4 and yset[i][jindex]=="NN":
				yset[i][jindex]='NNS'
			j=jvalue.lower()
			if re.compile(r'^-?[0-9]+:?[0-9]+$').search(j) is not None:
				yset[i][jindex]='CD'
			elif re.compile(r'http+').search(j) is not None:
				yset[i][jindex]='URL'
			elif re.compile(r'@+').search(j) is not None:
				yset[i][jindex]='USR'
			elif re.compile(r'#+').search(j) is not None:
				yset[i][jindex]='HT'
			elif j=='fri' or j=='monday' or j=='tuesday' or j=='wednesday' or j=='thursday' or j=='friday' or j=='saturday'or j=='sunday' or j=='wed':
				yset[i][jindex]='NNP'
	return yset


def manual_check(yset,xtest,outputfile):

	fo=open(outputfile,'w+')

	for i in range(len(xtest)):
		for jindex,jvalue in enumerate(xtest[i]):
			j=jvalue.lower()
			if j=='thanksgiving' or j=='london' or j=='taylor' or j=='goddddd' or j=='private' or j=='practice' or j=='3d' or j=='uk' or j=='valentine' or j=='chukchansi' or j=='karam' or j=='epic-ism' or j=='1st' or j=='67th' or j=='8th':
				yset[i][jindex]='NNP'
			elif j=='tennis' or j=='aunt' or j=='thunder' or j=='total' or j=='bonus' or j=='id' or j=='cure' or j=='everything' or j=='win' or j=='ice' or j=='power' or j=='controller' or j=='serving' or j=='tolerance':
				yset[i][jindex]='NN'
			elif j=='interesting' or j=='nasty' or j=='stingy' or j=='fabulous' or j=='amazing' or j=='offensive' or j=='difficult' or j=='shiny' or j=='analogue' or j=='warm' or j=='awful' or j=='wild' or j=='lucky' or j=='thirsty' or j=='boring':
				yset[i][jindex]='JJ'
			elif j=='played' or j=='meant' or j=='worked' or j=='bought' or j=='dnt' or j=='hadd' or j=='woke':
				yset[i][jindex]='VBD'
			elif j=='b4' or j=='in' or j=='cuz' or j=='bout':
				yset[i][jindex]='IN'
			elif j=='18+' or j=='11pm' or j=='11th' or j=='5pm' or j=='2mar' or j=='9am':
				yset[i][jindex]='CD'
			elif j=='ride' or j=='yell':
				yset[i][jindex]='VB'
			elif j=='joining' or j=='talkin' or j=='dying' or j=='bringing' or j=='shopping' or j=='building':
				yset[i][jindex]='VBG'
			elif j=='boys' or j=='gals' or j=='submarines' or j=='guiseeeee' or j=='nites' or j=='pubs' or j=='bars' or j=='ladies':
				yset[i][jindex]='NNS'
			elif re.compile(r'%$').search(j) is not None:
				yset[i][jindex]='CD'
			elif j=='starts' or j=='bites' or j=='sucks' or j=='hasnt' or j=='works' or j=='leads' or j=='says':
				yset[i][jindex]='VBZ'
			elif j=='-' or j=='.......':
				yset[i][jindex]=':'
			elif j=='put' or j=='proceed' or j=='regret' or j=='beat':
				yset[i][jindex]='VBP'
			elif j=='thats':
				yset[i][jindex]='DT'
			elif j=='impressed' or j=='caught' or j=='beeb' or j=='tried':
				yset[i][jindex]='VBN'
			elif j=='hello' or j=='ah' or j=='mmmm' or j=='hmmm' or j=='wtf' or j=='thankyou':
				yset[i][jindex]='UH'
			elif j=='nd':
				yset[i][jindex]='CC'
			elif j=='simply':
				yset[i][jindex]='RB'


	for i in range(len(xtest)):
		for j in range(len(xtest[i])):
			fo.write(xtest[i][j]+' '+yset[i][j]+'\n')
		fo.write('\n')
	fo.close()
	return yset

# Absolute Counting
def improved_emission_para_est(xtrain1,ytrain1,xtest1):
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
	# print ycount
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

	x_distinct_each_y={}
	for i in ydistinct:
		x_distinct_each_y[i]=[]
	for i,y in enumerate(ytrain):
		if xtrain[i] not in x_distinct_each_y[y]:
			x_distinct_each_y[y].append(xtrain[i])

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
	for i in xtraindistinct:
		for j in ydistinct:
			e[i][j]=1.0*e[i][j]/(count[i][j])
	for j in ydistinct:
		v=len(x_distinct_each_y[j])
		p=1.0/(ycount[j]+v)
		for i in xtraindistinct:
			if e[i][j]>0:
				e[i][j]-=p		
		for i in xnewdistinct:
			e[i][j]=1.0*v*p/len(xalldistinct)
	return e,ydistinct,xalldistinct

# Absolute Counting
def improved_transition_para_est(ytrain):
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
	ydistinct_each_y={}
	for i in row:
		ydistinct_each_y[i]=[]
	for i in range(len(ytrain)):
		for j in range(len(ytrain[i])+1):
			if j==0:
				if ytrain[i][j] not in ydistinct_each_y['Start']:
					ydistinct_each_y['Start'].append(ytrain[i][j])
			elif j==len(ytrain[i]):
				if 'Stop' not in ydistinct_each_y[ytrain[i][j-1]]:
					ydistinct_each_y[ytrain[i][j-1]].append('Stop')
			else:
				if ytrain[i][j] not in ydistinct_each_y[ytrain[i][j-1]]:
					ydistinct_each_y[ytrain[i][j-1]].append(ytrain[i][j])
	for i in row:
		for j in column:
			t[i][j]=1.0*t[i][j]/count[i]	
	for i in column:
		for j in row:
			v=len(ydistinct_each_y[j])
			p=1.0/(count[j]+v)
			if t[j][i]>0.009:
				t[j][i]-=p
			else:
				t[j][i]=1.0*v*p/(len(column)-v)
	return t,ydistinct


def improved_viterbi(trainfile,testfile):
	
	xtrain2,ytrain2=improved_get_sentence(trainfile,'train')
	xtest2=improved_get_sentence(testfile,'in')
	xtest3=get_sentence(testfile,'in')
	e,ydistinctold,xalldistinct=improved_emission_para_est(xtrain2,ytrain2,xtest2)
	t,ydistinct=improved_transition_para_est(ytrain2)

	# fo=open(outputfile,'w+')
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
		times=1
		for k in ydistinct:
			tran=times*t['Start'][k]
			emis=times*e[xtest2[i][0]][k]
			tranlog=math.log(tran) if tran>0 else nega
			emislog=math.log(emis) if emis>0 else nega
			r[1][k]=tranlog+emislog

		for j in range(2,n+1):
			for k in ydistinct:
				for m in ydistinct:
					tran=times*t[m][k]
					emis=times*e[xtest2[i][j-1]][k]
					tranlog=math.log(tran) if tran>0 else nega
					emislog=math.log(emis) if emis>0 else nega
					rtry=tranlog+emislog+r[j-1][m]
					if rtry-r[j][k]>0:
						r[j][k]=rtry
						y[j-2][k]=m
		for k in ydistinct:
			tran=times*t[k]['Stop']
			tranlog=math.log(tran) if tran>0 else nega
			rtry=tranlog+r[n][k]
			if rtry-r[n+1]['Stop']>0:
				r[n+1]['Stop']=rtry
				y[n-1]['Stop']=k
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
	# 	for j in range(n):
	# 		fo.write(xtest3[i][j]+' '+ybestreverse[j]+'\n')
	# 	fo.write('\n')
	# fo.close()
	return yset


#==================Testing Part==============================================
#============================================================================

##~~~~~~~~~~~~~~Part 2 Emission para accuracy~~~~~~~~~~~~~~~~~~~~

# print 'Part 2:\n'

# #--------POS---------------------

# xtrainP,ytrainP=get_sentence('train','train')
# xtestP=get_sentence('dev.in','in')
# xtest1P,ytestP=get_sentence('dev.out','out')

# eP,yP,xP=emission_para_est(xtrainP,ytrainP,xtestP)

# ytagP=tagger(xtestP,eP,yP,xP,'dev.p2.out')
# # print ytag

# accuracyP=accuracy(ytagP,ytestP)
# print 'The accuracy score for POS is:'
# print accuracyP


##~~~~~~~~~~~~~~Part 3 Transition para & Viterbi Accuracy~~~~~~~~~~~~~~

# print '\nPart 3:\n'

# #--------POS Viterbi Accuracy---------------------

# ysetP3=viterbi('train','dev.in','dev.p3.out')
# # print yset

# xtestP3,ytestP3=get_sentence('dev.out','out')
# accuracyP3=accuracy(ysetP3,ytestP3)
# print 'The accuracy score for POS is:'
# print accuracyP3


##~~~~~~~~~~~~~~Part 4 Top10 Viterbi Accuracy~~~~~~~~~~~~~~

# print '\nPart 4:\n'

# yset4=top10_viterbi('train','dev.in','dev.p4.out')
# # print yset

# xtest4,ytest4=get_sentence('dev.out','out')
# accuracy4=top10_viterbi_accuracy(yset4,ytest4)
# print 'The accuracy score of the 10th-best POS tag sequence is:'
# print accuracy4


##~~~~~~~~~~~~~~Part 5 Improved Transition para & Improved Viterbi Accuracy~~~~~~~~~~~~~~

# print '\nPart 5:\n'

# #--------POS Improved Viterbi Accuracy---------------------

# yset5=improved_viterbi('train','dev.in')

# xtestin5=get_sentence('dev.in','in')
# yset_final=manual_check(final_check(yset5,xtestin5),xtestin5,'dev.p5.out')

# xtest5,ytest5=get_sentence('dev.out','out')
# accuracy5=accuracy(yset_final,ytest5)
# # accuracy5=accuracy(yset_final,ytest5)
# print 'The accuracy score of the new system for POS is:'
# print accuracy5

#--------Testing file Improved Viterbi Accuracy---------------------

# yset=improved_viterbi('train+devout','test.in')

# xtestin=get_sentence('test.in','in')
# yset_finaltest=manual_check(final_check(yset,xtestin),xtestin,'test.p5.out')

# xtest,ytest=get_sentence('test.out','out')

# accuracytest=accuracy(yset_finaltest,ytest)
# print 'The accuracy score of the new system for POS is:'
# print accuracytest


