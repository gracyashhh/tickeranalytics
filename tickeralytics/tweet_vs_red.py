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
from nltk.sentiment import SentimentIntensityAnalyzer

TWITTER_HANDLES = {"spacguru", "satorimind", "daddyspac", "doctorspac", "spac_insider", "spacresearch",
                   "mrzackmorris", "thetawarrior", "traderstewie", "malibuinvest"}
DATE_TIME_FIELD = "date"
TICKER_FIELD = "ticker"
DEFAULT_LIMIT_ROWS = 10

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
website_selector = st.sidebar.selectbox('Select website for analysis', ('Twitter', 'Reddit', 'Twitter vs Reddit'))

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

lookback_hours_select = st.select_slider(
    'Select a lookback period',
    options=list(lookback_hours_dict.keys()))

lookback_hours = lookback_hours_dict[lookback_hours_select]


def twitter_analyse(lookback_hours):

    @st.cache
    def get_all_tweets(handles):
        all_tweets = {}
        for handle in handles:
            with open(f"D://web scrap//twitter analysis//venv//virtEnviron//twitter/{handle}_tweets.pickle",
                      "rb") as dump_file:
                all_tweets[handle] = pickle.load(dump_file)
            break

        return all_tweets

    all_tweets = get_all_tweets(TWITTER_HANDLES)
    analysis = []
    for handle, tweets in all_tweets.items():
        for tweet in tweets:
            print(tweet.tweet)
            if len(tweet.cashtags) > 0:
                print(tweet.cashtags)
                for cashtag in tweet.cashtags:
                    x = str(tweet.datetime)
                    date = x[0:19]
                    y = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                    analysis.append((y, cashtag.upper()))
    data = pd.DataFrame(analysis)
    data.columns = [DATE_TIME_FIELD, TICKER_FIELD]
    data.date = pd.to_datetime(data.date)

    # data

    def add_one(x):
        return x + 1

    datanew = data
    print("LENGTH", type(len(data)))
    # for i in range(1,len(data)):
    #     i
    #     data[i]
    #     datanew[i] = data[i].apply(add_one)
    # datanew
    # dates=data["date"].tolist()
    # date=[]
    # for i in range(len(data)):
    #     tackle =  datetime.fromtimestamp(1140825600)
    #     date.append(tackle)
    # # date
    # print(date)
    # print("DATE")
    # print(dates)
    # chart=plt.plot_date(dates, data["ticker"].tolist())
    # plt.tight_layout()
    # st.write(chart[0])

    # lookback_hours_dict = {'1 hour': 1, '4 hours': 4, '12 hours': 12,
    #                        '1 day': 24, '1 week': 24 * 7, '2 weeks': 24 * 15, '1 month': 24 * 30}
    #
    # lookback_hours_select = st.select_slider(
    #     'Select a lookback period',
    #     options=list(lookback_hours_dict.keys()))
    #
    # lookback_hours = lookback_hours_dict[lookback_hours_select]

    col1, col2 = st.beta_columns(2)

    limit_rows = DEFAULT_LIMIT_ROWS

    hours_filtered, filtered_value_counts_reset = filter_data(data, lookback_hours, limit_rows)
    ticker_mention_chart = (alt.Chart(filtered_value_counts_reset)
                        .mark_bar().encode(y=alt.Y('ticker', sort='-x'), x=alt.X('mentions')))
    # col1.altair_chart(alt.Chart(filtered_value_counts_reset)
    #                   .mark_bar().encode(y=alt.Y('ticker', sort='-x'), x=alt.X('mentions')))

    top_tickers = filtered_value_counts_reset.ticker.to_list()

    # selected_sector = st.sidebar.multiselect('Sector', top_tickers, top_tickers)
    # sort_emotion = st.sidebar.selectbox('Sort values based on emotions', ('No', 'Yes'))

    trendline_chart = (alt.Chart(hours_filtered).transform_window(
        cuml='count()',
        groupby=['ticker'],
        sort=[{'field': 'date'}],
        frame=[None, 0]
    ).mark_line(
    ).encode(
        x='date:T',
        y=alt.Y('cuml:Q'),
        color='ticker'
    ).transform_filter({'field': 'ticker', 'oneOf': top_tickers}))

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

    # test_col=st.beta_columns(1)
    # filtered_value_counts_reset
    # fig = px.bar(filtered_value_counts_reset, x="ticker", y="mentions", color="ticker",
    #              pattern_shape="ticker", pattern_shape_sequence=[".", "x", "+"])
    # fig.show()
    # st.plotly_chart(fig)

    data = data.set_index('date')
    # st.line_chart(data)

    input_col, pie_col = st.beta_columns(2)
    data = data.reset_index()
    data.columns = ['date', 'ticker']
    print(data)
    fig2 = px.pie(data)
    # input_col.write(fig2, values='date', names='ticker')

    return ticker_mention_chart, trendline_chart, scatter_plot, treeMap, sunBurst


