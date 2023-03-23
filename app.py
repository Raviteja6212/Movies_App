import csv
import os
from flask import Flask,  render_template, request, redirect, url_for
from jinja2 import Template
import sqlite3

app = Flask(__name__)

@app.route("/",methods=["GET","POST"])
def index(message=""):
    if request.method=="POST":
        username = request.form.getlist('username')[0]
        password = request.form.getlist('password')[0]
        try:
            print("TEST")
            sqliteConnection = sqlite3.connect('database.db')
            cursor = sqliteConnection.cursor()
            sqlite_select_Query = "select * from users_data;"
            cursor.execute(sqlite_select_Query)
            record = cursor.fetchall()
            venues_query = "select * from venues;"
            cursor.execute(venues_query)
            venues = cursor.fetchall()
            shows_query = "select * from shows;"
            cursor.execute(shows_query)
            shows = cursor.fetchall()
            venue_shows = {}
            for i in shows:
                if i[2] in venue_shows.keys():
                    venue_shows[i[2]]["shows"].append(i)
                else:
                    for j in venues:
                        if j[0]==i[2]:
                            venue_shows[i[2]]={}
                            venue_shows[i[2]]["venue"]=j
                            venue_shows[i[2]]["shows"]=[]
                            venue_shows[i[2]]["shows"].append(i)
                    
            cursor.close()

        except sqlite3.Error as err:
            print("Error while connecting to sqlite", err)
        
        print("venue shows are as follows")
        print(venue_shows)
        for i in record:
            if i[1]==username and i[2]==password:
                return render_template("homepage.html",username=username,venuelist=venue_shows)
        return render_template("errorpage.html")
    else:
        return render_template("index.html",error=message)

@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method=="GET":
        return render_template("singupPage.html")
    else:
        username = request.form.getlist('username')[0]
        password = request.form.getlist('password')[0]

        try:
            sqliteConnection = sqlite3.connect('database.db')
            cursor = sqliteConnection.cursor()
            sqlite_select_Query = "select * from users_data;"
            cursor.execute(sqlite_select_Query)
            record = cursor.fetchall()

        except sqlite3.Error as error:
            print("Error while connecting to sqlite", error)
        
        for i in record:
            if i[1]==username:
                return render_template("singupPage.html",error="Username already exists !!")
        
        Insert_Query = "INSERT INTO users_data (username,password) VALUES (?,?)"
        cursor.execute(Insert_Query,(username,password))
        sqliteConnection.commit()
        cursor.close()
        
        return redirect(url_for('index',error="User created successfully, you can login now:)Y"))


@app.route("/showDetails",methods=["GET","POST"])
def ViewShow():
    if request.method=="POST":
        show_id = request.form['show_id']
        sqliteConnection = sqlite3.connect('database.db')
        cursor = sqliteConnection.cursor()
        shows_query = "select * from shows;"
        cursor.execute(shows_query)
        shows = cursor.fetchall()
        venues_query = "select * from venues;"
        cursor.execute(venues_query)
        venues = cursor.fetchall()
        print("This is the show id received - ")
        print(show_id) 
        for i in shows:
            print("this is the show id - ")
            print(i[0])
            print("this is the received id - ")
            print(show_id) 
            if int(show_id)==i[0]: 
                for j in venues:
                    if j[0]==i[2]: 
                        return render_template("showdetails.html",showdata=i,venuedata=j)
        
        return render_template("errorpage.html")

if __name__=="__main__":
    app.run(debug=True)
    