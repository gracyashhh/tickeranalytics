import streamlit as st
import pandas as pd
import pickle
import csv
import altair as alt
from datetime import datetime
import numpy as np
import plotly.express as px
import base64
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from nltk.sentiment import SentimentIntensityAnalyzer
from reddit_sentiment import red_sent
from PIL import Image


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
website_selector = st.sidebar.selectbox('Select website for analysis', ( 'Twitter & Reddit','Twitter vs Reddit'))

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
            with open(f"twitter/{handle}_tweets.pickle",
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

    print(type(filtered_value_counts_reset))

    scatter_plot = px.scatter(data, x="date", y="ticker",
                              template="simple_white")

    treeMap = px.treemap(
        data_frame=data,
        values='date',
        path=['ticker'],
    )

    sunBurst = px.sunburst(
        data_frame=data,
        path=['ticker'],
        values='date',
        template="simple_white",
        title = 'Sun Burst'
    )

    return scatter_plot, treeMap, sunBurst

from tweets_sentiment import tweet_sent
tweet_sent.to_csv('tweet_sent.csv')
def reddit_analyse(lookback_hours):

    df = pd.read_csv("../nlp-macros/wallstreetbets.csv")
    df.drop("Unnamed: 0", axis=1, inplace=True)

    d1 = st.sidebar.checkbox("Display wallstretbets Dataset")

    if d1:
        st.write("""
            ### *Wallstreetbets dataset*
            """)
        st.write(df)

    analysis = []
    with open("../nlp-macros/wallstreetbets.csv", "r", encoding="utf8") as f:
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

    # st.write(top_tickers)

    #selecting only the rows whose tickers are in top ten list
    final_reddit = red_filtered_count_reset.loc[red_filtered_count_reset['ticker'].isin(top_tickers)]
    final_twitter = filtered_value_counts_reset.loc[filtered_value_counts_reset['ticker'].isin(top_tickers)]

    dff = hrs_filtered.groupby(hrs_filtered.columns.tolist(), as_index=False).size()
    reddit_filter = dff[dff['ticker'].isin(top_tickers)]
    reddit_filter.drop_duplicates()

    dff1 = hours_filtered.groupby(hours_filtered.columns.tolist(), as_index=False).size()
    twitter_filter = dff1[dff1['ticker'].isin(top_tickers)]
    twitter_filter.drop_duplicates()

    tweet_sent1 = tweet_sent[tweet_sent['ticker'].isin(top_tickers)]
    tweet_sent1.drop_duplicates()
    tweet_sent1.set_index('ticker')

    red_sent1 = red_sent[red_sent['ticker'].isin(top_tickers)]
    red_sent1.drop_duplicates()

    graph = st.beta_container()
    df = df[df['Tickers'].isin(top_tickers)]

    s1 = st.sidebar.checkbox("Display twitter sentiment Dataset")
    s2 = st.sidebar.checkbox("Display reddit sentiment Dataset")

    if s1:
        st.write("""
                ### *twitter sentiment*
                """)
        st.write(tweet_sent1)

    if s2:
        st.write("""
                ### *reddit sentiment*
                """)
        st.write(red_sent1)

    #multiselector
    # options = st.multiselect('Multiselect tickers', top_tickers)
    #
    #
    # reddit_filter = reddit_filter[reddit_filter['ticker'].isin(options)]  #reddit filtered data based on multiselect options
    # twitter_filter = twitter_filter[twitter_filter['ticker'].isin(options)] #twitter filtered data based on multiselect options


    with graph:
        scatter = px.scatter(data_frame=df, x='Date', y='Tickers', template='simple_white')

        tree = px.treemap(data_frame=df, path=['Tickers'])

        date_mention = px.line(reddit_filter,x='date',y='size',color='ticker')

        twitter_mention = px.line(twitter_filter, x='date', y='size', color='ticker')

        fig2 = go.Figure(data=[
            go.Bar(name='REDDIT', x=list(final_reddit.ticker), y=list(final_reddit.mentions),
                   marker={'color': final_reddit.mentions,
                           'colorscale': 'rainbow'}),
            go.Bar(name='TWITTER', x=list(final_twitter.ticker), y=list(final_twitter.mentions),
                   marker={'color': final_twitter.mentions,
                           'colorscale': 'rainbow'})
        ])
        fig2.update_layout(barmode='group')


        tweet_chart = px.bar(tweet_sent1, x='ticker', y='mentions',
                           hover_data=['Vader Analysis', 'mentions'], color='Vader Sentiment',
                           labels={'mentions': 'Number of Mentions', 'ticker': 'Top 10 Tickers from Twitter'},
                           barmode='group', height=400)

        red_chart = px.bar(red_sent1, x='ticker', y='mentions',
                             hover_data=['Vader Analysis', 'mentions'], color='Vader Sentiment',
                             labels={'mentions': 'Number of Mentions', 'ticker': 'Top 10 Tickers from Reddit'},
                             barmode='group', height=400)
        pie = px.pie(tweet_sent1, values='mentions', names='ticker', title='Number of Mentions-Twitter')
        pie.update_traces(textposition='inside', textinfo='percent+label')
        # st.plotly_chart(pie)
        pie2 = px.pie(red_sent1, values='mentions', names='ticker', title='Number of Mentions-Reddit')
        pie2.update_traces(textposition='inside', textinfo='percent+label')
        polar=px.scatter_polar(tweet_sent[:50], r="date", theta="ticker",color="ticker",size="mentions",symbol="Vader Analysis")

        # polar=px.line_polar(tweet_sent[:10], r="date", theta="ticker",color="ticker",line_close="True",template="plotly_dark")

        # polar=px.line_polar(tweet_sent, r="date", theta="mentions",color="ticker",line_close="True",template="plotly_dark")

        # polar.show()
        violin=px.violin(tweet_sent,y="mentions",x="Vader Analysis",color="ticker",box=True,points='all',hover_data=tweet_sent.columns)
        heatmap=px.density_heatmap(tweet_sent,x="mentions",y="date",z="ticker",color_continuous_scale="Viridis")
        print(df)
        # st.plotly_chart(pie2)
    return twitter_mention, date_mention, scatter, tree, tweet_chart, red_chart,pie,pie2,polar,violin,heatmap,fig2

if website_selector=="Twitter & Reddit":
    scatter_plot, treeMap, sunBurst = twitter_analyse(lookback_hours)
    twitter_mention, date_mention, reddit_scatter, reddit_tree, tweet_chart, red_chart ,pie,pie2,polar,violin,heatmap,fig2= reddit_analyse(lookback_hours)
    polar

elif website_selector == "Twitter vs Reddit":
    st.title('Twitter vs Reddit')
    scatter_plot, treeMap, sunBurst = twitter_analyse(lookback_hours)
    twitter_mention, date_mention, reddit_scatter, reddit_tree, tweet_chart, red_chart ,pie,pie2,polar,violin,heatmap,fig2= reddit_analyse(lookback_hours)

    col1, col2,col3,col4,col5 = st.beta_columns(5)
    imgt = Image.open("tweet.jpg")

    imgt=imgt.resize((170,170))
    imgr = Image.open("reddit.jpg")
    imgr=imgr.resize((140,140))

    col2.image(imgt)
    col5.image(imgr)
    fig2
    polar
    violin
    heatmap
    trendline = st.beta_container()
    mentions = st.beta_container()
    piechart= st.beta_container()
    scatter = st.beta_container()
    tree = st.beta_container()

    with trendline:
        trendline.write(f"Ticker trendline (common tickers) in the last {lookback_hours_select}")
        c1, c2 = trendline.beta_columns(2)
        c1.plotly_chart(twitter_mention)
        c2.plotly_chart(date_mention)

    with mentions:
        mentions.write(f"Ticker mentions (common tickers) in the last {lookback_hours_select}")
        c1, c2 = mentions.beta_columns(2)
        c1.plotly_chart(tweet_chart)
        c2.plotly_chart(red_chart)

    with scatter:
        scatter.write('Scatter Plot')
        c1, c2 = scatter.beta_columns(2)
        c1.plotly_chart(scatter_plot)
        c2.plotly_chart(reddit_scatter)

    with tree:
        tree.write('Tree Map')
        c1, c2 = tree.beta_columns(2)
        c1.plotly_chart(treeMap)
        c2.plotly_chart(reddit_tree)
        c1.plotly_chart(sunBurst)
    with piechart:
        piechart.write('Pie Chart')
        piechart.plotly_chart(pie)
        piechart.plotly_chart(pie2)