def reddit_analyse(lookback_hours):

    @st.cache
    def load_data():
        df = pd.read_csv("wallstreetbets.csv", index_col="Date")
        sent_df = pd.read_csv("ticker_list.csv")
        df.drop("Unnamed: 0", axis=1, inplace=True)
        sent_df.rename(columns={'Unnamed: 0': "Tickers",
                                "neg": "Negative", "neu": "Neutral",
                                "pos": "Positive", "compound": "Compound"}, inplace=True)
        column_df = sent_df.select_dtypes(['float', 'int'])
        column = list(column_df.columns)
        tickers = list(sent_df["Tickers"])
        return df, sent_df, tickers, column

    df, sent_df, ticker_list, col_list = load_data()

    d1 = st.sidebar.checkbox("Display wallstretbets Dataset")
    d2 = st.sidebar.checkbox("Display sentimental Dataset")

    if d1:
        st.write("""
            ### *Wallstreetbets dataset*
            """)
        st.write(df)
    if d2:
        st.write("""
            ### *Sentimental ticker dataset*
            """)
        st.write(sent_df)

    analysis = []
    with open("wallstreetbets.csv", "r", encoding="utf8") as f:
        read = csv.reader(f)
        next(read)
        for r in read:
            analysis.append((r[4], r[10]))

    print(analysis)
    data = pd.DataFrame(analysis)
    data.columns = [DATE_TIME_FIELD, TICKER_FIELD]
    data.date = pd.to_datetime(data.date)
    print(data)

    # date_dict = {'1 hour': 1, '4 hours': 4, '12 hours': 12, "1 day": 24, "2 days": 24 * 2, "3 days": 24 * 3,
    #              "1 week": 24 * 7, "1 month": 24 * 30}
    #
    # hr_select = st.select_slider(
    #     "Select a lookback period",
    #     options=list(date_dict.keys())
    # )
    #
    # lookback_hours = date_dict[hr_select]

    col1, col2 = st.beta_columns(2)

    hrs_filtered, count_reset = filter_data(data, lookback_hours, limit_rows=DEFAULT_LIMIT_ROWS)
    reddit_mention = (alt.Chart(count_reset)
                      .mark_bar().encode(y=alt.Y('ticker', sort='-x'), x=alt.X('mentions')))

    top_tickers = count_reset.ticker.to_list()

    reddit_trendline = (alt.Chart(hrs_filtered).transform_window(
        cuml='count()',
        groupby=['ticker'],
        sort=[{'field': 'date'}],
        frame=[None, 0]
    ).mark_line().encode(
        x='date:T',
        y=alt.Y('cuml:Q'),
        color='ticker'
    ).transform_filter({'field': 'ticker', 'oneOf': top_tickers}))

    model = st.beta_container()
    # with model:
    #     st.title("Plotting graph")
    #     col1, col2 = st.beta_columns(2)

        # ticker_choice = col1.selectbox(label="Ticker to plot", options=ticker_list)
        # plot_choice = col2.multiselect(label="Sentiment of ticker", options=col_list)
        #
        # data = df
        #
        # data = data[data["Tickers"] == ticker_choice]
        # df_up = data["Upvote"]
        #
        # plot_fig1 = px.bar(data_frame=df_up, x=df_up.index, y="Upvote", title=str(ticker_choice) + ' upvote score')
        # col1.plotly_chart(plot_fig1)
        #
        # if len(plot_choice) == 0:
        #     col2.text("Sentimental graph will be displayed here")
        # else:
        #     sent_df = sent_df[sent_df["Tickers"] == ticker_choice]
        #     df_plot = sent_df[plot_choice]
        #     if len(df_plot) > 0:
        #         plot_fig = px.bar(data_frame=df_plot, x=df_plot.index, y=plot_choice,
        #                           title=str(ticker_choice) + ' sentiment analysis')
        #         col2.plotly_chart(plot_fig)

    graph = st.beta_container()
    with graph:
        scatter = px.scatter(data_frame=df, x=df.index, y='Tickers', template='simple_white')

        tree = px.treemap(data_frame=df, path=['Tickers'])

    return reddit_mention, reddit_trendline, scatter, tree


