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

class Topic:
	
	def __init__(self, topic, tags, tweetVal, favVal, rtVal, exp):
		self._tweetVal=tweetVal	#popularity per tweet to be added for all tweets
		self._favVal=favVal 		#value for each favorite
		self._rtVal=rtVal			#value for retweets
		self._exp=exp 				#bool, if favVal/rtVal is multiplied or the exponent
		self._topic=topic			#name of Topic
		self._tags=tags				#list of tags associated with this topic
		self._tweets=[]				#list of tweet data, not used atm, but might as well keep it for now
		self._totalPop=tweetVal		#total popularity for topic (popularity being 0 is just sad, so i don't do that)
		self._pop=0					#popularity for topic in this 12 hr session
		self._total=0
		self._favs=0
		self._rts=0 
	

	def getName(self):
		return self._topic
	

	def getTags(self):
		return self._tags
	

	def getTweets(self):
		return self._tweets

	def export(self):
		return str(self._totalPop)+" "

	#receives tweet, extracts and compiles data
	def addTweet(self, tweet):
		favorites=tweet["favorite_count"]
		rt=tweet["retweet_count"]
		self._favs+=favorites
		self._rts+=rt
		self._total+=1
		self.compilePop(favorites,rt)
		self._tweets.append(tweet)	

	#returns total pop, and degrades old data
	def getPop(self):
		self._totalPop=self._totalPop**.75
		self._totalPop+=self._pop
		self._pop=self._tweetVal
		return self._totalPop

	def setPop(self,pop):
		self._totalPop=pop
	
	#takes the number of favorites/RTs for a tweet, and adds it to the current popularity
	def compilePop(self,favorites, rt):	
		if self._exp:
			self._pop+=favorites**self._favVal
			self._pop+=rt**self._rtVal
		else:
			self._pop+=favorites*self._favVal
			self._pop+=rt*self._rtVal
		self._pop+=self._tweetVal
