import plotly.utils
from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
import yaml
import sys
from flask import Markup
import json
from plotly.offline import plot
from plotly.graph_objs import Scatter
sys.path.insert(0, 'F:\Projects-of-all-time\CloudCosmos\september-internship\karunya-univ-july-2021\\tickeralytics')
from tickermain import polar



app = Flask(__name__)

db=yaml.load(open('db.yaml'))
app.config['MYSQL_HOST']=db['mysql_host']
app.config['MYSQL_USER']=db['mysql_user']
app.config['MYSQL_PASSWORD']=db['mysql_password']
app.config['MYSQL_DB']=db['mysql_db']

mysql=MySQL(app)

# signup
@app.route('/',methods=['GET','POST'])
def index():
    if request.method=='POST':
        userDetails=request.form
        name=userDetails['name']
        email=userDetails['email']
        password=userDetails['password']
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO users(name,email,password) VALUES(%s,%s,%s)",(name,email,password))
        mysql.connection.commit()
        cur.close()
        return redirect('/users')
    return render_template('signup.html')

# view all users
@app.route('/users')
def users():
    cur=mysql.connection.cursor()
    resultValue=cur.execute("select * from users")
    if resultValue>0:
        userDetails=cur.fetchall()
        return render_template('user.html',userDetails=userDetails)

# main content
@app.route('/main')
def mainpage():
    graph1JSON = json.dumps(polar, cls=plotly.utils.PlotlyJSONEncoder)

    graph2JSON = json.dumps(polar, cls=plotly.utils.PlotlyJSONEncoder)
    graph3JSON = json.dumps(polar, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('dashboard.html',graph1JSON=graph1JSON,  graph2JSON=graph2JSON, graph3JSON=graph3JSON
                              )

# login
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        userDetails=request.form
        email=userDetails['email']
        password=userDetails['password']
        cur=mysql.connection.cursor()
        email_check=cur.execute("SELECT * FROM users WHERE email=%s",(email,))
        mysql.connection.commit()
        if email_check:
            result=cur.execute("SELECT * FROM users WHERE email=%s and password=%s",(email,password))
            mysql.connection.commit()
            cur.close()
            if result:
                return redirect('/main')
            else:
                return 'Password Incorrect'
        else:
            return 'Sign up to login'
    return render_template('login.html')






if __name__=='__main__':
    app.run(debug=True)