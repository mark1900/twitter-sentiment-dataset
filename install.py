# @author: Guy Zyskind
#          guy@zyskind.com
# Created on June 18, 2013
#
# DESCRIPTION:
# Pulls tweet data from Twitter because ToS prevents distributing it directly.
#
# This is an updated version of Niek Sanders Corpus Install Script, which is compliant
# with twitter's new API v1.1. The old API (v1) has been deprecated and no longer works.
# This version also supports OAuth2, which is now required, but will also significantly
# improve the running time.
#
# Full information and credit - 
#   - Niek Sanders
#     njs@sananalytics.com
#     http://www.sananalytics.com/lab/twitter-sentiment/
#
# USAGE:
# 1. Fill in the following parameters (from your twitter's app):
#    CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET.
# 2. Run the script (Optional: change paths).
#
# Twitter currently limits such requests to 900/window (15 minutes).
# This will require around 1.5 hours for the script to complete.
#
##############################################################
#
# Updated to be Python 3 compatible and run against the current Twitter API.
#
# Tested Environment - Windows 10 Pro + Python 3.6.1 + tweepy 3.5.0
#
# - Mark
#
##############################################################
#
# New Dependency on tweepy - https://github.com/tweepy/tweepy
# - Install tweepy using pip, as...
#   - pip is the preferred installer program - https://docs.python.org/3/installing/
#   - With Python 3.4, pip is included by default with the Python binary installers.
# - Command
#   - pip install tweepy
#
#
import csv, getpass, json, os, time, urllib

import tweepy

CONSUMER_KEY = 'Your twitter app key'
CONSUMER_SECRET = 'Your twitter app secret'
ACCESS_TOKEN = 'Your access token key'
ACCESS_TOKEN_SECRET = 'Your access token secret'

def get_user_params():

    user_params = {}

    # get user input params
    user_params['inList']  = input( '\nInput file [./corpus.csv]: ' )
    user_params['outList'] = input( 'Results file [./full-corpus.csv]: ' )
    user_params['rawDir']  = input( 'Raw data dir [./rawdata/]: ' )
    
    # apply defaults
    if user_params['inList']  == '': 
        user_params['inList'] = './corpus.csv'
    if user_params['outList'] == '': 
        user_params['outList'] = './full-corpus.csv'
    if user_params['rawDir']  == '': 
        user_params['rawDir'] = './rawdata/'

    return user_params


def dump_user_params( user_params ):

    # dump user params for confirmation
    print('Input:    '   + user_params['inList'])
    print('Output:   '   + user_params['outList'])
    print('Raw data: '   + user_params['rawDir'])
    return


def read_total_list( in_filename ):

    # read total fetch list csv
    fp = open( in_filename, 'r', encoding="utf-8" )
    reader = csv.reader( fp, delimiter=',', quotechar='"' )

    total_list = []
    for row in reader:
        total_list.append( row )

    return total_list


def purge_already_fetched( fetch_list, raw_dir ):

    # list of tweet ids that still need downloading
    rem_list = []

    # check each tweet to see if we have it
    for item in fetch_list:

        # check if json file exists
        tweet_file = raw_dir + item[2] + '.json'
        if os.path.exists( tweet_file ):

            # attempt to parse json file
            try:
                parse_tweet_json( tweet_file )
                print('--> already downloaded #' + item[2])
            except RuntimeError:
                rem_list.append( item )
        else:
            rem_list.append( item )

    return rem_list


def get_time_left_str( cur_idx, fetch_list, download_pause ):

    tweets_left = len(fetch_list) - cur_idx
    total_seconds = tweets_left * download_pause

    str_hr = int( total_seconds / 3600 )
    str_min = int((total_seconds - str_hr*3600) / 60)
    str_sec = total_seconds - str_hr*3600 - str_min*60

    return '%dh %dm %ds' % (str_hr, str_min, str_sec)

def oauth_get_tweet(tweet_id, http_method="GET", post_body='', http_headers=None):
    
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    
    #print('Fetching tweet for ID %s', tweet_id)

    tweet = api.get_status(tweet_id)
    print("%s,%s" % (tweet_id, tweet.text))
    return tweet


