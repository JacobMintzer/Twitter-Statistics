# Twitter-Statistics #
This Twitter bot opens an active stream of tweets on topics as shown in the topics.json file. The bot then collects this information and determines how popular certain topics are based on a formula that will perpetually be updated.
Back end is written in Python, and uses the library Tweepy to mine data
Graphs are generated using Plotly, and exported to a png file, which is then uploaded to twitter
Check out my current bot at https://twitter.com/Statistics_Moe
## Current Formula ##
`Σ(n^0.5) n=tweets per person per topic`
