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
import datetime
import plotly.plotly as py
import plotly.graph_objs as go



class Statistics:

	def __init__(self, tags):
		self.stored_data = [] # Array of dictionaries, key is userID, value is num tweets
		self.labels = [] # Referenced name of all topics, used for file names
		self.lock=threading.Lock()
		self.startTime = time.time()
		self.totalEntries=0	
		for tag in tags:
			self.stored_data.append({})
			self.labels.append(tag)


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
						page[data["user"]["id_str"]]+=1
						found=False
					else:
						page[data["user"]["id_str"]]=1
						found=False
			self.lock.release()

		except KeyError:
			fileDir=os.path.dirname(os.path.realpath('__file__'))
			with open(os.path.join(fileDir,'data/errlog.txt'),'a+') as errlog:
				errlog.write('exception occured at {0} with tweet \n{1}\n\n'.format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),data))
			self.lock.release()


	def export(self):
		self.totalEntries=0
		for label,storedData in zip(self.labels,self.stored_data):
			self.totalEntries+=len(storedData)
			with open(fileCheck(label[0]),'w+') as file:
				json.dump(storedData,file)


		fileDir=os.path.dirname(os.path.realpath('__file__'))

		with open(os.path.join(fileDir,'data/info.txt'),'w+') as infoFile:
			infoFile.write('Starting time:{0}\nTotal {1} entries\nLast edited at {2}\n'.format(datetime.datetime.fromtimestamp(self.startTime).strftime('%Y-%m-%d %H:%M:%S'),self.totalEntries,datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))








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

def analyze(auth, num):
	print("starting analysis\n")
	while True:
		try:
			while(True):
				curTime=time.localtime()
				if(curTime.tm_hour==0 or curTime.tm_hour==6 or curTime.tm_hour==12 or curTime.tm_hour==18):
					if(curTime.tm_min>5):
						time.sleep(19000)
					
					else:
						break

				else:
					time.sleep(290)
			print ("pre-lock\n")
			tweetData.lock.acquire()
			totalTweets=[]
			popularityIndex=[]
			totalTweeters=[]
			mainTopics=[]
			for label,storedData in zip(tweetData.labels,tweetData.stored_data):
				mainTopics.append(label[0])
				numTweets=0
				popularity=0.0
				Tweeters=0
				for user in storedData:
					Tweeters+=1
					numTweets+=storedData[user]
					popularity+=(storedData[user]**.5)
				totalTweets.append(numTweets)
				popularityIndex.append(popularity)
				totalTweeters.append(Tweeters)
			tweetData.lock.release()
			print ("post lock\n")
			#trace=go.Bar(x=tweetData.labels,y=popularityIndex)
			data = [go.Bar(
            x=mainTopics,
            y=popularityIndex)]

			layout=go.Layout(title='{}'.format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:00')),width=1600, height=900)
			fig = go.Figure(data=data, layout=layout)
			py.image.save_as(fig, filename='image.png')
			api=tweepy.API(auth)
			api.update_with_media(filename='image.png',text='{}'.format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:00')))
			print("posted (in theory), sleeping for 6 hours")
			time.sleep(300)
		except Exception as ex:
			print("{} occured in analysis, resetting\n".format(ex))
			print(tweetData.labels)
			#tweetData.lock.release()



def fileCheck(fileName):
	fileDir=os.path.dirname(os.path.realpath('__file__'))
	return os.path.join(fileDir,'data/'+(fileName.replace('/','')+'.json'))

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
	tweetData=Statistics(queryData["tags"])
	myStreamListener = StdOutListener()
	myStream = Stream(auth, myStreamListener)
	try:
		myStream.filter(track=megatag, async=True)
	except AttributeError:
		System.exit("attribute error at {}".format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
	print (megatag)
	_thread.start_new_thread ( analyze, (auth,1) )
	while True:
		time.sleep(120)
		
		print("exporting")
		tweetData.lock.acquire()
		tweetData.export()
		tweetData.lock.release()
		print('total {} entries'.format(tweetData.totalEntries))