def download_tweets( fetch_list, raw_dir ):

    # ensure raw data directory exists
    if not os.path.exists( raw_dir ):
        os.mkdir( raw_dir )

    # Set rate limit and minus fudge factor of 100
    # https://dev.twitter.com/rest/public/rate-limits
    max_tweets_per_hr  = 4 * 900 - 100
    download_pause_sec = 3600.0 / max_tweets_per_hr
    print("Tweet Throttle - Max tweets per hour = %d (One every %f seconds)" % \
            (max_tweets_per_hr, download_pause_sec))

    # download tweets
    for idx in range(0,len(fetch_list)):

        # current item
        item = fetch_list[idx]

        # print status
        trem = get_time_left_str( idx, fetch_list, download_pause_sec )
        print('--> downloading tweet #%s (%d of %d) (%s left)' % \
              (item[2], idx+1, len(fetch_list), trem))

        # pull data
        try:
            data = oauth_get_tweet(item[2])
            with open(raw_dir + item[2] + '.json', 'w', encoding="utf-8") as outfile:
                json.dump(data._json, outfile, ensure_ascii=False, indent=2)
        except tweepy.TweepError as te:
            print("Failed to get tweet ID %s: %s" % (item[2], te))
            # traceback.print_exc(file=sys.stderr)
            pass
          
        # stay in Twitter API rate limits 
        print('    pausing %f seconds to obey Twitter API rate limits' % \
              (download_pause_sec))
        time.sleep( download_pause_sec )

    return


def parse_tweet_json( filename ):
    
    # read tweet
    print('opening: ' + filename)
	
    # parse json    
    with open( filename, 'rt', encoding="utf-8" ) as infile:
        try:
            tweet_json = json.load( infile )
        except ValueError as e:
            raise RuntimeError("Error parsing json - %s" % str(e))
        except json.JSONDecodeError as e:
            raise RuntimeError("Error parsing json - %s" % str(e))

    # look for twitter api error msgs
    if 'errors' in tweet_json:
        raise RuntimeError('error in downloaded tweet')

    # extract creation date and tweet text
    return [ tweet_json['created_at'], tweet_json['text'] ]


def build_output_corpus( out_filename, raw_dir, total_list ):

    # open csv output file
    fp = open( out_filename, 'w', newline='', encoding="utf-8" )
    writer = csv.writer( fp, delimiter=',', quotechar='"', escapechar='\\', 
                         quoting=csv.QUOTE_ALL )

    # write header row
    writer.writerow( ['Topic','Sentiment','TweetId','TweetDate','TweetText'] )

    # parse all downloaded tweets
    missing_count = 0
    for item in total_list:

        # ensure tweet exists
        if os.path.exists( raw_dir + item[2] + '.json' ):

            try: 
                # parse tweet
                parsed_tweet = parse_tweet_json( raw_dir + item[2] + '.json' )
                full_row = item + parsed_tweet
        
                # write csv row
                writer.writerow( full_row )

            except RuntimeError:
                print('--> bad data in tweet #' + item[2])
                missing_count += 1

        else:
            print('--> missing tweet #' + item[2])
            missing_count += 1

    # indicate success
    if missing_count == 0:
        print('\nSuccessfully downloaded corpus!')
        print('Output in: ' + out_filename + '\n')
    else: 
        print('\nMissing %d of %d tweets!' % (missing_count, len(total_list)))
        print('Partial output in: ' + out_filename + '\n')

    return


def main():

    # get user parameters
    user_params = get_user_params()
    dump_user_params( user_params )

    # get fetch list
    total_list = read_total_list( user_params['inList'] )
    fetch_list = purge_already_fetched( total_list, user_params['rawDir'] )

    # start fetching data from twitter
    download_tweets( fetch_list, user_params['rawDir'] )

    # second pass for any failed downloads
    print('\nStarting second pass to retry any failed downloads')
    fetch_list = purge_already_fetched( total_list, user_params['rawDir'] )
    download_tweets( fetch_list, user_params['rawDir'] )

    # build output corpus
    build_output_corpus( user_params['outList'], user_params['rawDir'], 
                         total_list )

    return


if __name__ == '__main__':
    main()
