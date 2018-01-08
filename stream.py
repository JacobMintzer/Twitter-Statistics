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
from statistics import Statistics
from topic import Topic




#override tweepy.StreamListener to add logic to on_status
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



def analyze(auth,Status):
	global tweetData
	try:
		print("starting analysis\n")
		totalTweets=[]
		totalTweeters=[]
		mainTopics=[]
		TweetIDs=[]
		debug=False
		msg=0
		if Status=="debug":
			debug=True
	except Exception as ex:
		with open ("./twitter_errlog.txt","a") as errlog:
			errlog.write("{0} error of type {1} occured in early analysis\n".format(ex,ex.__class__.__name__))
		print ("{} exception in early analysis".format(ex))
	while True:
		try:
			

			while(True):	#system so that program only runs at 8 am/pm
				curTime=time.localtime()
				if debug:
					time.sleep(30)
					break
				if curTime.tm_hour%12==1:
					if curTime.tm_min>1:
						time.sleep(12*60*(60-curTime.tm_min))
					else:
						break
				else:
					time.sleep((60-curTime.tm_min)*60)
			#print("#1\n")

			compile(auth)
			#print("finished compiling\n ")
			#compiling data from each topic

			
			

			tweetData.export()
			
			popularity=tweetData.getPop()
			data = [go.Bar(x=tweetData.getTopicNames(),y=popularity,text=popularity,textposition='auto',)]
			print ("#4\n")
			layout=go.Layout(title='{}'.format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M')),width=1600, height=900)
			print ("#5\n")
			fig = go.Figure(data=data, layout=layout)
			py.image.save_as(fig, filename='image.png')
			with open ("./msg.txt","r+") as message:
				if "reset" in message.readline():
					msg=1
			with open ("./msg.txt","w+") as message:
				message.truncate()
			api=tweepy.API(auth)
			if debug:
				print("not posting to twitter because in debug mode, check the file yourself")
			elif msg==1:
				api.update_with_media(filename='image.png',status="program briefly stopping for update after this\n {}".format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:00')))
			elif Status=="":
				api.update_with_media(filename='image.png',status="{}".format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:00')))
			else:
				api.update_with_media(filename='image.png',status="{1}\n{0}".format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:00'),Status))
				Status=""
			print("posted")
			if msg==1:
				sys.exit(0)
			time.sleep(300)
		except Exception as ex:
			print("{}  {} occured in late analysis, resetting\n".format(ex,ex.__class__.__name__))
			with open ("./twitter_errlog.txt","a") as errlog:
				errlog.write("{0} error of type {1} occured in late analysis\n".format(ex,ex.__class__.__name__))
			#tweetData.lock.release()
			if msg==1:
				sys.exit(0)

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
		#print ("{0} arrays of tweets left of length {1}\n".format(len(tweetData.tweetIDs),len(tweetData.tweetIDs[0])))
		if len(tweetData.tweetIDs[0])<100:
			#print("last\n")
			last=True
		try:
			#print("time to lookup!")
			print("tweet data is \n {} \n".format(tweetData.tweetIDs[0]))
			dataList=api.statuses_lookup(tweetData.tweetIDs.pop(0))
			#tweetData.times.pop(0)
			for data in dataList:
				jsonData=json.dumps(data._json)
				tweetData.add(json.loads(jsonData))
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

	#variables:
	tweetVal=1
	favVal=0.5
	rtVal=0.25
	exp=True
	deg=.85



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
	tweetData=Statistics(queryData["tags"], clean, tweetVal, favVal, rtVal, exp, deg)
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
