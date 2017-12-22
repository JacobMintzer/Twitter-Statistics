#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'statisticsdotmoe@gmail.com'
import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
import json
import time
import os
import copy
import threading
import _thread
import sys
import datetime
import plotly.plotly as py
import plotly.graph_objs as go
import test
from topic import Topic
class Statistics:

	def __init__(self, tags, clean, tweetVal, favVal, rtVal, exp):
		#self.stored_data = {} # Array of dictionaries, key is tag, value is array of number of favs, RTs
		#self.topics = {} #holds all the topic data structures
		#self.lock=threading.Lock() #not currently being used
		self.startTime = time.time()
		self.tweetIDs=[]
		self.topicNames=[]
		self.topics={}
		for tag in tags:
			self.topicNames.append(tag[0])
			self.topics[tag[0]]=(Topic(tag[0],tag, tweetVal, favVal, rtVal, exp))
			#self.stored_data[tag[0]]=[]
			#print (tag)
		
		
		else:
			with open("popularity.txt") as pop:
				popList=pop.readline().split()
			for popVal,topic in zip(popList,self.topicNames):
				#print(str(popVal))
				self.topics[topic].setPop(float(popVal))
	

	# def clear(self):
	# 	for tag in self.topics:
	# 		self.stored_data[tag]=[]

	def getTopicNames(self):
		return self.topicNames

	def getPop(self):
		pop=[]
		for topicName in self.topicNames:
			pop.append(self.topics[topicName].getPop())
		return pop

	def collect(self,ID):
		if(len(self.tweetIDs)==0):
			self.tweetIDs.append([])
		elif len(self.tweetIDs[len(self.tweetIDs)-1])%100==0:
			self.tweetIDs.append([])
		self.tweetIDs[len(self.tweetIDs)-1].append(ID)

	def add(self,data):
		try:
			
			#self.lock.acquire()
			#print( type(data))
			#print ("\n\n{}\n\n".format(data["text"]))
			#print("\n{}\n".format(type(data["text"])))
			#print (type(self.tags[0]))
			found=False
			for topicName in self.topicNames:

				for tag in self.topics[topicName].getTags():
					if tag in data["text"]:
						found=True
				if found:
					#print("just found\n")
					self.topics[topicName].addTweet(data)
					found=False
					
				
			#self.lock.release()

		except Exception as ex:
			#fileDir=os.path.dirname(os.path.realpath('__file__'))
			# with open(os.path.join(fileDir,'data/errlog.txt'),'a+') as errlog:
			# 	errlog.write('exception occured at {0} with tweet \n{1}\n\n'.format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),data))
			with open ("./twitter_errlog.txt","a") as errlog:
				errlog.write("{0} error of type {1} occured in add\n".format(ex,ex.__class__.__name__))
			print ("{} error occured in add\n".format(ex))
			print (ex.__class__.__name__)
			print ("\n")
			#self.lock.release()


	def export(self):
		print("exporting\n")
		with open("./popularity.txt",'w') as file:
			output=""
			for topicName in self.topicNames:
				output+=self.topics[topicName].export()
				output+=" "
			file.write(output)

		# fileDir=os.path.dirname(os.path.realpath('__file__'))

		# with open(os.path.join(fileDir,'data/info.txt'),'w+') as infoFile:
		# 	infoFile.write('Starting time:{0}\nTotal {1} entries\nLast edited at {2}\n'.format(datetime.datetime.fromtimestamp(self.startTime).strftime('%Y-%m-%d %H:%M:%S'),self.totalEntries,datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))


