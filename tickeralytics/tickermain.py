import streamlit as st
import pandas as pd
import pickle
import csv
from datetime import datetime
import plotly.express as px
import plotly
import json
from plotly.offline import plot
from plotly.graph_objs import Scatterpolar

TWITTER_HANDLES = {"spacguru", "satorimind", "daddyspac", "spac_insider", "spacresearch",
                   "mrzackmorris", "thetawarrior", "traderstewie", "malibuinvest"}
DATE_TIME_FIELD = "date"
TICKER_FIELD = "ticker"
DEFAULT_LIMIT_ROWS = 50
top_tickers = []

st.set_page_config(
    page_title="Tickeralytics!",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title('Ticker Analysis')
st.markdown("""
This app helps visualize the **Ticker Trend** and its corresponding **Sentiment Analysis** on their source!
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn
* **Data:** Based on Reddit and Twitter Posts,Comments and Tweets.
""")
st.sidebar.header('User Input Features')

def filter_data(data, hours, limit_rows=DEFAULT_LIMIT_ROWS):
    max_date_in_data = data[DATE_TIME_FIELD].max()
    cutoff_date = max_date_in_data - pd.Timedelta(hours=hours)
    hours_filtered = data[data[DATE_TIME_FIELD] > cutoff_date]

    filtered_value_counts = hours_filtered[TICKER_FIELD].value_counts()
    filtered_value_counts_reset = filtered_value_counts.reset_index()
    filtered_value_counts_reset.columns = ["ticker", "mentions"]
    return hours_filtered, filtered_value_counts_reset.head(limit_rows)

lookback_hours_dict = {'1 hour': 1, '4 hours': 4, '12 hours': 12,
                           '1 day': 24, '1 week': 24 * 7, '2 weeks': 24 * 15, '1 month': 24 * 30}
lookback_hours_select = st.sidebar.select_slider(
    'Select a lookback period',
    options=list(lookback_hours_dict.keys()))
lookback_hours = lookback_hours_dict[lookback_hours_select]

def twitter_analyse(lookback_hours):

    @st.cache
    def get_all_tweets(handles):
        all_tweets = {}
        for handle in handles:
            with open(f"F:\Projects-of-all-time\CloudCosmos\september-internship\karunya-univ-july-2021\\tickeralytics\\twitter\{handle}_tweets.pickle",
                      "rb") as dump_file:
                all_tweets[handle] = pickle.load(dump_file)
            break

        return all_tweets

    all_tweets = get_all_tweets(TWITTER_HANDLES)
    analysis = []
    data1 = []
    for handle, tweets in all_tweets.items():
        for tweet in tweets:
            print(tweet.tweet)
            if len(tweet.cashtags) > 0:
                print(tweet.cashtags)
                for cashtag in tweet.cashtags:
                    x = str(tweet.datetime)
                    date_time = x[0:19]
                    y = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
                    d = x[0:10]
                    z = datetime.strptime(d, '%Y-%m-%d')
                    # analysis.append((y, cashtag.upper()))
                    analysis.append((datetime.date(z), cashtag.upper()))
                    data1.append((datetime.date(z), cashtag.upper(), tweet.tweet))

    data = pd.DataFrame(analysis)
    data.columns = [DATE_TIME_FIELD, TICKER_FIELD]
    data.date = pd.to_datetime(data.date)
    sentiment_data = pd.DataFrame(data1)
    sentiment_data.columns = [DATE_TIME_FIELD, TICKER_FIELD, 'TWEETS']
    sentiment_data.to_csv('sentiment_data.csv')

    limit_rows = DEFAULT_LIMIT_ROWS

    global filtered_value_counts_reset, hours_filtered

    hours_filtered, filtered_value_counts_reset = filter_data(data, lookback_hours, limit_rows)

from tweets_sentiment import tweet_sent
tweet_sent.to_csv('tweet_sent.csv')
def reddit_analyse(lookback_hours):

    df = pd.read_csv("F:\Projects-of-all-time\CloudCosmos\september-internship\karunya-univ-july-2021\\nlp-macros\wallstreetbets.csv")
    df.drop("Unnamed: 0", axis=1, inplace=True)

    analysis = []
    with open("F:\Projects-of-all-time\CloudCosmos\september-internship\karunya-univ-july-2021\\nlp-macros\wallstreetbets.csv", "r", encoding="utf8") as f:
        read = csv.reader(f)
        next(read)
        for r in read:
            analysis.append((r[2], r[-1]))

    data = pd.DataFrame(analysis)
    data.columns = [DATE_TIME_FIELD, TICKER_FIELD]
    data.date = pd.to_datetime(data.date)

    hrs_filtered, red_filtered_count_reset = filter_data(data, lookback_hours, limit_rows=DEFAULT_LIMIT_ROWS)

    reddit_tickers = red_filtered_count_reset.ticker.to_list()

    global top_tickers

    top_tickers = [t for t in filtered_value_counts_reset.ticker if t in reddit_tickers]

    dff = hrs_filtered.groupby(hrs_filtered.columns.tolist(), as_index=False).size()
    reddit_filter = dff[dff['ticker'].isin(top_tickers)]
    reddit_filter.drop_duplicates()

    dff1 = hours_filtered.groupby(hours_filtered.columns.tolist(), as_index=False).size()
    twitter_filter = dff1[dff1['ticker'].isin(top_tickers)]
    twitter_filter.drop_duplicates()

    tweet_sent1 = tweet_sent[tweet_sent['ticker'].isin(top_tickers)]
    tweet_sent1.drop_duplicates()
    tweet_sent1.set_index('ticker')
    twitter_mention = px.line(tweet_sent, x='date', y='size', color='ticker')

    polar=px.scatter_polar(tweet_sent[:50], r="date", theta="ticker",color="ticker",size="mentions",symbol="Vader Analysis")
    # polar=plot([Scatterpolar(tweet_sent[:50], r="date", theta="ticker",color="ticker",size="mentions",symbol="Vader Analysis")],output_type='div')
    polar.update_layout({
        'plot_bgcolor': 'rgba(111, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0,111, 0)',
    })
    return polar,twitter_mention

twitter_analyse(lookback_hours)
polar,twitter_mention= reddit_analyse(lookback_hours)
polar
# polar=json.dumps(polar,cls=plotly.utils.PlotlyJSONEncoder)
