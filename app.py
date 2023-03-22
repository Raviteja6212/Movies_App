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
        venues=[
            {"venue":"venue-1","shows":["10:30","10:40","10:50","11:00"]},
            {"venue":"venue-2","shows":["10:30","10:40","10:50"]},
            {"venue":"venue-3","shows":["10:30","10:40"]},
            {"venue":"venue-4","shows":["10:30"]}]
        try:
            sqliteConnection = sqlite3.connect('database.db')
            cursor = sqliteConnection.cursor()
            sqlite_select_Query = "select * from users_data;"
            cursor.execute(sqlite_select_Query)
            record = cursor.fetchall()
            cursor.close()

        except sqlite3.Error as err:
            print("Error while connecting to sqlite", err)
        
        for i in record:
            if i[1]==username and i[2]==password:
                return render_template("homepage.html",username=username,venuelist=venues)
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

if __name__=="__main__":
    app.run(debug=True)
    