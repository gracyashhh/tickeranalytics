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
from tweets_sentiment import tweet_sent
from reddit_sentiment import red_sent

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
# lookback_hours = lookback_hours_dict[lookback_hours_select]
lookback_hours = 24*30

def twitter_analyse(lookback_hours):
    pass

# from twitter_sentiment import tweet_sent
# from reddit_sentiment import red_sent
tweet_sent.to_csv('tweet_sent.csv')
red_sent.to_csv('red_sent.csv')
def reddit_analyse(lookback_hours):
    pass

def main(lookback_hours):
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
    data.to_csv('data.csv')
    sentiment_data = pd.DataFrame(data1)
    sentiment_data.columns = [DATE_TIME_FIELD, TICKER_FIELD, 'TWEETS']
    sentiment_data.to_csv('sentiment_data.csv')

    limit_rows = DEFAULT_LIMIT_ROWS

    hours_filtered, filtered_value_counts_reset = filter_data(data, lookback_hours, limit_rows)

    analysis = []

    with open("F:\Projects-of-all-time\CloudCosmos\september-internship\karunya-univ-july-2021\\nlp-macros\wallstreetbets.csv",
            "r", encoding="utf8") as f:
        read = csv.reader(f)
        next(read)
        for r in read:
            analysis.append((r[2], r[-1]))

    data = pd.DataFrame(analysis)
    data.columns = [DATE_TIME_FIELD, TICKER_FIELD]
    data.date = pd.to_datetime(data.date)

    hrs_filtered, red_filtered_count_reset = filter_data(data, lookback_hours, limit_rows=DEFAULT_LIMIT_ROWS)

    twitter_tickers = filtered_value_counts_reset.ticker.to_list()
    reddit_tickers = red_filtered_count_reset.ticker.to_list()

    top_tickers = [t for t in twitter_tickers if t in reddit_tickers]
    # st.write(top_tickers)

    dff = hrs_filtered.groupby(hrs_filtered.columns.tolist(), as_index=False).size()
    reddit_filter = dff[dff['ticker'].isin(top_tickers)]
    reddit_filter.drop_duplicates()

    dff1 = hours_filtered.groupby(hours_filtered.columns.tolist(), as_index=False).size()
    twitter_filter = dff1[dff1['ticker'].isin(top_tickers)]
    twitter_filter.drop_duplicates()

    # st.write(twitter_filter)
    # st.write(reddit_filter)

    tweet_sent1 = tweet_sent[tweet_sent['ticker'].isin(top_tickers)]
    tweet_sent1.drop_duplicates()
    tweet_sent1.set_index('ticker')

    red_sent1 = red_sent[red_sent['ticker'].isin(top_tickers)]
    red_sent1.drop_duplicates()
    tweet_sent.to_csv('tweet_sent1.csv')
    # st.write(tweet_sent)
    # st.write(red_sent1)

    polar = px.scatter_polar(tweet_sent[:85], r="date", theta="ticker", color="ticker", size="mentions",
                             symbol="Vader Analysis")
    polar_r = px.scatter_polar(red_sent[:85], r="date", theta="ticker", color="ticker", size="mentions",
                               symbol="Vader Analysis")

    sun_t = px.sunburst(tweet_sent1, path=['ticker', 'date', 'Vader Analysis'],
                        title='Twitter',
                        values='size',
                        color='Vader Analysis',
                        color_discrete_map={'Neutral': '#636EFA',
                                            'Positive': '#00CC96', 'Negative': '#EF553B'}
                        )
    sun_r = px.sunburst(red_sent1, path=['ticker', 'date', 'Vader Analysis'],
                        title='Reddit',
                        values='size',
                        color='Vader Analysis',
                        color_discrete_map={'Neutral': '#636EFA',
                                            'Positive': '#00CC96', 'Negative': '#EF553B'}
                        )
    print('##### ',red_sent,type(red_sent))
    twitter_mention = px.line(tweet_sent, x='date', y='size', color='ticker')
    reddit_mention = px.line(red_sent, x='date', y='size', color='ticker')
    polar.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0,0, 0)',
    })
    polar_r.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0,0, 0)',
    })
    sun_t.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0,0, 0)',
    })
    sun_r.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0,0, 0)',
    })
    twitter_mention.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0,0, 0)',
    })
    reddit_mention.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0,0, 0)',
    })
    return polar, polar_r, sun_t, sun_r, twitter_mention, reddit_mention

polar, polar_r, sun_t, sun_r, twitter_mention, reddit_mention= main(lookback_hours)

