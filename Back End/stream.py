__author__ = 'jrmintz3@gmail.com'
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import time
import os
import copy
import threading
import datetime


class Statistics:

	def __init__(self, tags):
		self.stored_data = []
		self.labels = []
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



def fileCheck(fileName):
	fileDir=os.path.dirname(os.path.realpath('__file__'))
	return os.path.join(fileDir,'data/'+(fileName.replace('/','')+'.json'))

if __name__=='__main__':
	with open('credentials.json') as credFile:
		data=json.load(credFile)
	auth=OAuthHandler(data["consumer_key"],data["consumer_secret"])
	auth.set_access_token(data["access_key"],data["access_secret"])
	#api=tweepy.API(auth)
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
	myStream.filter(track=megatag, async=True)
	print (megatag)
	while True:
		time.sleep(120)
		print("exporting")
		tweetData.lock.acquire()
		tweetData.export()
		tweetData.lock.release()
		print('total {} entries'.format(tweetData.totalEntries))
