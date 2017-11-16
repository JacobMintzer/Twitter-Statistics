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
		self.tweetIDs=[]
		self.times=[]
		if clean:
			for tag in tags:
				self.popularityIndex.append(0)
		else:
			with open("popularity.txt") as pop:
				popList=pop.readline().split()
			for popVal in popList:
				#print(str(popVal))
				self.popularityIndex.append(int(popVal))
		for tag in tags:
			self.stored_data.append({})
			#print (tag)
			self.labels.append(tag)

	def clear(self):
		self.stored_data=[]
		for tag in self.labels:
			self.stored_data.append({})

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
			found=False
			#self.lock.acquire()
			#print( type(data))
			#print ("\n\n{}\n\n".format(data))
			#print("\n{}\n".format(type(data["text"])))

			for (label,page) in zip(self.labels,self.stored_data):
				for tag in label:
					if tag in data["text"]:
						found=True
				if found:
					#print("found")
					if data["user"]["id_str"] in page.keys():
						page[data["user"]["id_str"]].append([data["retweet_count"],data["favorite_count"]])
						found=False
					else:
						page[data["user"]["id_str"]]=[]
						page[data["user"]["id_str"]].append([data["retweet_count"],data["favorite_count"]])
						found=False
				else:
					print("tag not found, dumping tweet \n{}\n".format(data))
			#self.lock.release()

		except Exception as ex:
			fileDir=os.path.dirname(os.path.realpath('__file__'))
			# with open(os.path.join(fileDir,'data/errlog.txt'),'a+') as errlog:
			# 	errlog.write('exception occured at {0} with tweet \n{1}\n\n'.format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),data))
			print ("{} error occurd in add\n".format(ex))
			#self.lock.release()


	def export(self):
		with open("popularity.txt",'w+') as file:
			for popVal in self.popularityIndex:
				file.write(str(popVal))
				file.write(" ")


		# fileDir=os.path.dirname(os.path.realpath('__file__'))

		# with open(os.path.join(fileDir,'data/info.txt'),'w+') as infoFile:
		# 	infoFile.write('Starting time:{0}\nTotal {1} entries\nLast edited at {2}\n'.format(datetime.datetime.fromtimestamp(self.startTime).strftime('%Y-%m-%d %H:%M:%S'),self.totalEntries,datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))








#override tweepy.StreamListener to add logic to on_status
#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):


	def on_data(self, data):
		global tweetData
		ID=json.loads(data)
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
	
	#print("starting analysis\n")
	totalTweets=[]
	popularityIndex=tweetData.popularityIndex
	totalTweeters=[]
	mainTopics=[]
	TweetIDs=[]
	debug=False
	if Status=="debug":
		debug=True
	else:
		time.sleep(3700)
	while True:
		try:
			

			while(True):	#system so that program only runs at 6 or 12, adjusted since server is an hour off of my time
				curTime=time.localtime()
				if debug:
					time.sleep(30)
					break
				if curTime.tm_hour%3==2:
					if curTime.tm_min>5:
						time.sleep(5*60*(60-curTime.tm_min))
					else:
						break
				else:
					time.sleep(298)
				print("#1\n")			

			compile(auth)
			print("finished compiling\n")
			#compiling data from each topic
			for label,topicData,popularity in zip(tweetData.labels,tweetData.stored_data,popularityIndex):
				mainTopics.append(label[0])
				numTweets=0
				Tweeters=0
				totalRetweet=0
				totalFav=0
				for user in topicData:
					Tweeters+=1
					retweet=0
					fav=0
					userPop=0.0
					for userTweets in topicData[user]:
						numTweets+=1
						retweet=userTweets[0]
						fav=userTweets[1]
						totalRetweet+=retweet
						totalFav+=fav
						popPerTweet=1+fav**(1/4)+retweet**(1/2)
						userPop+=popPerTweet
					popularity+=userPop**(1/2)
				
				#popularityIndex.append(popularity)
				totalTweeters.append(Tweeters)
			print("#2\n")
			tweetData.export()
			print("#3\n")
			#tweetData.lock.release()
			#trace=go.Bar(x=tweetData.labels,y=popularityIndex)
			#print (mainTopics)
			#print (popularityIndex)
			data = [go.Bar(
            x=mainTopics,
            y=popularityIndex)]
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
			if not debug:
				time.sleep(300)
		except Exception as ex:
			print("{} occured in analysis, resetting\n".format(ex))
			sys.exit()
			
			#tweetData.lock.release()
		finally:
			tweetData.popularityIndex=popularityIndex
			for pop in tweetData.popularityIndex:
				pop=pop**.75

def stream(mystream,megatag):
	while True:
		try:
			myStream.filter(track=megatag)
		except Exception as error:
			print("error {1} in stream at {0}, resetting stream\n".format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),error))

def compile(auth):
	global tweetData
	api=tweepy.API(auth)
	while len(tweetData.tweetIDs)>0
		try:
			#curTime=time.localtime()
			#elapsed=times[0]-curTime
			#if elapsed.tm_hour>=1:
				print("time to lookup!")
				dataList=api.statuses_lookup(tweetData.tweetIDs.pop(0))
				#tweetData.times.pop(0)
				for data in dataList:
					jsonData=json.dumps(data._json)
					tweetData.add(json.loads(jsonData))
			#else:
			#	time.sleep (120)
		except Exception as error:
			print ("{} error in compilation".format(error))
		time.sleep(60)



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
	_thread.start_new_thread(analyze, (auth,Status) )
	print (megatag)
	# while True:
	# 	time.sleep(120)
		
	# 	print("exporting")
	# 	tweetData.lock.acquire()
	# 	tweetData.export()
	# 	tweetData.lock.release()
	# 	print('total {} entries'.format(tweetData.totalEntries))
