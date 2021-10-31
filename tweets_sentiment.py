import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import json
import csv
import plotly.express as px



df = pd.read_csv('sentiment_data.csv')
df.drop('Unnamed: 0', axis = 'columns', inplace=True)
analyzer = SentimentIntensityAnalyzer()

def vadersentimentanalysis(tweet):
    vs = analyzer.polarity_scores(tweet)
    print(vs,"vs")
    return vs['compound']
df['Vader Sentiment'] = df['TWEETS'].apply(vadersentimentanalysis)
print(df)
print(df.columns)

def vader_analysis(compound):
    if compound >= 0.5:
        return 'Positive'
    elif compound <= -0.5 :
        return 'Negative'
    else:
        return 'Neutral'

df['Vader Analysis'] = df['Vader Sentiment'].apply(vader_analysis)
print(df.head())
df.to_csv("sentiment_on_tweets.csv")

cnt= dict(df.ticker.value_counts())
print(dict(cnt))
print(type(cnt))
df["mentions"]=''

for index, row in df.iterrows():
    df.at[index,'mentions']=cnt[row['ticker']]

tweet_sent = df.groupby(df.columns.tolist(), as_index=False).size()

