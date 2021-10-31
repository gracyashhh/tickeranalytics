import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import json
import csv
import plotly.express as px


data = []
with open('F:\Projects-of-all-time\CloudCosmos\september-internship\karunya-univ-july-2021\\nlp-macros\wallstreetbets.csv', 'r', encoding='utf8') as f:
    read = csv.reader(f)
    next(read)
    for r in read:
        data.append((r[2], r[-1], r[1]))

df = pd.DataFrame(data)
df.columns = ['date', 'ticker', 'TWEETS']

analyzer = SentimentIntensityAnalyzer()

def reddit_sentiment(tweet):
    vs = analyzer.polarity_scores(tweet)
    print(vs,"vs")
    return vs['compound']
df['Vader Sentiment'] = df['TWEETS'].apply(reddit_sentiment)
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

df.to_csv("sentiment_on_reddit.csv")

cnt= dict(df.ticker.value_counts())
print(dict(cnt))
print(type(cnt))
df["mentions"]=''

for index, row in df.iterrows():
    df.at[index,'mentions']=cnt[row['ticker']]

red_sent = df.groupby(df.columns.tolist(), as_index=False).size()
