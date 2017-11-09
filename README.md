# Twitter-Statistics #
This Twitter bot opens an active stream of tweets on topics as shown in the topics.json file. The bot then collects this information and determines how popular certain topics are based on a formula that will perpetually be updated.
Back end is written in Python, and uses the library Tweepy (version 3.2.0 for stability) to mine data
Graphs are generated using Plotly, and exported to a png file, which is then uploaded to twitter
Check out my current bot [HERE](https://twitter.com/Statistics_Moe)
## Current Formula ##
![Equation 2](https://pbs.twimg.com/media/DOKLlqGVAAE-S40.jpg)


## Data Structures ##
Right now the data structures are a bit confusing, and I play on cleannig it up soon, but for now, this is a basic overview
### data ### 
This refers to the json file that is a tweet. This holds all the information that a tweet holds, and is imported as a dictionary. Relevant data: 
data["user"]["id_str"] : unique ID string
data["quote_count"] : number of people who quote retweet
data["reply_count"] : number of people who reply to this tweet
data["retweet_count"] : number of people who retweet
data["favorite_count"] : number of people who favorite
### tweetData ###
This is an instance of the class Statistics. This class hold an array of strings: **lables**, which is the primary name of each topic, which at the moment is just the first tag.
tweetData also holds the next data structure, **stored_data**
### stored_data ##
This holds all the collected data from each tweet. This is structured in that it is an array of dictionaries. Each entry in the array refers to a dictionary, who's key value is the unique user ID, and the value is an array of arrays. Each array in the array of arrays refers to a single tweet, and the data stored in the array is [quote_count,reply_count,retweet_count,favorite_count] for each tweet
