# Requirements
* Python 3.9
* Virtual environment

# Dev environment

## Mac instructions

### conda

```
conda create -p conda-venv python
conda activate conda-venv
conda install --file requirements.txt

# conda does not have twint
pip install twint
# need the latest twint
pip install --upgrade "git+https://github.com/twintproject/twint.git@origin/master#egg=twint"
```

## Windows instructions

# Running project

## Gather tweets(Twitter Repo)
```
cd twitter
python tweets_gather.py
cd ..
```
## Steps to Run Reddit(NLP-macros Repo)

1. `` python data1.py ``
   * To Collect the tickers name and store them in a pickle.
2. `` python data.py ``
   * To Collect the missing tickers and load the pickle(previously generated) into a list.
3. `` python red_tick.py ``
   * To use the previously created list and filter the posts from reddit based on the occurrence of the tickers 
   * Store the data collected in the form of a csv
   * Column names of the CSV file consists of:
     * Title
     * Date
     * Time
     * Number of comments
     * Score
     * Upvote count
     * Ticker name
     
## python stramlit app
```
streamlit python streamlit_app.py
```

