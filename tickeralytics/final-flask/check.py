from flask import Flask
from flask import render_template
import pandas as pd
import json
import plotly
import plotly.express as px
import sys
sys.path.insert(0, 'F:\Projects-of-all-time\CloudCosmos\september-internship\karunya-univ-july-2021\\tickeralytics')
from tickermain import polar
app=Flask(__name__)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/chart1')
def chart1():
    graph1JSON = json.dumps(polar, cls=plotly.utils.PlotlyJSONEncoder)

    # Graph two

    graph2JSON = json.dumps(polar, cls=plotly.utils.PlotlyJSONEncoder)

    # Graph three
    df = px.data.gapminder().query("continent=='Oceania'")
    fig3 = px.line(df, x="year", y="lifeExp", color='country',  title="Life Expectancy")
    graph3JSON = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template('dashboard.html', graph1JSON=graph1JSON,  graph2JSON=graph2JSON, graph3JSON=graph3JSON)

if __name__=="__main__":
    app.run(debug=True)