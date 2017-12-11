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


class Statistics:

	def __init__(self, tags, clean):
		self.stored_data = {} # Array of dictionaries, key is tag, value is array of number of favs, RTs
		self.topics = [] # Referenced name of all topics
		self.lock=threading.Lock() #not currently being used
		self.startTime = time.time()
		self.tags={}
		self.totalEntries=0	
		self.popularityIndex={}
		self.tweetIDs=[]
		self.times=[]
		
		for tag in tags:
			self.tags[tag[0]]=tag
			self.topics.append(tag[0])
			self.stored_data[tag[0]]=[]
			#print (tag)
		
		if clean:
			for topic in self.topics:
				self.popularityIndex[topic]=1
		else:
			with open("popularity.txt") as pop:
				popList=pop.readline().split()
			for popVal,topic in zip(popList,self.topics):
				#print(str(popVal))
				self.popularityIndex[topic]=float(popVal)
		

	def clear(self):
		self.stored_data={}
		for tag in self.topics:
			self.stored_data[tag]=[]

	def collect(self,ID):
		if(len(self.tweetIDs)==0):
			self.tweetIDs.append([])
			self.times.append(time.localtime())
		elif len(self.tweetIDs[len(self.tweetIDs)-1])%100==0:
			self.tweetIDs.append([])
			self.times.append(time.localtime())
		self.tweetIDs[len(self.tweetIDs)-1].append(ID)

	def add(self,data):
		try:
			
			#self.lock.acquire()
			#print( type(data))
			#print ("\n\n{}\n\n".format(data["text"]))
			#print("\n{}\n".format(type(data["text"])))
			#print (type(self.tags[0]))
			found=False
			for topic in self.topics:

				for tag in self.tags[topic]:
					if tag in data["text"]:
						found=True
				if found:
					#print("just found\n")
					self.stored_data[topic].append([1+data["retweet_count"],1+data["favorite_count"]])
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
			for topic in self.topics:
				output+=str(self.popularityIndex[topic])
				output+=" "
			file.write(output)

		# fileDir=os.path.dirname(os.path.realpath('__file__'))

		# with open(os.path.join(fileDir,'data/info.txt'),'w+') as infoFile:
		# 	infoFile.write('Starting time:{0}\nTotal {1} entries\nLast edited at {2}\n'.format(datetime.datetime.fromtimestamp(self.startTime).strftime('%Y-%m-%d %H:%M:%S'),self.totalEntries,datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))








#override tweepy.StreamListener to add logic to on_status
#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):


	def on_data(self, data):
		global tweetData
		ID=json.loads(data)
		if not ID['retweeted'] and 'RT @' not in ID['text']:
			tweetData.collect(ID["id"])
		return True

	def on_error(self, status):
		print ("\nerror ")
		print (status)
		print ("\n")


# def parseData(tags):
# 	global tweets
# 	statistics=[]
# 	for mainTag in tags:
# 		statistics.append({})
# 	while True:

