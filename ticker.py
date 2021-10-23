import pandas as pd
import pickle
import csv
from datetime import datetime
import plotly.express as px
import sys
import yfinance as yf
from plotly.subplots import make_subplots
import plotly.graph_objects as go
sys.path.insert(0, 'F:\Projects-of-all-time\CloudCosmos\september-internship\karunya-univ-july-2021\\tickeralytics')
from tweets_sentiment import tweet_sent
from reddit_sentiment import red_sent

class analytics:
    def __init__(self):
        self.TWITTER_HANDLES = {"spacguru", "satorimind", "daddyspac", "spac_insider", "spacresearch",
                           "mrzackmorris", "thetawarrior", "traderstewie", "malibuinvest"}
        self.DATE_TIME_FIELD = "date"
        self.DEFAULT_LIMIT_ROWS = 50
        self.top_tickers = []
        self.TICKER_FIELD='ticker'
    def filter_data(self,data, hours, limit_rows=50):
        max_date_in_data = data[self.DATE_TIME_FIELD].max()
        cutoff_date = max_date_in_data - pd.Timedelta(hours=hours)
        hours_filtered = data[data[self.DATE_TIME_FIELD] > cutoff_date]

        filtered_value_counts = hours_filtered[self.TICKER_FIELD].value_counts()
        filtered_value_counts_reset = filtered_value_counts.reset_index()
        filtered_value_counts_reset.columns = ["ticker", "mentions"]
        return hours_filtered, filtered_value_counts_reset.head(limit_rows)

    lookback_hours = 24*30
    tweet_sent.to_csv('tweet_sent.csv')
    red_sent.to_csv('red_sent.csv')

    def main(self,user_choice='TSLA',lookback_hours=24*30):
        self.user_choice=user_choice
        def get_all_tweets(handles):
            all_tweets = {}
            for handle in handles:
                with open(
                        f"F:\Projects-of-all-time\CloudCosmos\september-internship\karunya-univ-july-2021\\tickeralytics\\twitter\{handle}_tweets.pickle",
                        "rb") as dump_file:
                    all_tweets[handle] = pickle.load(dump_file)
                break
            return all_tweets

        all_tweets = get_all_tweets(self.TWITTER_HANDLES)
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
                        analysis.append((datetime.date(z), cashtag.upper()))
                        data1.append((datetime.date(z), cashtag.upper(), tweet.tweet))

        data = pd.DataFrame(analysis)
        data.columns = [self.DATE_TIME_FIELD, self.TICKER_FIELD]
        data.date = pd.to_datetime(data.date)
        data.to_csv('data.csv')
        sentiment_data = pd.DataFrame(data1)
        sentiment_data.columns = [self.DATE_TIME_FIELD, self.TICKER_FIELD, 'TWEETS']
        sentiment_data.to_csv('sentiment_data.csv')

        limit_rows = self.DEFAULT_LIMIT_ROWS
        hours_filtered, filtered_value_counts_reset = self.filter_data(data, lookback_hours, limit_rows)
        analysis = []

        with open(
                "F:\Projects-of-all-time\CloudCosmos\september-internship\karunya-univ-july-2021\\nlp-macros\wallstreetbets.csv",
                "r", encoding="utf8") as f:
            read = csv.reader(f)
            next(read)
            for r in read:
                analysis.append((r[2], r[-1]))

        data = pd.DataFrame(analysis)
        data.columns = [self.DATE_TIME_FIELD, self.TICKER_FIELD]
        data.date = pd.to_datetime(data.date)

        hrs_filtered, red_filtered_count_reset = self.filter_data(data, lookback_hours, limit_rows=self.DEFAULT_LIMIT_ROWS)

        twitter_tickers = filtered_value_counts_reset.ticker.to_list()
        reddit_tickers = red_filtered_count_reset.ticker.to_list()

        top_tickers = [t for t in twitter_tickers if t in reddit_tickers]

        dff = hrs_filtered.groupby(hrs_filtered.columns.tolist(), as_index=False).size()
        reddit_filter = dff[dff['ticker'].isin(top_tickers)]
        reddit_filter.drop_duplicates()

        dff1 = hours_filtered.groupby(hours_filtered.columns.tolist(), as_index=False).size()
        twitter_filter = dff1[dff1['ticker'].isin(top_tickers)]
        twitter_filter.drop_duplicates()

        data_r = pd.DataFrame(analysis)
        data_r.columns = [self.DATE_TIME_FIELD, self.TICKER_FIELD]
        data_r.date = pd.to_datetime(data.date)
        hrs_filtered, red_filtered_count_reset = self.filter_data(data, lookback_hours, limit_rows=self.DEFAULT_LIMIT_ROWS)

        twitter_tickers = filtered_value_counts_reset.ticker.to_list()
        reddit_tickers = red_filtered_count_reset.ticker.to_list()

        top_tickers = [t for t in twitter_tickers if t in reddit_tickers]

        dff = hrs_filtered.groupby(hrs_filtered.columns.tolist(), as_index=False).size()
        reddit_filter = dff[dff['ticker'].isin(top_tickers)]
        reddit_filter.drop_duplicates()

        dff1 = hours_filtered.groupby(hours_filtered.columns.tolist(), as_index=False).size()
        twitter_filter = dff1[dff1['ticker'].isin(top_tickers)]
        twitter_filter.drop_duplicates()

        tweet_sent['Type'] = 'Twitter'
        red_sent['Type'] = 'Reddit'

        tweet_sent.date = pd.to_datetime(tweet_sent.date)
        red_sent.date = pd.to_datetime(red_sent.date)

        tweet_sent1, h = self.filter_data(tweet_sent, lookback_hours, limit_rows)
        tweet_sent1.drop_duplicates()
        # user_choice = 'TSLA'
        tweet_sent1 = tweet_sent[tweet_sent['ticker'].isin(top_tickers)]
        red_sent1 = red_sent[red_sent['ticker'].isin(top_tickers)]
        red_sent1.drop_duplicates()
        tweet_sent.to_csv('tweet_sent1.csv')

        # rachel portion

        main_df = pd.concat([tweet_sent, red_sent])


        # self.user_choice = list(self.user_choice)

        main_df = main_df[main_df['ticker']==self.user_choice]
        main_df.date = pd.to_datetime(main_df.date)
        self.user_df, h = self.filter_data(main_df, lookback_hours, limit_rows)
        main_df = self.user_df.groupby(["date", "ticker", "Type"]).size().reset_index(name="occurance")

        #ends here



        polar = px.scatter_polar(tweet_sent[:65], r="date", theta="ticker", color="ticker", size="mentions",
                                 symbol="Vader Analysis")
        polar_r = px.scatter_polar(red_sent[:85], r="date", theta="ticker", color="ticker", size="mentions",
                                   symbol="Vader Analysis")

        sun_t = px.sunburst(tweet_sent1, path=['ticker', 'date', 'Vader Analysis'],
                            title='Twitter',
                            values='size',
                            maxdepth=2,
                            color='Vader Analysis',
                            color_discrete_map={'Neutral': '#636EFA',
                                                'Positive': '#00CC96', 'Negative': '#EF553B'}
                            )
        sun_r = px.sunburst(red_sent1, path=['ticker', 'date', 'Vader Analysis'],
                            title='Reddit',
                            values='size',
                            maxdepth=2,
                            color='Vader Analysis',
                            color_discrete_map={'Neutral': '#636EFA',
                                                'Positive': '#00CC96', 'Negative': '#EF553B'}
                            )
        print('##### ', red_sent, type(red_sent))
        twitter_mention = px.line(main_df, x='date', y='occurance', color='Type',
                            color_discrete_map={'Twitter': '#636EFA',
                                                'Reddit': '#EF553B'},title=user_choice
                            )

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
        ticker = user_choice
        i = "30m"
        p = 30
        stock = yf.Ticker(ticker)
        history_data = stock.history(interval=i, period=str(p) + "d")
        fig = make_subplots(
            rows=1, cols=2,
            column_widths=[0.2, 0.8],
            specs=[[{}, {}]],
            horizontal_spacing=0.01
        )
        dateStr = history_data.index.strftime("%d-%m-%Y")
        fig.add_trace(
            go.Candlestick(x=dateStr,
                           open=history_data['Open'],
                           high=history_data['High'],
                           low=history_data['Low'],
                           close=history_data['Close'],
                           yaxis="y2"
                           ),
            row=1, col=2
        )
        fig.update_layout(
            title_text=user_choice,  # title of plot
            bargap=0.01,  # gap between bars of adjacent location coordinates,
            showlegend=False,
            xaxis=dict(
                showticklabels=False
            ),
            yaxis=dict(
                showticklabels=False
            ),
            yaxis2=dict(
                title="Price (USD)",
                side="right"
            )
        )
        fig.update_yaxes(nticks=20)
        fig.update_yaxes(side="right")
        fig.update_layout(height=515)
        fig.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0,0, 0)',
        })

        # reddit_mention.update_layout({
        #     'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        #     'paper_bgcolor': 'rgba(0, 0,0, 0)',
        # })
        return polar, polar_r, sun_t, sun_r, twitter_mention, fig


    # polar, polar_r, sun_t, sun_r, twitter_mention, reddit_mention = main(lookback_hours)


