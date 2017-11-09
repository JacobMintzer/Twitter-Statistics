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
		self.stored_data = [] # Array of dictionaries, key is userID, value is num tweets
		self.labels = [] # Referenced name of all topics, used for file names
		self.lock=threading.Lock()
		self.startTime = time.time()
		self.totalEntries=0	
		self.popularityIndex=[]
		if clean:
			for tag in tags:
				self.popularityIndex.append(0)
		else:
			with open("popularity.txt") as pop:
				popList=pop.readline().split()
			for popVal in popList:
				self.popularityIndex.append(int(popVal))
		for tag in tags:
			self.stored_data.append({})
			self.labels.append(tag)

	def clear(self):
		self.stored_data=[]
		for tag in self.labels:
			self.stored_data.append({})

	def add(self,data):
		try:
			found=False
			self.lock.acquire()
			for (label,page) in zip(self.labels,self.stored_data):
				for tag in label:
					if tag in data["text"]:
						found=True
				if found:
					if data["user"]["id_str"] in page.keys():
						page[data["user"]["id_str"]].append([data["quote_count"],data["reply_count"],data["retweet_count"],data["favorite_count"]])
						found=False
					else:
						page[data["user"]["id_str"]]=[]
						page[data["user"]["id_str"]].append([data["quote_count"],data["reply_count"],data["retweet_count"],data["favorite_count"]])
						found=False
			self.lock.release()

		except KeyError:
			fileDir=os.path.dirname(os.path.realpath('__file__'))
			with open(os.path.join(fileDir,'data/errlog.txt'),'a+') as errlog:
				errlog.write('exception occured at {0} with tweet \n{1}\n\n'.format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),data))
			self.lock.release()


	def export(self):
		with open("popularity.txt",'w+') as file:
			for popVal in self.popularityIndex:
				file.write(popVal+' ')


		# fileDir=os.path.dirname(os.path.realpath('__file__'))

		# with open(os.path.join(fileDir,'data/info.txt'),'w+') as infoFile:
		# 	infoFile.write('Starting time:{0}\nTotal {1} entries\nLast edited at {2}\n'.format(datetime.datetime.fromtimestamp(self.startTime).strftime('%Y-%m-%d %H:%M:%S'),self.totalEntries,datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))








#override tweepy.StreamListener to add logic to on_status
#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):


	def on_data(self, data):
		global tweetData
		tweetData.add(json.loads(data))
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
	print("starting analysis\n")
	totalTweets=[]
	popularityIndex=tweetData.popularityIndex
	totalTweeters=[]
	mainTopics=[]
	while True:
		try:
			

			while(True):	#system so that program only runs at 6 or 12, adjusted since server is an hour off of my time
				curTime=time.localtime()
				if(curTime.tm_hour==23 or curTime.tm_hour==5 or curTime.tm_hour==11 or curTime.tm_hour==17):
					if(curTime.tm_min>5):
						time.sleep(5*60*(60-curTime.tm_min))
					else:
						break
				else:
					time.sleep(298)
			tweetData.lock.acquire()
			# tweetData.stored_data=[{"string":7},{"string2":8}]
			# for topicData in tweetData.stored_data:
			# 	print(type(topicData))
			# 	for user in topicData:
			# 		print(type(topicData[user]))

			#compiling data from each topic
			for label,topicData,popularity,totTweet in zip(tweetData.labels,tweetData.stored_data,popularityIndex,totalTweets):
				mainTopics.append(label[0])
				numTweets=0
				Tweeters=0
				totalQuote=0
				totalReply=0
				totalRetweet=0
				totalFav=0
				for user in topicData:
					Tweeters+=1
					quote=0
					reply=0
					retweet=0
					fav=0
					userPop=0.0
					for userTweets in topicData[user]:
						numTweets+=1
						quote=userTweets[0]
						reply=userTweets[1]
						retweet=userTweets[2]
						fav=userTweets[3]
						totalQuote+=quote
						totalReply+=reply
						totalRetweet+=retweet
						totalFav+=fav
						popPerTweet=fav**(1/4)+retweet**(1/2)+reply**(1/3)+quote**(1/3)
						userPop+=popPerTweet
					popularity+=userPop**(1/2)
				totTweets+=numTweets
				#popularityIndex.append(popularity)
				totalTweeters.append(Tweeters)
			tweetData.export()
			tweetData.lock.release()
			#trace=go.Bar(x=tweetData.labels,y=popularityIndex)
			data = [go.Bar(
            x=mainTopics,
            y=popularityIndex)]

			layout=go.Layout(title='{}'.format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:00')),width=1600, height=900)
			fig = go.Figure(data=data, layout=layout)
			py.image.save_as(fig, filename='image.png')
			api=tweepy.API(auth)
			if Status=="":
				api.update_with_media(filename='image.png',status="{}".format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:00')))
			else:
				api.update_with_media(filename='image.png',status=Status+"\n{}".format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:00')))
				Status=""
			#print("posted , sleeping for 6 hours")
			time.sleep(300)
		except Exception as ex:
			print("{} occured in analysis, resetting\n".format(ex))
			print(tweetData.labels)
			#tweetData.lock.release()
		finally:
			for pop in popularityIndex:
				pop=pop**.75

def stream(mystream,megatag):
	while True:
		try:
			myStream.filter(track=megatag)
		except AttributeError:
			print("error in stream at {}, resetting stream\n".format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))

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
		status="Program starting with no previous data on {}.".format(datetime.datetime.fromtimestamp(time.time()).strftime('%m-%d at %H:%M'))
		clean=True
	elif sys.argv[1]=="1":
		status="Program just crashed, restarting with previous data on {}.".format(datetime.datetime.fromtimestamp(time.time()).strftime('%m-%d at %H:%M'))
		clean=False
	else:
		status="Program stopped at unknown time, restarting with previous data on {}".format(datetime.datetime.fromtimestamp(time.time()).strftime('%m-%d at %H:%M'))
		clean=False
	tweetData=Statistics(queryData["tags"],clean)
	myStreamListener = StdOutListener()
	myStream = Stream(auth, myStreamListener)
	_thread.start_new_thread ( stream, (myStream,megatag) )
	print (megatag)
	analyze(auth,status) 
	# while True:
	# 	time.sleep(120)
		
	# 	print("exporting")
	# 	tweetData.lock.acquire()
	# 	tweetData.export()
	# 	tweetData.lock.release()
	# 	print('total {} entries'.format(tweetData.totalEntries))