def analyze(auth,Status):
	global tweetData
	try:
		print("starting analysis\n")
		totalTweets=[]
		totalTweeters=[]
		mainTopics=[]
		TweetIDs=[]
		debug=False
		if Status=="debug":
			debug=True
		else:
			time.sleep(3700)
	except Exception as ex:
		with open ("./twitter_errlog.txt","a") as errlog:
			errlog.write("{0} error of type {1} occured in early analysis\n".format(ex,ex.__class__.__name__))
		print ("{} exception in early analysis".format(ex))
	while True:
		try:
			

			while(True):	#system so that program only runs at 6 or 12, adjusted since server is an hour off of my time, sometimes changed for debugging
				curTime=time.localtime()
				if debug:
					time.sleep(30)
					break
				if curTime.tm_hour%6==5:
					if curTime.tm_min>5:
						time.sleep(6*60*(60-curTime.tm_min))
					else:
						break
				else:
					time.sleep(300)
			print("#1\n")			

			compile(auth)
			print("finished compiling\n ")
			#compiling data from each topic

			
			for topic in tweetData.topics:
				try:
					#print ("topic {} has {} tweets starting with pop {}\n".format(topic,len(tweetData.stored_data[topic]),tweetData.popularityIndex[topic]))
					numTweets=0
					Tweeters=0
					totalRetweet=0
					totalFav=0
					topicPop=0
					for tweetStat in tweetData.stored_data[topic]:
						rt=tweetStat[0]
						fav=tweetStat[1]
						totalRetweet+=rt
						totalFav+=fav
						popPerTweet=.1+fav**.5+rt**.75
						topicPop+=popPerTweet
					tweetData.popularityIndex[topic]+=topicPop
				except Exception as ex1:
					with open ("./twitter_errlog.txt","a") as errlog:
						errlog.write("{0} error of type {1} occured in mid analysis\n".format(ex1,ex1.__class__.__name__))
					print ("{} {}  error in mid analysis\n".format (ex1,ex1.__class__.__name__))
			print("#2\n")
			# print (tweetData.popularityIndex)
			# print("\n{}\n".format(popularityIndex))
			#tweetData.popularityIndex=popularityIndex
			print ("\n")
			tweetData.export()
			print("#3\n")
			#tweetData.lock.release()
			#trace=go.Bar(x=tweetData.labels,y=popularityIndex)
			#print (mainTopics)
			#print (popularityIndex)
			popularity=[]
			for topic in tweetData.topics:
				popularity.append("%.5f"%tweetData.popularityIndex[topic])
			data = [go.Bar(x=tweetData.topics,y=popularity,text=popularity,textposition='auto',)]
			print ("#4\n")
			layout=go.Layout(title='{}'.format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M')),width=1600, height=900)
			print ("#5\n")
			fig = go.Figure(data=data, layout=layout)
			py.image.save_as(fig, filename='image.png')
			api=tweepy.API(auth)
			if debug:
				print("not posting to twitter because in debug mode, check the file yourself")
			elif Status=="":
				api.update_with_media(filename='image.png',status="{}".format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:00')))
			else:
				api.update_with_media(filename='image.png',status="{1}\n{0}".format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:00'),Status))
				Status=""
			print("posted")
			time.sleep(300)
		except Exception as ex:
			print("{}  {} occured in late analysis, resetting\n".format(ex,ex.__class__.__name__))
			with open ("./twitter_errlog.txt","a") as errlog:
				errlog.write("{0} error of type {1} occured in late analysis\n".format(ex,ex.__class__.__name__))
			
			#tweetData.lock.release()
		finally:
			#tweetData.popularityIndex=popularityIndex
			for pop in tweetData.popularityIndex:
				tweetData.popularityIndex[pop]=tweetData.popularityIndex[pop]**0.5	#data deteriorates: old data less important, but still important

def stream(mystream,megatag):
	while True:
		try:
			myStream.filter(track=megatag)
		except Exception as ex:
			print("error {1} in stream at {0}, resetting stream\n".format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),ex))
			with open ("./twitter_errlog.txt","a") as errlog:
				errlog.write("{0} error of type {1} occured in stream\n".format(ex,ex.__class__.__name__))

def compile(auth):
	global tweetData
	api=tweepy.API(auth)
	last=False
	i=0
	while len(tweetData.tweetIDs)>0 and i<60:
		i+=1
		print ("{0} arrays of tweets left of length {1}\n".format(len(tweetData.tweetIDs),len(tweetData.tweetIDs[0])))
		if len(tweetData.tweetIDs[0])<100:
			print("last\n")
			last=True
		try:
			#curTime=time.localtime()
			#elapsed=times[0]-curTime
			#if elapsed.tm_hour>=1:
				#print("time to lookup!")
				print("tweet data is \n {} \n".format(tweetData.tweetIDs[0]))
				dataList=api.statuses_lookup(tweetData.tweetIDs.pop(0))
				#tweetData.times.pop(0)
				for data in dataList:
					jsonData=json.dumps(data._json)
					tweetData.add(json.loads(jsonData))
			#else:
			#	time.sleep (120)
		except Exception as ex:
			print ("{} error in compilation".format(ex))
			with open ("./twitter_errlog.txt","a") as errlog:
				errlog.write("{0} error of type {1} occured in compilation\n".format(ex,ex.__class__.__name__))
		if last:
			break
		time.sleep(60)
	if i>70:
		tweetData.tweetIDs=[]


# def fileCheck(fileName):
# 	fileDir=os.path.dirname(os.path.realpath('__file__'))
# 	return os.path.join(fileDir,'data/'+(fileName.replace('/','')+'.json'))

if __name__=='__main__':

	with open('credentials.json') as credFile:
		data=json.load(credFile)
	auth=OAuthHandler(data["consumer_key"],data["consumer_secret"])
	auth.set_access_token(data["access_key"],data["access_secret"])
	#api=tweepy.API(auth)
	py.sign_in(data["username"], data["apikey"])
	with open('topics.json') as topicFile:
		queryData=json.load(topicFile)
	megatag=[]
	global tweets
	tweets=[]
	for tag in queryData["tags"]:
		megatag=megatag+tag
	global tweetData
	if sys.argv[1]=="0":
		Status="Program starting with no previous data on {}.".format(datetime.datetime.fromtimestamp(time.time()).strftime('%m-%d at %H:%M'))
		clean=True
	elif sys.argv[1]=="1":
		Status="Program just crashed, restarting with previous data on {}.".format(datetime.datetime.fromtimestamp(time.time()).strftime('%m-%d at %H:%M'))
		clean=False
	elif sys.argv[1]=="2":
		Status="Program stopped at unknown time, restarting with previous data on {}".format(datetime.datetime.fromtimestamp(time.time()).strftime('%m-%d at %H:%M'))
		clean=False
	else:
		clean=False
		Status="debug"
		print ("\n\nWARNING, YOU ARE IN DEBUG MODE, THIS ISN'T ACTUALLY RUNNING, IT WILL NOT BE POSTED TO TWITTER\n\n")
	tweetData=Statistics(queryData["tags"],clean)
	myStreamListener = StdOutListener()
	myStream = Stream(auth, myStreamListener)
	_thread.start_new_thread ( stream, (myStream,megatag) )
	print (megatag)
	analyze (auth,Status) 
	# while True:
	# 	time.sleep(120)
		
	# 	print("exporting")
	# 	tweetData.lock.acquire()
	# 	tweetData.export()
	# 	tweetData.lock.release()
	# 	print('total {} entries'.format(tweetData.totalEntries))