if website_selector == 'Twitter':
    st.title('Twitter Analysis')
    mention_chart, trendline_chart, scatter_plot, treeMap, sunBurst = twitter_analyse(lookback_hours)
    col1,col2 = st.beta_columns(2)
    col1.altair_chart(mention_chart)
    col2.altair_chart(trendline_chart)
    st.plotly_chart(scatter_plot)
    st.plotly_chart(treeMap)
    st.plotly_chart(sunBurst)

elif website_selector == 'Reddit':
    st.title('Reddit Analysis')
    reddit_mention, reddit_trendline, scatter, tree = reddit_analyse(lookback_hours)
    col1, col2 = st.beta_columns(2)
    col1.altair_chart(reddit_mention)
    col2.altair_chart(reddit_trendline)
    st.plotly_chart(scatter)
    st.plotly_chart(tree)

else:
    st.title('Twitter vs Reddit')
    ticker_mention, trendline_chart, scatter_plot, treeMap, sunBurst = twitter_analyse(lookback_hours)
    reddit_mention, reddit_trendline, reddit_scatter, reddit_tree = reddit_analyse(lookback_hours)

    col1, col2 = st.beta_columns(2)
    col1.title('Twitter')
    col2.title('Reddit')

    mentions = st.beta_container()
    trendline = st.beta_container()
    scatter = st.beta_container()
    tree = st.beta_container()

    with mentions:
        mentions.write(f"Ticker mentions (top{DEFAULT_LIMIT_ROWS}) in the last {lookback_hours_select}")
        c1, c2 = mentions.beta_columns(2)
        # c1.write(f"Ticker mentions (top{DEFAULT_LIMIT_ROWS}) in the last {lookback_hours_select}")
        c1.altair_chart(ticker_mention)
        # c2.write(f"Ticker mentions (top{DEFAULT_LIMIT_ROWS}) in the last {lookback_hours_select}")
        c2.altair_chart(reddit_mention)

    with trendline:
        trendline.write(f"Ticker trendline (top{DEFAULT_LIMIT_ROWS}) in the last {lookback_hours_select}")
        c1, c2 = trendline.beta_columns(2)
        # c1.write(f"Ticker trendline (top{DEFAULT_LIMIT_ROWS}) in the last {lookback_hours_select}")
        c1.altair_chart(trendline_chart)
        # c2.write(f"Ticker trendline (top{DEFAULT_LIMIT_ROWS}) in the last {lookback_hours_select}")
        c2.altair_chart(reddit_trendline)

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


