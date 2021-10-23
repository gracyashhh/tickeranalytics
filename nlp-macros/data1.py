import csv
import pickle

'''includes US stock symbols with market cap > 100 Million, and price above $3. As wsb doesn't allow
penny stocks discussions.
Download the csv file  https://www.nasdaq.com/market-activity/stocks/screener?exchange=nasdaq&letter=0&render=download
of all the NYSE, NASDAQ and NYSEAMERICAN public traded companies.
'''
ticker_list=[]
with open ("nasdaq_screener_1628247557520.csv", 'r', encoding='utf8') as f:
    read = csv.reader(f)
    next(read)
    for r in read:
        ticker_list.append(r[0])

print(ticker_list)

fn1 = 'ticker_ls'
outfile = open(fn1,'wb')
pickle.dump(ticker_list,outfile)
outfile.close()
