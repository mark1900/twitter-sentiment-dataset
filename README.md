# Overview

This code serves as an extension to [Sanders Analytics twitter sentiment corpus](http://www.sananalytics.com/lab/twitter-sentiment/), originally designed for training and testing Twitter sentiment analysis algorithms.

# Updated
## See also [guyz / twitter-sentiment-dataset](https://github.com/guyz/twitter-sentiment-dataset).
## Updated to be Python 3 compatible and run against the current Twitter API.


Running this script will generate ~5K hand-classified tweets. For more information, please refer to 'readme.pdf'.

# Installation

1. Install tweepy lib 
  ```
  pip install tweepy
  ```  

2. Create a [Twitter app](https://apps.twitter.com/), and update the global authentication properties in 'install.py'.
3. Run <code>python install.py</code>. If it fails with an SSL error, run as a superuser - <code>sudo python install.py</code>.
4. Hit enter three times to accept the defaults (make sure <b>rawdata</b> folder exists), or set your own paths.
5. Wait until completion (~1.5h). You should have a new file called <code>full-corpus.csv</code> with the entire labeled dataset.


#### Enjoy data-mining :)!

