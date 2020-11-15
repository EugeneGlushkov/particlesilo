import tweepy as tw 
import pandas as pd
import csv
import sys
import requests
import re
import os

# API set-ups for the use of Twitter API
# Insert your keys and tokens below
consumer_key = 'BwDCBfUPvHsT30VF5aOrgElrx'
consumer_secret = '0UmESAqvPPNLX65GN6EbvermCGZd1yrG0IczcnxiBkIalLBDWf'
access_token = '390620577-aaRyoQaKesbOeSiYKEAZHknuRuLVZtenspPrbQIO'
access_token_secret = 'F5HwHzau082A1Q9oGgSCrXhrhNc0HbKDvM4kkSwQpi3QT'


#function to get certain number of tweets having a media file
def get_tweets(listOfTweets, keyword, numOfTweets, data_since, data_until):

    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tw.API(auth, wait_on_rate_limit=True)
    
    make_dir(keyword)

    for tweet in tw.Cursor(api.search, q=keyword+' -filter:retweets', since=data_since, until=data_until, lang='en', tweet_mode='extended').items(numOfTweets):
        try:
                print(tweet.entities['media'][0]['media_url'])
        except (NameError, KeyError):
                #we dont want to have any entries without the media_url so lets do nothing
                dict_ = {
                         'Keywords': keyword,
                         'User Name': tweet.user.name,
                         'Screen Name': tweet.user.screen_name,
                         'Tweet Created at': tweet.created_at,
                         'Tweet Text': tweet.full_text,
                         'Tweet Media': 'No media',
                         'Location': tweet.user.location,
                         'Likes': tweet.favorite_count,
                         'Retweets': tweet.retweet_count
                         }
                #listOfTweets.append(dict_)    
                pass
        else:
                #got media_url - means add it to the output
                dict_ = {
                         'Keywords': keyword,
                         'id':tweet.id,
                         'User Name': tweet.user.name,
                         'Screen Name': tweet.user.screen_name,
                         'Tweet Created at': tweet.created_at,
                         'Tweet Text': tweet.full_text,
                         'Tweet Media': tweet.entities['media'][0]['media_url'],
                         'Hashtags': get_hashtags(tweet.entities['hashtags']),
                         'Location': tweet.user.location,
                         'Likes': tweet.favorite_count,
                         'Retweets': tweet.retweet_count
                         }
                listOfTweets.append(dict_)
                
                #saving the media
                #file_path = os.path.join(keyword, tweet.id)
                r = requests.get(tweet.entities['media'][0]['media_url'], allow_redirects=True)
                #filename = getFilename_fromCd(r.headers.get('content-disposition'))
                open(os.path.join(keyword, str(tweet.id)+'.jpg'), 'wb').write(r.content)
    
                
    return listOfTweets

def get_hashtags(dict_tags):
    str_tags = ''
    for tag in dict_tags:
        str_tags = str_tags + tag['text']+' '
    return str_tags

def make_dir(dst):
    try:
        os.makedirs(dst)
    except:
        pass



def get_all_tweets(screen_name):
        #Twitter only allows access to a users most recent 3240 tweets with this method

        #authorize twitter, initialize tweepy
        auth = tw.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tw.API(auth)

        #initialize a list to hold all the tweepy Tweets
        alltweets = []

        #make initial request for most recent tweets (200 is the maximum allowed count)
        new_tweets = api.user_timeline(screen_name = screen_name,count=1)

        #save most recent tweets
        alltweets.extend(new_tweets)

        #save the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1
        

        #keep grabbing tweets until there are no tweets left to grab
        while len(new_tweets) > 0:
                print("getting tweets before %s",oldest)

                #all subsequent requests use the max_id param to prevent duplicates
                new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)

                #save most recent tweets
                alltweets.extend(new_tweets)

                #update the id of the oldest tweet less one
                oldest = alltweets[-1].id - 1

                print("...%s tweets downloaded so far",(len(alltweets)))

        #go through all found tweets and remove the ones with no images 
        outtweets = [] #initialize master list to hold our ready tweets
        for tweet in alltweets:
                #not all tweets will have media url, so lets skip them
                try:
                        if tweet.entities['media'][0]['type'] == 'animated_gif':
                                print(tweet.entities['media'][0]['media_url'])
                except (NameError, KeyError):
                        #we dont want to have any entries without the media_url so lets do nothing
                        pass
                else:
                        #got media_url - means add it to the output
                        outtweets.append([tweet.id_str, tweet.created_at, tweet.text.encode("utf-8"), tweet.entities['media'][0]['media_url']])

        #write the csv  
        print("Writing the csv file...")

        with open('%s_tweets.csv' % screen_name, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['id','created_at','text','media_url'])
                writer.writerows(outtweets)


        pass

def get_200_tweets(screen_name):
        #Twitter only allows access to a users most recent 3240 tweets with this method

        #authorize twitter, initialize tweepy
        auth = tw.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tw.API(auth, wait_on_rate_limit=True)

        #initialize a list to hold all the tweepy Tweets
        alltweets = []

        #make initial request for most recent tweets (200 is the maximum allowed count)
        new_tweets = api.user_timeline(screen_name = screen_name,count=1)

        #save most recent tweets
        alltweets.extend(new_tweets)
        

        #go through all found tweets and remove the ones with no images 
        outtweets = [] #initialize master list to hold our ready tweets
        for tweet in alltweets:
                #not all tweets will have media url, so lets skip them
                try:
                        print(tweet.entities['media'][0]['media_url'])
                except (NameError, KeyError):
                        #we dont want to have any entries without the media_url so lets do nothing
                        pass
                else:
                        #got media_url - means add it to the output
                        outtweets.append([tweet.id_str, tweet.created_at, tweet.text.encode("utf-8"), tweet.entities['media'][0]['media_url']])

        #write the csv  
        print("Writing the csv file...")
        with open('%s_tweets.csv' % screen_name, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['id','created_at','text','media_url'])
                writer.writerows(outtweets)

        pass
    


if __name__ == '__main__':
        #pass in the username of the account you want to download
        #get_200_tweets("particlesilo")
        
        #if want to search for posts with specific hashtag in the last 7 days
        list_1 = []
        numberOfPosts = 300 #limit for single search
        Start_date = '2010-01-01'
        End_date = '2020-11-15'
        hashtags = 'particlephysics'
        get_tweets(list_1, hashtags, numberOfPosts, Start_date, End_date)
        result_df = pd.DataFrame(list_1)   
        result_df.to_csv('results_{}.csv'.format(hashtags), index=None)